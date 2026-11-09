import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {Catalog,releaseFacts,gitFacts} from '../../web/catalog/catalog.mjs';
const C='a'.repeat(40),D='b'.repeat(40);
const fixture=name=>readFile(new URL(`../catalog-contract/fixtures/${name}.yaml`,import.meta.url),'utf8');
function transport(files){const calls=[];return {calls,fetcher:async url=>{calls.push(url);const path=new URL(url).pathname.split('/').slice(4).join('/');return new Response(files[path]??'',{status:Object.hasOwn(files,path)?200:404});}};}
test('strict lazy roots, exact IDs, decoded media and URLs',async()=>{
 const net=transport({'catalog.yaml':await fixture('catalog'),'apps.yaml':await fixture('apps'),'repositories/example.yaml':await fixture('repository')});
 const client=new Catalog(net.fetcher),roots=await client.roots(C);
 assert.equal(net.calls.length,2);assert.equal(roots.apps.example,'repositories/example.yaml');
 const source=await client.doc(C,roots.apps.example),r=releaseFacts(source,'9007199254740993');
 assert.equal(source.repository_id,9007199254740993n);assert.equal(r.assets['9007199254740993'].size,9223372036854775807n);
 assert.equal(r.assets['9223372036854775807'].media_type,'application/zip');assert.match(r.assets['789'].url,/app\?x=a:b#part$/);
 await client.doc(C,roots.apps.example);assert.equal(net.calls.length,3);
});
test('cache keys include the immutable pin',async()=>{
 const net=transport({'apps.yaml':await fixture('apps')}),client=new Catalog(net.fetcher);
 await client.doc(C,'apps.yaml');await client.doc(D,'apps.yaml');assert.equal(net.calls.length,2);
});
test('failed reads retry the same path/pin; status failure preserves catalog',async()=>{
 const files={'apps.yaml':await fixture('apps')},net=transport(files),client=new Catalog(net.fetcher);
 const apps=await client.doc(C,'apps.yaml');await assert.rejects(client.report(D));
 await assert.rejects(client.doc(C,'repositories/example.yaml'));
 files['repositories/example.yaml']=await fixture('repository');await client.doc(C,'repositories/example.yaml');
 assert.equal(await client.doc(C,'apps.yaml'),apps);
 assert.equal(net.calls.at(-1),net.calls.at(-2));
});
test('reject paths/pins and cross-kind documents before use',async()=>{
 const net=transport({'apps.yaml':await fixture('catalog')}),client=new Catalog(net.fetcher);
 for(const [pin,path] of [['main','apps.yaml'],[C,'../apps.yaml'],[C,'repositories/a/b.yaml']])await assert.rejects(client.doc(pin,path));
 assert.equal(net.calls.length,0);await assert.rejects(client.doc(C,'apps.yaml'),/kind/);
});
test('refuse unsupported/malformed original bytes and oversized streams',async()=>{
 for(const body of [await fixture('bad-alias'),await fixture('bad-unknown-field'),'x'.repeat(2097153),new Uint8Array([0xff,10])]){
  const client=new Catalog(async()=>new Response(body));await assert.rejects(client.doc(C,'apps.yaml'));
 }
});
test('positive architecture evidence and changed-input refusal',async()=>{
 const net=transport({'provenance/example.yaml':await fixture('provenance')}),client=new Catalog(net.fetcher);
 const source={repository_id:9007199254740993n},root={inputs:{recipes:C,rules:C,schemas:C}};
 const apps={...(await import('../catalog-contract/reader.mjs')).parseDocument(await fixture('apps')).apps};
 const b=await client.provenance(C,'example','repositories/example.yaml',source,root,apps);
 assert.equal(b.aarch64.classification,'shared');assert.equal(b.x86_64.classification,'unknown');
 await assert.rejects(client.provenance(C,'example','repositories/example.yaml',{repository_id:1n},root,apps));
 await assert.rejects(client.provenance(C,'example','repositories/example.yaml',source,{inputs:{recipes:D,rules:C,schemas:C}},apps));
});
test('independent last report and invalid run references',async()=>{
 const files={'status.yaml':await fixture('status'),'runs/123-2/summary.yaml':await fixture('summary')};
 const client=new Catalog(transport(files).fetcher),r=await client.report(D);assert.equal(r.summary.collection,'partial');
 files['runs/123-2/summary.yaml']=files['runs/123-2/summary.yaml'].replace('id: 123','id: 124').replace('/runs/123"','/runs/124"');
 await assert.rejects(new Catalog(transport(files).fetcher).report(D),/identity/);
});
test('leading-equals literals retain exactly one decoded layer',async()=>{
 const source=await new Catalog(transport({'repositories/example.yaml':await fixture('repository-mime-literals')}).fetcher).doc(C,'repositories/example.yaml');
 const values=Object.keys(source.releases).flatMap(id=>Object.values(releaseFacts(source,id).assets).map(a=>a.media_type));
 assert.ok(values.includes('raw'));assert.ok(values.includes('zip'));assert.ok(values.includes('=raw'));
});

test('source failure binds run and identity; unavailable detail is unknown',async()=>{
 const files={'status.yaml':await fixture('status'),'runs/123-2/summary.yaml':await fixture('summary'),'runs/123-2/sources/example.yaml':await fixture('source')};
 const client=new Catalog(transport(files).fetcher),report=await client.report(D),source={repository_id:9007199254740993n,repository:'example/app'};
 assert.equal((await client.sourceReport(D,report,'repositories/example.yaml',source)).outcome,'failed');
 await assert.rejects(client.sourceReport(D,report,'repositories/example.yaml',{...source,repository_id:2n}));
 report.root.details={};assert.equal(await client.sourceReport(D,report,'repositories/example.yaml',source),undefined);
});
test('refuse changed schema input on roots and lazy sources',async()=>{
 const files={'catalog.yaml':(await fixture('catalog')).replace('  schemas: "'+C+'"','  schemas: "'+D+'"'),'apps.yaml':await fixture('apps'),'repositories/example.yaml':await fixture('repository')};
 const client=new Catalog(transport(files).fetcher);await assert.rejects(client.roots(C),/binding/);
 await assert.rejects(client.source(C,'repositories/example.yaml',{inputs:{schemas:D}}),/binding/);
});
test('bundled review uses its own content identity without live channel resolution',async()=>{
 const calls=[],review={pin:C};
 const client=new Catalog(async url=>{calls.push(url);return new Response(await fixture('apps'));},review);
 assert.equal(await client.resolve('release-catalog-v3'),C);
 await assert.rejects(client.resolve('catalog-status-v1'),/not published/);
 await client.doc(C,'apps.yaml');assert.match(calls[0],new RegExp('/review-data/'+C+'/apps.yaml$'));
 await assert.rejects(client.doc(D,'apps.yaml'),/unavailable/);assert.equal(calls.length,1);
});
test('browser fetch keeps its Window receiver for document and channel reads',async()=>{
 function browserFetch(url){
  if(this!==globalThis)throw new TypeError("Failed to execute 'fetch' on 'Window': Illegal invocation");
  return Promise.resolve(new Response(url.includes('api.github.com')?JSON.stringify({object:{sha:C}}):body));
 }
 const body=await fixture('apps');
 const client=new Catalog(browserFetch);
 assert.equal(await client.resolve('release-catalog-v3'),C);
 assert.equal((await client.doc(C,'apps.yaml')).kind,'apps');
});
test('UTF-8 line limit stays exact for ASCII, multibyte and surrogate pairs',async()=>{
 const {parseDocument}=await import('../catalog-contract/reader.mjs'),original=await fixture('repository');
 const prefix='    title: "',suffix='"',room=65536-prefix.length-suffix.length;
 for(const unit of ['a','é','中','🐧']){
  const count=Math.floor(room/new TextEncoder().encode(unit).length);
  const text=original.replace(/^    title: .*$/m,prefix+unit.repeat(count)+suffix);
  assert.doesNotThrow(()=>parseDocument(text));
  assert.throws(()=>parseDocument(original.replace(/^    title: .*$/m,prefix+unit.repeat(count+1)+suffix)),/control\/whitespace/);
 }
});
test('provenance is source-local and refuses incomplete or misplaced identity groups',async()=>{
 const files={'provenance/example.yaml':await fixture('provenance')},net=transport(files),client=new Catalog(net.fetcher);
 const {parseDocument}=await import('../catalog-contract/reader.mjs');
 const apps=parseDocument(await fixture('apps')).apps,source={repository_id:9007199254740993n},root={inputs:{recipes:C,rules:C,schemas:C}};
 await client.provenance(C,'example-nightly','repositories/example.yaml',source,root,apps);
 assert.equal(net.calls.length,1);assert.match(net.calls[0],/\/provenance\/example.yaml$/);
 await assert.rejects(client.provenance(C,'example','repositories/other.yaml',source,root,apps),/source mismatch/);
 const missing=files['provenance/example.yaml'].replace('  "example-nightly":','  "other":');
 await assert.rejects(new Catalog(transport({'provenance/example.yaml':missing}).fetcher).provenance(C,'example','repositories/example.yaml',source,root,apps),/coverage/);
 await assert.rejects(new Catalog(transport({}).fetcher).provenance(C,'example','repositories/example.yaml',source,root,apps),/Unavailable/);
 await assert.rejects(client.doc(C,'provenance.yaml'),/path/);
});

test('Git observations preserve branch/file facts and observed tag positions',()=>{
 const branch={name:'refs/heads/master',commit:'b'.repeat(40),observed_at:'2026-11-09T12:00:00Z',files:{key:{path:'VERSION',content:'1.2\n',blob:'c'.repeat(40)}}};
 const tag=(name,position)=>({name:'refs/tags/'+name,position:BigInt(position)});
 const source={git_refs:{last:tag('v1',2),branch,first:tag('v3',0),middle:tag('v2',1)}};
 assert.deepEqual(gitFacts(source).map(r=>r.name),['refs/heads/master','refs/tags/v3','refs/tags/v2','refs/tags/v1']);
 assert.deepEqual(gitFacts(source,'version'),[branch]);
 assert.deepEqual(gitFacts(source,'unknown'),[]);
 assert.equal(gitFacts(source,'MASTER')[0].files.key.content,'1.2\n');
 assert.deepEqual(gitFacts({}),[]);
});
