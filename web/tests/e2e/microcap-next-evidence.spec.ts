import {expect,test} from '@playwright/test';

test('historical event and future-input evidence stays scoped across locales',async({page})=>{
 await page.goto('research/microcap/?lang=en-US');
 const live=page.locator('#microcap-next-evidence [data-next-live]');
 await expect(page.locator('#microcap-next-evidence h2')).toContainText('Version 1.0.5 snapshot');
 await expect(live).toContainText('91 then unreviewed events');
 await expect(live.locator('a[href="#microcap-chain"]')).toContainText('current account-chain review');
 await expect(live).toContainText('94 distinct dated blocked events');
 await expect(live).toContainText('resolver was not recomputed');
 await expect(live).toContainText('zero completed months');
 await expect(live).toContainText('No new capital grid');
 await expect(live.locator('.case-outcomes tbody tr')).toHaveCount(4);
 await expect(live.locator('.case-outcomes')).toContainText('1.2255331');
 await expect(live.locator('.case-outcomes')).toContainText('0.3158');
 await expect(live.locator('.case-outcomes')).toContainText('2025-01-24');
 await live.locator('details').first().locator('summary').click();
 await expect(live).toContainText('no multi-day unlisted phase is observed');
 await expect(live).toContainText('cannot be filled with zero');
 await expect(live.locator('details').first().locator('tbody tr')).toHaveCount(8);
 await page.getByRole('button',{name:'Switch to Chinese'}).click();
 await expect(live).toContainText('原解析器未重算');
 await live.locator('details').first().locator('summary').click();
 await expect(live.locator('details').first()).toContainText('缺失或冲突的金额不能补零');
 const publicData=await(await page.request.get('data/microcap_next_evidence_review.json')).json();
 expect(publicData.raw_share_ready).toBe(false);
 expect(publicData.readiness.admitted).toBe(false);
 expect(publicData.readiness.issue_count).toBe(7);
 expect(publicData.initial_readiness.issue_count).toBe(8);
 expect(publicData.calendar.vendor_calendar_mismatches).toBe(0);
 expect(JSON.stringify(publicData)).not.toMatch(/ts_code|\/home\/|private_path/);
 for(const locale of ['en-US','zh-CN']){
  const md=await(await page.request.get(`downloads/microcap-research.${locale}.md`)).text();
  expect(md).toContain('94');expect(md).toContain('83');expect(md).toContain('91');
 }
 await page.evaluate(()=>{document.documentElement.dataset.theme='dark';});
 await page.setViewportSize({width:390,height:844});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 await expect(live.locator('.case-outcomes td').first()).toHaveCSS('white-space','normal');
});
