import delivery from './delivery.mjs';
import {Catalog,releaseFacts,gitFacts,guess,failure} from './catalog.mjs';
import {installKeyboard} from './keyboard.mjs';
const $=id=>document.getElementById(id),client=new Catalog(fetch,{review:delivery}),names={A:'Directory',B:'Explorer',C:'Release desk'};
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const link=(url,label)=>/^https:\/\//.test(url??'')?`<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(label)}</a>`:esc(label);
const ARCHES=['x86_64','aarch64','i686','armv7l'],OLD_DAYS=14;
// Ticket 13's validated text: one sentence per topic.
const helpTopics={
 search:['Search','App search looks at app names. Inside an app, the filter searches its release titles, tags and file names.'],
 seen:['Last seen','When this repository’s releases were last read from GitHub. A release with its own “last seen” wasn’t in the latest check: GitHub may have deleted it.'],
 kept:['Kept releases','The 8 newest releases, plus the newest stable one and the newest one with Linux downloads. Older ones are in the catalog’s history, not on this page.'],
 failed:['Failed checks','The last good list stays. “Never collected” means no check has succeeded yet, so there’s nothing to install from.'],
 old:['Old data','Not seen for more than 14 days. AM warns before installing from it, then continues.'],
 recipes:['Recipes','“Reviewed installer” or “Recipe script, read it before installing”, per processor type. An app without a recipe for a processor type isn’t listed for it.'],
 guesses:['Guesses','Linux and processor type are guessed from file names (AppImage, linux, x86_64, aarch64, i686, armv7l and their aliases). A guess doesn’t mean AM can install the file.'],
 same:['Same source, several apps','Several AM apps can install from one GitHub repository; each has its own recipe and rules.'],
 health:['Catalog health','The last 64 checks: how many repositories each read, how many failed, and why a check stopped early. Also how old the data is: under 24 hours, up to 2 days, up to 14 days, older, or never collected.'],
};
const HOW=[
 ['The catalog lists the releases GitHub shows for each app AM knows.','AM looks up downloads here instead of asking GitHub on every install.'],
 ['The catalog only records what GitHub lists; AM’s recipe for each app decides which release and file to install.','one list serves every recipe’s own rules, such as stable or nightly, and the processor type.'],
 ['Each check reads a few hundred repositories, so every repository is read again every few days.','GitHub limits how much one check may read.'],
 ['Each repository shows when its releases were last read from GitHub (“Last seen 3 h ago”).','so you can tell how current its list is.'],
 ['We keep each app’s 8 newest releases, plus its newest stable one and its newest one with Linux downloads.','enough to install and update any app, while the catalog stays small.'],
 ['A release deleted on GitHub is removed once the catalog reads the repository’s whole release list; the catalog’s history keeps it. A release kept on purpose that GitHub no longer showed in the latest check shows when it was last seen.','the list matches GitHub without guessing that something is gone.'],
 ['Two releases can share one tag; both are listed.','some projects publish one version as two releases, each with part of the files.'],
 ['When a check fails, the repository keeps its last good list and says why: “last attempt failed 1 h ago: GitHub couldn’t be reached.”','a passing GitHub problem shouldn’t empty an app.'],
 ['A repository not seen for more than 14 days is marked, and AM warns before installing from data this old.','old data may point at files that changed or are gone; AM still lets you install.'],
 ['“Reviewed installer”: this app’s AM recipe only names what to download; AM’s reviewed installer does the rest. “Recipe script”: this app’s AM recipe is its own shell script; read it before installing.','a reviewed installer can be trusted without reading shell; a script can do anything.'],
 ['We guess from file names which downloads are for Linux and which processor they need; a guess doesn’t mean AM can install it.','GitHub doesn’t say which file is for which system.'],
 ['Downloads come from each project on GitHub, not from the catalog, and the catalog doesn’t check that a file is safe.','the catalog records facts; trust is between you, the project and the recipe.'],
];
const LABELS={declaration:'Reviewed installer',script:'Recipe script, read it before installing'};
const helpButton=topic=>`<button type="button" class="context-help" data-help="${topic}" aria-label="About ${esc(helpTopics[topic][0].toLowerCase())}" aria-haspopup="dialog">?</button>`;
if(delivery){$('review-notice').hidden=false;$('review-notice').textContent=`Preview · ${delivery.label}`;}
let helpOrigin;
document.addEventListener('click',e=>{
 const button=e.target.closest('[data-help]');if(!button)return;
 const entry=helpTopics[button.dataset.help];if(!entry)return;
 helpOrigin=button;$('context-title').textContent=entry[0];$('context-body').textContent=entry[1];
 $('context-help').showModal();
});
$('close-context-help').onclick=()=>$('context-help').close();
$('context-help').addEventListener('close',()=>{
 const replacement=helpOrigin?.isConnected?helpOrigin:[...document.querySelectorAll('[data-help]')].find(b=>b.dataset.help===helpOrigin?.dataset.help);
 replacement?.focus({preventScroll:true});
});
let selected,variant='A',release,apps={},source,loading=false,query='',sourceQuery='',generation=0,page=0;
const expanded=new Set(),limits=new Map(),metrics=[];
const route=()=>'?'+new URLSearchParams({variant,...(selected?{app:selected}:{}),...(release?{release}:{})});
function save(replace=false){
 if(!replace)history.replaceState({scroll:window.scrollY,app:document.activeElement?.dataset?.app},'',location.href);
 history[replace?'replaceState':'pushState'](replace?history.state:null,'',route());}
function readRoute(){const p=new URLSearchParams(location.search);selected=p.get('app');release=p.get('release');variant=names[p.get('variant')]?p.get('variant'):'A';expanded.clear();limits.clear();if(release)expanded.add(release);}
function error(e){$('error').textContent=e.message;$('retry').hidden=false;}
const hoursSince=time=>Math.max(0,(Date.now()-Date.parse(time))/3600000);
function ago(time){const h=hoursSince(time);return h<48?`${Math.round(h)} h ago`:`${Math.floor(h/24)} days ago`;}
function sizeLabel(value){const units=['B','KiB','MiB','GiB','TiB'];let unit=0,scale=1n;while(unit<units.length-1&&value>=scale*1024n){scale*=1024n;unit++;}return `${value/scale}${scale>1n?'.'+(value%scale*10n/scale):''} ${units[unit]}`;}
function releases(d){return Object.entries(d.releases).sort(([a,x],[b,y])=>y.published_at.localeCompare(x.published_at)||(BigInt(a)<BigInt(b)?1:BigInt(a)>BigInt(b)?-1:0));}
function recipes(app){
 const entry=apps[app],rows=ARCHES.filter(arch=>entry[arch]).map(arch=>`<p><strong>${esc(arch)}</strong> · ${LABELS[entry[arch]]} · ${link(`https://github.com/mareklangiewicz/AM/blob/main-marek/programs/${arch}/${app}`,'Read the recipe')}</p>`);
 return `<details class="recipe-overview"><summary>AM recipes ${helpButton('recipes')}</summary><div class="recipe-list">${rows.join('')||'<p>No recipe.</p>'}</div></details>`;
}
// Ticket 11's state line: last seen, a later failure, data older than 14 days.
function state(){
 const reason=failure(source),failed=source.failed_at?` · last attempt failed ${ago(source.failed_at)}: ${esc(reason)} ${helpButton('failed')}`:'';
 if(!source.observed_at)return `<p>Never collected${failed}</p>`;
 const old=hoursSince(source.observed_at)>OLD_DAYS*24?` · <strong>Last seen ${Math.floor(hoursSince(source.observed_at)/24)} days ago: AM warns before installing from data this old.</strong> ${helpButton('old')}`:'';
 return `<p title="${esc(source.observed_at)}">Last seen ${ago(source.observed_at)} ${helpButton('seen')}${failed}${old}</p>`;
}
function gitObservations(){
 if(!source.git_scope)return '';
 const refs=gitFacts(source,sourceQuery);
 return `<section class="git-observations"><h3>Git refs</h3><p>Tags: ${source.git_scope.tags?(source.git_scope.tags_history_complete?'every tag':'the newest 100'):'not read'}.</p>${refs.map(([name,ref])=>`<details class="source-details"><summary>${esc(name)}</summary><p>${link(`https://github.com/${source.repository}/tree/${ref.commit}`,ref.commit)}</p>${Object.entries(ref.files??{}).map(([path,file])=>`<details><summary>${esc(path)}</summary><p>Blob ${esc(file.blob)}</p><pre style="white-space:pre-wrap;overflow-wrap:anywhere">${esc(file.content)}</pre></details>`).join('')}</details>`).join('')||'<p>No refs match this filter.</p>'}</section>`;
}
function detail(){
 if(!selected)return '';
 if(!Object.hasOwn(apps,selected))return '<article><h2>App not in the catalog</h2></article>';
 if(!source)return `<article><h2>${esc(selected)}</h2><p>${loading?'Loading…':'Repository unavailable; retry.'}</p></article>`;
 const path=apps[selected].repository,same=Object.keys(apps).filter(n=>apps[n].repository===path);
 const rs=releases(source).filter(([,r])=>!sourceQuery||`${r.tag} ${r.title??''} ${Object.values(r.assets).map(a=>a.name).join(' ')}`.toLowerCase().includes(sourceQuery));
 const platform=$('platform').value,arch=$('arch').value;
 return `<article><div class="app-heading"><div><h2 tabindex="-1" id="app-title">${esc(selected)}</h2><p>${link('https://github.com/'+source.repository,source.repository)}</p></div><span class="badge">${Object.keys(source.releases).length} releases ${helpButton('kept')}</span></div><div class="app-meta">${state()}</div>${same.length>1?`<p class="related">Same source: ${same.filter(n=>n!==selected).map(n=>`<a href="?${new URLSearchParams({variant,app:n})}" data-app="${esc(n)}">${esc(n)}</a>`).join(', ')} ${helpButton('same')}</p>`:''}${recipes(selected)}${gitObservations()}${release&&!source.releases[release]?'<p role="status">This release is no longer in the catalog.</p>':''}${rs.map(([id])=>{
 const r=releaseFacts(source,id),assets=Object.entries(r.assets).filter(([,a])=>!sourceQuery||`${r.tag} ${r.title} ${a.name}`.toLowerCase().includes(sourceQuery)),limit=limits.get(id)??60,open=expanded.has(id);
 return `<details ${open?'open':''}><summary data-release="${id}">${esc(r.tag)} · ${r.prerelease?'Prerelease':'Stable'} · ${esc(r.published_at.slice(0,10))}</summary>${open?`<p class="release-meta">${link(r.url,'Release notes ↗')}${r.own_observation?` · <span title="${esc(r.observed_at)}">Last seen ${ago(r.observed_at)}</span> ${helpButton('seen')}`:''} · Guesses ${helpButton('guesses')}</p>${assets.slice(0,limit).map(([aid,a])=>{const g=guess(a.name),filtered=platform!=='all'||arch!=='all',match=(platform==='all'||(platform==='linux')===g.linux)&&(arch==='all'||arch===g.arch);return `<div class="asset">${link(a.url,a.name)} · <small>${sizeLabel(a.size)} · ${g.linux?'Linux':'not Linux'} / ${g.arch??'processor unknown'} (guess)${filtered&&match?' · Possible match':''}</small><details class="source-details"><summary>File details</summary><small>Asset ${aid} · ${a.size} bytes${a.sha256pre?` · SHA-256 starts ${esc(a.sha256pre)}`:''}</small></details></div>`;}).join('')||'<p>No files match this filter.</p>'}${assets.length>limit?`<button data-more="${id}">Show 60 more (${assets.length-limit} remaining)</button>`:''}`:''}</details>`;
 }).join('')}<details class="source-details"><summary>Repository details</summary><p>GitHub repository ID ${source.repository_id} · ${link(client.url(path),'Catalog file')}</p>${source.observed_at?`<p>Last read ${esc(source.observed_at)} · that read ${source.history_complete?'reached':'did not reach'} the end of the release list.</p>`:''}</details></article>`;
}
function render(){
 $('source-tools').hidden=!selected;document.body.classList.toggle('has-selection',Boolean(selected));
 const start=performance.now(),active=document.activeElement,activeId=$('content').contains(active)?active.id:null,key=active?.dataset?.app?['app',active.dataset.app]:active?.dataset?.release?['release',active.dataset.release]:active?.dataset?.more?['more',active.dataset.more]:active?.dataset?.help?['help',active.dataset.help]:null;
 const rows=Object.keys(apps).filter(n=>n.includes(query)),shown=rows.slice(page*100,(page+1)*100);
 const href=n=>'?'+new URLSearchParams({variant,app:n});
 const nav=shown.map(n=>`<a class="${selected===n?'selected':''}" data-app="${esc(n)}" href="${href(n)}">${esc(n)}</a>`).join('');
 const cards=shown.map(n=>`<a class="card" data-app="${esc(n)}" href="${href(n)}"><span class="tile">${esc(n.slice(0,2).toUpperCase())}</span><h3>${esc(n)}</h3></a>`).join('');
 const desk=`<table><thead><tr><th>AM app</th><th>Repository file</th></tr></thead><tbody>${shown.map(n=>`<tr><td><a data-app="${esc(n)}" href="${href(n)}">${esc(n)}</a></td><td>${esc(apps[n].repository)}</td></tr>`).join('')}</tbody></table>`;
 $('variant').textContent=variant+' · '+names[variant];
 const pagination=`<div class="directory-toolbar"><p>${rows.length} apps${rows.length>100?` · Page ${page+1} of ${Math.ceil(rows.length/100)}`:''}</p>${rows.length>100?`<button data-page="-1" ${page===0?'disabled':''}>Previous apps</button><button data-page="1" ${(page+1)*100>=rows.length?'disabled':''}>Next apps</button>`:''}</div>`;
 $('content').innerHTML=variant==='B'?`<div class="split"><aside class="list">${pagination}${nav}</aside><section>${detail()||'<h2>Choose an app</h2>'}</section></div>`:`${detail()}${pagination}${variant==='C'?'<div class="table-wrap">'+desk+'</div>':`<div class="grid">${cards}</div>`}`;
 $('content').querySelectorAll('[data-app]').forEach(a=>a.onclick=e=>{if(e.button!==0||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;e.preventDefault();selected=a.dataset.app;release=null;expanded.clear();limits.clear();save();loadDetail(true);});
 $('content').querySelectorAll('[data-release]').forEach(a=>a.onclick=e=>{e.preventDefault();const id=a.dataset.release;expanded.has(id)?expanded.delete(id):expanded.add(id);release=expanded.has(id)?id:null;save();render();});
 $('content').querySelectorAll('[data-more]').forEach(a=>a.onclick=()=>{limits.set(a.dataset.more,(limits.get(a.dataset.more)??60)+60);render();});
 $('content').querySelectorAll('[data-page]').forEach(a=>a.onclick=()=>{page+=Number(a.dataset.page);render();});
 if(activeId)$(activeId)?.focus({preventScroll:true});
 else if(key)[...$('content').querySelectorAll('[data-'+key[0]+']')].find(el=>el.dataset[key[0]]===key[1])?.focus({preventScroll:true});
 metrics.push({renderMs:performance.now()-start});if(metrics.length>20)metrics.shift();
 $('diagnostics').textContent=JSON.stringify({variant,selected,release,metrics},null,2);
}
async function loadDetail(focus=false){
 const token=++generation,app=selected;source=null;loading=true;$('error').textContent='';$('retry').hidden=true;render();
 if(!app||!Object.hasOwn(apps,app)){loading=false;render();return;}
 try{
  const d=await client.source(apps[app].repository);if(token!==generation)return;source=d;
  if(!release&&releases(d).length)expanded.add(releases(d)[0][0]);
  loading=false;render();if(focus)$('app-title')?.focus({preventScroll:true});
 }catch(e){if(token===generation){loading=false;error(e);render();}}
}
async function start(){
 const token=++generation;source=null;apps={};$('error').textContent='';$('retry').hidden=true;$('status').textContent='Loading catalog…';render();
 try{
  const a=await client.apps();if(token!==generation)return;apps=a;
  $('status').textContent=`${Object.keys(apps).length} apps · ${new Set(Object.values(apps).map(e=>e.repository)).size} GitHub repositories`;render();if(selected)await loadDetail();
 }catch(e){if(token===generation){$('status').textContent='Catalog unavailable';error(e);}}
}
function cycle(d){keyboard.resetScope();variant=['A','B','C'][(['A','B','C'].indexOf(variant)+d+3)%3];save();render();}
const keyboard=installKeyboard({document,window,cycle,help:$('keyhelp')});
$('prev').onclick=()=>cycle(-1);$('next').onclick=()=>cycle(1);
$('shortcuts').onclick=()=>$('keyhelp').showModal();$('closehelp').onclick=()=>$('keyhelp').close();
$('search').oninput=e=>{query=e.target.value.toLowerCase();page=0;render();};
$('source-search').oninput=e=>{sourceQuery=e.target.value.toLowerCase();render();};
$('platform').onchange=$('arch').onchange=render;
$('retry').onclick=()=>Object.keys(apps).length?loadDetail():start();
$('theme').onclick=()=>{const theme=getComputedStyle(document.body).getPropertyValue('--bg').trim()==='#101820'?'light':'dark';document.body.classList.remove('light','dark');document.body.classList.add(theme);};
$('how').onclick=()=>{$('info').innerHTML=`<h2>How it works</h2><ol>${HOW.map(([rule,why])=>`<li>${esc(rule)}<br><em>Why: ${esc(why)}</em></li>`).join('')}</ol>`;};
$('health').onclick=async()=>{
 $('info').textContent='Loading catalog health…';
 try{
  const [runs,stats]=await Promise.all([client.runs(),client.statistics()]);
  const rows=Object.entries(runs).reverse().map(([key,r])=>`<tr><td>${esc(key)}</td><td title="${esc(r.reported_at)}">${ago(r.reported_at)}</td><td>${r.selected}</td><td>${r.succeeded}</td><td>${r.failed}</td><td>${esc(r.stop_reason??'')}</td></tr>`).join('');
  const buckets=[['under_24h','Under 24 hours'],['from_24_to_48h','Up to 2 days'],['from_48h_to_14d','Up to 14 days'],['over_14d','Older'],['never_collected','Never collected']];
  $('info').innerHTML=`<h2>Catalog health ${helpButton('health')}</h2><h3>How old the data is</h3><p>Counted ${ago(stats.measured_at)}.</p><dl>${buckets.map(([k,label])=>`<dt>${label}</dt><dd>${stats[k]}</dd>`).join('')}</dl><h3>The last ${Object.keys(runs).length} checks</h3><div class="table-wrap"><table><thead><tr><th>Run</th><th>Reported</th><th>Read</th><th>Succeeded</th><th>Failed</th><th>Stopped early</th></tr></thead><tbody>${rows}</tbody></table></div><p>${link('https://github.com/mareklangiewicz/AM/actions/workflows/catalog.yml','Collector runs on GitHub')}</p>`;
 }catch(e){$('info').textContent='Catalog health unavailable. Browsing still works.';error(e);}
};
window.addEventListener('popstate',async e=>{const state=e.state;readRoute();await start();if(state?.app)[...$('content').querySelectorAll('[data-app]')].find(a=>a.dataset.app===state.app)?.focus({preventScroll:true});window.scrollTo(0,state?.scroll??0);});readRoute();start();
