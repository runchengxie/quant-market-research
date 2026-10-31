import { test, expect } from '@playwright/test';
for (const width of [320,1280]) for (const locale of ['en-US','zh-CN']) {
 test(`robustness costs and evidence fit ${width} ${locale}`,async({page})=>{
  await page.setViewportSize({width,height:900});
  await page.goto(`research/cashflow/?lang=${locale}#cashflow-robustness`);
  const section=page.locator('#cashflow-robustness');
  await expect(section).toBeVisible();
  await expect(section.locator('table')).toHaveCount(5);
  await expect(page.locator('#allocation-rules tbody tr:visible')).toHaveCount(7);
  const before=await page.locator('#allocation-rules tbody tr:visible').allTextContents();
  await page.locator('#allocation-cost').selectOption('50');
  await expect(page.locator('#allocation-rules tbody tr:visible')).toHaveCount(7);
  await expect(page.locator('#allocation-rules tbody tr[data-cost="50"]:visible')).toHaveCount(6);
  const after=await page.locator('#allocation-rules tbody tr:visible').allTextContents();
  expect(after).not.toEqual(before);
  await expect(section).toContainText(locale==='en-US'?'not optimized rules':'不是优化后的策略');
  await expect(section).toContainText(locale==='en-US'?'fixed-cohort earnings attribution is blocked':'固定成分盈利归因仍阻断');
  await expect(section).toContainText('292/300');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 });
}
test('robustness keeps zero-cost evidence available without JavaScript',async({browser})=>{
 const context=await browser.newContext({javaScriptEnabled:false});
 const page=await context.newPage();
 await page.goto('research/cashflow/#cashflow-robustness');
 await expect(page.locator('#allocation-rules tbody tr:visible')).toHaveCount(7);
 await expect(page.locator('#cashflow-robustness')).toContainText('138/300');
 await context.close();
});
