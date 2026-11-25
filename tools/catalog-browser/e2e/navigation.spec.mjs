import {test,expect} from '@playwright/test';
import {readFile} from 'node:fs/promises';
const example=name=>readFile(new URL(`../../catalog-contract/examples/${name}.yaml`,import.meta.url),'utf8');
const RAW='https://raw.githubusercontent.com/mareklangiewicz/AM/main-marek/catalog/';

// The live reader against controlled raw main-marek/catalog/ files: real browser fetch and DOM.
async function catalog(page,{source,health=true}={}){
 const requests=[];let healthy=health;
 await page.route('**/delivery.mjs',r=>r.fulfill({contentType:'text/javascript',body:'export default null;'}));
 await page.route(RAW+'**',async r=>{
  const path=r.request().url().slice(RAW.length);
  requests.push(path);
  if(path==='repositories/example.yaml'&&source&&await source(r))return;
  const name={'apps.yaml':'apps','repositories/example.yaml':'repository','status/runs.yaml':'runs','status/statistics.yaml':'statistics'}[path];
  if(!name||(!healthy&&path.startsWith('status/')))return r.fulfill({status:503,body:'No fixture'});
  await r.fulfill({contentType:'text/plain',body:await example(name)});
 });
 return {requests,failHealth:()=>{healthy=false;}};
}
test.beforeEach(async({page})=>{
 test.skip(Boolean(process.env.CATALOG_BASE_URL),'Controlled catalog files are local-only');
 page.on('pageerror',e=>{throw e;});
});

test('release links and Back/Forward preserve context; nothing names a catalog commit',async({page})=>{
 const network=await catalog(page);
 await page.goto('web/catalog/?app=example&release=9&variant=B');
 await expect(page.locator('.asset')).toHaveCount(1);
 await expect(page.locator('.asset a')).toHaveAttribute('href','https://github.com/example/app/releases/download/v1.0/app-x86_64.AppImage');
 await page.locator('#content .related [data-app="example-nightly"]').click();
 await expect(page.locator('#app-title')).toHaveText('example-nightly');
 await expect(page.locator('#app-title')).toBeFocused();
 await page.goBack();
 await expect(page.locator('#app-title')).toHaveText('example');
 await expect(page).toHaveURL(/release=9/);
 await expect(page).not.toHaveURL(/pin=/);
 await expect(page.getByRole('button',{name:'Load latest'})).toHaveCount(0);
 await page.goForward();
 await expect(page.locator('#app-title')).toHaveText('example-nightly');
 expect(network.requests.filter(path=>path==='repositories/example.yaml').length).toBeGreaterThanOrEqual(1);
 await page.goto('web/catalog/?app=example&release=999');
 await expect(page.locator('article')).toContainText('no longer in the catalog');
 await page.goto('web/catalog/?app=missing');
 await expect(page.locator('article')).toContainText('App not in the catalog');
 await expect(page.locator('#content [data-app="example"]').first()).toBeVisible();
});

test('an obsolete source failure cannot replace the newly selected app',async({page})=>{
 let delayed,requested;const arrived=new Promise(resolve=>requested=resolve);
 await catalog(page,{source:async r=>{if(!delayed){delayed=r;requested();return true;}return false;}});
 await page.goto('web/catalog/?app=example');
 await arrived;
 await page.locator('#content [data-app="example-nightly"]').click();
 await expect(page.locator('#app-title')).toHaveText('example-nightly');
 await expect(page.locator('.asset')).toHaveCount(1);
 await delayed.fulfill({status:503,body:'Old request failed'});
 await expect(page.locator('#error')).toBeEmpty();
 await expect(page.locator('#app-title')).toHaveText('example-nightly');
});

test('recipe labels, shared apps, the failure sentence and catalog health',async({page})=>{
 const network=await catalog(page);
 await page.goto('web/catalog/?app=example');
 await expect(page.locator('article')).toContainText('Last seen');
 await expect(page.locator('article')).toContainText("last attempt failed");
 await expect(page.locator('article')).toContainText("GitHub couldn't be reached.");
 const recipes=page.locator('details.recipe-overview');
 await recipes.locator('summary').click();
 await expect(recipes).toContainText('x86_64 · Reviewed installer');
 await expect(recipes).toContainText('aarch64 · Recipe script, read it before installing');
 await expect(recipes.locator('a[href$="/programs/aarch64/example"]')).toHaveAttribute('href','https://github.com/mareklangiewicz/AM/blob/main-marek/programs/aarch64/example');
 await expect(recipes.locator('a')).toHaveCount(2);
 await page.getByRole('button',{name:'Catalog health',exact:true}).click();
 await expect(page.locator('#info')).toContainText('The last 3 checks');
 await expect(page.locator('#info dt').filter({hasText:/^Older$/}).locator('+ dd')).toHaveText('14');
 await expect(page.locator('#info tbody tr').first()).toContainText('10-2');
 await expect(page.locator('#info')).toContainText('quota');
 network.failHealth();
 await page.reload();
 await page.getByRole('button',{name:'Catalog health',exact:true}).click();
 await expect(page.locator('#info')).toContainText('Catalog health unavailable');
 await expect(page.locator('.asset')).toHaveCount(1);
 await page.locator('#content .related [data-app="example-nightly"]').click();
 await recipes.locator('summary').click();
 await expect(page.locator('details.recipe-overview')).toContainText('x86_64 · Recipe script');
 await expect(page.locator('details.recipe-overview')).not.toContainText('aarch64');
});

test('a never-collected repository shows its failed attempt instead of facts',async({page})=>{
 const body=await example('repository-never-collected');
 await catalog(page,{source:async r=>{await r.fulfill({contentType:'text/plain',body});return true;}});
 await page.goto('web/catalog/?app=example');
 await expect(page.locator('article')).toContainText('Never collected');
 await expect(page.locator('article')).toContainText("GitHub says this repository doesn't exist or isn't public.");
 await expect(page.locator('.asset')).toHaveCount(0);
});

test('data last seen more than 14 days ago is marked',async({page})=>{
 await page.clock.setFixedTime(new Date('2026-12-20T00:00:00Z'));
 await catalog(page);
 await page.goto('web/catalog/?app=example');
 await expect(page.locator('article')).toContainText('AM warns before installing from data this old.');
});
