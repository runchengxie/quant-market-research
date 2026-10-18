import {test,expect} from '@playwright/test';
const route='research/style-theme-rotation/';
for(const locale of ['en-US','zh-CN'] as const)for(const width of [390,1280]){
 test(`foundation cause and component controls in ${locale} at ${width}px`,async({page})=>{
  await page.setViewportSize({width,height:900});const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(route+'?lang='+locale);
  const panel=page.locator('#rotation-foundation');
  await expect(panel.getByRole('heading',{name:locale==='en-US'?'What the new study can establish':'新一轮研究能说明什么',exact:true})).toBeVisible();
  await expect(panel.getByTestId('foundation-cell-count')).toHaveText('2,525');
  await panel.getByLabel(locale==='en-US'?'Cause category':'缺口原因',{exact:true}).selectOption('unresolved');
  await expect(panel.getByTestId('foundation-cell-count')).toHaveText('1');
  await panel.getByLabel(locale==='en-US'?'Component comparison':'组件对照',{exact:true}).selectOption('theme-overlay:combined');
  await expect(panel.getByTestId('foundation-result')).toHaveAttribute('data-status','unavailable');
  await expect(panel.getByTestId('foundation-result').locator('svg')).toHaveCount(0);
  await panel.getByLabel(locale==='en-US'?'Cost and execution case':'成本与执行情形',{exact:true}).selectOption('delay-two');
  await panel.getByLabel(locale==='en-US'?'Component comparison':'组件对照',{exact:true}).selectOption('combined:passive');
  await expect(panel.getByTestId('foundation-result')).toHaveAttribute('data-status','available');
  const details=panel.locator('details').filter({has:page.locator('summary',{hasText:locale==='en-US'?'Inspect announcement evidence':'查看公告证据'})});
  await details.locator('summary').focus();await page.keyboard.press('Enter');await expect(details).toHaveAttribute('open','');
  await expect(panel).toContainText(locale==='en-US'?'Capture unarmed':'尚未启用捕获');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();expect(errors).toEqual([]);
 });
}
test('foundation locale persists and old links preserve locale and fragment',async({page})=>{
 await page.goto(route+'?lang=zh-CN');await expect(page.locator('#rotation-foundation h2')).toHaveText('新一轮研究能说明什么');
 await page.goto(route);await expect(page.locator('#rotation-foundation h2')).toHaveText('新一轮研究能说明什么');
 for(const old of ['etf-rotation','hotsector']){await page.goto(`research/${old}/?lang=zh-CN#rotation-foundation`);await expect(page).toHaveURL(/style-theme-rotation\/\?lang=zh-CN#rotation-foundation/);await expect(page.locator('#rotation-foundation h2')).toHaveText('新一轮研究能说明什么');}
});

test('foundation keeps primary evidence readable without JavaScript',async({browser,baseURL})=>{
 const context=await browser.newContext({javaScriptEnabled:false,baseURL,viewport:{width:390,height:844}});const page=await context.newPage();
 await page.goto(route);const panel=page.locator('#rotation-foundation');
 await expect(panel.getByRole('heading',{name:'What the new study can establish',exact:true})).toBeVisible();
 await expect(panel.locator('table').nth(1).locator('tbody tr')).toHaveCount(5);
 await expect(panel).toContainText('709');await expect(panel).toContainText('150');
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();await context.close();
});
