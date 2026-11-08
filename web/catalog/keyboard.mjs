// Native and Vim keyboard layer. Native Tab / Shift-Tab / Enter / Space stay available.
export function installKeyboard({document,window,cycle,help}) {
 let lastG=0,scope='all';
 const content=()=>document.getElementById('content');
 const targets=()=>[...content().querySelectorAll(scope==='apps'?'[data-app]':scope==='detail'?'article a[href], article button, article summary':'a[href],button,summary')].filter(el=>el.getClientRects().length&&!el.disabled);
 const focus=el=>{el?.focus({preventScroll:true});el?.scrollIntoView({block:'nearest',inline:'nearest'});};
 function move(step){const items=targets(),i=items.indexOf(document.activeElement);focus(items[i<0?(step>0?0:items.length-1):Math.max(0,Math.min(items.length-1,i+step))]);}
 const handler=e=>{
  if(e.defaultPrevented||e.isComposing)return;
  // Context dialogs keep native Escape, Tab and button activation.
  if(e.target.closest('dialog[open]')&&!help.open)return;
  if(help.open){if(e.key==='Escape'){e.preventDefault();help.close();}return;}
  if(e.key==='Escape'){document.activeElement?.blur();scope='all';lastG=0;return;}
  if(e.target.closest('input,select,textarea,[contenteditable]:not([contenteditable="false"])'))return;
  if(e.ctrlKey||e.metaKey||e.altKey){
   if(e.ctrlKey&&!e.metaKey&&!e.altKey&&!e.shiftKey&&['d','u'].includes(e.key)){e.preventDefault();const pane=document.activeElement?.closest('.list');(pane||window).scrollBy({top:(e.key==='d'?1:-1)*(pane?pane.clientHeight:window.innerHeight)/2,behavior:'smooth'});}
   return;
  }
  const key=e.key,now=Date.now(),doubleG=key==='g'&&lastG&&now-lastG<700;lastG=key==='g'&&!doubleG?now:0;
  if(key==='j'||key==='k'){e.preventDefault();move(key==='j'?1:-1);}
  else if(key==='h'){e.preventDefault();scope='apps';focus(targets().find(el=>el.classList.contains('selected'))||targets()[0]);}
  else if(key==='l'){e.preventDefault();scope='detail';focus(content().querySelector('article summary')||targets()[0]);}
  else if(doubleG||key==='G'){e.preventDefault();const items=targets();focus(key==='G'?items.at(-1):items[0]);}
  else if(key==='g')e.preventDefault();
  else if(key==='/'){e.preventDefault();document.getElementById('search').focus();}
  else if(key==='?'){e.preventDefault();help.showModal();}
  else if(['[',']','ArrowLeft','ArrowRight'].includes(key)){e.preventDefault();cycle(key==='['||key==='ArrowLeft'?-1:1);}
 };
 document.addEventListener('keydown',handler);
 return {resetScope(){scope='all';},handler};
}
