import {test,expect} from '@playwright/test';
import {readFile} from 'node:fs/promises';
const oldPin='a'.repeat(40),newPin='b'.repeat(40),release='9007199254740993';
const fixture=name=>readFile(new URL(`../../catalog-contract/fixtures/${name}.yaml`,import.meta.url),'utf8');

// Normal channel reader with controlled HTTP responses, real browser fetch and DOM.
// No public channel is changed.
async function channels(page,{source,health=false}={}){
 const requests=[];let current=oldPin,statusAvailable=health;
 await page.route('**/delivery.mjs',r=>r.fulfill({contentType:'text/javascript',body:'export default null;'}));
 await page.route('https://api.github.com/**',r=>{
  const status=r.request().url().endsWith('catalog-status-v1');
  return r.fulfill({status:status&&!statusAvailable?503:200,json:{object:{sha:status?oldPin:current}}});
 });
 await page.route('https://raw.githubusercontent.com/mareklangiewicz/AM/**',async r=>{
  const [pin,...parts]=new URL(r.request().url()).pathname.split('/').slice(3),path=parts.join('/');
  requests.push({pin,path});
  if(path==='repositories/example.yaml'&&source&&await source(r,pin))return;
  const name={'catalog.yaml':'catalog','apps.yaml':'apps','provenance.yaml':'provenance','repositories/example.yaml':'repository','status.yaml':'status','runs/123-2/summary.yaml':'summary'}[path];
  if(!name)return r.fulfill({status:404,body:'No fixture'});
  const body=await fixture(name);
  await r.fulfill({contentType:'text/plain',body});
 });
 return {requests,latest:()=>{current=newPin;},failHealth:()=>{statusAvailable=false;}};
}
test.beforeEach(async({page})=>{
 test.skip(Boolean(process.env.CATALOG_BASE_URL),'Controlled channel fixtures are local-only');
 page.on('pageerror',e=>{throw e;});
});

test('pinned release links, explicit latest and Back/Forward preserve context',async({page})=>{
 const network=await channels(page);
 await page.goto(`web/catalog/?pin=${oldPin}&app=example&release=${release}&variant=B`);
 await expect(page.locator('.asset')).toHaveCount(4);
 await page.locator('#content .related [data-app="example-nightly"]').click();
 await expect(page.locator('#app-title')).toHaveText('example-nightly');
 await expect(page.locator('#app-title')).toBeFocused();
 await page.goBack();
 await expect(page.locator('#app-title')).toHaveText('example');
 await expect(page.locator('.asset')).toHaveCount(4);
 await expect(page).toHaveURL(new RegExp(`release=${release}`));
 await expect(page.locator('#content [data-app="example-nightly"]').first()).toBeFocused();
 network.latest();
 await page.getByRole('button',{name:'Load latest',exact:true}).click();
 await expect(page).toHaveURL(new RegExp(`pin=${newPin}`));
 await expect(page.locator('.asset')).toHaveCount(4);
 await page.goBack();
 await expect(page).toHaveURL(new RegExp(`pin=${oldPin}`));
 await expect(page.locator('.asset')).toHaveCount(4);
 await page.goForward();
 await expect(page).toHaveURL(new RegExp(`pin=${newPin}`));
 await expect(page.locator('#app-title')).toHaveText('example');
 expect(network.requests.some(r=>r.pin===newPin&&r.path==='repositories/example.yaml')).toBe(true);
 await page.goto(`web/catalog/?pin=${oldPin}&app=example&release=999`);
 await expect(page.locator('article')).toContainText('Linked release is absent');
 await page.goto(`web/catalog/?pin=${oldPin}&app=missing`);
 await expect(page.locator('article')).toContainText('App absent from this snapshot');
 await expect(page.locator('#content [data-app="example"]').first()).toBeVisible();
});

test('an obsolete source failure cannot replace the newly selected identity',async({page})=>{
 let delayed,requested;const arrived=new Promise(resolve=>requested=resolve);
 await channels(page,{source:async r=>{if(!delayed){delayed=r;requested();return true;}return false;}});
 await page.goto('web/catalog/?app=example');
 await arrived;
 await page.locator('#content [data-app="example-nightly"]').click();
 await expect(page.locator('#app-title')).toHaveText('example-nightly');
 await expect(page.locator('.asset')).toHaveCount(4);
 await delayed.fulfill({status:503,body:'Old request failed'});
 await expect.poll(()=>page.evaluate(()=>performance.getEntriesByType('resource').filter(r=>r.name.endsWith('/repositories/example.yaml')).length)).toBe(2);
 await expect(page.locator('#error')).toBeEmpty();
 await expect(page.locator('#app-title')).toHaveText('example-nightly');
 await expect(page.locator('article')).toContainText('Not yet classified');
});

test('recipe evidence, shared identities and independent health stay distinct',async({page})=>{
 const network=await channels(page,{health:true});
 await page.goto('web/catalog/?app=example');
 const recipes=page.locator('details.recipe-overview');
 await expect(recipes).toBeVisible();
 await recipes.locator('summary').click();
 for(const label of ['Shared installer','Template-based recipe','Custom recipe','Not yet classified'])await expect(recipes).toContainText(label);
 await expect(recipes).toContainText('Installation choice / channel policy: unknown');
 for(const arch of ['aarch64','armv7l','i686'])await expect(recipes.locator(`a[href$="/programs/${arch}/example"]`)).toHaveAttribute('href',`https://github.com/mareklangiewicz/AM/blob/${oldPin}/programs/${arch}/example`);
 await expect(page.locator('p.recipe-overview a')).toBeVisible();
 await page.getByRole('button',{name:'Catalog health',exact:true}).click();
 await expect(page.locator('#info')).toContainText('Catalog confirmed by this report');
 await expect(page.locator('#info')).toContainText('Last reported run');
 await expect(page.locator('#info dt').filter({hasText:/^received_bytes$/}).locator('+ dd')).toHaveText('unknown');
 network.latest();
 await page.getByRole('button',{name:'Load latest',exact:true}).click();
 await expect(page).toHaveURL(new RegExp(`pin=${newPin}`));
 await expect(page.locator('#info')).toContainText('Catalog differs from the report’s confirmed revision');
 network.failHealth();
 await page.reload();
 await page.getByRole('button',{name:'Catalog health',exact:true}).click();
 await expect(page.locator('#info')).toContainText('Status unavailable');
 await expect(page.locator('.asset')).toHaveCount(4);
 await page.locator('#content .related [data-app="example-nightly"]').click();
 await expect(page.locator('#app-title')).toHaveText('example-nightly');
 await expect(page.locator('article')).toContainText('AM recipes: Not yet classified');
 await expect(page.locator('article a[href*="/programs/"]')).toHaveCount(0);
});
