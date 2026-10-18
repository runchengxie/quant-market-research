import {expect,test} from '@playwright/test';
test('holdings impact agrees with reviewed data and downloads across locales and dark mobile',async({page})=>{
 await page.goto('research/microcap/?lang=en-US');
 const live=page.locator('#microcap-impact [data-impact-live]');
 await expect(live).toContainText('seven intersect');await expect(live).toContainText('Six other groups');
 await expect(live.locator('[data-impact-block="exposure"] tbody tr')).toHaveCount(6);
 await expect(live.locator('[data-impact-block="exposure"] tbody tr').nth(2).locator('td')).toHaveText(['7','0','81','6']);
 await expect(live).toContainText('0.15–0.26');await expect(live).toContainText('not an estimated event loss');
 await expect(live.locator('[data-impact-block="account"] tbody tr')).toHaveCount(4);
 await expect(live.locator('[data-impact-block="register"] tbody tr')).toHaveCount(2);
 await live.locator('summary').click();await expect(live.locator('details')).toHaveAttribute('open','');
 await page.evaluate(()=>{document.documentElement.lang='zh-CN';});await expect(live).toHaveAttribute('lang','zh-CN');await expect(live.locator('details')).toHaveAttribute('open','');
 await page.evaluate(()=>{document.documentElement.lang='en-US';});await expect(live).toHaveAttribute('lang','en-US');
 await page.getByRole('button',{name:'Switch to Chinese'}).click();
 await expect(live).toContainText('最低有效观测数');await expect(live).toContainText('库存仍未知');await expect(live).toContainText('revision_safe=false');
 const data=await(await page.request.get('data/microcap_impact_review.json')).json();
 expect(data.raw_share_ready).toBe(false);expect(data.exposure.plans['90'].inventory.owner_ideal_fee10.unknown).toBe(6);
 for(const locale of ['en-US','zh-CN']){
  const latest=await(await page.request.get(`downloads/microcap-research.${locale}.md`)).text();
  const fixed=await(await page.request.get(`downloads/archive/microcap-research.v1.0.7.${locale}.md`)).text();
  expect(latest).toBe(fixed);expect(latest).toContain(data.register.head_sha256);expect(latest).toContain('0.15–0.26');
 }
 await page.evaluate(()=>{document.documentElement.dataset.theme='dark';});await page.setViewportSize({width:390,height:844});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 await expect(live.locator('td').first()).toHaveCSS('white-space','normal');
 await page.locator('#microcap-impact').screenshot({path:'/tmp/microcap-impact-dark-mobile.png'});
});
