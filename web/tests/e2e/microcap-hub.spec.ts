import { expect, test } from '@playwright/test';

test('hub connects questions, source-backed charts and revised evidence in both languages', async ({ page }) => {
  await page.goto('research/microcap/?lang=en-US');
  await expect(page.locator('#microcap-map').getByRole('link')).toHaveCount(6);
  await page.locator('.topic-nav').getByRole('link', { name: 'Research map', exact: true }).click();
  const mapHeading = await page.locator('#microcap-map h2').boundingBox();
  const masthead = await page.locator('.site-header').boundingBox();
  expect(mapHeading!.y).toBeGreaterThanOrEqual(masthead!.y + masthead!.height);
  const links = await page.locator('#microcap-map a').evaluateAll(nodes => nodes.map(node => (node as HTMLAnchorElement).href));
  for (const href of links) expect((await page.request.get(href)).status()).toBe(200);
  const windows = page.locator('#microcap-window-evidence');
  await expect(windows).toContainText('2015–2026');
  await expect(windows.locator('[data-metric-panel="return"]')).toContainText('7.60%');
  await windows.getByRole('button', { name: 'Maximum drawdown', exact: true }).click();
  await expect(windows.locator('[data-metric-panel="drawdown"]')).toBeVisible();
  await expect(windows.locator('[data-metric-panel="return"]')).toBeHidden();
  await expect(windows.locator('[data-metric-panel="drawdown"]')).toContainText('-65.01%');
  const matrix = page.locator('#microcap-rule-matrix');
  await expect(matrix.locator('tbody td')).toHaveCount(16);
  await expect(matrix).toContainText('weight-level screening engine');
  await expect(page.locator('#microcap-revisions')).toContainText('Next-session execution');
  await expect(page.locator('#microcap-open-questions')).toContainText('Not yet published');
  await page.getByRole('button', { name: 'Switch to Chinese' }).click();
  await expect(page.locator('#microcap-map')).toContainText('研究地图');
  await expect(page.locator('#microcap-window-evidence')).toContainText('最大回撤');
  await expect(page.locator('#microcap-revisions')).toContainText('下一交易日执行');
});

test('hub and numerical evidence remain readable without JavaScript on mobile', async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  await page.goto('research/microcap/');
  await expect(page.locator('#microcap-map')).toContainText('Research map');
  await expect(page.locator('#microcap-window-evidence')).toContainText('7.60%');
  const sourceLink = page.locator('#microcap-window-evidence a[href$="low_turnover_exploration.json"]');
  expect((await page.request.get((await sourceLink.getAttribute('href'))!)).status()).toBe(200);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await context.close();
});
