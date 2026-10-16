import { expect, test } from '@playwright/test';

for (const id of ['etf-rotation', 'hotsector']) {
  test(`${id} direct route shows reviewed aggregate results in both languages`, async ({ page }) => {
    await page.goto(`research/${id}/`);
    await expect(page.locator('main h1')).toBeVisible();
    await expect(page.locator('main')).toContainText('Historical diagnostic; not investment validation');
    await page.locator('details.results summary').click();
    await expect(page.locator('details.results table tbody tr')).toHaveCount(id === 'etf-rotation' ? 66 : 6);
    if (id === 'etf-rotation') await expect(page.locator('main')).toContainText('Interval lower bound');
    else {
      await expect(page.locator('main')).toContainText('Mean event uplift');
      await expect(page.locator('main')).toContainText('percentage points');
    }
    await page.getByRole('button', { name: 'Switch to Chinese' }).click();
    await expect(page.locator('main')).toContainText('历史诊断，尚非投资有效性验证');
    await expect(page.locator('details.results table tbody tr')).toHaveCount(id === 'etf-rotation' ? 66 : 6);
    if (id === 'etf-rotation') await expect(page.locator('main')).toContainText('区间下界');
    else {
      await expect(page.locator('main')).toContainText('事件平均增量');
      await expect(page.locator('main')).toContainText('百分点');
    }
    await page.reload();
    await expect(page.locator('main')).toContainText('这些诊断结果不能证明策略盈利');
  });
}

test('ETF cost and price controls update the chart data table', async ({ page }) => {
  await page.goto('research/etf-rotation/');
  await expect(page.getByRole('heading', { name: 'How do costs and price conventions change results?' })).toBeVisible();
  await expect(page.getByRole('table').first()).toContainText('-8.14%');
  await page.getByLabel('Price convention', { exact: true }).selectOption('raw');
  await expect(page.getByRole('table').first()).toContainText('-11.50%');
  await page.getByRole('button', { name: 'Switch to Chinese' }).click();
  await expect(page.getByLabel('价格口径', { exact: true })).toBeVisible();
  await expect(page.locator('main')).toContainText('按退出年份汇总');
});

test('hotspot chart switches between paired uplift and positive-event count without event rows', async ({ page }) => {
  await page.goto('research/hotsector/');
  await expect(page.getByRole('heading', { name: 'How much uplift remains after costs?' })).toBeVisible();
  await page.getByLabel('Show measure').selectOption('positive');
  await expect(page.locator('main')).toContainText('3 / 4');
  await expect(page.locator('main')).toContainText('0.239 pp');
  await expect(page.locator('main')).not.toContainText('2025-02-');
});

test('Barra conclusion and archive notes lead the explorer and its summary chart is interactive', async ({ page }) => {
  await page.goto('research/style-factors-18y/');
  await expect(page.getByRole('heading', { name: 'Current conclusion' })).toBeVisible();
  await expect(page.locator('main')).toContainText('Nineteen archived factor series differ widely and overlap');
  const conclusion = await page.locator('#current-conclusion').evaluate(node => node.compareDocumentPosition(document.querySelector('.barra-explorer')!) & Node.DOCUMENT_POSITION_FOLLOWING);
  expect(conclusion).toBeTruthy();
  await expect(page.getByLabel('Chart measure')).toBeVisible();
  await page.getByLabel('Chart measure').selectOption('sharpe');
  await expect(page.locator('.factor-summary-chart')).toHaveAttribute('aria-label', /Sharpe ratio/);
});
