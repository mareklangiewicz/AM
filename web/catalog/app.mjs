import {Catalog,rawURL,releaseFacts} from './catalog.mjs';
import {installKeyboard} from './keyboard.mjs';
const $=id=>document.getElementById(id),client=new Catalog(),names={A:'Directory',B:'Explorer',C:'Release desk'};
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const link=(url,label)=>/^https:\/\//.test(url??'')?`<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(label)}</a>`:esc(label);
let pin,selected,variant='A',release,apps={},root,source,bindings,loading=false,query='',sourceQuery='',generation=0,page=0,statusPin,report,sourceHealth='Refresh outcome not yet checked.';
const expanded=new Set(),limits=new Map(),metrics=[];
const route=()=>'?'+new URLSearchParams({variant,...(pin?{pin}:{}),...(selected?{app:selected}:{}),...(release?{release}:{})});
function save(replace=false){
 if(!replace)history.replaceState({scroll:window.scrollY,app:document.activeElement?.dataset?.app},'',location.href);
 history[replace?'replaceState':'pushState'](replace?history.state:null,'',route());}
function readRoute(){const p=new URLSearchParams(location.search);pin=p.get('pin');selected=p.get('app');release=p.get('release');variant=names[p.get('variant')]?p.get('variant'):'A';expanded.clear();limits.clear();if(release)expanded.add(release);}
function error(e){$('error').textContent=e.message+' — Retry reads this same snapshot. Load latest explicitly chooses a new snapshot.';}
function age(time){const hours=Math.max(0,(Date.now()-Date.parse(time))/3600000);return `${esc(time)} (${hours.toFixed(1)} hours ago)`;}
function releases(d){return Object.entries(d.releases).sort(([a,x],[b,y])=>(y.published_at??y.created_at).localeCompare(x.published_at??x.created_at)||(BigInt(a)<BigInt(b)?1:BigInt(a)>BigInt(b)?-1:0));}
function guess(name){const n=name.toLowerCase();return {os:/appimage|linux/.test(n)?'linux':/\.exe$|\.msi$|windows|win32|win64/.test(n)?'windows':/\.dmg$|darwin|macos|osx/.test(n)?'mac':'unknown',arch:/aarch64|arm64/.test(n)?'arm64':/x86_64|amd64|x64/.test(n)?'x64':'unknown'};}
function provenance(){
 if(!bindings||!Object.keys(bindings).length)return '<p>Not yet classified. Recipe availability, AM installation choice and channel policy: unknown. Catalog inclusion does not prove a recipe is absent.</p>';
 const labels={shared:'Shared installer',template:'Template-based recipe',custom:'Custom recipe',unknown:'Not yet classified'};
 return '<h3>AM installation recipes</h3>'+Object.entries(bindings).map(([arch,b])=>`<p>${esc(arch)}: ${labels[b.classification]} · recipe availability: ${esc(b.availability)} ${b.recipe?link(`https://github.com/${b.recipe.repository}/blob/${b.recipe.commit}/${b.recipe.path}`,'Review installation recipe'):''}</p>`).join('')+'<p>Classification describes pinned recipe evidence. Custom does not mean malicious. A shared installer does not establish binary authenticity or safety. Installation asset selection and channel policy are not evaluated here; review the architecture-specific recipe.</p>';
}
function detail(){
 if(!selected)return '';
 if(!Object.hasOwn(apps,selected))return '<article><h2>App absent from this snapshot</h2></article>';
 if(!source)return `<article><h2>${esc(selected)}</h2><p>${loading?'Loading source…':'Source unavailable; retry the same snapshot.'}</p></article>`;
 const same=Object.keys(apps).filter(n=>apps[n]===apps[selected]);
 const rs=releases(source).filter(([,r])=>!sourceQuery||`${r.tag} ${r.title??''} ${Object.values(r.assets).map(a=>a.name).join(' ')}`.toLowerCase().includes(sourceQuery));
 return `<article><h2 tabindex="-1" id="app-title">${esc(selected)}</h2><p>${link('https://github.com/'+source.repository,source.repository)} · Source ID ${source.repository_id}</p><p>Source collection: ${age(source.collected_at)}. This does not reobserve every retained release.</p><p>Bounded retained history: up to 32 newest releases plus a stable exception. History may be partial. Last scope ${source.scope.history_complete?'reached the end of upstream pagination':'did not reach the end of upstream pagination'}.</p><p>Same upstream source: ${same.map(n=>`<a href="?${new URLSearchParams({pin,variant,app:n})}" data-app="${esc(n)}">${esc(n)}</a>`).join(', ')}. Each AM identity and channel stays separate.</p><p>${link(rawURL(pin,apps[selected]),'Pinned source YAML')}</p><p>${esc(sourceHealth)}</p>${provenance()}${release&&!source.releases[release]?'<p role="status">Linked release is absent from this snapshot.</p>':''}${rs.map(([id])=>{
 const r=releaseFacts(source,id),assets=Object.entries(r.assets).filter(([,a])=>!sourceQuery||`${r.tag} ${r.title??''} ${a.name}`.toLowerCase().includes(sourceQuery)),limit=limits.get(id)??60,open=expanded.has(id);
 return `<details ${open?'open':''}><summary data-release="${id}">${esc(r.tag)} · ${r.prerelease?'Prerelease':'Non-prerelease'} · ${esc(r.published_at??r.created_at)}</summary>${open?`<p>${link(r.url,'Upstream release')} · Release ID ${id} · Observed ${age(r.observed_at)}</p><p>Platform highlighting is filename inference, separate from AM support. Binary authenticity is not established by catalog observation.</p>${assets.slice(0,limit).map(([aid,a])=>{const g=guess(a.name),match=($('platform').value==='all'||$('platform').value===g.os)&&($('arch').value==='all'||$('arch').value===g.arch);return `<div class="asset">${link(a.url,a.name)} · ${a.size} bytes<br><small>Asset ${aid} · media type: ${esc(a.media_type)} · inferred ${g.os} / ${g.arch}${match&&($('platform').value!=='all'||$('arch').value!=='all')?' · Possible platform match':''}</small></div>`;}).join('')||'<p>No assets match this source filter.</p>'}${assets.length>limit?`<button data-more="${id}">Show 60 more (${assets.length-limit} remaining)</button>`:''}`:''}</details>`;
 }).join('')}</article>`;
}
function render(){
 const start=performance.now(),active=document.activeElement,key=active?.dataset?.app?['app',active.dataset.app]:active?.dataset?.release?['release',active.dataset.release]:active?.dataset?.more?['more',active.dataset.more]:null;
 const rows=Object.keys(apps).filter(n=>n.includes(query)),shown=rows.slice(page*100,(page+1)*100);
 const href=n=>'?'+new URLSearchParams({pin,variant,app:n});
 const nav=shown.map(n=>`<a class="${selected===n?'selected':''}" data-app="${esc(n)}" href="${href(n)}">${esc(n)}</a>`).join('');
 const cards=shown.map(n=>`<a class="card" data-app="${esc(n)}" href="${href(n)}"><span class="tile">${esc(n.slice(0,2).toUpperCase())}</span><h3>${esc(n)}</h3><small>Open to load upstream facts</small></a>`).join('');
 const desk=`<table><thead><tr><th>AM identity</th><th>Source document</th></tr></thead><tbody>${shown.map(n=>`<tr><td><a data-app="${esc(n)}" href="${href(n)}">${esc(n)}</a></td><td>${esc(apps[n])}</td></tr>`).join('')}</tbody></table>`;
 $('variant').textContent=variant+' · '+names[variant];
 const pagination=`<p>${rows.length} matching AM identities · page ${page+1} of ${Math.max(1,Math.ceil(rows.length/100))}</p><button data-page="-1" ${page===0?'disabled':''}>Previous apps</button> <button data-page="1" ${(page+1)*100>=rows.length?'disabled':''}>Next apps</button>`;
 $('content').innerHTML=variant==='B'?`<div class="split"><aside class="list">${pagination}${nav}</aside><section>${detail()||'<h2>Choose an app</h2>'}</section></div>`:`${detail()}${pagination}${variant==='C'?desk:`<div class="grid">${cards}</div>`}`;
 $('content').querySelectorAll('[data-app]').forEach(a=>a.onclick=e=>{if(e.button!==0||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;e.preventDefault();selected=a.dataset.app;release=null;expanded.clear();limits.clear();save();loadDetail(true);});
 $('content').querySelectorAll('[data-release]').forEach(a=>a.onclick=e=>{e.preventDefault();const id=a.dataset.release;expanded.has(id)?expanded.delete(id):expanded.add(id);release=expanded.has(id)?id:null;save();render();});
 $('content').querySelectorAll('[data-more]').forEach(a=>a.onclick=()=>{limits.set(a.dataset.more,(limits.get(a.dataset.more)??60)+60);render();});
 $('content').querySelectorAll('[data-page]').forEach(a=>a.onclick=()=>{page+=Number(a.dataset.page);render();});
 if(key)[...$('content').querySelectorAll('[data-'+key[0]+']')].find(el=>el.dataset[key[0]]===key[1])?.focus({preventScroll:true});
 metrics.push({renderMs:performance.now()-start});if(metrics.length>20)metrics.shift();
 $('diagnostics').textContent=JSON.stringify({pin,statusPin,variant,selected,release,metrics},null,2);
}
async function loadDetail(focus=false){
 const token=++generation,c=pin,app=selected;source=null;bindings=null;sourceHealth='Refresh outcome not yet checked.';loading=true;$('error').textContent='';render();
 if(!app||!Object.hasOwn(apps,app)){loading=false;render();return;}
 try{
  const d=await client.source(c,apps[app],root);if(token!==generation)return;source=d;
  if(!release&&releases(d).length)expanded.add(releases(d)[0][0]);
  loading=false;render();checkSourceHealth(token,c,app,d);if(focus)$('app-title')?.focus({preventScroll:true});
  try{const b=await client.provenance(c,app,apps[app],d,root);if(token!==generation)return;bindings=b;render();}catch(e){if(token===generation)error(e);}
 }catch(e){if(token===generation){loading=false;error(e);render();}}
}
async function checkSourceHealth(token,c,app,d){
 try{
  statusPin??=await client.resolve('catalog-status-v1');
  const r=await client.report(statusPin),result=await client.sourceReport(statusPin,r,apps[app],d);
  if(token!==generation||c!==pin)return;
  sourceHealth=result?`Last reported source result: ${result.outcome}${result.reason?' ('+result.reason+')':''}, report ${r.summary.reported_at}, input C ${result.input_catalog??result.input_catalog_state}. It may describe a different catalog or an earlier attempt. Failed/unattempted refreshes do not freshen retained facts.`:'Source outcome unknown: detail is not available for the last reported run.';
 }catch{if(token!==generation)return;sourceHealth='Refresh outcome unknown: status or source detail unavailable. Catalog facts remain available.';}
 render();
}
async function start(latest=false){
 const token=++generation;source=null;bindings=null;apps={};root=null;$('error').textContent='';$('status').textContent='Loading catalog…';render();
 try{
  if(latest||!pin){const c=await client.resolve('release-catalog-v3');if(token!==generation)return;pin=c;save(!latest);}
  const c=pin,result=await client.roots(c);if(token!==generation)return;root=result.root;apps=result.apps;save(true);
  $('status').textContent=`${Object.keys(apps).length} AM identities · ${new Set(Object.values(apps)).size} distinct source documents · Snapshot ${c}`;render();if(selected)await loadDetail();
 }catch(e){if(token===generation){$('status').textContent='Catalog unavailable';error(e);}}
}
function cycle(d){keyboard.resetScope();variant=['A','B','C'][(['A','B','C'].indexOf(variant)+d+3)%3];save();render();}
const keyboard=installKeyboard({document,window,cycle,help:$('keyhelp')});
$('prev').onclick=()=>cycle(-1);$('next').onclick=()=>cycle(1);
$('shortcuts').onclick=()=>$('keyhelp').showModal();$('closehelp').onclick=()=>$('keyhelp').close();
$('search').oninput=e=>{query=e.target.value.toLowerCase();page=0;render();};
$('source-search').oninput=e=>{sourceQuery=e.target.value.toLowerCase();render();};
$('platform').onchange=$('arch').onchange=render;
$('refresh').onclick=()=>start(true);$('retry').onclick=()=>root?loadDetail():start();
$('theme').onclick=()=>{document.body.className=getComputedStyle(document.body).getPropertyValue('--bg').trim()==='#101820'?'light':'dark';};
$('how').onclick=()=>{$('info').innerHTML='<h2>How it works</h2><p>Upstream source → observed release facts → client selection → installation recipe. The catalog records upstream metadata; clients choose releases and assets. AM executes an installation recipe only when you install an app. Catalog-only inclusion proves neither installation support nor recipe absence.</p><p>Public browsing needs no GitHub token. Maintainer collection consumes the maintainer’s GitHub quota. Downloads come from upstream; inspect their provenance and the pinned recipe before installation. Observation is not verification of binary authenticity.</p><p>Each tab keeps a catalog commit C. Load latest is explicit. Source collection time and each retained release’s observation time are different. Failed or unattempted refreshes leave prior facts unchanged. Earlier Git metadata does not guarantee old binaries remain downloadable.</p>';};
$('health').onclick=async()=>{
 $('info').textContent='Loading independent status…';
 try{
  statusPin??=await client.resolve('catalog-status-v1');report=await client.report(statusPin);
  const {root:s,summary:r}=report,measure=m=>m.state==='known'?String(m.value):'unknown';
  $('info').innerHTML=`<h2>Catalog health</h2><p>Last reported run: ${age(r.reported_at)}. It may not be the latest attempt: interruption or reporting failure can leave gaps.</p><p>Status S: ${statusPin}. Catalog C: ${esc(pin)}. ${s.last_confirmed_publication.state==='confirmed'?(s.last_confirmed_publication.commit===pin?'This catalog is the last confirmed publication known to this report.':'C differs from the publication known to this report. Confirmation may lag, or this is a different/older pin; ancestry is not established.'):'Last confirmed publication is unknown.'}</p><p>Collection: ${r.collection}; validation: ${r.validation}; publication: ${r.publication.state}; stop: ${r.stop_reason}.</p><h3>Distinct source counts</h3><dl>${Object.entries(r.counts).map(([k,v])=>`<dt>${esc(k)}</dt><dd>${measure(v)}</dd>`).join('')}</dl><h3>Observed usage</h3><dl>${Object.entries(r.metrics).map(([k,v])=>`<dt>${esc(k)}</dt><dd>${measure(v)}</dd>`).join('')}</dl><h3>Configured allowances</h3><dl>${Object.entries(r.budgets).map(([k,v])=>`<dt>${esc(k)}</dt><dd>${v}</dd>`).join('')}</dl><p>Current tree, local objects, packed history and remote storage are separate measurements. Unknown is not zero; configured allowances do not establish capacity.</p><p>${Object.keys(s.summaries).length} retained reports, ${Object.keys(s.details).length} attempts with available detail; missing reports do not mean success. ${link(r.actions_url,'Reported Actions run')} · ${link(r.recent_runs_url,'Recent collection runs')} (Actions may require sign-in).</p><button id="statistics">Load freshness and daily history</button>`;
  $('statistics').onclick=async()=>{try{const stats=await client.statistics(statusPin,report);$('info').insertAdjacentHTML('beforeend',`<h3>Source observation ages</h3><p>Measured ${esc(stats.measured_at)}; evaluated ${esc(stats.freshness.evaluated_at)} at C ${esc(stats.freshness.catalog)}. Source ages do not measure retained-release freshness.</p><dl>${Object.entries(stats.freshness).filter(([,v])=>typeof v==='object').map(([k,v])=>`<dt>${esc(k)}</dt><dd>${measure(v)}</dd>`).join('')}</dl><h3>Reported daily history</h3>${Object.entries(stats.days).map(([day,d])=>`<p>${esc(day)}: ${d.reported_attempts} reported attempts, ${d.successful_sources} successful / ${d.failed_sources} failed source totals; ${d.unknown_source_count_attempts} attempts with unknown counts. Reports ${esc(d.first_report)} to ${esc(d.last_report)}.</p>`).join('')}<p>Missing days/attempts are gaps, never interpolated successes. Tree retention does not erase Git history.</p>`);}catch(e){error(e);}};
 }catch(e){$('info').textContent='Status unavailable. Catalog browsing remains available. Retry Catalog health at the same resolved S.';error(e);}
};
window.addEventListener('popstate',async e=>{const state=e.state;readRoute();await start();if(state?.app)[...$('content').querySelectorAll('[data-app]')].find(a=>a.dataset.app===state.app)?.focus({preventScroll:true});window.scrollTo(0,state?.scroll??0);});readRoute();start();
