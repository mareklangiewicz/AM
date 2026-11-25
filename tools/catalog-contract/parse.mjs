// AM catalog reader for the page: the grammar of docs/catalog-format.md,
// checked against schema.mjs (generated from schemas/catalog.schema.yaml) and
// the cross-field rules below, the same as modules/catalog-parser.am.
import contract from './schema.mjs';
const defs=contract.definitions;
const headers=Object.fromEntries(contract.kinds.map(kind=>[defs[kind].properties.$schema.const,kind]));
const order=new WeakMap();
const bad=message=>{throw Error(`AM catalog: ${message}`);};
const own=(o,k)=>Object.hasOwn(o,k);
const encoder=new TextEncoder();
const bytes=s=>encoder.encode(s).length;
const INT64=9223372036854775807n;
const ESCAPES={n:'\n',r:'\r',t:'\t',N:'\u0085',L:'\u2028',P:'\u2029','"':'"','\\':'\\'};

// The index of the quote closing the string that starts at s[0]; -1 if none.
function stringEnd(s) {
 for(let i=1;i<s.length;i++) {
  if(s[i]==='\\') i++;
  else if(s[i]==='"') return i;
 }
 return -1;
}
function decode(raw) {
 if(raw.length<2||raw[0]!=='"'||raw.at(-1)!=='"') bad('quoted string');
 let out='';
 for(let i=1;i<raw.length-1;i++) {
  let c=raw[i];
  if(c==='"') bad('unescaped quote');
  if(c==='\\') {c=ESCAPES[raw[++i]]; if(c===undefined||i>=raw.length-1) bad('unsupported escape');}
  out+=c;
 }
 return out;
}
const validTime=s=>/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(s)&&s>='1970'&&Number.isFinite(Date.parse(s))&&new Date(s).toISOString()===s.replace('Z','.000Z');
const resolve=rule=>rule.$ref?defs[rule.$ref.split('/').at(-1)]:rule;
// Keys made of digits are numbers; a run key is two numbers.
function keyBefore(pattern,a,b) {
 if(pattern==='^[1-9][0-9]*$') return BigInt(a)<BigInt(b);
 if(pattern==='^[1-9][0-9]*-[1-9][0-9]*$') {
  const [x,y]=[a,b].map(k=>k.split('-').map(BigInt));
  return x[0]<y[0]||x[0]===y[0]&&x[1]<y[1];
 }
 return byteLess(encoder.encode(a),encoder.encode(b));
}
// Byte order of UTF-8, as awk compares in the C locale; no Node-only Buffer (the page runs this).
function byteLess(x,y) {
 for(let i=0;i<Math.min(x.length,y.length);i++) if(x[i]!==y[i]) return x[i]<y[i];
 return x.length<y.length;
}
function scalar(value,rule,path) {
 const type=rule.type??'string';
 if(type==='integer') {
  if(typeof value!=='bigint') bad(`type ${path}`);
  if(value>INT64) bad(`integer over 64 bits ${path}`);
  if(rule.minimum!==undefined&&value<BigInt(rule.minimum)) bad(`minimum ${path}`);
  // A JSON number rounds past 2^53: INT64 above is the bound for the 64-bit maximums.
  if(rule.maximum!==undefined&&rule.maximum<Number.MAX_SAFE_INTEGER&&value>BigInt(rule.maximum)) bad(`maximum ${path}`);
 } else if(typeof value!==type) bad(`type ${path}`);
 if(rule.const!==undefined&&value!==rule.const) bad(`constant ${path}`);
 if(rule.enum&&!rule.enum.includes(value)) bad(`enum ${path}`);
 if(rule.pattern&&!new RegExp(rule.pattern,'u').test(value)) bad(`pattern ${path}`);
 if(rule.format==='date-time'&&!validTime(value)) bad(`timestamp ${path}`);
}
// quoted: the parser's record of which keys were written quoted.
function check(value,rule,path,quoted) {
 rule=resolve(rule);
 if(rule.type!=='object') return scalar(value,rule,path);
 if(typeof value!=='object') bad(`mapping ${path}`);
 const keys=order.get(value)??[];
 if(rule.properties) {
  const names=Object.keys(rule.properties); let previous=-1;
  for(const key of keys) {
   const at=names.indexOf(key);
   if(at<0||at<=previous) bad(`unknown or out-of-order field ${path}/${key}`);
   if(quoted.get(value).get(key)) bad(`quoted field name ${path}/${key}`);
   previous=at; check(value[key],rule.properties[key],`${path}/${key}`,quoted);
  }
  for(const key of rule.required??[]) if(!own(value,key)) bad(`missing field ${path}/${key}`);
 } else {
  const [pattern,sub]=Object.entries(rule.patternProperties)[0]; let previous;
  if(rule.maxProperties!==undefined&&keys.length>rule.maxProperties) bad(`more than ${rule.maxProperties} entries ${path}`);
  for(const key of keys) {
   if(!quoted.get(value).get(key)||!new RegExp(pattern,'u').test(key)) bad(`table key ${path}/${key}`);
   if(pattern==='^[1-9][0-9]*$'&&BigInt(key)>INT64) bad('ID over 64 bits');
   if(previous!==undefined&&!keyBefore(pattern,previous,key)) bad(`key order ${path}`);
   previous=key; check(value[key],sub,`${path}/${key}`,quoted);
  }
 }
}
const validRef=s=>!/[\x00-\x1f\x7f~^:?*\\[]/.test(s)&&!s.includes('..')&&!s.includes('@{')&&!s.includes('//')&&!/[/.]$/.test(s)&&!s.endsWith('.lock')&&bytes(s)<=1024;
const validPath=s=>bytes(s)<=1024&&!s.split('/').some(part=>part==='.'||part==='..');
function repositoryRules(doc) {
 const collected=own(doc,'observed_at'),failed=own(doc,'failed_at');
 if(collected!==own(doc,'history_complete')) bad('observed_at and history_complete come together');
 if(failed!==own(doc,'failed_with')) bad('failed_at and failed_with come together');
 if(!collected&&(!failed||Object.keys(doc.releases).length||own(doc,'git_scope'))) bad('a never-collected repository has only its failure');
 if(collected&&failed&&doc.failed_at<=doc.observed_at) bad('failure not after observation');
 for(const release of Object.values(doc.releases)) if(own(release,'observed_at')&&release.observed_at>=doc.observed_at) bad('release last seen not older than the repository');
 if(own(doc,'git_scope')!==own(doc,'git_refs')) bad('git_scope and git_refs come together');
 if(!own(doc,'git_refs')) return;
 const scope=doc.git_scope,positions=new Set(); let tags=0,branches=0;
 if(scope.tags_history_complete&&!scope.tags) bad('tag history without tags');
 for(const [name,ref] of Object.entries(doc.git_refs)) {
  if(!validRef(name)) bad('Git ref name');
  if(name.startsWith('refs/tags/')) {
   tags++;
   if(!scope.tags||!own(ref,'position')||own(ref,'files')) bad('Git tag scope');
   if(positions.has(ref.position)) bad('Git tag position repeated');
   positions.add(ref.position);
  } else {
   branches++;
   if(own(ref,'position')) bad('Git branch scope');
  }
  for(const [path,file] of Object.entries(ref.files??{})) {
   if(!validPath(path)) bad('Git file path');
   if(bytes(file.content)>1048576) bad('Git file content over 1 MiB');
  }
 }
 if(branches>4) bad('more than 4 Git branches');
 for(let i=0n;i<BigInt(tags);i++) if(!positions.has(i)) bad('Git tag position gap');
}
function runsRules(doc) {
 for(const run of Object.values(doc.runs)) if(run.selected>run.enrolled||run.succeeded+run.failed>run.selected) bad('run counts');
}
// Parse and validate one whole document; refuse anything the host would refuse.
export function parseDocument(text,{maxBytes=2097152}={}) {
 if(typeof text!=='string'||maxBytes<1||maxBytes>33554432||bytes(text)>maxBytes||!text.endsWith('\n')) bad('byte bound or final newline');
 const root=Object.create(null),stack=[{depth:-1,value:root}],quoted=new Map([[root,new Map()]]);
 let kind,number=0;
 for(const line of text.slice(0,-1).split('\n')) {
  number++;
  // UTF-8 needs at most three bytes per UTF-16 code unit: short lines fit
  // without allocating; only a Git file's content may exceed 64 KiB.
  if(!line||line.endsWith(' ')||/[\x00-\x1f\x7f-\x9f\u2028\u2029\ufffe\uffff]/.test(line)) bad('control, blank line or trailing space');
  if(line.length>21845&&bytes(line)>65536&&!/^ {8}content: "/.test(line)) bad('size limit');
  const indent=/^ */.exec(line)[0].length,depth=indent/2,rest=line.slice(indent);
  if(indent%2||depth>12) bad('indentation');
  let key,raw,isQuoted;
  if(rest[0]==='"') {
   const end=stringEnd(rest);
   if(end<0||rest[end+1]!==':') bad('key');
   key=decode(rest.slice(0,end+1)); raw=rest.slice(end+2); isQuoted=true;
  } else {
   const colon=rest.indexOf(':');
   if(colon<0) bad('missing colon');
   key=rest.slice(0,colon); raw=rest.slice(colon+1); isQuoted=false;
   if(!/^[a-z][a-z0-9_]*$/.test(key)&&!(number===1&&key==='$schema')) bad('key');
  }
  while(stack.at(-1).depth>=depth) if(Object.keys(stack.pop().value).length===0) bad('use {} for an empty mapping');
  if(stack.at(-1).depth!==depth-1) bad('indentation');
  const parent=stack.at(-1).value;
  if(typeof parent!=='object') bad('child of a scalar');
  if(own(parent,key)) bad('duplicate key');
  let value;
  if(raw==='') value=Object.create(null);
  else {
   if(raw[0]!==' '||raw[1]===' ') bad('scalar spacing');
   raw=raw.slice(1);
   if(raw==='{}') value=Object.create(null);
   else if(raw[0]==='"') {if(stringEnd(raw)!==raw.length-1) bad('text after string'); value=decode(raw);}
   else if(raw==='true'||raw==='false') value=raw==='true';
   else if(/^(0|[1-9][0-9]*)$/.test(raw)) value=BigInt(raw);
   else bad('scalar');
  }
  if(number===1) {
   if(key!=='$schema') bad('$schema first');
   kind=headers[value];
   if(!kind) bad('unknown $schema');
  }
  parent[key]=value;
  if(!order.has(parent)) order.set(parent,[]);
  order.get(parent).push(key);
  quoted.get(parent).set(key,isQuoted);
  if(typeof value==='object') quoted.set(value,new Map());
  if(raw==='') stack.push({depth,value});
 }
 for(const item of stack.slice(1)) if(Object.keys(item.value).length===0) bad('use {} for an empty mapping');
 if(!kind) bad('empty document');
 check(root,defs[kind],'',quoted);
 if(kind==='repository') repositoryRules(root);
 if(kind==='runs') runsRules(root);
 return {kind,document:root};
}
