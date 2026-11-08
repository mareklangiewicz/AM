// Format-3/status-1 bounded readers. No network, schema fetch or recipe execution.
import contract from './definitions.mjs';
const defs=contract.definitions;
const sourceOrder=new WeakMap();
const bad=message=>{throw Error(`AM contract: ${message}`);};
const own=(o,k)=>Object.hasOwn(o,k);
const isMap=o=>o!==null && typeof o==='object';
const bytes=s=>new TextEncoder().encode(s).length;
function string(raw) {
 if(raw[0]!=='"'||raw.at(-1)!=='"') bad('quoted string');
 let out='';
 const escapes={'n':'\n','r':'\r','t':'\t','N':'\u0085','L':'\u2028','P':'\u2029','"':'"','\\':'\\'};
 for(let i=1;i<raw.length-1;i++) {
  let c=raw[i];
  if(c==='"') bad('unescaped quote');
  if(c==='\\') {c=escapes[raw[++i]]; if(c===undefined||i>=raw.length-1) bad('escape');}
  out+=c;
 }
 return out;
}
const validTime=s=>/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(s)&&s>='1970'&&Number.isFinite(Date.parse(s))&&new Date(s).toISOString()===s.replace('Z','.000Z');
function check(value, rule, path) {
 if(rule.$ref) return validateNode(value,rule.$ref.split('/').at(-1),path);
 if(rule.type==='integer') {
  if(typeof value!=='bigint'||value<0n||value>9223372036854775807n) bad('integer');
  if(rule.minimum!==undefined&&value<BigInt(rule.minimum)) bad('minimum');
  // JSON's maximum rounds past int64; explicit bound above remains authoritative.
  if(rule.maximum!==undefined&&rule.maximum<Number.MAX_SAFE_INTEGER&&value>BigInt(rule.maximum)) bad('maximum');
 } else if(typeof value!==rule.type) bad(`type ${path}`);
 if(rule.const!==undefined&&value!==(rule.type==='integer'?BigInt(rule.const):rule.const)) bad('constant');
 if(rule.enum&&!rule.enum.includes(value)) bad('enum');
 if(rule.pattern&&!new RegExp(rule.pattern).test(value)) bad(`pattern ${path}`);
 if(rule.format==='date-time'&&!validTime(value)) bad('timestamp');
}
function validateNode(obj,type,path='') {
 if(!isMap(obj)) bad('mapping');
 const schema=defs[type], keys=sourceOrder.get(obj)??Object.keys(obj);
 if(schema.properties) {
  let previous=-1;
  for(const key of keys) {
   const order=Object.keys(schema.properties).indexOf(key);
   if(order<0||order<=previous) bad('unknown/order');
   previous=order; check(obj[key],schema.properties[key],path+'/'+key);
  }
  for(const key of schema.required) if(!own(obj,key)) bad('required');
 } else {
  const [pattern,rule]=Object.entries(schema.patternProperties)[0]; let previous;
  for(const key of keys) {
   if(!new RegExp(pattern).test(key)||key.length>64||key==='.'||key==='..') bad('table key');
   if(type==='releases'||type==='assets') {
    if(BigInt(key)>9223372036854775807n||previous!==undefined&&BigInt(previous)>=BigInt(key)) bad('ID order');
   } else if(previous!==undefined&&previous>=key) bad('table order');
   previous=key; check(obj[key],rule,path+'/'+key);
  }
 }
 if(type==='measurement' && (obj.state==='known')!==own(obj,'value')) bad('measurement state');
 if(type==='publication' && (obj.state==='confirmed')!==own(obj,'commit')) bad('publication confirmation');
 if(type==='provenance_binding') {
  if((obj.availability==='present')!==own(obj,'recipe')) bad('recipe availability');
  if(obj.classification==='unknown') {if(own(obj,'evidence')) bad('unknown evidence');}
  else {
   const methods={shared:'whole_wrapper',template:'whole_template',custom:'reviewed_custom'};
   if(obj.availability!=='present'||!obj.evidence||obj.evidence.method!==methods[obj.classification]) bad('classification evidence');
   if(obj.classification==='custom'&&!own(obj.evidence,'description')) bad('custom description');
   if(obj.classification!=='custom'&&Object.keys(obj.evidence.dependencies).length===0) bad('dependencies');
  }
 }
}
export function parseDocument(text,{maxBytes=2097152}={}) {
 if(typeof text!=='string'||bytes(text)>maxBytes||maxBytes<1||maxBytes>33554432||!text.endsWith('\n')) bad('byte bound/newline');
 const root=Object.create(null), stack=[{depth:-1,value:root}], quotedKeys=new Map();
 for(const line of text.slice(0,-1).split('\n')) {
  if(!line||bytes(line)>65536||/[\x00-\x1f\x7f-\x9f\u2028\u2029\ufffe\uffff]/.test(line)||line.endsWith(' ')) bad('control/whitespace');
  const m=/^( *)("[a-z0-9][a-z0-9_.+-]*"|[a-z][a-z0-9_]*):(?: (.*))?$/.exec(line);
  if(!m||m[1].length%2) bad('grammar');
  const depth=m[1].length/2;
  if(depth>12) bad('depth');
  while(stack.at(-1).depth>=depth) {const last=stack.pop(); if(Object.keys(last.value).length===0) bad('implicit empty mapping');}
  if(stack.at(-1).depth!==depth-1) bad('indentation');
  const parent=stack.at(-1).value, quoted=m[2][0]==='"',key=quoted?string(m[2]):m[2],raw=m[3];
  if(own(parent,key)) bad('duplicate key');
  let value;
  if(raw===undefined||raw==='{}') value=Object.create(null);
  else if(raw[0]==='"') value=string(raw);
  else if(raw==='true'||raw==='false') value=raw==='true';
  else if(/^(0|[1-9][0-9]*)$/.test(raw)) value=BigInt(raw);
  else bad('scalar');
  parent[key]=value;
  if(!sourceOrder.has(parent)) sourceOrder.set(parent,[]);
  sourceOrder.get(parent).push(key);
  if(!quotedKeys.has(parent)) quotedKeys.set(parent,new Map());
  quotedKeys.get(parent).set(key,quoted);
  if(raw===undefined) stack.push({depth,value});
 }
 for(const item of stack.slice(1)) if(Object.keys(item.value).length===0) bad('implicit empty mapping');
 if(!contract.kinds.includes(root.kind)) bad('kind');
 const visit=(obj,type)=>{
  const schema=defs[type],props=schema.properties;
  for(const key of Object.keys(obj)) {
   if(quotedKeys.get(obj)?.get(key)!==!Boolean(props)) bad('key quoting');
   const rule=props?.[key]??Object.values(schema.patternProperties??{})[0];
   if(rule?.$ref) visit(obj[key],rule.$ref.split('/').at(-1));
  }
 };
 validateNode(root,root.kind); visit(root,root.kind); semantics(root); return root;
}
function semantics(doc) {
 if(doc.kind==='repository') {
  if(doc.observed_at>doc.collected_at) bad('observation order');
  const entries=Object.entries(doc.releases),tags=new Set(); let stable=0;
  for(const [,release] of entries) {
   if(!own(release,'published_at')&&!own(release,'created_at')) bad('ordering timestamp');
   const observed=release.observed_at??doc.observed_at;
   if(observed>doc.collected_at||own(release,'observed_at')&&observed===doc.observed_at) bad('release observation');
   if(tags.has(release.tag)) bad('exact tag conflict'); tags.add(release.tag);
   if(!release.prerelease) stable++;
   if(own(release,'download_base')&&!release.download_base.endsWith('/')) bad('base');
   for(const asset of Object.values(release.assets)) {
    if(own(asset,'url')===own(asset,'url_suffix')) bad('URL choice');
    const url=own(asset,'url')?asset.url:own(release,'download_base')?release.download_base+asset.url_suffix:bad('suffix without base');
    if(!/^https:\/\/[^/\s][^\s]*$/.test(url)) bad('reconstructed URL');
    const mime=asset.media_type??'application/octet-stream';
    if(mime!==''&&mime!=='zip'&&!/^[^\s/]+\/[^\s/]+/.test(mime)) bad('MIME alias');
   }
  }
  if(entries.length>33||entries.length===33&&stable!==1) bad('retention');
  if(entries.length===33) {
   const [stableId,s]=entries.find(([,r])=>!r.prerelease),time=s.published_at??s.created_at;
   for(const [id,r] of entries) if(id!==stableId) {
    const other=r.published_at??r.created_at;
    if(time>other||time===other&&BigInt(stableId)>BigInt(id)) bad('unneeded stable exception');
   }
  }
 }
 if(doc.kind==='summary') {
  if(doc.started_at>doc.reported_at) bad('run time');
  if(doc.actions_url!==`https://github.com/mareklangiewicz/AM/actions/runs/${doc.run.id}`||doc.recent_runs_url!=='https://github.com/mareklangiewicz/AM/actions/workflows/catalog.yml') bad('investigation links');
  if(Object.values(doc.counts).every(v=>v.state==='known')) {
   const c=Object.fromEntries(Object.entries(doc.counts).map(([k,v])=>[k,v.value]));
   if(c.attempted!==c.successful+c.failed+c.unknown||c.selected!==c.attempted+c.unattempted||c.selected>c.enrolled||c.deferred>c.unattempted) bad('counts');
  }
 }
}
export function releaseFacts(doc,id) {
 if(doc.kind!=='repository') bad('repository required');
 const release=doc.releases[id]; if(!release) return undefined;
 return {...release,observed_at:release.observed_at??doc.observed_at,assets:Object.fromEntries(Object.entries(release.assets).map(([id,a])=>{
  const media_type=a.media_type==='zip'?'application/zip':a.media_type??'application/octet-stream';
  return [id,{...a,url:own(a,'url')?a.url:release.download_base+a.url_suffix,media_type,content_type:media_type}];
 }))};
}
export function validateSnapshot(documents,channel='catalog') {
 const docs=new Map(),ids=new Set();
 if(Object.keys(documents).length>20000) bad('tree bound'); let total=0;
 for(const [path,text] of Object.entries(documents)) {
  total+=bytes(text); if(total>1073741824) bad('tree bytes');
  const allowed=channel==='catalog'?/^(catalog|apps|provenance)\.yaml$|^repositories\/[a-z0-9][a-z0-9_.+-]{0,63}\.yaml$/:/^(status|statistics)\.yaml$|^runs\/[1-9][0-9]*-[1-9][0-9]*\/(summary\.yaml|sources\/[a-z0-9][a-z0-9_.+-]{0,63}\.yaml)$/;
  if(!allowed.test(path)) bad('path');
  const doc=parseDocument(text), expected=path.includes('/')?(channel==='catalog'?'repository':path.endsWith('/summary.yaml')?'summary':'source'):path.slice(0,-5);
  if(doc.kind!==expected) bad('path kind');
  if(doc.kind==='repository') {if(ids.has(doc.repository_id)) bad('duplicate source'); ids.add(doc.repository_id);}
  docs.set(path,doc);
 }
 if(channel==='catalog') {
  if(!['catalog.yaml','apps.yaml','provenance.yaml'].every(path=>docs.has(path))) bad('roots');
  const apps=docs.get('apps.yaml').apps;
  for(const path of Object.values(apps)) if(!docs.has(path)) bad('missing source');
  for(const [app,arches] of Object.entries(docs.get('provenance.yaml').apps)) {
   if(!own(apps,app)) bad('provenance app');
   for(const [arch,binding] of Object.entries(arches)) {
    if(binding.repository_id!==docs.get(apps[app]).repository_id) bad('provenance identity');
    if(binding.recipe&&binding.recipe.path!==`programs/${arch}/${app}`) bad('recipe identity');
   }
  }
 } else {
  const s=docs.get('status.yaml'); if(!s) bad('status root');
  if(Object.keys(s.summaries).length>64||Object.keys(s.details).length>8) bad('retention');
  for(const [key,path] of Object.entries(s.summaries)) if(path!==`runs/${key}/summary.yaml`||!docs.has(path)) bad('summary reference');
  if(!Object.values(s.summaries).includes(s.last_report)) bad('last report');
  for(const [path,doc] of docs) if(doc.kind==='source'||doc.kind==='summary') {
   const key=`${doc.run.id}-${doc.run.attempt}`;
   if(!path.startsWith(`runs/${key}/`)) bad('run identity');
   if(doc.kind==='source'&&!own(s.details,key)) bad('detail coverage');
  }
  if(docs.has('statistics.yaml')&&Object.keys(docs.get('statistics.yaml').days).length>90) bad('days');
 }
 return docs;
}
