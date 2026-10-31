import { test, expect } from '@playwright/test';
for (const width of [320, 1280]) for (const locale of ['en-US', 'zh-CN']) {
  test(`asset-return evidence retains scope and fits ${width} ${locale}`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto(`research/cashflow/?lang=${locale}#cashflow-long-run`);
    const section = page.locator('#cashflow-long-run');
    await expect(section).toBeVisible();
    await expect(section.locator('table')).toHaveCount(4);
    await expect(section.getByText('10.40%', { exact: true })).toHaveCount(1);
    await expect(section).toContainText(locale === 'en-US' ? 'not future probabilities' : '不是未来概率');
    await expect(section).toContainText(locale === 'en-US' ? 'not measured execution costs' : '未校准实测执行费用');
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  });
}
