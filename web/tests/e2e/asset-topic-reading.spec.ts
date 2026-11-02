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
test('topic links preserve Chinese when browser storage is blocked',async({page})=>{
 await page.addInitScript(()=>{Storage.prototype.getItem=()=>{throw Error('storage blocked')};Storage.prototype.setItem=()=>{throw Error('storage blocked')};});
 await page.goto('research/asset-returns/?lang=zh-CN');
 await page.locator('.asset-topic-links').first().getByRole('link',{name:'分散配置与取款',exact:true}).click();
 await expect(page.locator('html')).toHaveAttribute('lang','zh-CN');await expect(page).toHaveURL(/asset-allocation\/\?lang=zh-CN$/);
 await page.locator('.asset-topic-links').first().getByRole('link',{name:'现金流指数研究',exact:true}).click();await expect(page.locator('html')).toHaveAttribute('lang','zh-CN');
});
test('every allocation and spending assumption is labeled and visible without scripts',async({browser})=>{
 const context=await browser.newContext({javaScriptEnabled:false});const page=await context.newPage();await page.goto('research/asset-allocation/');
 await expect(page.locator('#allocation-rules tbody tr:visible')).toHaveCount(19);
 for(const cost of ['0','10','50'])expect(await page.locator(`#allocation-rules tr[data-cost="${cost}"]:visible`).count()).toBeGreaterThan(0);
 await expect(page.locator('#decision-spending tbody tr:visible')).toHaveCount(108);
 await expect(page.locator('#decision-spending tbody tr[data-demand="6"][data-shock="60"]:visible')).toHaveCount(9);
 await expect(page.locator('#decision-spending tbody tr[data-demand="6"][data-shock="60"]').first()).toContainText('After 60 months');
 await context.close();
});
