import { expect, test } from '@playwright/test';
const route = 'research/style-theme-rotation/';

test('directory exposes one combined topic and both legacy links preserve language and study anchors', async ({ page }) => {
  await page.goto('research/');
  await expect(page.locator('.research-card').filter({ hasText: 'Style and Theme Rotation' })).toHaveCount(1);
  await expect(page.locator('.research-card[href$="/research/hotsector/"]')).toHaveCount(0);
  for (const study of ['etf-rotation', 'hotsector']) {
    await page.goto(`research/${study}/?lang=zh-CN`);
    await expect(page).toHaveURL(new RegExp(`style-theme-rotation/\\?lang=zh-CN#${study}`));
    await expect(page.locator('h1')).toContainText('风格与主题轮动');
    await expect(page.locator(`#${study}`)).toContainText('历史诊断');
  }
  await page.goto('research/etf-rotation/?lang=en-US#etf-cost-chart-title');
  await expect(page).toHaveURL(/style-theme-rotation\/\?lang=en-US#etf-cost-chart-title/);
});

test('experiment filters and weekly measures change real evidence tables', async ({ page }) => {
  await page.goto(route);
  await page.getByLabel('Research branch', { exact: true }).selectOption('bridge');
  await expect(page.locator('#experiments article')).toHaveCount(1);
  await expect(page.locator('#experiments')).toContainText('no published performance result');
  const weekly = page.locator('#weekly');
  await expect(weekly.locator('tbody tr')).toHaveCount(9);
  await weekly.getByRole('button', { name: 'Maximum drawdown' }).click();
  await expect(weekly.locator('tbody tr').first()).toContainText('-8.45');
  await weekly.getByRole('button', { name: 'Maximum drawdown' }).click();
  await expect(weekly.locator('tbody tr').first()).toContainText('-22.86');
  await weekly.getByLabel('Search table contents').fill('HRP');
  await expect(weekly.locator('tbody tr')).toHaveCount(3);
  await page.getByRole('region', { name: 'Compare one experiment family' }).getByLabel('Experiment group', { exact: true }).selectOption('holdover');
  await expect(weekly.locator('tbody tr')).toHaveCount(3);
  await expect(weekly).toContainText('595');
  await expect(weekly).not.toContainText('64.22%');
  await page.getByLabel('Chart measure', { exact: true }).selectOption('sharpe');
  await expect(weekly.getByRole('img')).toHaveAttribute('aria-label', /0.480/);
  await expect(weekly.getByRole('img')).not.toHaveAttribute('aria-label', /0.480%/);
  await page.getByRole('region', { name: 'Compare one experiment family' }).getByLabel('Experiment group', { exact: true }).selectOption('pool');
  await expect(weekly.locator('tbody tr')).toHaveCount(8);
  await expect(weekly).toContainText('1.122');
  await page.getByRole('region', { name: 'Compare one experiment family' }).getByLabel('Experiment group', { exact: true }).selectOption('score');
  await expect(weekly.locator('tbody tr')).toHaveCount(4);
  await expect(weekly).toContainText('Ridge challenger A');
});

test('Chinese persists and all evidence scopes and chart units use the chosen language', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(`${route}?lang=zh-CN`);
  await expect(page.getByLabel('实验分组', { exact: true })).toBeVisible();
  await page.getByLabel('实验分组', { exact: true }).selectOption('pool');
  await expect(page.locator('#weekly')).toContainText('逐期相关性去重');
  await expect(page.locator('#etf-rotation')).toContainText('基准为起始等权');
  await expect(page.locator('#etf-rotation')).not.toContainText('Initially equal-weight');
  await expect(page.locator('#hotsector')).toContainText('个百分点');
  await expect(page.locator('#hotsector')).not.toContainText(' pp');
  await expect(page.locator('#hotsector')).not.toContainText(' bps');
  await page.reload();
  await expect(page.locator('h1')).toContainText('风格与主题轮动');
  await page.getByRole('button', { name: '切换到英文' }).click();
  await expect(page.getByRole('region', { name: 'Compare one experiment family' }).getByLabel('Experiment group', { exact: true })).toBeVisible();
  await expect(page.locator('main')).not.toContainText('历史诊断');
  await expect(page.locator('#hotspot-sensitivity-title')).toBeVisible();
  expect(errors).toEqual([]);
});

test('mobile topic navigation and interactive tables stay within the viewport', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`${route}?lang=zh-CN`);
  await expect(page.locator('h1')).toBeVisible();
  await page.locator('.rotation-nav').getByRole('link', { name: '周频 ETF 实验' }).click();
  await expect(page.getByLabel('实验分组', { exact: true })).toBeVisible();
  await page.getByLabel('实验分组', { exact: true }).selectOption('holdover');
  await expect(page.locator('#weekly tbody tr')).toHaveCount(3);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)).toBe(true);
});

test('without JavaScript, reviewed summaries and all weekly values remain readable', async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto('http://127.0.0.1:' + (process.env.PORT ?? '4321') + '/quant-market-research/' + route);
  await expect(page.locator('#weekly tbody tr')).toHaveCount(24);
  await expect(page.locator('#weekly')).toContainText('6.70%');
  await expect(page.locator('#experiments article')).toHaveCount(5);
  await page.locator('#etf-rotation details.results summary').click();
  await expect(page.locator('#etf-rotation details.results tbody tr')).toHaveCount(66);
  await context.close();
});
