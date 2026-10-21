import { test, expect } from '@playwright/test';

for (const locale of ['en-US', 'zh-CN']) {
  test(`low valuation topic preserves annual scope, gaps and support on mobile: ${locale}`, async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(`research/valuation-groups/?lang=${locale}`);
    await expect(page.getByRole('heading', { level: 1 })).toHaveText(locale === 'en-US' ? 'Low-valuation research' : '低估值研究');
    await expect(page.getByTestId('annual-table').locator('tbody tr')).toHaveCount(11);
    await expect(page.getByTestId('valuation-early-coverage')).toContainText('2,558');
    const row = page.getByTestId('annual-table').locator('tr').filter({ hasText: '2024-12-31' });
    await expect(row).toContainText('0.2552');
    await expect(row).toContainText('0.5337');
    await expect(row).toContainText('5,210 / 5,218');
    await page.getByTestId('valuation-annual').locator('.valuation-detail summary').click();
    const extreme = page.getByTestId('annual-extremes').locator('tr').filter({ hasText: '2024-06-28' });
    await expect(extreme).toContainText('0.1431');
    if (process.env.STUDY_SCREENSHOTS) await page.getByTestId('valuation-annual').screenshot({ path: `${process.env.STUDY_SCREENSHOTS}/low-valuation-annual-mobile-${locale}.png` });
    await page.getByTestId('annual-group').selectOption('star_st');
    await expect(page.getByTestId('gap-scope')).toContainText(locale === 'en-US' ? 'Fixed scope: all quoted names' : '固定范围为全部有报价证券');
    await page.getByTestId('annual-metric').selectOption('pe_deducted_proxy');
    await expect(page.getByTestId('annual-table').locator('tr').filter({ hasText: '2026-10-16' })).toContainText('4 / 88');
    await expect(page.getByTestId('valuation-evidence')).toContainText('weekly-20260904');
    await expect(page.getByTestId('valuation-evidence')).toContainText('missing_holding_return=zero');
    await expect(page.getByTestId('gap-total')).toContainText('4,560');
    await page.getByTestId('gap-metric').selectOption('pe_deducted_proxy');
    await expect(page.getByTestId('gap-total')).toContainText('2,160');
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  });
}

test('desktop topic separates rank overlap, legacy returns and conditional evidence', async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 960 });
  await page.goto('research/valuation-groups/?lang=en-US');
  await expect(page.getByTestId('valuation-rank-comparison')).toContainText('0.5066');
  await expect(page.getByTestId('valuation-rank-comparison')).toContainText('28.07%');
  await expect(page.getByTestId('valuation-legacy')).toContainText('10.64%');
  await expect(page.getByTestId('valuation-legacy')).toContainText('5.24%');
  await expect(page.getByTestId('valuation-legacy')).toContainText('6.04%');
  await expect(page.getByTestId('valuation-gaps')).toContainText('3,373');
  await expect(page.getByTestId('valuation-warning')).toContainText('revision_safe=false');
  if (process.env.STUDY_SCREENSHOTS) {
    await page.getByTestId('valuation-annual').screenshot({ path: `${process.env.STUDY_SCREENSHOTS}/low-valuation-annual-desktop.png` });
    await page.getByTestId('valuation-evidence').screenshot({ path: `${process.env.STUDY_SCREENSHOTS}/low-valuation-evidence-desktop.png` });
  }
});

test('existing topic URL, research discovery and method URLs remain usable', async ({ page }) => {
  await page.goto('research/?lang=en-US');
  const topic = page.locator('a[href*="/research/valuation-groups/"]').first();
  await expect(topic).toBeVisible();
  await topic.click();
  await expect(page.getByTestId('valuation-topic')).toBeVisible();
  for (const target of ['style-factors-18y', 'microcap', 'cashflow']) await expect(page.locator(`.valuation-topic a[href*="/research/${target}/"]`).first()).toHaveAttribute('href', /lang=/);
  await page.goto('docs/research/experiments/grouped-valuation-20261021/?lang=en-US');
  await expect(page.locator('main')).toContainText('Low-valuation research');
  await page.goto('docs/research/experiments/valuation-panel-20261018/?lang=en-US');
  await expect(page.locator('main')).toContainText('valuation');
});
