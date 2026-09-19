import { expect, test } from '@playwright/test';

const docs = ['docs/', 'docs/research-closeout-status/', 'docs/research/factors/low-turnover/', 'docs/research/factors/microcap/', 'docs/research/factors/smallcap-turnover-history/', 'docs/research/factors/barra-factor-dictionary/', 'docs/research/factors/barra-source-inventory/'];

test('all seven public documents use the shared shell and preserve readable content', async ({ page }) => {
  for (const route of docs) {
    await page.goto(route);
    await expect(page.locator('main h1')).toHaveCount(1);
    await expect(page.getByRole('navigation', { name: '主导航' })).toBeVisible();
    const html = await page.locator('html').evaluate((node) => node.outerHTML);
    expect(html).not.toContain('\u0000');
    expect(html).not.toContain('INTERNAL_ONLY_SENTINEL');
  }
});
