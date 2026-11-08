import {parseDocument,releaseFacts} from '../../tools/catalog-contract/reader.mjs';
export {releaseFacts};
export const rawURL=(pin,path)=>`https://raw.githubusercontent.com/mareklangiewicz/AM/${pin}/${path}`;
const commit=/^[a-f0-9]{40}$/;
const catalogPath=/^(catalog|apps)\.yaml$|^(repositories|provenance)\/[a-z0-9][a-z0-9_.+-]{0,63}\.yaml$/;
export const provenancePath=path=>{if(!/^repositories\/[a-z0-9][a-z0-9_.+-]{0,63}\.yaml$/.test(path))throw Error('Invalid provenance source path');return path.replace('repositories/','provenance/');};
const statusPath=/^(status|statistics)\.yaml$|^runs\/[1-9][0-9]*-[1-9][0-9]*\/(summary\.yaml|sources\/[a-z0-9][a-z0-9_.+-]{0,63}\.yaml)$/;
export class Catalog {
 constructor(fetcher=fetch,review=null){this.fetcher=fetcher.bind(globalThis);this.cache=new Map();this.review=review;}
 url(pin,path){return this.review?new URL(`../../review-data/${pin}/${path}`,import.meta.url).href:rawURL(pin,path);}
 async resolve(ref){
  if(!['release-catalog-v3','catalog-status-v1'].includes(ref))throw Error('Unsupported channel');
  if(this.review){if(ref==='catalog-status-v1')throw Error('Health is not published for this review snapshot');return this.review.pin;}
  const r=await this.fetcher(`https://api.github.com/repos/mareklangiewicz/AM/git/ref/heads/${ref}`);
  if(!r.ok)throw Error(`Channel unavailable (HTTP ${r.status})`);
  const pin=(await r.json()).object?.sha;if(!commit.test(pin))throw Error('Invalid channel commit');return pin;
 }
 async doc(pin,path,channel='catalog'){
  if(this.review&&pin!==this.review.pin)throw Error('Review snapshot unavailable in this build; choose Load latest');
  if(!commit.test(pin)||!(channel==='catalog'?catalogPath:statusPath).test(path))throw Error('Invalid pinned path');
  const key=pin+'/'+path;if(this.cache.has(key))return this.cache.get(key);
  const r=await this.fetcher(this.url(pin,path));if(!r.ok)throw Error(`Unavailable ${path} (HTTP ${r.status})`);
  // Enforce the byte bound before materializing an unbounded response body.
  const reader=r.body.getReader(),chunks=[];let length=0;
  try{for(;;){const {done,value}=await reader.read();if(done)break;length+=value.byteLength;if(length>2097152)throw Error('Document byte bound');chunks.push(value);}}
  finally{await reader.cancel();}
  const bytes=new Uint8Array(length);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length;}
  const d=parseDocument(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
  const kind=path.includes('/')?(channel==='catalog'?(path.startsWith('provenance/')?'provenance':'repository'):path.endsWith('/summary.yaml')?'summary':'source'):path.slice(0,-5);
  if(d.kind!==kind)throw Error('Path kind mismatch');
  if(this.cache.size>=64)this.cache.delete(this.cache.keys().next().value);
  this.cache.set(key,d);return d;
 }
 async roots(pin){
  const [root,map]=await Promise.all([this.doc(pin,'catalog.yaml'),this.doc(pin,'apps.yaml')]);
  this.binding(root,root);this.binding(map,root);return {root,apps:map.apps};
 }
 binding(doc,root){if(!doc.schema.includes('/'+root.inputs.schemas+'/'))throw Error('Schema input binding mismatch');return doc;}
 async source(pin,path,root){return this.binding(await this.doc(pin,path),root);}
 async provenance(pin,app,path,source,root,apps){
  if(!apps||apps[app]!==path)throw Error('Provenance app source mismatch');
  const p=this.binding(await this.doc(pin,provenancePath(path)),root);
  const expected=Object.keys(apps).filter(name=>apps[name]===path).sort();
  if(JSON.stringify(Object.keys(p.apps).sort())!==JSON.stringify(expected))throw Error('Provenance app coverage mismatch');
  for(const [name,arches] of Object.entries(p.apps))for(const [arch,b] of Object.entries(arches)){
   if(b.repository_id!==source.repository_id||b.recipe&&(b.recipe.path!==`programs/${arch}/${name}`||b.recipe.commit!==root.inputs.recipes)||b.evidence&&b.evidence.rules!==root.inputs.rules)throw Error('Provenance binding mismatch');
  }
  return p.apps[app];
 }

 async statistics(pin,report){
  const d=await this.doc(pin,'statistics.yaml','status');
  if(!d.schema.includes('/'+report.root.schemas+'/')||Object.keys(d.days).length>90)throw Error('Statistics binding/retention');
  return d;
 }
 async sourceReport(pin,report,path,source){
  const key=`${report.summary.run.id}-${report.summary.run.attempt}`;
  if(!Object.hasOwn(report.root.details,key))return undefined;
  const name=path.slice('repositories/'.length,-5);
  const d=await this.doc(pin,`runs/${key}/sources/${name}.yaml`,'status');
  if(!d.schema.includes('/'+report.root.schemas+'/')||d.repository_id!==source.repository_id||d.repository!==source.repository||`${d.run.id}-${d.run.attempt}`!==key||d.input_catalog_state!==report.summary.input_catalog_state||d.input_catalog!==report.summary.input_catalog)throw Error('Source report binding mismatch');
  return d;
 }
 async report(pin){
  const root=await this.doc(pin,'status.yaml','status');
  if(Object.keys(root.summaries).length>64||Object.keys(root.details).length>8||!Object.values(root.summaries).includes(root.last_report))throw Error('Invalid status references');
  for(const [key,path] of Object.entries(root.summaries))if(path!==`runs/${key}/summary.yaml`)throw Error('Summary path mismatch');
  const summary=await this.doc(pin,root.last_report,'status');
  if(root.last_report!==`runs/${summary.run.id}-${summary.run.attempt}/summary.yaml`||root.reported_at!==summary.reported_at)throw Error('Report identity mismatch');
  if(!summary.schema.includes('/'+root.schemas+'/')||summary.inputs.schemas!==root.schemas)throw Error('Status schema binding mismatch');
  return {root,summary};
 }
}
