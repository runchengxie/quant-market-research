import {expect,test} from '@playwright/test';
test('overview shares current topics and retains locale across navigation',async({page})=>{
 await page.goto('?lang=zh-CN');
 const cards=page.locator('[data-research-id]');await expect(cards).toHaveCount(9);
 await expect(page.locator('main h1')).toHaveText('各专题目前发现了什么');
 await expect(cards.first()).toContainText('2019-05-31 至 2026-06-30');
 await expect(page.locator('main')).not.toContainText('Not provided');
 await page.getByRole('button',{name:'切换到英文'}).click();
 await expect(page.locator('main h1')).toHaveText('Current findings by topic');
 await expect(cards.first()).toContainText('2019-05-31 to 2026-06-30');
 await page.getByRole('button',{name:'Switch to Chinese'}).click();
 await page.goto('research/');await expect(page.locator('main h1')).toHaveText('各专题目前发现了什么');
});
