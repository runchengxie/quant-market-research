import {test,expect} from '@playwright/test';
const topics=[{route:'asset-returns',kinds:['returns','holding','endpoints','waiting','uncertainty']},{route:'asset-allocation',kinds:['allocation','spending','stress']},{route:'asset-implementation',kinds:['launch','etf']}];
for(const width of [320,1280])for(const locale of ['en-US','zh-CN'])test(`complete asset topics stay expanded at ${width} ${locale}`,async({page})=>{
 await page.setViewportSize({width,height:900});await page.emulateMedia({reducedMotion:'reduce'});
 for(const topic of topics){const response=await page.goto(`research/${topic.route}/?lang=${locale}`);expect(response?.ok()).toBe(true);await expect(page.locator('main h1')).toHaveCount(1);await expect(page.locator('[data-asset-chart]')).toHaveCount(topic.kinds.length);
  for(const kind of topic.kinds){const root=page.locator(`[data-asset-chart="${kind}"]`);await root.scrollIntoViewIfNeeded();await expect(root).toHaveAttribute('data-chart-ready','true');}
  await expect(page.locator('main details:not([open])')).toHaveCount(0);await expect(page.locator('body')).toHaveJSProperty('scrollWidth',width);
  expect(await page.locator('main table').count()).toBeGreaterThanOrEqual(topic.kinds.length);
 }
 await page.goto(`research/cashflow/?lang=${locale}#asset-chart-spending-title`);await expect(page).toHaveURL(/asset-allocation\/\?lang=.+#asset-chart-spending-title$/);await expect(page.locator('html')).toHaveAttribute('lang',locale);
});
test('full topic evidence and relocation links remain usable without scripts',async({browser})=>{
 const context=await browser.newContext({javaScriptEnabled:false});const page=await context.newPage();
 for(const topic of topics){await page.goto(`research/${topic.route}/`);await expect(page.locator('main details:not([open])')).toHaveCount(0);expect(await page.locator('main table').count()).toBeGreaterThanOrEqual(topic.kinds.length);}
 await page.goto('research/cashflow/#cashflow-long-run');await expect(page.locator('a[href$="/research/asset-returns/"]').first()).toBeVisible();await context.close();
});
