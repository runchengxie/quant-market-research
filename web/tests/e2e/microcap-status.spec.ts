import {expect,test} from '@playwright/test';

test('status table leads evidence and survives locale/theme changes',async({page})=>{
 await page.goto('research/microcap/?lang=en-US');
 const status=page.locator('#microcap-current-status');
 const live=status.locator('[data-status-live]');
 await expect(live.locator('tbody tr')).toHaveCount(6);
 await expect(live).toContainText('runtime remains unrecovered');
 await expect(live).toContainText('completed months remain zero');
 expect(await status.evaluate(el=>Boolean(el.compareDocumentPosition(document.querySelector('#microcap-research-agenda')!)&Node.DOCUMENT_POSITION_FOLLOWING))).toBe(true);
 for(const link of await live.locator('tbody a').all())expect(await page.locator((await link.getAttribute('href'))!).count()).toBe(1);
 const html=await(await page.request.get('research/microcap/')).text();
 expect(html).toContain('data-status-live');
 expect(html).toContain('runtime remains unrecovered');
 expect(html).toContain('<template data-status-locale="zh-CN"');
 await page.getByRole('button',{name:'Switch to Chinese'}).click();
 await expect(live).toContainText('原始运行仍未找回');
 await expect(live).toContainText('已完成月份仍为零');
 const md=await(await page.request.get('downloads/microcap-research.zh-CN.md')).text();
 expect(md).toContain('## 当前研究状态');
 await page.evaluate(()=>{document.documentElement.dataset.theme='dark';});
 expect(await live.locator('table').evaluate(el=>getComputedStyle(el).color)).not.toBe('rgb(0, 0, 0)');
 await page.setViewportSize({width:390,height:844});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 await expect(live.locator('.status-table')).toHaveCSS('overflow-x','auto');
 await expect(live.locator('tbody th').first()).toHaveCSS('white-space','normal');
});
