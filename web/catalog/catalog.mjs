// The page reads raw main-marek/catalog/ files (docs/catalog-format.md), like AM does:
// no pins, a bounded retry while GitHub's CDN catches up, a 2 MiB bound per file.
import {parseDocument} from '../../tools/catalog-contract/parse.mjs';
import platforms from '../../tools/catalog-contract/platforms.json' with {type:'json'};

export const RAW='https://raw.githubusercontent.com/mareklangiewicz/AM/main-marek/catalog/';
const BYTES=2097152,TRIES=3;
const repositoryPath=/^repositories\/[a-z0-9][a-z0-9_.+-]{0,63}\.yaml$/;
const own=(o,k)=>Object.hasOwn(o,k);
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));

// A release with everything the document leaves out filled in, as the host's reader does.
export function releaseFacts(source,id) {
 const release=source.releases[id];if(!release)return undefined;
 const repo=source.repository,tag=release.tag;
 return {...release,
  title:release.title??tag,
  url:release.url??`https://github.com/${repo}/releases/tag/${tag}`,
  source_zip_url:release.source_zip_url??`https://api.github.com/repos/${repo}/zipball/${tag}`,
  source_tar_url:release.source_tar_url??`https://api.github.com/repos/${repo}/tarball/${tag}`,
  observed_at:release.observed_at??source.observed_at,
  own_observation:own(release,'observed_at'),
  assets:Object.fromEntries(Object.entries(release.assets).map(([aid,a])=>[aid,
   {...a,url:a.url??`https://github.com/${repo}/releases/download/${tag}/${a.name}`}]))};
}

// The one Linux/processor guess (platforms.json), shared with the collector's retention.
export function guess(name) {
 const lower=name.toLowerCase();
 const arch=Object.entries(platforms.architectures).find(([,words])=>words.some(w=>lower.includes(w)));
 return {linux:platforms.linux.some(w=>lower.includes(w)),arch:arch?arch[0]:null};
}

const FAILURES={not_found:"GitHub says this repository doesn't exist or isn't public.",
 too_large:"GitHub's answer was larger than the catalog accepts.",
 invalid_response:"GitHub's answer wasn't what the catalog expects.",
 transport:"GitHub couldn't be reached."};
export const failure=source=>source.failed_with?FAILURES[source.failed_with]:null;

// [name, ref] pairs: branches first by name, then tags by GitHub's position.
export function gitFacts(source,query='') {
 const needle=query.toLowerCase();
 return Object.entries(source.git_refs??{}).sort(([a,x],[b,y])=>{
  const at=a.startsWith('refs/tags/'),bt=b.startsWith('refs/tags/');
  return at&&bt?Number(x.position-y.position):at!==bt?(at?1:-1):a.localeCompare(b);
 }).filter(([name,ref])=>!needle||[name,ref.commit,...Object.keys(ref.files??{})].join(' ').toLowerCase().includes(needle));
}

export class Catalog {
 // review: a staged build's saved files instead of the live catalog (stage.py).
 constructor(fetcher=fetch,{review=null,retryDelay=2000}={}){
  this.fetcher=fetcher.bind(globalThis);this.cache=new Map();this.review=review;this.retryDelay=retryDelay;
 }
 url(path){return this.review?new URL(`../../review-data/catalog/${path}`,import.meta.url).href:RAW+path;}
 async doc(path,kind){
  if(this.cache.has(path))return this.cache.get(path);
  let response;
  for(let attempt=1;;attempt++){
   response=await this.fetcher(this.url(path));
   if(response.status!==404||attempt>=TRIES)break;
   await sleep(this.retryDelay);
  }
  if(!response.ok)throw Error(`Unavailable ${path} (HTTP ${response.status})`);
  // Enforce the byte bound before materializing an unbounded response body.
  const reader=response.body.getReader(),chunks=[];let length=0;
  try{for(;;){const {done,value}=await reader.read();if(done)break;length+=value.byteLength;if(length>BYTES)throw Error('Document byte bound');chunks.push(value);}}
  finally{await reader.cancel();}
  const bytes=new Uint8Array(length);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length;}
  const parsed=parseDocument(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
  if(parsed.kind!==kind)throw Error(`${path}: expected a ${kind} document, got ${parsed.kind} kind`);
  if(this.cache.size>=64)this.cache.delete(this.cache.keys().next().value);
  this.cache.set(path,parsed.document);return parsed.document;
 }
 async apps(){return (await this.doc('apps.yaml','apps')).apps;}
 async source(path){
  if(!repositoryPath.test(path))throw Error('Invalid repository path');
  return this.doc(path,'repository');
 }
 async runs(){return (await this.doc('status/runs.yaml','runs')).runs;}
 async statistics(){return this.doc('status/statistics.yaml','statistics');}
}
