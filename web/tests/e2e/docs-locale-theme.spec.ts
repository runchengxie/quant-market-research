import { expect, test } from '@playwright/test';

test('canonical documentation switches the full body and contents between languages', async ({ page }) => {
  await page.goto('docs/research/experiments/microcap-execution-diagnostic-20260928/?lang=zh-CN');
  if(await page.locator('#microcap-archive').count() && await page.locator('#microcap-archive').getAttribute('open')===null) await page.locator('#microcap-archive > summary').click();
  await expect(page.locator('.article-content h1')).toContainText('微盘组合公共执行模拟诊断');
  await expect(page.locator('.article-content')).toContainText('5% 成交参与率');
  await page.locator('.article-content').getByRole('link', {name:'English page',exact:true}).click();
  await expect(page.locator('.article-content h1')).toContainText('Microcap portfolio execution diagnostic');
  await page.getByRole('button', { name: 'Switch to Chinese' }).click();
  await expect(page.locator('.article-content h1')).toContainText('微盘组合公共执行模拟诊断');
  await page.getByRole('button', { name: '切换到英文' }).click();
  await expect(page.locator('.article-content h1')).toContainText('Microcap portfolio execution diagnostic');
  await page.goto('docs/research/factors/microcap/?lang=zh-CN');
  if(await page.locator('#microcap-archive').count() && await page.locator('#microcap-archive').getAttribute('open')===null) await page.locator('#microcap-archive > summary').click();
  await expect(page.locator('.article-toc')).toContainText('先看结论');
  await expect(page.locator('.article-content h1')).toContainText('微盘股');
});

test('dark documentation and hub use readable code and links', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('market-research-theme', 'dark'));
  await page.goto('docs/research/experiments/microcap-execution-diagnostic-20260928/?lang=zh-CN');
  if(await page.locator('#microcap-archive').count() && await page.locator('#microcap-archive').getAttribute('open')===null) await page.locator('#microcap-archive > summary').click();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  const code = page.locator('.article-content pre').first();
  await expect(code).toBeVisible();
  const bg = await code.evaluate(el => getComputedStyle(el).backgroundColor);
  expect(bg).not.toBe('rgb(255, 255, 255)');
  await page.goto('research/microcap/?lang=zh-CN');
  if(await page.locator('#microcap-archive').count() && await page.locator('#microcap-archive').getAttribute('open')===null) await page.locator('#microcap-archive > summary').click();
  const link = page.locator('#microcap-map a').first();
  expect(await link.evaluate(el => getComputedStyle(el).color)).not.toBe('rgb(0, 0, 238)');
  const selected = page.locator('#microcap-window-evidence button[aria-pressed="true"]');
  await expect(selected).toBeVisible();
  expect(await selected.evaluate(el => getComputedStyle(el).backgroundColor)).not.toBe('rgb(18, 103, 214)');
});

test('complete report is available as localized web content and downloadable Markdown', async ({ page }) => {
  await page.goto('research/microcap/?lang=zh-CN');
  if(await page.locator('#microcap-archive').count() && await page.locator('#microcap-archive').getAttribute('open')===null) await page.locator('#microcap-archive > summary').click();
  const download = page.locator('a[download="microcap-research.zh-CN.md"]');
  await expect(download).toBeVisible();
  const response = await page.request.get((await download.getAttribute('href'))!);
  expect(response.status()).toBe(200);
  const markdown = await response.text();
  expect(markdown).toContain('微盘组合公共执行模拟诊断');
  expect(markdown).toContain('换手定义');
  expect(markdown).toContain('退市');
  expect(markdown).not.toMatch(/\/home\/|\/Users\/|\/mnt\//);
  await page.getByRole('link', { name: '阅读研究历史与证据汇编', exact: true }).first().click();
  await expect(page.locator('.article-content')).toContainText('当前结论');
  await expect(page.locator('.article-content table')).not.toHaveCount(0);
  await expect(page.locator('.article-content svg')).toHaveCount(3);
  for (const chart of await page.locator('.article-content svg').all()) await expect(chart).toBeVisible();
  await page.setViewportSize({width:390,height:844});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});


test('system theme follows operating-system changes without reloading', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('market-research-theme', 'system'));
  await page.emulateMedia({ colorScheme: 'light' });
  await page.goto('research/microcap/');
  if(await page.locator('#microcap-archive').count() && await page.locator('#microcap-archive').getAttribute('open')===null) await page.locator('#microcap-archive > summary').click();
  await expect(page.locator('.theme-toggle')).toContainText('System');
  await page.emulateMedia({ colorScheme: 'dark' });
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
});
