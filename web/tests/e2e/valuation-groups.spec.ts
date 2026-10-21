import { test, expect } from '@playwright/test';

for (const locale of ['en-US', 'zh-CN']) {
  test(`grouped valuations expose sample support and limitations on mobile: ${locale}`, async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(`research/valuation-groups/?lang=${locale}`);
    await expect(page.getByTestId('valuation-distribution')).toBeVisible();
    await expect(page.getByTestId('valuation-warning')).toContainText('revision_safe=false');
    await page.getByTestId('valuation-group').selectOption('star_st');
    await page.getByTestId('valuation-basis').selectOption('common_five');
    await expect(page.getByTestId('valuation-factor-basis')).toContainText('metric_available');
    await page.getByTestId('valuation-metric').selectOption('pe_deducted_proxy');
    await expect(page.getByTestId('valuation-summary')).toContainText('*ST');
    await expect(page.getByTestId('valuation-distribution')).toContainText('proxy');
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    if (process.env.STUDY_SCREENSHOTS) await page.screenshot({ path: `${process.env.STUDY_SCREENSHOTS}/valuation-mobile-${locale}.png`, fullPage: true });
    await page.getByTestId('valuation-group').selectOption('unknown');
    await expect(page.getByTestId('valuation-factor')).toContainText(locale === 'en-US' ? 'unavailable' : '不计算');
    await page.getByTestId('valuation-date').selectOption('20160129');
    await expect(page.getByTestId('valuation-summary')).toContainText('20160129');
  });
}

test('desktop review displays actual sample support and all five factor groups', async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 960 });
  await page.goto('research/valuation-groups/?lang=en-US');
  await expect(page.getByTestId('valuation-distribution')).toContainText('3,703 / 5,567');
  await page.getByTestId('valuation-group').selectOption('st');
  await page.getByTestId('valuation-metric').selectOption('pb_parent');
  await expect(page.getByTestId('valuation-factor').locator('tbody tr')).toHaveCount(5);
  await expect(page.getByTestId('valuation-distribution')).toContainText('101 / 108');
  const first = page.getByTestId('valuation-factor').locator('tbody tr').first();
  await expect(first.locator('td').nth(0)).toContainText('/ 8');
  await expect(first.locator('td').nth(1)).toContainText('/ 2');
  await expect(first.locator('td').nth(2)).toContainText('/ 2');
  await page.getByTestId('valuation-basis').selectOption('common_five');
  await expect(page.getByTestId('valuation-factor-basis')).toContainText('metric_available');
  await expect(first.locator('td').nth(0)).toContainText('/ 8');
  await expect(first.locator('td').nth(1)).toContainText('/ 2');
  if (process.env.STUDY_SCREENSHOTS) await page.screenshot({ path: `${process.env.STUDY_SCREENSHOTS}/valuation-desktop-en-US.png`, fullPage: true });
});
