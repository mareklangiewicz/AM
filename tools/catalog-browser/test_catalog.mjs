// The page's catalog client: raw main-marek/catalog/ files through a fake fetch.
// Documents are the contract's worked examples (tools/catalog-contract/examples/).
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import {Catalog,RAW,releaseFacts,guess,gitFacts,failure} from '../../web/catalog/catalog.mjs';

const example=name=>readFileSync(new URL(`../catalog-contract/examples/${name}`,import.meta.url),'utf8');
const FILES={'apps.yaml':example('apps.yaml'),'repositories/example.yaml':example('repository.yaml'),
 'status/runs.yaml':example('runs.yaml'),'status/statistics.yaml':example('statistics.yaml')};
function transport(files=FILES,{missing={}}={}) {
 const calls=[],left={...missing};
 const fetcher=async url=>{
  calls.push(url);
  const path=url.startsWith(RAW)?url.slice(RAW.length):null;
  if(path&&left[path]>0){left[path]--;return new Response('404: Not Found',{status:404});}
  return path!==null&&Object.hasOwn(files,path)?new Response(files[path]):new Response('404: Not Found',{status:404});
 };
 return {calls,fetcher};
}
const quick={retryDelay:0};

test('apps first, a repository file only when opened, each read once',async()=>{
 const net=transport(),client=new Catalog(net.fetcher,quick);
 const apps=await client.apps();
 assert.deepEqual(Object.keys(apps),['example','example-nightly']);
 assert.equal(apps.example.repository,'repositories/example.yaml');
 assert.deepEqual(net.calls,[RAW+'apps.yaml']);
 const source=await client.source(apps.example.repository);
 assert.equal(source.repository_id,123n);
 await client.source(apps['example-nightly'].repository);
 assert.deepEqual(net.calls,[RAW+'apps.yaml',RAW+'repositories/example.yaml']);
});

test('release facts fill derived URLs and inherited last-seen times',async()=>{
 const source=await new Catalog(transport().fetcher,quick).source('repositories/example.yaml');
 const old=releaseFacts(source,'9'),twin=releaseFacts(source,'11');
 assert.equal(old.url,'https://github.com/example/app/releases/tag/v1.0');
 assert.equal(old.assets['90'].url,'https://github.com/example/app/releases/download/v1.0/app-x86_64.AppImage');
 assert.equal(old.observed_at,'2026-11-20T10:00:00Z');
 assert.equal(old.own_observation,true);
 assert.equal(twin.observed_at,'2026-11-24T10:00:00Z');
 assert.equal(twin.own_observation,false);
 assert.equal(twin.url,'https://github.com/example/app/releases/tag/nightly-elsewhere');
 assert.equal(twin.assets['110'].url,'https://cdn.example.org/app?x=a:b#part');
 assert.equal(twin.source_zip_url,'https://example.org/src.zip');
 assert.equal(twin.source_tar_url,'https://api.github.com/repos/example/app/tarball/nightly');
});

test('a file the CDN has not served yet is retried; a lasting 404 refuses and a later read retries',async()=>{
 const lagging=transport(FILES,{missing:{'apps.yaml':2}});
 assert.ok(await new Catalog(lagging.fetcher,quick).apps());
 assert.equal(lagging.calls.length,3);
 const gone=transport({}),client=new Catalog(gone.fetcher,quick);
 await assert.rejects(client.apps(),/apps\.yaml \(HTTP 404\)/);
 assert.equal(gone.calls.length,3);
 await assert.rejects(client.apps());
 assert.equal(gone.calls.length,6);
});

test('paths outside catalog/ and documents of the wrong kind are refused before use',async()=>{
 const net=transport({...FILES,'repositories/swapped.yaml':FILES['apps.yaml']}),client=new Catalog(net.fetcher,quick);
 for(const path of ['../apps.yaml','repositories/a/b.yaml','repositories/x.yml','catalog.yaml'])
  await assert.rejects(client.source(path),/path/);
 assert.equal(net.calls.length,0);
 await assert.rejects(client.source('repositories/swapped.yaml'),/kind/);
});

test('malformed and oversized documents are refused',async()=>{
 for(const body of [FILES['apps.yaml'].replace('apps:','# comment\napps:'),'x'.repeat(2097153)]) {
  const client=new Catalog(async()=>new Response(body),quick);
  await assert.rejects(client.apps());
 }
});

test('catalog health reads the runs and the age buckets',async()=>{
 const client=new Catalog(transport().fetcher,quick);
 const runs=await client.runs(),stats=await client.statistics();
 assert.deepEqual(Object.keys(runs),['9-1','10-1','10-2']);
 assert.equal(runs['10-1'].stop_reason,'quota');
 assert.equal(stats.over_14d,14n);
});

test('failures read as sentences',async()=>{
 const source=await new Catalog(transport().fetcher,quick).source('repositories/example.yaml');
 assert.equal(failure(source),"GitHub couldn't be reached.");
 assert.equal(failure({}),null);
});

test('Linux and processor guesses come from platforms.json',()=>{
 assert.deepEqual(guess('KLens-0.6.5-x86_64.AppImage'),{linux:true,arch:'x86_64'});
 assert.deepEqual(guess('k8sdockside-0.1.11-darwin-arm64.dmg'),{linux:false,arch:'aarch64'});
 assert.deepEqual(guess('checksums.txt.sig'),{linux:false,arch:null});
});

test('Git refs list branches first, then tags by position, filtered by name, commit or path',async()=>{
 const source=await new Catalog(transport().fetcher,quick).source('repositories/example.yaml');
 assert.deepEqual(gitFacts(source).map(([name])=>name),['refs/heads/main','refs/tags/v1.0']);
 assert.deepEqual(gitFacts(source,'version.txt').map(([name])=>name),['refs/heads/main']);
});
