import { test, expect } from '@playwright/test';

test('overseas study exposes timing limits, complete results and Chinese locale on mobile', async ({page}, testInfo) => {
  await page.setViewportSize({width: 390, height: 844});
  await page.goto('research/overseas-leadlag/?lang=en-US');
  await expect(page.locator('h1')).toHaveText('Overseas signals and the A-share open');
  await expect(page.getByText('Zero historical retrieval vintages are verified.', {exact: false})).toBeVisible();
  await expect(page.locator('#forecasts table').first().locator('tbody tr')).toHaveCount(6);
  await page.locator('summary').filter({hasText: 'Delay every external'}).click();
  await expect(page.locator('#forecasts details').first().locator('tbody tr')).toHaveCount(6);
  await page.locator('figure img').scrollIntoViewIfNeeded();
  await expect.poll(() => page.locator('figure img').evaluate((image: HTMLImageElement) => image.naturalWidth)).toBeGreaterThan(0);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
  await page.evaluate(() => scrollTo(0, 0));
  await page.screenshot({path: testInfo.outputPath('overseas-mobile-en.png')});
  await page.locator('.nav-toggle').click();
  await page.locator('[data-locale-toggle]').click();
  await expect(page.locator('h1')).toHaveText('海外盘面对 A 股开盘的领先信息');
  await expect(page.locator('figure img')).toHaveAttribute('alt', /成本敏感性/);
  await page.evaluate(() => scrollTo(0, 0));
  await page.screenshot({path: testInfo.outputPath('overseas-mobile-zh.png')});
  await page.getByRole('link', {name: '阅读完整方法与来源'}).click();
  await expect(page.locator('[data-document-body]')).toHaveAttribute('data-document-locale', 'zh-CN');
  await expect(page.locator('[data-document-body]')).toContainText('没有补造历史抓取时间');
});
