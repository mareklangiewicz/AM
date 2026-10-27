#!/usr/bin/env node
// THROWAWAY acceptance replay: node tools/proto-freshness/replay.cjs
const F=require('./core.js'), fs=require('node:fs'),path=require('node:path'),os=require('node:os'),cp=require('node:child_process'),crypto=require('node:crypto');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex'),encode=s=>Buffer.from(s),clone=v=>structuredClone(v);
const out=fs.mkdtempSync(path.join(os.tmpdir(),'PROTOTYPE-freshness-')),repo=path.join(out,'publication');fs.mkdirSync(repo);
const git=(...args)=>cp.execFileSync('git',['-C',repo,...args],{encoding:'utf8',stdio:['pipe','pipe','pipe']}).trim();
git('init','--quiet','--template=');git('config','user.name','Offline freshness prototype');git('config','user.email','prototype@invalid');git('config','commit.gpgsign','false');git('config','core.autocrlf','false');git('config','gc.auto','0');
const now='2026-10-28T12:00:00Z', at=seconds=>new Date(Date.parse(now)-seconds*1000).toISOString();
const url='https://api.github.com/repos/example/one/releases',other='https://api.github.com/repos/example/two/releases';
const sources={},entries={},aliases={},manifestAliases={},bodies={};
for(let n=0;n<6;n++){
 const u=n===0?url:n===1?other:`https://api.github.com/repos/example/source${n}/releases`;
 const desc={url:u,api_version:'2022-11-28',accept:'application/vnd.github+json'},rid=F.descriptor(desc,hash,encode);
 const raw=encode('[{"id":1,"tag_name":"v1","draft":false,"assets":[]}]\n');sources[rid]=desc;manifestAliases[u]=rid;aliases[u]={state:'active',request_id:rid};
 entries[rid]={descriptor:desc,availability:'available',validators:{etag:'fixture-v1'},
 observation:{path:`bodies/${rid}.json`,scope:'single-response',bytes:raw.length,sha256:hash(raw),received_at:at(90000),validated_at:at(86401),received_time_basis:'response-completed',validation_time_basis:'response-completed'},latest_attempt:{status:200,at:at(86401)}};
 bodies[`bodies/${rid}.json`]=raw;
}
const rid=aliases[url].request_id;
const fixture={schema_version:2,generated_at:now,manifest:{sources,aliases:manifestAliases},aliases,entries};
const tree=index=>({'index.json':encode(JSON.stringify(index)),...bodies});
let tip=null;const checks=[];
function check(name,fn){const value=fn();if(!value)throw Error(`failed: ${name}`);checks.push({name,result:'passed'});}
function refuses(name,fn){try{fn()}catch(e){checks.push({name,result:'refused',reason:e.message});return}throw Error(`not refused: ${name}`);}
function validateCandidate(files,packBytes=0){
 const raw=files['index.json'];if(!Buffer.isBuffer(raw))throw Error('index missing');
 F.caps({sources:Object.keys(JSON.parse(raw).manifest.sources).length,body:Math.max(0,...Object.entries(files).filter(([p])=>p.startsWith('bodies/')).map(([,b])=>b.length)),index:raw.length,tree:Object.values(files).reduce((a,b)=>a+b.length,0),pack:packBytes});
 const index=JSON.parse(raw),expected=new Set(['index.json']);
 if(index.schema_version!==2)throw Error('schema');
 for(const [id,e]of Object.entries(index.entries)){
  if(F.descriptor(e.descriptor,hash,encode)!==id)throw Error('identity');
  if(e.observation){let o=e.observation;if(o.path!==`bodies/${id}.json`)throw Error('path');let b=files[o.path];if(!b||b.length!==o.bytes||hash(b)!==o.sha256)throw Error('body');expected.add(o.path);}
 }
 if(Object.keys(files).length!==expected.size||Object.keys(files).some(p=>!expected.has(p)||!Buffer.isBuffer(files[p])))throw Error('unexpected files');
 return index;
}
function publish(files,parent,packBytes=0){
 validateCandidate(files,packBytes);if(parent!==tip)throw Error('stale parent');
 if(git('remote'))throw Error('remote not allowed');
 for(const [p,b]of Object.entries(files)){let dest=path.join(repo,p);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,b);}
 git('add','--','index.json','bodies');git('commit','--quiet','--allow-empty','-m','PROTOTYPE synthetic publication');
 const next=git('rev-parse','HEAD');git('update-ref','refs/heads/publication',next,parent||'0'.repeat(40));tip=next;return next;
}
function readPinned(commit,u=url,acceptance=null){
 if(!/^[a-f0-9]{40}$/.test(commit))throw Error('full commit required');
 const index=JSON.parse(git('show',`${commit}:index.json`));const alias=index.aliases[u],entry=alias&&index.entries[alias.request_id];
 let body=null;if(entry?.observation){const p=entry.observation.path;if(p!==`bodies/${alias.request_id}.json`)throw Error('path');body=cp.execFileSync('git',['-C',repo,'show',`${commit}:${p}`],{stdio:['pipe','pipe','pipe']});}
 return F.lookup({index,body,url:u,commit,now,acceptance},hash,encode);
}
const a=publish(tree(fixture),null),accepted={commit:a,request_id:rid,sha256:fixture.entries[rid].observation.sha256};
const evaluate=(i=fixture,extra={})=>F.lookup({index:i,commit:a,url,body:bodies[`bodies/${rid}.json`],now,...extra},hash,encode);
for(const age of [0,86399,86400,86401]){let i=clone(fixture);i.entries[rid].observation.validated_at=at(age);check(`age ${age}`,()=>evaluate(i).decision===(age<=86400?'fresh':'acceptance-required'));}
check('explicit stale acceptance',()=>evaluate(fixture,{acceptance:accepted}).decision==='accepted-stale');
check('acceptance does not mutate times',()=>evaluate(fixture,{acceptance:accepted}).validated_at===at(86401));
for(const [name,change]of [['other commit',{commit:'b'.repeat(40)}],['other source',{request_id:aliases[other].request_id}],['changed digest',{sha256:'f'.repeat(64)}]])check(`acceptance rejects ${name}`,()=>evaluate(fixture,{acceptance:{...accepted,...change}}).decision==='acceptance-required');
for(const state of ['unknown','unavailable','retired']){let i=clone(fixture);i.entries[rid].availability=state;refuses(`acceptance cannot override ${state}`,()=>evaluate(i,{acceptance:accepted}));}
let removed=clone(fixture);removed.aliases[url].state='removed';
refuses('removed alias refuses with active descriptor',()=>evaluate(removed,{acceptance:accepted}));
check('other alias keeps descriptor usable',()=>{let i=clone(removed);const alias='https://api.github.com/repos/example/alias/releases';i.aliases[alias]={state:'active',request_id:rid};i.manifest.aliases[alias]=rid;return evaluate(i,{url:alias,acceptance:accepted}).decision==='accepted-stale'});
let transient=clone(fixture);transient.entries[rid].latest_attempt={status:503,at:now};check('temporary error retains age',()=>evaluate(transient).age_seconds===86401);
let conditional=clone(fixture);conditional.entries[rid]=F.notModified(conditional.entries[rid],now,{etag:'fixture-v1'});
check('304 preserves receipt, advances validation',()=>evaluate(conditional).decision==='fresh'&&conditional.entries[rid].observation.received_at===at(90000));
check('304 preserves separate receipt timing basis',()=>{let e=clone(fixture.entries[rid]);e.observation.received_time_basis='saved-round-completion-upper-bound';const n=F.notModified(e,now,{etag:'fixture-v1'});return n.observation.received_time_basis==='saved-round-completion-upper-bound'&&n.observation.validation_time_basis==='response-completed'});
const reenrolled=F.reenroll(fixture.entries[rid]);check('re-enrollment clears current state, retains history',()=>reenrolled.availability==='unknown'&&Object.keys(reenrolled.validators).length===0&&reenrolled.observation===null&&reenrolled.historical_observation!==null);
refuses('re-enrollment cannot reuse 304',()=>F.notModified(reenrolled,now,{etag:'fixture-v1'}));
refuses('304 mismatched validator',()=>F.notModified(fixture.entries[rid],now,{etag:'wrong'}));
for(const [name,value]of [['missing',null],['malformed','yesterday'],['invalid date','2026-02-30T12:00:00Z'],['future',at(-1)]]){let i=clone(fixture);i.entries[rid].observation.validated_at=value;refuses(`${name} validation time`,()=>evaluate(i));}
for(const field of ['received_time_basis','validation_time_basis']){let i=clone(fixture);i.entries[rid].observation[field]='saved-round-completion-upper-bound';refuses(`historical ${field}`,()=>evaluate(i));}
checks.push({name:'historical saved timing demonstration',result:'historical only',received_time_basis:'saved-round-completion-upper-bound',current_lookup:'refused'});
for(const [name,mutate]of [['schema',i=>i.schema_version=9],['descriptor',i=>i.entries[rid].descriptor.url=other],['alias target',i=>i.aliases[url].request_id='f'.repeat(64)],['manifest alias',i=>i.manifest.aliases[url]='f'.repeat(64)],['unsafe path',i=>i.entries[rid].observation.path='../outside'],['digest',i=>i.entries[rid].observation.sha256='0'.repeat(64)],['byte count',i=>i.entries[rid].observation.bytes++],['future publication',i=>i.generated_at=at(-1)]]){let i=clone(fixture);mutate(i);refuses(`lookup ${name}`,()=>evaluate(i));}
const b=publish(tree(conditional),a);
check('ref moves to B',()=>git('rev-parse','refs/heads/publication')===b);
check('pinned A stays stale after B',()=>readPinned(a).decision==='acceptance-required'&&readPinned(b).decision==='fresh');
check('A acceptance cannot authorize B when B later stale',()=>{let i=clone(conditional);i.entries[rid].observation.validated_at=at(86401);return evaluate(i,{commit:b,acceptance:accepted}).decision==='acceptance-required'});
refuses('stale parent',()=>publish(tree(fixture),a));
const invalidPinned=clone(fixture);invalidPinned.entries[rid].observation.path=`bodies/${rid}.json`;let missing=tree(invalidPinned);delete missing[`bodies/${rid}.json`];
// Construct an intentionally broken independent commit with commit-tree, never advance publication.
const badRoot=git('mktree');const badCommit=cp.execFileSync('git',['-C',repo,'commit-tree',badRoot],{input:'PROTOTYPE intentionally missing pinned files\n',encoding:'utf8'}).trim();
refuses('missing pinned index never falls back to tip',()=>readPinned(badCommit));
refuses('missing pinned body rejects candidate',()=>publish(missing,b));
// Build broken index-only commit without touching publication ref.
const indexOid=cp.execFileSync('git',['-C',repo,'hash-object','-w','--stdin'],{input:JSON.stringify(fixture),encoding:'utf8'}).trim();
const indexTree=cp.execFileSync('git',['-C',repo,'mktree'],{input:`100644 blob ${indexOid}\tindex.json\n`,encoding:'utf8'}).trim();
const missingBodyCommit=cp.execFileSync('git',['-C',repo,'commit-tree',indexTree],{input:'PROTOTYPE missing body\n',encoding:'utf8'}).trim();refuses('missing pinned body never falls back',()=>readPinned(missingBodyCommit));
const baselineCounts={sources:6,body:8000000,index:2000000,tree:50000000,pack:128000000};
check('exact cap boundaries allowed',()=>{F.caps(baselineCounts);return true});
for(const k of Object.keys(baselineCounts))refuses(`cap ${k} plus one`,()=>F.caps({...baselineCounts,[k]:baselineCounts[k]+1}));
refuses('pack cap rejects publication before write',()=>publish(tree(fixture),b,128000001));
let tooMany=clone(fixture);tooMany.manifest.sources['extra']=sources[rid];refuses('source cap rejects publication',()=>publish(tree(tooMany),b));
let oversized=tree(fixture);oversized[`bodies/${rid}.json`]=Buffer.alloc(8000001);refuses('body cap rejects publication',()=>publish(oversized,b));
let bigIndex=tree(fixture);bigIndex['index.json']=encode(JSON.stringify({...fixture,padding:'x'.repeat(2000000)}));refuses('index cap rejects publication',()=>publish(bigIndex,b));
// Shared pure preflight receives measured sizes; injection avoids allocating 50 MB.
refuses('injected tree cap rejects before publication',()=>{F.caps({...baselineCounts,tree:50000001});publish(tree(fixture),b)});
check('all rejected publications preserve B',()=>git('rev-parse','refs/heads/publication')===b&&git('rev-parse','HEAD')===b);
git('repack','-adf','--window=10','--depth=50');const packBytes=fs.readdirSync(path.join(repo,'.git/objects/pack')).reduce((sum,n)=>sum+fs.statSync(path.join(repo,'.git/objects/pack',n)).size,0);
const report={question:'Can pinned lookup explain age and refuse unavailable data?',synthetic:true,checks,commits:{a,b,missing_index:badCommit,missing_body:missingBodyCommit},pack_bytes:packBytes,limits:F.CAPS,notes:['Synthetic measured timestamps, not real endpoint completion evidence','No HTTP, remote or installer integration','Injected tree/pack boundary measurements are logic checks, not large-file measurements','Experimental schema 2 is a prototype marker, not production version adoption']};
fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({output:out,checks:checks.length,pack_bytes:packBytes},null,2));
