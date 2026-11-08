import delivery from './delivery.mjs';
import {Catalog,releaseFacts} from './catalog.mjs';
import {installKeyboard} from './keyboard.mjs';
const $=id=>document.getElementById(id),client=new Catalog(fetch,delivery),names={A:'Directory',B:'Explorer',C:'Release desk'};
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const link=(url,label)=>/^https:\/\//.test(url??'')?`<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(label)}</a>`:esc(label);
const helpTopics={
 search:['Search scope','App search covers names across the catalog. The source filter searches release titles, tags and asset names only within the opened source. Sources are loaded when opened.'],
 platform:['Platform guesses','Platform and architecture highlights are inferred from asset filenames. A possible match does not establish AM installation support or binary authenticity.'],
 freshness:['Observation times','Source collection time records a successful collection scope. Retained releases can have older observation times; refreshing a source does not reobserve every retained release. Failed or unattempted refreshes leave prior facts unchanged.'],
 history:['Retained history','The catalog keeps up to 32 newest observed releases, plus the newest non-prerelease if those 32 contain none. Retained history may be partial even when the last collection reached the end of upstream pagination. Earlier Git metadata does not guarantee old binaries remain downloadable.'],
 identity:['AM identities','AM identities sharing an upstream source remain separate entries. Their installation recipes and stable/nightly channel policies can differ.'],
 recipe:['Recipe evidence','Classification describes evidence bound to a pinned, architecture-specific recipe. Unknown does not mean custom, and custom does not mean malicious. A shared installer does not establish binary authenticity or safety. Catalog inclusion proves neither installation support nor recipe absence. This browser does not evaluate installation asset selection or channel policy; review the linked recipe.'],
 refresh:['Reported refresh','The source result comes from the last reported run, which may describe a different catalog or an earlier attempt. Failed or unattempted refreshes do not freshen retained facts. Missing detail means unknown.'],
 snapshot:['Pinned snapshots','Each tab keeps one catalog revision. Retry reads that same revision. Load latest explicitly chooses a new one. Status is resolved independently and can lag catalog publication; different revisions alone do not establish which is newer.'],
 reporting:['Last reported run','This may not be the latest attempt. Interruption or reporting failure can leave gaps. Missing reports or days do not mean success. Actions links may require sign-in; public summaries do not.'],
 resources:['Measurements and limits','Current tree, local objects, packed history and remote storage are separate measurements. Unknown is not zero. Configured allowances do not establish capacity.'],
 statistics:['Freshness and history','Source-age buckets describe successful source scopes, not the freshness of every retained release. Daily totals cover reported attempts only; missing days and attempts are gaps. Tree retention does not erase Git history.']
};
const helpButton=topic=>`<button type="button" class="context-help" data-help="${topic}" aria-label="About ${esc(helpTopics[topic][0].toLowerCase())}" aria-haspopup="dialog">?</button>`;
if(delivery){
 $('review-notice').hidden=false;
 $('review-notice').textContent='Preview · Saved release data';
 helpTopics.snapshot[1]+=` This review uses saved public observations from ${delivery.baseline}. Its snapshot ID identifies bundled content, not a catalog Git commit. ${delivery.refused.length} source was omitted for conflicting saved tag evidence. Recipe evidence is not included; unknown does not mean absent. Load latest selects the snapshot bundled with this site build.`;
}
let helpOrigin,sourceHealthContext='Refresh pending';
document.addEventListener('click',e=>{
 const button=e.target.closest('[data-help]');if(!button)return;
 const topic=button.dataset.help,entry=helpTopics[topic];if(!entry)return;
 helpOrigin=button;$('context-title').textContent=entry[0];$('context-body').textContent=entry[1]+(topic==='refresh'?'\n\n'+sourceHealthContext:topic==='history'&&source?'\n\nLast collection '+(source.scope.history_complete?'reached':'did not reach')+' the end of upstream pagination.':'');
 $('context-help').showModal();
});
$('close-context-help').onclick=()=>$('context-help').close();
$('context-help').addEventListener('close',()=>{
 const replacement=helpOrigin?.isConnected?helpOrigin:[...document.querySelectorAll('[data-help]')].find(b=>b.dataset.help===helpOrigin?.dataset.help);
 replacement?.focus({preventScroll:true});
});
let pin,selected,variant='A',release,apps={},root,source,bindings,loading=false,query='',sourceQuery='',generation=0,page=0,statusPin,report,sourceHealth='Refresh pending';
const expanded=new Set(),limits=new Map(),metrics=[];
const route=()=>'?'+new URLSearchParams({variant,...(pin?{pin}:{}),...(selected?{app:selected}:{}),...(release?{release}:{})});
function save(replace=false){
 if(!replace)history.replaceState({scroll:window.scrollY,app:document.activeElement?.dataset?.app},'',location.href);
 history[replace?'replaceState':'pushState'](replace?history.state:null,'',route());}
function readRoute(){const p=new URLSearchParams(location.search);pin=p.get('pin');selected=p.get('app');release=p.get('release');variant=names[p.get('variant')]?p.get('variant'):'A';expanded.clear();limits.clear();if(release)expanded.add(release);}
function error(e){$('error').textContent=e.message;$('retry').hidden=false;}
function age(time){const hours=Math.max(0,(Date.now()-Date.parse(time))/3600000);return `${esc(time)} (${hours.toFixed(1)} hours ago)`;}
function shortAge(time){const h=Math.max(0,(Date.now()-Date.parse(time))/3600000);return h<48?`${Math.round(h)}h ago`:`${Math.floor(h/24)}d ago`;}
function sizeLabel(value){const units=['B','KiB','MiB','GiB','TiB'];let unit=0,scale=1n;while(unit<units.length-1&&value>=scale*1024n){scale*=1024n;unit++;}return `${value/scale}${scale>1n?'.'+(value%scale*10n/scale):''} ${units[unit]}`;}
function releases(d){return Object.entries(d.releases).sort(([a,x],[b,y])=>(y.published_at??y.created_at).localeCompare(x.published_at??x.created_at)||(BigInt(a)<BigInt(b)?1:BigInt(a)>BigInt(b)?-1:0));}
function guess(name){const n=name.toLowerCase();return {os:/appimage|linux/.test(n)?'linux':/\.exe$|\.msi$|windows|win32|win64/.test(n)?'windows':/\.dmg$|darwin|macos|osx/.test(n)?'mac':'unknown',arch:/aarch64|arm64/.test(n)?'arm64':/x86_64|amd64|x64/.test(n)?'x64':'unknown'};}
function provenance(){
 const labels={shared:'Shared installer',template:'Template-based recipe',custom:'Custom recipe',unknown:'Not yet classified'};
 if(!bindings||!Object.keys(bindings).length)return `<p class="recipe-overview">AM recipes: Not yet classified ${helpButton('recipe')}</p>`;
 const entries=Object.entries(bindings),known=entries.some(([,b])=>b.classification!=='unknown');
 const review=b=>b.recipe?link(`https://github.com/${b.recipe.repository}/blob/${b.recipe.commit}/${b.recipe.path}`,'Review installation recipe'):'';
 return entries.filter(([,b])=>b.classification==='custom').map(([arch,b])=>`<p class="recipe-overview">${esc(arch)} · Custom recipe · ${review(b)}</p>`).join('')+`<details class="recipe-overview"><summary>AM recipes · ${known?'Architecture-specific evidence':'Not yet classified'}</summary><div class="recipe-list">${entries.map(([arch,b])=>`<p><strong>${esc(arch)}</strong> · ${labels[b.classification]} · ${esc(b.availability)} ${review(b)}</p>`).join('')}</div><p>Installation choice / channel policy: unknown. ${helpButton('recipe')}</p></details>`;
}
function detail(){
 if(!selected)return '';
 if(!Object.hasOwn(apps,selected))return '<article><h2>App absent from this snapshot</h2></article>';
 if(!source)return `<article><h2>${esc(selected)}</h2><p>${loading?'Loading source…':'Source unavailable; retry the same snapshot.'}</p></article>`;
 const same=Object.keys(apps).filter(n=>apps[n]===apps[selected]);
 const rs=releases(source).filter(([,r])=>!sourceQuery||`${r.tag} ${r.title??''} ${Object.values(r.assets).map(a=>a.name).join(' ')}`.toLowerCase().includes(sourceQuery));
 return `<article><div class="app-heading"><div><h2 tabindex="-1" id="app-title">${esc(selected)}</h2><p>${link('https://github.com/'+source.repository,source.repository)}</p></div><span class="badge">${Object.keys(source.releases).length} releases</span></div><div class="app-meta"><p title="${esc(source.collected_at)}">Collected ${shortAge(source.collected_at)} ${helpButton('freshness')}</p><p>Bounded / partial history ${helpButton('history')}</p><p>${esc(sourceHealth)} ${helpButton('refresh')}</p></div>${same.length>1?`<p class="related">Same source: ${same.filter(n=>n!==selected).map(n=>`<a href="?${new URLSearchParams({pin,variant,app:n})}" data-app="${esc(n)}">${esc(n)}</a>`).join(', ')} ${helpButton('identity')}</p>`:''}${provenance()}${release&&!source.releases[release]?'<p role="status">Linked release is absent from this snapshot.</p>':''}${rs.map(([id])=>{
 const r=releaseFacts(source,id),assets=Object.entries(r.assets).filter(([,a])=>!sourceQuery||`${r.tag} ${r.title??''} ${a.name}`.toLowerCase().includes(sourceQuery)),limit=limits.get(id)??60,open=expanded.has(id);
 return `<details ${open?'open':''}><summary data-release="${id}">${esc(r.tag)} · ${r.prerelease?'Prerelease':'Non-prerelease'} · ${esc((r.published_at??r.created_at).slice(0,10))}</summary>${open?`<p class="release-meta" title="${esc(r.observed_at)}">${link(r.url,'Release notes ↗')} · Observed ${shortAge(r.observed_at)} · Filename guesses ${helpButton('platform')}</p>${assets.slice(0,limit).map(([aid,a])=>{const g=guess(a.name),match=($('platform').value==='all'||$('platform').value===g.os)&&($('arch').value==='all'||$('arch').value===g.arch);return `<div class="asset">${link(a.url,a.name)} · <small>${sizeLabel(a.size)} · inferred ${g.os} / ${g.arch}${match&&($('platform').value!=='all'||$('arch').value!=='all')?' · Possible match':''}</small><details class="source-details"><summary>Asset details</summary><small>Asset ${aid} · ${a.size} bytes · media type: ${esc(a.media_type)}</small></details></div>`;}).join('')||'<p>No assets match this source filter.</p>'}${assets.length>limit?`<button data-more="${id}">Show 60 more (${assets.length-limit} remaining)</button>`:''}`:''}</details>`;
 }).join('')}<details class="source-details"><summary>Source details</summary><p>Source ID ${source.repository_id} · ${link(client.url(pin,apps[selected]),'Pinned source YAML')}</p><p>Collected ${esc(source.collected_at)} · Last scope ${source.scope.history_complete?'reached':'did not reach'} the end of upstream pagination.</p></details></article>`;
}
function render(){
 $('source-tools').hidden=!selected;document.body.classList.toggle('has-selection',Boolean(selected));
 const start=performance.now(),active=document.activeElement,key=active?.dataset?.app?['app',active.dataset.app]:active?.dataset?.release?['release',active.dataset.release]:active?.dataset?.more?['more',active.dataset.more]:active?.dataset?.help?['help',active.dataset.help]:null;
 const rows=Object.keys(apps).filter(n=>n.includes(query)),shown=rows.slice(page*100,(page+1)*100);
 const href=n=>'?'+new URLSearchParams({pin,variant,app:n});
 const nav=shown.map(n=>`<a class="${selected===n?'selected':''}" data-app="${esc(n)}" href="${href(n)}">${esc(n)}</a>`).join('');
 const cards=shown.map(n=>`<a class="card" data-app="${esc(n)}" href="${href(n)}"><span class="tile">${esc(n.slice(0,2).toUpperCase())}</span><h3>${esc(n)}</h3></a>`).join('');
 const desk=`<table><thead><tr><th>AM identity</th><th>Source document</th></tr></thead><tbody>${shown.map(n=>`<tr><td><a data-app="${esc(n)}" href="${href(n)}">${esc(n)}</a></td><td>${esc(apps[n])}</td></tr>`).join('')}</tbody></table>`;
 $('variant').textContent=variant+' · '+names[variant];
 const pagination=`<div class="directory-toolbar"><p>${rows.length} apps${rows.length>100?` · Page ${page+1} of ${Math.ceil(rows.length/100)}`:''}</p>${rows.length>100?`<button data-page="-1" ${page===0?'disabled':''}>Previous apps</button><button data-page="1" ${(page+1)*100>=rows.length?'disabled':''}>Next apps</button>`:''}</div>`;
 $('content').innerHTML=variant==='B'?`<div class="split"><aside class="list">${pagination}${nav}</aside><section>${detail()||'<h2>Choose an app</h2>'}</section></div>`:`${detail()}${pagination}${variant==='C'?'<div class="table-wrap">'+desk+'</div>':`<div class="grid">${cards}</div>`}`;
 $('content').querySelectorAll('[data-app]').forEach(a=>a.onclick=e=>{if(e.button!==0||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;e.preventDefault();selected=a.dataset.app;release=null;expanded.clear();limits.clear();save();loadDetail(true);});
 $('content').querySelectorAll('[data-release]').forEach(a=>a.onclick=e=>{e.preventDefault();const id=a.dataset.release;expanded.has(id)?expanded.delete(id):expanded.add(id);release=expanded.has(id)?id:null;save();render();});
 $('content').querySelectorAll('[data-more]').forEach(a=>a.onclick=()=>{limits.set(a.dataset.more,(limits.get(a.dataset.more)??60)+60);render();});
 $('content').querySelectorAll('[data-page]').forEach(a=>a.onclick=()=>{page+=Number(a.dataset.page);render();});
 if(key)[...$('content').querySelectorAll('[data-'+key[0]+']')].find(el=>el.dataset[key[0]]===key[1])?.focus({preventScroll:true});
 metrics.push({renderMs:performance.now()-start});if(metrics.length>20)metrics.shift();
 $('diagnostics').textContent=JSON.stringify({pin,statusPin,variant,selected,release,metrics},null,2);
}
async function loadDetail(focus=false){
 const token=++generation,c=pin,app=selected;source=null;bindings=null;sourceHealth='Refresh pending';sourceHealthContext=sourceHealth;loading=true;$('error').textContent='';$('retry').hidden=true;render();
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
  sourceHealthContext=result?`Report ${r.summary.reported_at}; input catalog: ${result.input_catalog??result.input_catalog_state}.`:'Source detail is not available for the last reported run.';
  sourceHealth=result?`Last refresh: ${result.outcome}`:'Refresh unknown';
 }catch{if(token!==generation)return;sourceHealth='Refresh unknown';sourceHealthContext='Status or source detail is unavailable. Catalog facts remain available.';}
 render();
}
async function start(latest=false){
 const token=++generation;source=null;bindings=null;apps={};root=null;$('error').textContent='';$('retry').hidden=true;$('status').textContent='Loading catalog…';render();
 try{
  if(latest||!pin){const c=await client.resolve('release-catalog-v3');if(token!==generation)return;pin=c;save(!latest);}
  const c=pin,result=await client.roots(c);if(token!==generation)return;root=result.root;apps=result.apps;save(true);
  $('status').textContent=`${Object.keys(apps).length} AM identities · ${new Set(Object.values(apps)).size} sources · ${delivery?'Review snapshot':'Snapshot'} ${c.slice(0,10)}`;render();if(selected)await loadDetail();
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
$('theme').onclick=()=>{const theme=getComputedStyle(document.body).getPropertyValue('--bg').trim()==='#101820'?'light':'dark';document.body.classList.remove('light','dark');document.body.classList.add(theme);};
$('how').onclick=()=>{$('info').innerHTML='<h2>How it works</h2><p>Upstream source → observed release facts → client selection → installation recipe. The catalog records upstream metadata; clients choose releases and assets. AM executes an installation recipe only when you install an app. Catalog-only inclusion proves neither installation support nor recipe absence.</p><p>Public browsing needs no GitHub token. Maintainer collection consumes the maintainer’s GitHub quota. Downloads come from upstream; inspect their provenance and the pinned recipe before installation. Observation is not verification of binary authenticity.</p><p>Each tab keeps a catalog commit C. Load latest is explicit. Source collection time and each retained release’s observation time are different. Failed or unattempted refreshes leave prior facts unchanged. Earlier Git metadata does not guarantee old binaries remain downloadable.</p>';};
$('health').onclick=async()=>{
 $('info').textContent='Loading independent status…';
 try{
  statusPin??=await client.resolve('catalog-status-v1');report=await client.report(statusPin);
  const {root:s,summary:r}=report,measure=m=>m.state==='known'?String(m.value):'unknown';
  $('info').innerHTML=`<h2>Catalog health</h2><p>Last reported run: ${age(r.reported_at)} ${helpButton('reporting')}</p><details><summary>Catalog and status revisions</summary><p>Status: ${statusPin}<br>Catalog: ${esc(pin)}</p></details><p>${s.last_confirmed_publication.state==='confirmed'?(s.last_confirmed_publication.commit===pin?'Catalog confirmed by this report.':'Catalog differs from the report’s confirmed revision.'):'Last confirmed publication is unknown.'} ${helpButton('snapshot')}</p><p>Collection: ${r.collection}; validation: ${r.validation}; publication: ${r.publication.state}; stop: ${r.stop_reason}.</p><h3>Distinct source counts</h3><dl>${Object.entries(r.counts).map(([k,v])=>`<dt>${esc(k)}</dt><dd>${measure(v)}</dd>`).join('')}</dl><h3>Observed usage ${helpButton('resources')}</h3><dl>${Object.entries(r.metrics).map(([k,v])=>`<dt>${esc(k)}</dt><dd>${measure(v)}</dd>`).join('')}</dl><h3>Configured allowances</h3><dl>${Object.entries(r.budgets).map(([k,v])=>`<dt>${esc(k)}</dt><dd>${v}</dd>`).join('')}</dl><p>${Object.keys(s.summaries).length} retained reports, ${Object.keys(s.details).length} attempts with detail. ${link(r.actions_url,'Reported Actions run')} · ${link(r.recent_runs_url,'Recent collection runs')}.</p><button id="statistics">Load freshness and daily history</button>`;
  $('statistics').onclick=async()=>{try{const stats=await client.statistics(statusPin,report);$('info').insertAdjacentHTML('beforeend',`<h3>Source observation ages ${helpButton('statistics')}</h3><p>Measured ${esc(stats.measured_at)}; evaluated ${esc(stats.freshness.evaluated_at)} at C ${esc(stats.freshness.catalog)}.</p><dl>${Object.entries(stats.freshness).filter(([,v])=>typeof v==='object').map(([k,v])=>`<dt>${esc(k)}</dt><dd>${measure(v)}</dd>`).join('')}</dl><h3>Reported daily history</h3>${Object.entries(stats.days).map(([day,d])=>`<p>${esc(day)}: ${d.reported_attempts} reported attempts, ${d.successful_sources} successful / ${d.failed_sources} failed source totals; ${d.unknown_source_count_attempts} attempts with unknown counts. Reports ${esc(d.first_report)} to ${esc(d.last_report)}.</p>`).join('')}`);}catch(e){error(e);}};
 }catch(e){$('info').textContent='Status unavailable. Catalog browsing remains available. Retry Catalog health at the same resolved S.';error(e);}
};
window.addEventListener('popstate',async e=>{const state=e.state;readRoute();await start();if(state?.app)[...$('content').querySelectorAll('[data-app]')].find(a=>a.dataset.app===state.app)?.focus({preventScroll:true});window.scrollTo(0,state?.scroll??0);});readRoute();start();
