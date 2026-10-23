import { test, expect } from '@playwright/test';
test('research library groups all topics without hiding their sample or limitation', async ({ page }) => {
  await page.goto('research/?lang=en-US');
  await expect(page.locator('.library-group')).toHaveCount(4);
  await expect(page.locator('[data-research-id]')).toHaveCount(9);
  await page.getByRole('navigation', { name: 'Research areas' }).getByRole('link').last().click();
  await expect(page).toHaveURL(/#area-execution$/);
  await expect(page.locator('[data-research-id="liquidity"] .reading-limit')).toBeVisible();
});
test('cashflow replication report retains figures, steps, boundaries and source versions', async ({ page, request }) => {
  await page.goto('research/cashflow/?lang=en-US');
  await expect(page.getByRole('link', { name: 'Rule reproduction, shadow portfolios and evidence history →' })).toHaveAttribute('href', '/quant-market-research/research/cashflow/replication/');
  await page.goto('research/cashflow/replication/?lang=en-US');
  await expect(page.locator('main h1')).toHaveText('Cash Flow Indices: Rule Reproduction and Strategy Boundaries');
  await expect(page.locator('[data-research-step]')).toHaveCount(4);
  await expect(page.locator('[data-research-chart]')).toHaveCount(2);
  await expect(page.locator('main')).toContainText('0.997');
  await expect(page.locator('main')).toContainText('0.992');
  await expect(page.locator('main')).toContainText('no historical weights');
  await expect(page.locator('main')).toContainText('2024-09-18');
  const response = await request.get('data/cashflow-replication/exploration.json');
  expect(response.ok()).toBe(true);
  expect((await response.json()).charts[0].series[0].values[0]).toBe(.1699);
  await page.getByRole('button', { name: 'Switch to Chinese' }).click();
  await expect(page.locator('main h1')).toHaveText('现金流指数：规则复现与策略边界');
  await expect(page.locator('main')).toContainText('历史权重');
});

for (const width of [360, 900, 1440]) for (const locale of ['en-US', 'zh-CN']) {
 test('library and migrated report fit ' + width + 'px in ' + locale, async ({ page }) => {
  await page.setViewportSize({ width, height: 900 });
  await page.addInitScript(() => localStorage.setItem('market-research-theme', 'dark'));
  for (const route of ['research/', 'research/cashflow/replication/']) {
   await page.goto(route + '?lang=' + locale);
   await expect(page.locator('main h1')).toBeVisible();
   expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
   if (route.includes('replication')) {
    await page.locator('[data-research-chart]').first().locator('summary').click();
    await expect(page.locator('[data-research-chart]').first().locator('table')).toContainText('16.99%');
   }
   await expect(page.locator('html')).toHaveAttribute('data-theme','dark');
  }
 });
}

test('jump-link headings remain below the desktop sticky header', async ({ page }) => {
 await page.setViewportSize({ width: 1440, height: 900 });
 await page.goto('research/?lang=en-US');
 await page.locator('.library-nav a[href="#area-portfolios"]').click();
 await expect.poll(async () => page.locator('#heading-portfolios').evaluate(el => el.getBoundingClientRect().top - document.querySelector('.site-header')!.getBoundingClientRect().bottom)).toBeGreaterThanOrEqual(0);
 await page.goto('research/cashflow/replication/?lang=en-US');
 await page.locator('.replication-nav a[href="#calibration"]').click();
 await expect.poll(async () => page.locator('#calibration h2').evaluate(el => el.getBoundingClientRect().top - document.querySelector('.site-header')!.getBoundingClientRect().bottom)).toBeGreaterThanOrEqual(0);
});
