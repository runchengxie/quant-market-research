import { test, expect } from '@playwright/test';

for (const locale of ['en-US', 'zh-CN']) {
  test(`ledger checkpoint keeps limitations beside scenarios and survives locale: ${locale}`, async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(`research/valuation-groups/?lang=${locale}`);
    await expect(page.getByTestId('valuation-checkpoint')).toBeVisible();
    await expect(page.getByTestId('ledger-warning')).toContainText('raw_share_ready=false');
    await expect(page.getByTestId('ledger-warning')).toContainText('revision_safe=false');
    await expect(page.getByTestId('ledger-unresolved-scope')).toContainText('39');
    await expect(page.getByTestId('ledger-support').locator('tbody tr')).toHaveCount(5);
    await expect(page.getByTestId('ledger-support').locator('tbody tr').first()).toContainText('51');
    await expect(page.getByTestId('ledger-action-gap')).toContainText('1,390');
    await page.getByTestId('ledger-sensitivity').locator('summary').click();
    await expect(page.getByTestId('ledger-sensitivity-table').locator('tbody tr').first()).toContainText('50.99%');
    await expect(page.getByTestId('ledger-sensitivity-table').locator('tbody tr').first()).toContainText(locale === 'en-US' ? 'Unavailable' : '不可用');
    await page.getByTestId('ledger-metric').selectOption('pe_deducted_proxy');
    await page.getByTestId('ledger-scenario').selectOption('close10');
    await expect(page.getByTestId('ledger-sensitivity-table').locator('tbody tr').last()).toContainText('36.36%');
    await expect(page.getByTestId('persistence-table').locator('tbody tr')).toHaveCount(4);
    await expect(page.getByTestId('condition-limit')).toContainText(locale === 'en-US' ? 'not returns from the new ledger' : '并非新账本收益');
    await expect(page.getByTestId('checkpoint-coverage-table').locator('tbody tr')).toHaveCount(5);
    await expect(page.getByTestId('checkpoint-coverage-table')).toContainText('1,743');
    await expect(page.getByTestId('valuation-cases').locator('li')).toHaveCount(3);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    if (process.env.STUDY_SCREENSHOTS) await page.getByTestId('valuation-ledger').screenshot({ style: 'header, .skip-link { visibility: hidden !important; }', path: `${process.env.STUDY_SCREENSHOTS}/valuation-ledger-mobile-${locale}.png` });
  });
}

test('desktop checkpoint retains PB scenario sensitivity and static-industry qualification', async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 960 });
  await page.goto('research/valuation-groups/?lang=en-US');
  await page.getByTestId('ledger-sensitivity').locator('summary').click();
  await page.getByTestId('ledger-scenario').selectOption('touch30');
  await expect(page.getByTestId('ledger-sensitivity-table').locator('tbody tr').first()).toContainText('31.48%');
  await expect(page.getByTestId('ledger-fill-limits')).toContainText('feasible order sequencing');
  await expect(page.getByTestId('ledger-audit-note')).toContainText('only orders marked filled');
  await expect(page.getByTestId('ledger-audit-note')).toContainText('cash allocation');
  await expect(page.getByTestId('valuation-coverage-audit')).toContainText('2026-09-28');
  await expect(page.getByTestId('valuation-coverage-audit')).toContainText('not point-in-time');
  await expect(page.locator('.valuation-conclusions nav a[href="#valuation-ledger"]')).toBeVisible();
  if (process.env.STUDY_SCREENSHOTS) await page.getByTestId('valuation-ledger').screenshot({ style: 'header, .skip-link { visibility: hidden !important; }', path: `${process.env.STUDY_SCREENSHOTS}/valuation-ledger-desktop.png` });
});
