import { expect, test } from '@playwright/test';

for (const route of ['research/cashflow/', 'research/cashflow/recovery/', 'research/microcap/', 'research/microcap/cross-market-liquidity/', 'research/indices/', 'research/liquidity/', 'research/factors/low-turnover/']) {
  test(`${route} has a single readable heading and topic navigation`, async ({ page }) => {
    await page.goto(route);
    await expect(page.locator('main h1')).toHaveCount(1);
    await expect(page.getByRole('navigation', { name: '本页目录' })).toBeVisible();
    const links = page.getByRole('navigation', { name: '本页目录' }).locator('a');
    for (let i = 0; i < await links.count(); i += 1) await expect(page.locator(await links.nth(i).getAttribute('href') ?? '#')).toHaveCount(1);
  });
}
