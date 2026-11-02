import { test, expect } from '@playwright/test';
for (const width of [320,1280]) for (const locale of ['en-US','zh-CN']) {
 test(`robustness costs and evidence fit ${width} ${locale}`,async({page})=>{
  await page.setViewportSize({width,height:900});
  await page.goto(`research/asset-allocation/?lang=${locale}#asset-fixed-rules`);
  let section=page.locator('#asset-fixed-rules');
  await expect(section).toBeVisible();
  await expect(section.locator('.robustness-table > table')).toHaveCount(1);
  const graph=page.locator('[data-asset-chart=allocation]');await graph.scrollIntoViewIfNeeded();await expect(graph).toHaveAttribute('data-chart-ready','true');
  const table=page.locator('details[data-asset-table=allocation]');if((await table.getAttribute('open'))===null)await table.locator('summary').click();
  await expect(page.locator('#allocation-rules tbody tr:visible')).toHaveCount(7);
  const before=await page.locator('#allocation-rules tbody tr:visible').allTextContents();
  await page.locator('#allocation-cost').selectOption('50');
  await expect(page.locator('#allocation-rules tbody tr:visible')).toHaveCount(7);
  await expect(page.locator('#allocation-rules tbody tr[data-cost="50"]:visible')).toHaveCount(6);
  const after=await page.locator('#allocation-rules tbody tr:visible').allTextContents();
  expect(after).not.toEqual(before);
  await expect(section).toContainText(locale==='en-US'?'not optimized rules':'所有结果均来自历史样本');
  await page.goto(`research/asset-implementation/?lang=${locale}`);section=page.locator('#cashflow-robustness');
  await expect(section).toContainText(locale==='en-US'?'fixed-cohort earnings attribution is blocked':'还需补齐股份账本和财报原始版本');
  await expect(section).toContainText('292/300');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 });
}
test('robustness keeps zero-cost evidence available without JavaScript',async({browser})=>{
 const context=await browser.newContext({javaScriptEnabled:false});
 const page=await context.newPage();
 await page.goto('research/asset-allocation/');
 await expect(page.locator('#allocation-rules tbody tr:visible')).toHaveCount(7);
 await page.goto('research/asset-implementation/');await expect(page.locator('#cashflow-robustness')).toContainText('138/300');
 await context.close();
});
