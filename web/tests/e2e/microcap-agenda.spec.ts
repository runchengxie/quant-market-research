import {expect,test} from '@playwright/test';

test('four followups retain scopes, current evidence and downloadable charts across locales',async({page})=>{
 await page.goto('research/microcap/?lang=en-US');
 if(await page.locator('#microcap-archive').count() && await page.locator('#microcap-archive').getAttribute('open')===null) await page.locator('#microcap-archive > summary').click();
 const section=page.locator('#microcap-research-agenda');
 const live=section.locator('[data-agenda-live]');
 await expect(live).toContainText('New eligible completed months: 0');
 await expect(live).toContainText('1,252');
 await expect(live).toContainText('1.47');
 await expect(live).toContainText('future prices do not rerank');
 await expect(live.locator('.claim')).toHaveCount(6);
 await live.locator('.claim').first().locator('summary').click();
 await expect(live.locator('.claim').first()).toContainText('Current stage');
 await page.evaluate(()=>{document.documentElement.dataset.theme='dark';localStorage.setItem('market-research-theme','dark');});
 const svg=live.locator('svg').first();
 expect(await svg.locator('rect').first().evaluate(el=>getComputedStyle(el).fill)).not.toBe('rgb(255, 255, 255)');
 await page.getByRole('button',{name:'Switch to Chinese'}).click();
 await expect(live).toContainText('新样本已完成合格月份：0');
 await expect(live).toContainText('前高至恢复');
 await expect(live.locator('.claim').first()).toContainText('历史描述');
 await live.locator('.claim').first().locator('summary').click();
 expect(await live.locator('.claim').first().evaluate(d=>(d as HTMLDetailsElement).open)).toBe(true);
 await page.evaluate(()=>{document.documentElement.lang='en-US';});
 await expect(live).toContainText('Current stage');
 expect(await live.locator('.claim').first().evaluate(d=>(d as HTMLDetailsElement).open)).toBe(true);
 await page.evaluate(()=>{document.documentElement.lang='zh-CN';});
 await expect(live).toContainText('历史描述');
 for(const locale of ['en-US','zh-CN'])for(const chart of ['microcap-failure-atlas','microcap-size-liquidity']){
  const response=await page.request.get(`downloads/${chart}.${locale}.svg`);
  expect(response.status()).toBe(200);expect(await response.text()).toContain('<svg');
 }
 const md=await(await page.request.get('downloads/microcap-research.zh-CN.md')).text();
 expect(md).toContain('版本 1.0.9');expect(md).toContain('MC-C06');expect(md).toContain('1.47');
 await page.setViewportSize({width:390,height:844});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 await live.locator('.agenda-chart').first().screenshot({path:'/tmp/microcap-agenda-dark-chart.png'});
});
