import { expect, test } from '@playwright/test';

for (const [locale, title] of [['en-US', 'Low valuation'], ['zh-CN', '低估值研究']]) {
  test(`valuation numeric tables retain complete values on mobile ${locale}`, async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(`docs/research/experiments/valuation-denominators-20261018/?lang=${locale}`);
    await expect(page.locator('.article-content h1')).toContainText(title);
    const tables = page.locator('.article-content table');
    await expect(tables).toHaveCount(3);
    const sample = tables.nth(1);
    await expect(sample.locator('tbody tr')).toHaveCount(6);
    await expect(sample.locator('tbody td').first()).toHaveText('000651.SZ');
    expect(await sample.evaluate(el => el.scrollWidth > el.clientWidth)).toBe(true);
    expect(await sample.locator('tbody td').first().evaluate(el => getComputedStyle(el).whiteSpace)).toBe('nowrap');
    expect(await sample.locator('tbody tr').first().evaluate(el => el.getBoundingClientRect().height)).toBeLessThan(80);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
  });
}
