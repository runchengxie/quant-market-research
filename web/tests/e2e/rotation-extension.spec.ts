import {test,expect} from '@playwright/test';
const route='research/style-theme-rotation/';
for(const lang of ['en-US','zh-CN']){
 test(`forward status, source filtering and robustness controls ${lang}`,async({page})=>{
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(`${route}?lang=${lang}`);
  const forward=page.locator('#rotation-forward');
  await expect(forward.locator('input[type=search]')).toBeVisible();
  await expect(forward).toContainText(lang==='en-US'?'Waiting for fresh inputs':'等待新数据');
  await forward.locator('input').fill('515910');
  await expect(forward.locator('tbody').first().getByRole('row')).toHaveCount(1);
  await expect(forward.locator('tbody').first()).toContainText('515910');
  const robust=page.locator('#rotation-robustness');
  const selects=robust.locator('select');await expect(selects).toHaveCount(6);
  await selects.nth(2).selectOption('10');await selects.nth(3).selectOption('2');
  await selects.nth(4).selectOption('last_252');
  await expect(robust.getByTestId('robustness-period')).toContainText('252');
  await expect(page).toHaveURL(/robustCost=10/);await expect(page).toHaveURL(/robustDelay=2/);
  await selects.nth(0).selectOption('pool');
  await expect(robust).toContainText(lang==='en-US'?'quality':'质量');
  await expect(robust).toContainText(lang==='en-US'?'dividend':'红利');
  expect(errors).toEqual([]);
 });
 test(`release compatibility and mobile layout ${lang}`,async({page})=>{
  await page.setViewportSize({width:390,height:844});await page.goto(`${route}?lang=${lang}`);
  const versions=page.locator('#rotation-versions');
  await expect(versions.getByRole('button')).toBeVisible();
  await versions.getByRole('button',{name:lang==='en-US'?'Compare releases':'比较版本',exact:true}).click();
  await expect(versions).toContainText(lang==='en-US'?'numerical deltas are suppressed':'不显示数值差额');
  await expect(versions).not.toContainText(lang==='en-US'?'Could not verify':'无法验证');
  await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
 });
}
test('no JavaScript keeps the five workstreams and real status readable',async({browser})=>{
 const context=await browser.newContext({javaScriptEnabled:false});const page=await context.newPage();
 await page.goto(route+'?lang=en-US');
 await expect(page.locator('#rotation-forward')).toContainText('Waiting for fresh inputs');
 await expect(page.locator('#rotation-sources')).toContainText('515910');
 await expect(page.locator('#rotation-robustness')).toContainText('Annualized return');
 await expect(page.locator('#rotation-versions')).toContainText('recovered');
 await context.close();
});
