import {test,expect} from '@playwright/test';
const route='research/style-theme-rotation/';
for(const locale of ['en-US','zh-CN'] as const)for(const width of [390,1280]){
 test(`operational evidence remains readable in ${locale} at ${width}px`,async({page})=>{
  await page.setViewportSize({width,height:900});const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(route+'?lang='+locale);
  const operations=page.locator('#rotation-operations');
  await expect(operations.getByRole('heading',{name:locale==='en-US'?'Operational evidence and complete-calendar checks':'运行状态与完整样本检查',exact:true})).toBeVisible();
  await expect(operations).toContainText('12,998');await expect(operations).toContainText('336');
  const year=operations.getByLabel(locale==='en-US'?'Audit year':'审计年份',{exact:true});await year.selectOption('2021');await expect(page).toHaveURL(/opsAuditYear=2021/);
  const matched=page.locator('#rotation-matched');await expect(matched.getByTestId('matched-result')).toHaveAttribute('data-status','unavailable');
  await expect(matched).toContainText('8,640');
  const baseline=matched.getByLabel(locale==='en-US'?'Reference strategy':'参考策略',{exact:true});await baseline.focus();await baseline.press('ArrowDown');await baseline.press('Enter');await expect(baseline).toHaveValue('pool-core');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();expect(errors).toEqual([]);
 });
}
test('paired cost/window controls load reviewed data and restore URL history',async({page})=>{
 await page.goto(route+'?lang=en-US');const panel=page.locator('#rotation-matched');
 await panel.getByLabel('Cost and execution case',{exact:true}).selectOption('delay-two');
 await expect(panel.getByTestId('matched-result')).toHaveAttribute('data-status','unavailable');
 await expect(page).toHaveURL(/opsCase=delay-two/);
 await panel.getByLabel('Evaluation window',{exact:true}).selectOption('last_252');await expect(page).toHaveURL(/opsWindow=last_252/);
 await panel.getByLabel('Comparison',{exact:true}).selectOption('estimated-risk');await expect(page).toHaveURL(/opsComparison=estimated-risk/);
 await page.reload();await expect(panel.getByLabel('Evaluation window',{exact:true})).toHaveValue('last_252');await expect(panel.getByTestId('matched-result')).toHaveAttribute('data-status','unavailable');
 await panel.getByLabel('Evaluation window',{exact:true}).selectOption('last_756');await page.goBack();await expect(panel.getByLabel('Evaluation window',{exact:true})).toHaveValue('last_252');
});
test('a corrupt operations release produces a retry state and no unverified row',async({page})=>{
 await page.route('**/data/rotation/releases/rotation-operations-*.json',r=>r.fulfill({status:200,body:'{}'}));
 await page.goto(route+'?lang=en-US');const panel=page.locator('#rotation-matched');
 await panel.getByLabel('Evaluation window',{exact:true}).selectOption('last_252');
 await expect(panel.getByRole('alert')).toContainText('could not be verified');await expect(panel.getByTestId('matched-result')).toHaveCount(0);
 await page.unroute('**/data/rotation/releases/rotation-operations-*.json');await panel.getByRole('button',{name:'Retry',exact:true}).click();await expect(panel.getByTestId('matched-result')).toHaveAttribute('data-status','unavailable');
});
test('static summaries preserve the current negative result without JavaScript',async({browser,baseURL})=>{
 const context=await browser.newContext({javaScriptEnabled:false,baseURL,viewport:{width:390,height:844}});const page=await context.newPage();
 await page.goto(route+'?lang=en-US');await expect(page.locator('#rotation-operations').getByRole('heading',{name:'Operational evidence and complete-calendar checks',exact:true})).toBeVisible();
 await expect(page.locator('#rotation-matched tbody tr')).toHaveCount(8);await expect(page.locator('#rotation-matched')).toContainText('8,640');
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();await context.close();
});
