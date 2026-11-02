import{test,expect}from'@playwright/test';
const topics=[{route:'asset-returns',kinds:['holding','returns','endpoints','waiting','uncertainty']},{route:'asset-allocation',kinds:['allocation','spending','stress']},{route:'asset-implementation',kinds:['launch','etf']}];
for(const width of [320,1280])for(const locale of ['en-US','zh-CN']){
 test(`asset charts follow controls and theme at ${width}px ${locale}`,async({page})=>{
  await page.emulateMedia({reducedMotion:'reduce'});await page.setViewportSize({width,height:900});
  for(const topic of topics){await page.goto(`research/${topic.route}/?lang=${locale}`);for(const kind of topic.kinds){const root=page.locator(`[data-asset-chart="${kind}"]`);await root.scrollIntoViewIfNeeded();await expect(root).toHaveAttribute('data-chart-ready','true');await expect(root.locator('canvas')).toHaveCount(1);await expect(root.locator('[role="img"]')).toHaveAttribute('aria-label',/.+/);}}
  await page.goto(`research/asset-returns/?lang=${locale}`);
  const endpoint=page.locator('[data-asset-chart="endpoints"]');await expect(endpoint.locator('.asset-selected-table')).toHaveAttribute('open','');
  await endpoint.locator('[data-asset-control="asset"]').selectOption('gold');const endpointRows=endpoint.locator('.asset-selected-table tbody tr:not([hidden])');expect(await endpointRows.count()).toBeGreaterThan(1);await expect(endpointRows.first()).toHaveAttribute('data-asset-row','gold');
  const uncertainty=page.locator('[data-asset-chart="uncertainty"]');await uncertainty.locator('select').focus();await page.keyboard.press('ArrowDown');await page.keyboard.press('Enter');await expect(uncertainty).toHaveAttribute('data-chart-selection',/annual_minus_hold_cagr/);await expect(uncertainty.locator('[data-asset-chart-summary]')).toContainText(locale==='zh-CN'?'中位数':'median');
  await page.goto(`research/asset-implementation/?lang=${locale}`);const etf=page.locator('[data-asset-chart="etf"]');await etf.locator('[data-asset-control="cost"]').selectOption('10');await expect(etf.locator('.asset-selected-table tbody tr:not([hidden])')).toHaveCount(1);await expect(etf.locator('.asset-selected-table tbody tr:not([hidden])')).toHaveAttribute('data-cost-row','10');
  await page.goto(`research/asset-allocation/?lang=${locale}`);const spending=page.locator('[data-asset-chart="spending"]');await page.selectOption('#decision-shock','12');await page.selectOption('#decision-demand','4');await expect.poll(()=>spending.getAttribute('data-chart-selection')).toContain('"shock":"12"');
  let view=JSON.parse((await spending.getAttribute('data-chart-values'))!);expect(view.series[0].values[0]).toBeCloseTo(6/108,12);expect(view.sample_windows).toBe(108);
  await spending.locator('select').selectOption('minimum_terminal_real_capital');view=JSON.parse((await spending.getAttribute('data-chart-values'))!);expect(view.unit).toBe('capital');
  await page.getByRole('button',{name:/Theme:|切换主题/}).click();await spending.scrollIntoViewIfNeeded();await expect(spending).toHaveAttribute('data-chart-ready','true');await expect(page.locator('body')).toHaveJSProperty('scrollWidth',width);
  const glossary=page.locator('#reader-glossary');await glossary.locator('summary').click();await expect(glossary).toContainText(locale==='zh-CN'?'两个百分比直接相减':'Subtract two percentages directly');
 });
}
test('static evidence tables remain open without JavaScript',async({browser})=>{
 const context=await browser.newContext({javaScriptEnabled:false});const page=await context.newPage();
 for(const topic of topics){await page.goto(`research/${topic.route}/`);for(const kind of topic.kinds)await expect(page.locator(`details[data-asset-table="${kind}"]`)).toHaveAttribute('open','');}
 await expect(page.locator('[data-asset-chart="etf"] .asset-selected-table tbody tr')).toHaveCount(9);
 await page.goto('research/asset-returns/');expect(await page.locator('[data-asset-chart="endpoints"] .asset-selected-table tbody tr').count()).toBeGreaterThan(20);
 await page.goto('research/asset-allocation/');await expect(page.locator('#decision-spending tbody tr:visible')).toHaveCount(9);await expect(page.locator('#allocation-rules tbody tr:visible')).toHaveCount(7);await context.close();
});
