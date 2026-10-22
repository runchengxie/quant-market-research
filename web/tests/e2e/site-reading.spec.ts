import {expect,test} from '@playwright/test';
test('current topics, evidence links and archived anchors remain accessible',async({page})=>{
 await page.goto('research/?lang=zh-CN');
 await expect(page.locator('[data-research-id]')).toHaveCount(9);
 await expect(page.locator('[data-research-id="microcap"] h2')).toHaveText('小微盘研究');
 await page.goto('research/microcap/?lang=zh-CN');
 await expect(page.locator('#microcap-archive')).not.toHaveAttribute('open','');
 await page.goto('research/microcap/?lang=zh-CN#microcap-chain');
 await expect(page.locator('#microcap-archive')).toHaveAttribute('open','');
 await expect(page.locator('#microcap-chain')).toBeVisible();
 await page.locator('#microcap-archive > summary').click();
 await page.locator('#microcap-current-status a[href="#microcap-chain"]').first().click();
 await expect(page.locator('#microcap-archive')).toHaveAttribute('open','');
 await page.goto('data-sources/?lang=zh-CN#research-rotation');
 await expect(page.locator('#research-rotation')).toContainText('尚无统一业绩窗口');
 await page.locator('#research-rotation summary').click();
 await expect(page.locator('#research-rotation code').first()).toContainText('SHA-256');
});
for(const locale of ['en-US','zh-CN'])test(`summary PNG and mobile reading in ${locale}`,async({page})=>{
 await page.setViewportSize({width:390,height:844});
 await page.goto(`research/overseas-leadlag/?lang=${locale}`);
 const button=page.getByTestId('download-research-image');await button.scrollIntoViewIfNeeded();
 const download=page.waitForEvent('download');await button.click();
 expect((await download).suggestedFilename()).toMatch(new RegExp(`overseas-leadlag.*${locale}\\.png`));
 await expect(page.getByTestId('research-image-preview')).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});
