import {test,expect} from '@playwright/test';
const app=process.env.CATALOG_APP||'example';
const errors=[];
test.beforeEach(async({page})=>{
 errors.length=0;
 page.on('pageerror',e=>errors.push(e.message));
});
test.afterEach(()=>expect(errors).toEqual([]));

test('browse, search, releases, help and history in all three views',async({page},info)=>{
 await page.goto('web/catalog/');
 await expect(page.locator('#content [data-app]').first()).toBeVisible();
 await expect(page.locator('#error')).toBeEmpty();
 await page.getByLabel('Search app names').fill(app);
 await page.locator(`#content [data-app="${app}"]`).first().click();
 await expect(page.locator('#app-title')).toHaveText(app);
 await expect(page.locator('.asset').first()).toBeVisible();
 await expect(page.locator('#error')).toBeEmpty();
 await page.locator('#source-search').fill('no-such-asset-unique');
 await expect(page.locator('.asset')).toHaveCount(0);
 await page.locator('#source-search').fill('');
 await expect(page.locator('.asset').first()).toBeVisible();
 await page.locator('article [data-help="history"]').click();
 await expect(page.locator('#context-help')).toBeVisible();
 await page.screenshot({path:info.outputPath('help.png')});
 await page.keyboard.press('Escape');
 await expect(page.locator('#context-help')).not.toBeVisible();
 await expect(page.locator('article [data-help="history"]')).toBeFocused();
 const release=page.locator('[data-release]').first();
 await release.click();
 await expect(release.locator('..')).not.toHaveAttribute('open','');
 await release.click();
 await expect(page.locator('.asset').first()).toBeVisible();
 for(const view of ['A','B','C']){
  await expect(page.locator('#variant')).toContainText(view);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
  await page.screenshot({path:info.outputPath(`${view}.png`),fullPage:true});
  await page.getByRole('button',{name:'Next variant'}).click();
 }
 await page.goBack();
 await expect(page.locator('#variant')).toContainText('C');
 await page.getByRole('button',{name:'Light / dark'}).click();
 await expect(page.locator('body')).toHaveClass(/dark|light/);
 await page.screenshot({path:info.outputPath('dark.png'),fullPage:true});
});

test('directory fits the viewport and hides source-only controls',async({page},info)=>{
 await page.goto('web/catalog/');
 await expect(page.locator('#content [data-app]').first()).toBeVisible();
 await expect(page.locator('#source-search')).not.toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
 const box=await page.getByRole('navigation',{name:'Catalog views'}).boundingBox();
 expect(box.x).toBeGreaterThanOrEqual(0);
 expect(box.x+box.width).toBeLessThanOrEqual(page.viewportSize().width+1);
 await page.keyboard.press('h');
 const apps=page.locator('#content [data-app]');
 await expect(apps.nth(0)).toBeFocused();
 await page.keyboard.press('j');await expect(apps.nth(1)).toBeFocused();
 await page.keyboard.press('k');await expect(apps.nth(0)).toBeFocused();
 await page.keyboard.press('/');await expect(page.locator('#search')).toBeFocused();
 await page.keyboard.type('jk');await expect(page.locator('#search')).toHaveValue('jk');
 await page.locator('#search').fill('');
 await page.keyboard.press('Tab');await expect(page.locator('#prev')).toBeFocused();
 await page.keyboard.press('Shift+Tab');await expect(page.locator('#search')).toBeFocused();
 await page.keyboard.press('Escape');
 await page.screenshot({path:info.outputPath('directory.png'),fullPage:true});
});

test('source fetch failure keeps directory usable and retry stays at the same URL',async({page})=>{
 test.skip(Boolean(process.env.CATALOG_BASE_URL),'Failure injection belongs to the local fixture run');
 let failedURL;
 await page.route('**/repositories/example.yaml',async route=>{
  if(!failedURL){failedURL=route.request().url();await route.abort('failed');}
  else{expect(route.request().url()).toBe(failedURL);await route.continue();}
 });
 await page.goto('web/catalog/?app=example');
 await expect(page.locator('#error')).not.toBeEmpty();
 await expect(page.locator('#content [data-app]').first()).toBeVisible();
 await page.getByRole('button',{name:'Retry same snapshot'}).click();
 await expect(page.locator('.asset').first()).toBeVisible();
 await expect(page.locator('#error')).toBeEmpty();
});
