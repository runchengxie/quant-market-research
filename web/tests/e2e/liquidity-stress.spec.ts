import {expect,test} from '@playwright/test';

test('stress, persistence and recorded clock windows remain separate and interactive',async({page})=>{
 await page.goto('research/liquidity/?lang=en-US');
 const panel=page.locator('#liquidity-stress');await expect(panel).toBeVisible();
 await expect(panel).toContainText('2025-01, 2025-02, 2025-05');
 await expect(panel).toContainText('82.13%');
 await expect(panel).toContainText('92.06%');
 await expect(panel).toContainText('99.18%');
 await panel.getByLabel('Recorded timestamp window',{exact:true}).selectOption('close30');
 await expect(panel).toContainText('15.27%');
 await panel.getByLabel('Full-day hypothetical budget to scale (USD)',{exact:true}).fill('');
 await expect(panel).toContainText('Enter a valid full-day budget');
 await panel.getByLabel('Full-day hypothetical budget to scale (USD)',{exact:true}).fill('2000000');
 await expect(panel).toContainText('305,379.36');
 await panel.getByLabel('Analysis year',{exact:true}).selectOption('2015');
 await expect(panel).toContainText('No qualified minute observations');
});

for(const theme of ['dark','light'])test(`stress explorer supports Chinese and mobile ${theme} presentation`,async({page})=>{
 await page.addInitScript(value=>localStorage.setItem('market-research-theme',value),theme);
 await page.setViewportSize({width:390,height:900});
 await page.goto('research/liquidity/?lang=zh-CN');
 const panel=page.locator('#liquidity-stress');await expect(panel).toBeVisible();
 await expect(panel).toContainText('月末冻结名单');
 await expect(panel.locator('.research-chart canvas').first()).toBeVisible();
 await panel.screenshot({path:test.info().outputPath(`stress-${theme}.png`)});
 await panel.getByLabel('压力分析市值组',{exact:true}).selectOption('0');
 await expect(panel).toContainText('合格月份不足');
 await expect(panel).toContainText('没有合格分钟观测');
 if(theme==='dark')expect(await panel.locator('.panel').first().evaluate(el=>getComputedStyle(el).backgroundColor)).not.toBe('rgb(255, 255, 255)');
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBeTruthy();
});
