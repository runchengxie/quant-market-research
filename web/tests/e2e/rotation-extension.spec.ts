import { test, expect } from '@playwright/test';
const route = 'research/style-theme-rotation/';
for (const lang of ['en-US', 'zh-CN']) {
    test(`forward status, source filtering and robustness controls ${lang}`, async ({ page }) => {
        const errors: string[] = [];
        page.on('pageerror', e => errors.push(e.message));
        await page.goto(`${route}?lang=${lang}`);
        const forward = page.locator('#rotation-forward');
        await expect(forward.locator('input[type=search]')).toBeVisible();
        await expect(forward).toContainText(lang === 'en-US' ? 'Waiting for fresh inputs' : '等待新数据');
        await forward.locator('input').fill('515910');
        await expect(forward.locator('#rotation-sources tbody').first().getByRole('row')).toHaveCount(1);
        await expect(forward.locator('#rotation-sources tbody').first()).toContainText('515910');
        const robust = page.locator('#rotation-robustness');
        const selects = robust.locator('select');
        await expect(selects).toHaveCount(6);
        await selects.nth(2).selectOption('10');
        await selects.nth(3).selectOption('2');
        await selects.nth(4).selectOption('last_252');
        await expect(robust.getByTestId('robustness-period')).toContainText('252');
        await expect(page).toHaveURL(/robustCost=10/);
        await expect(page).toHaveURL(/robustDelay=2/);
        await selects.nth(0).selectOption('pool');
        await expect(robust).toContainText(lang === 'en-US' ? 'quality' : '质量');
        await expect(robust).toContainText(lang === 'en-US' ? 'dividend' : '红利');
        expect(errors).toEqual([]);
    });
    test(`release compatibility and mobile layout ${lang}`, async ({ page }) => {
        await page.setViewportSize({ width: 390, height: 844 });
        await page.goto(`${route}?lang=${lang}`);
        const versions = page.locator('#rotation-versions');
        await expect(versions.getByRole('button')).toBeVisible();
        await versions.getByRole('button', { name: lang === 'en-US' ? 'Compare releases' : '比较版本', exact: true }).click();
        await expect(versions).toContainText(lang === 'en-US' ? 'numerical deltas are suppressed' : '不显示数值差额');
        await expect(versions).not.toContainText(lang === 'en-US' ? 'Could not verify' : '无法验证');
        await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
    });
}
test('no JavaScript keeps the five workstreams and real status readable', async ({ browser }) => {
    const context = await browser.newContext({ javaScriptEnabled: false });
    const page = await context.newPage();
    await page.goto(route + '?lang=en-US');
    await expect(page.locator('#rotation-forward')).toContainText('Waiting for fresh inputs');
    await expect(page.locator('#rotation-sources')).toContainText('515910');
    await expect(page.locator('#rotation-robustness')).toContainText('Annualized return');
    await expect(page.locator('#rotation-versions')).toContainText(/recovered/i);
    await context.close();
});

test('rolling diagnostics load verified data and preserve an explicit window',async({page})=>{
 await page.goto(route+'?lang=en-US');const robust=page.locator('#rotation-robustness');
 await robust.getByRole('button',{name:'Load rolling-window diagnostics',exact:true}).click();
 await expect(robust.locator('option[value="rolling_252_2026-07-31"]')).toHaveCount(1,{timeout:30000});
 await robust.getByLabel('Evaluation window',{exact:true}).selectOption('rolling_252_2026-07-31');
 await expect(robust.getByTestId('robustness-period')).toContainText('252');
 await expect(page).toHaveURL(/robustWindow=rolling_252_2026-07-31/);
 await robust.scrollIntoViewIfNeeded();await page.screenshot({path:'/tmp/rotation-forward-desktop.png'});
});

test('failed rolling integrity check leaves earlier valid diagnostics readable',async({page})=>{
 await page.route('**/rotation/releases/rotation-forward-20261017-v1.json',r=>r.fulfill({status:200,body:'{}'}));
 await page.goto(route+'?lang=zh-CN');const robust=page.locator('#rotation-robustness');
 await robust.getByRole('button',{name:'加载滚动窗口检验',exact:true}).click();
 await expect(robust.getByRole('alert')).toContainText('无法验证');
 await expect(robust.getByTestId('robustness-period')).toContainText('2181');
 await page.setViewportSize({width:390,height:844});await page.emulateMedia({colorScheme:'dark'});
 await robust.scrollIntoViewIfNeeded();await page.screenshot({path:'/tmp/rotation-forward-mobile.png'});
});
