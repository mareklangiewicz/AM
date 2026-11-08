import {defineConfig} from '@playwright/test';
export default defineConfig({
 testDir:'./e2e', workers:1, retries:0, timeout:30000,
 reporter:'list',
 use:{baseURL:(process.env.CATALOG_BASE_URL||'http://127.0.0.1:8766').replace(/\/?$/,'/'),trace:'retain-on-failure',screenshot:'only-on-failure'},
 projects:[
  {name:'desktop',use:{browserName:'chromium',viewport:{width:1280,height:900}}},
  {name:'mobile',use:{browserName:'chromium',viewport:{width:390,height:844},isMobile:true,hasTouch:true}},
  ...(process.env.CATALOG_FIREFOX?[{name:'firefox',use:{browserName:'firefox',viewport:{width:1280,height:900}}}]:[])
 ],
 webServer:process.env.CATALOG_BASE_URL?undefined:{command:'python3 serve_test_site.py',url:'http://127.0.0.1:8766/web/catalog/',reuseExistingServer:false}
});
