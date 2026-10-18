import { test, expect } from '@playwright/test';

for (const locale of ['en-US', 'zh-CN']) {
  test(`valuation coverage and forward protocol render on mobile: ${locale}`, async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(`docs/research/experiments/valuation-panel-20261018/?lang=${locale}`);
    const article = page.locator('[data-document-body]');
    await expect(article).toContainText('1,743');
    await expect(article).toContainText('31.3%');
    await expect(article.locator('table')).toHaveCount(4);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    const annual = article.locator('table').nth(2);
    expect(await annual.evaluate(el => el.scrollWidth > el.clientWidth)).toBe(true);
    await page.goto(`docs/research/experiments/overseas-forward-v1/?lang=${locale}`);
    await expect(page.locator('[data-document-body]')).toContainText('08:45');
    await expect(page.locator('[data-document-body]')).toContainText('60');
    await page.goto(`docs/research/experiments/microcap-st-paired-short-window-20261018/?lang=${locale}`);
    await expect(page.locator('[data-document-body]')).toContainText('ST');
  });
}
