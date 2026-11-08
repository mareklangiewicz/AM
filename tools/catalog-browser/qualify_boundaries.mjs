// Optional wire-limit timing; no CI timing gate, external fetch or deployment.
import {chromium} from 'playwright';
import {createServer} from 'node:http';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {resolve,join} from 'node:path';
import assert from 'node:assert/strict';
const [dataArg,outArg]=process.argv.slice(2);
if(!dataArg||!outArg)throw Error('usage: node qualify_boundaries.mjs DATA_DIRECTORY NEW_OUTPUT_DIRECTORY');
const data=resolve(dataArg),out=resolve(outArg),root=fileURLToPath(new URL('../..',import.meta.url));
await mkdir(out,{recursive:false});
const fixture=JSON.parse(await readFile(join(data,'cases.json'),'utf8'));
const files=new Map(),hashes={};
for(const path of ['web/catalog/index.html','web/catalog/style.css','web/catalog/app.mjs','web/catalog/catalog.mjs','web/catalog/keyboard.mjs','tools/catalog-contract/reader.mjs','tools/catalog-contract/definitions.mjs']){
 const body=await readFile(join(root,path));files.set('/'+path,body);hashes[path]=createHash('sha256').update(body).digest('hex');
}
for(const row of Object.values(fixture.cases))for(const [path,hash] of Object.entries(row.hashes)){
 const body=await readFile(join(data,row.folder,path));assert.equal(createHash('sha256').update(body).digest('hex'),hash);
 files.set(`/review-data/${row.pin}/${path}`,body);
}
let active;const requests=[];
const server=createServer((req,res)=>{
 const requested=new URL(req.url,'http://localhost').pathname;
 const path=requested.endsWith('/')?requested+'index.html':requested;
 requests.push(requested);
 let body=path==='/web/catalog/delivery.mjs'?Buffer.from('export default '+JSON.stringify(active.delivery)+';\n'):files.get(path);
 res.setHeader('Cache-Control','no-store');
 res.setHeader('Content-Type',path.endsWith('.mjs')?'text/javascript':path.endsWith('.css')?'text/css':path.endsWith('.yaml')?'application/yaml':'text/html');
 if(!body){res.writeHead(404);res.end();return;}
 res.setHeader('Content-Length',body.length);res.end(body);
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
let browser;const rows=[];
try{
 browser=await chromium.launch({headless:true});
 for(const [name,entry] of Object.entries(fixture.cases))for(const profile of ['desktop-local','narrow-4x-10Mbps-100ms'])for(let sample=1;sample<=3;sample++){
  active=entry;
  const context=await browser.newContext({viewport:profile==='desktop-local'?{width:1280,height:900}:{width:390,height:844}});
  try{
   const page=await context.newPage(),cdp=await context.newCDPSession(page),errors=[];
   page.on('pageerror',error=>errors.push(error.message));
   await cdp.send('Network.enable');await cdp.send('Network.setCacheDisabled',{cacheDisabled:true});
   if(profile!=='desktop-local'){
    await cdp.send('Emulation.setCPUThrottlingRate',{rate:4});
    await cdp.send('Network.emulateNetworkConditions',{offline:false,latency:100,downloadThroughput:1250000,uploadThroughput:1250000});
   }
   await page.addInitScript(()=>{
    window.boundaryTiming={};
    new MutationObserver(()=>{
     if(!boundaryTiming.detail&&document.querySelector('#app-title')&&document.querySelector('.asset'))
      requestAnimationFrame(()=>requestAnimationFrame(()=>{boundaryTiming.detail??=performance.now();}));
    }).observe(document,{childList:true,subtree:true});
   });
   assert.equal((await page.goto(`http://127.0.0.1:${server.address().port}/web/catalog/`)).status(),200);
   await page.locator('#content [data-app="boundary"]').first().click();
   await page.waitForFunction(()=>boundaryTiming.detail,{},{timeout:60000});
   const timing=await page.evaluate(()=>({afterSourceBytesMs:boundaryTiming.detail-performance.getEntriesByType('resource').find(row=>row.name.endsWith('/repositories/boundary.yaml')).responseEnd,
     renderedAssets:document.querySelectorAll('.asset').length,viewportFits:document.documentElement.scrollWidth<=innerWidth+1,
     error:document.querySelector('#error').textContent}));
   assert.equal(timing.error,'');assert.equal(timing.viewportFits,true);assert.deepEqual(errors,[]);
   if(name==='density')assert.equal(timing.renderedAssets,60);
   if(sample===1)await page.screenshot({path:join(out,`${name}-${profile}.png`)});
   rows.push({fixture:name,profile,sample,...timing});
   console.log(JSON.stringify(rows.at(-1)));
  }finally{await context.close();}
 }
 const result={synthetic:true,browser:browser.version(),date:new Date().toISOString(),
  cases:fixture.cases,sourceFilesSha256:hashes,rows,
  method:'One-app native loopback fetch, fresh contexts/cache disabled, responseEnd to first assets plus two frames. Wire-limit stress shapes, not real acquisition, public HTTPS, physical-device or 5000-app directory acceptance.'};
 await writeFile(join(out,'receipt.json'),JSON.stringify(result,null,2)+'\n');
}finally{await browser?.close();await new Promise(resolve=>server.close(resolve));}
