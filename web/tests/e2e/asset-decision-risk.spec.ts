import {test,expect} from '@playwright/test';
for(const width of [1280,390]){
 test(`decision experiments retain scope, selectors and evidence at ${width}px`,async({page,request})=>{
  await page.setViewportSize({width,height:844});
  await page.goto('research/asset-allocation/?lang=en-US');
  const root=page.locator('#asset-decision-evidence');
  await expect(root).toContainText('not future loss probabilities');
  await expect(root).toContainText('do not certify rising interest rates');
  const graph=page.locator('[data-asset-chart=spending]');await graph.scrollIntoViewIfNeeded();await expect(graph).toHaveAttribute('data-chart-ready','true');
  const table=page.locator('details[data-asset-table=spending]');if((await table.getAttribute('open'))===null)await table.locator('summary').click();
  await expect(root.locator('#decision-spending tbody tr:visible')).toHaveCount(9);
  await page.selectOption('#decision-shock','12');
  await expect(root.locator('#decision-spending tbody tr:visible')).toContainText(['5.56%','4.63%','3.70%','0.00%','0.00%','0.00%','0.00%','0.00%','0.00%']);
  await page.selectOption('#decision-demand','6');
  await expect(root.locator('#decision-spending tbody tr:visible')).toHaveCount(9);
  await page.goto('research/asset-allocation/?lang=zh-CN');
  await expect(root).toContainText('未来表现仍需继续观察');
  await expect(root).toContainText('从初始本金划出');
  await page.goto('research/asset-implementation/?lang=zh-CN');
  await expect(root).toContainText('2012年11月末缺少记录');
  await expect(root).toContainText('复核条件');
  const response=await request.get((await root.getByRole('link',{name:'已核查实验汇总与结论台账'}).getAttribute('href'))!);
  expect(response.ok()).toBe(true);
  const data=await response.json();
  expect(data.spending).toHaveLength(108);
  expect(data.conclusion_register.claims).toHaveLength(7);
  expect(data).not.toHaveProperty('spending_details');
  await expect(page.locator('body')).toHaveJSProperty('scrollWidth',width);
 });
}
