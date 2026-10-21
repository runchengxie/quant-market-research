import { expect, test } from '@playwright/test';

test('one heading and a compact shared navigation', async ({ page }) => {
  for (const route of ['./', 'research/', 'data-sources/', 'research/style-factors-18y/', '404.html']) {
    await page.goto(route);
    await expect(page.locator('main h1')).toHaveCount(1);
    await expect(page.locator('header h1')).toHaveCount(0);
    await expect(page.getByRole('navigation', { name: 'Primary navigation' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Methods & dictionary', exact: true })).toHaveAttribute('href', /\/docs\/$/);
  }
});

test('mobile navigation can be closed with Escape', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('./');
  const toggle = page.locator('.nav-toggle');
  await toggle.click();
  await expect(toggle).toHaveAttribute('aria-expanded', 'true');
  await page.keyboard.press('Escape');
  await expect(toggle).toHaveAttribute('aria-expanded', 'false');
  await expect(toggle).toBeFocused();
});

test('research topics switch between English and Chinese shell copy', async ({ page }) => {
  await page.goto('research/cashflow/');
  await expect(page.locator('main h1')).toHaveText('Cash-flow index research');
  await page.getByRole('button', { name: 'Switch to Chinese' }).click();
  await expect(page).toHaveURL(/research\/cashflow\/\?lang=zh-CN$/);
  await expect(page.locator('html')).toHaveAttribute('lang', 'zh-CN');
  await expect(page.locator('main h1')).toHaveText('现金流指数研究');
  await page.getByRole('button', { name: '切换到英文' }).click();
  await expect(page).toHaveURL(/research\/cashflow\/\?lang=en-US$/);
  await expect(page.locator('html')).toHaveAttribute('lang', 'en-US');
  await expect(page.locator('main h1')).toHaveText('Cash-flow index research');
});

test('research card category labels follow the selected locale', async ({ page }) => {
  await page.goto('research/?lang=en-US');
  const labels = page.locator('.research-card .section-kicker');
  await expect(labels).toHaveText([
    'Style research', 'Overseas lead-lag research', 'Style and theme rotation',
    'Cash-flow index research', 'Micro-cap research', 'Micro-cap research',
    'Index research', 'Style research', 'Style research', 'Liquidity, costs and capacity', 'Low-turnover research',
  ]);

  await page.getByRole('button', { name: 'Switch to Chinese' }).click();
  await expect(page.locator('html')).toHaveAttribute('lang', 'zh-CN');
  await expect(labels).toHaveText([
    '风格研究', '海外领先指标研究', '风格与主题轮动',
    '现金流指数研究', '微盘研究', '微盘研究', '指数研究',
    '风格研究', '风格研究', '流动性、成本与容量', '低换手研究',
  ]);
});

test('a shared locale URL overrides a conflicting saved preference', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('quant-market-research-locale', 'en-US'));
  await page.goto('research/cashflow/?lang=zh-CN');
  await expect(page.locator('html')).toHaveAttribute('lang', 'zh-CN');
  await expect(page.locator('main h1')).toHaveText('现金流指数研究');
});

test('an unsupported URL locale falls back to the saved supported locale', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('quant-market-research-locale', 'zh-CN'));
  await page.goto('research/cashflow/?lang=fr-FR');
  await expect(page.locator('html')).toHaveAttribute('lang', 'zh-CN');
  await expect(page.locator('main h1')).toHaveText('现金流指数研究');
});

test('unsupported URL and saved locales fall back to English', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('quant-market-research-locale', 'fr-FR'));
  await page.goto('research/cashflow/?lang=fr-FR');
  await expect(page.locator('html')).toHaveAttribute('lang', 'en-US');
  await expect(page.locator('main h1')).toHaveText('Cash-flow index research');
  await expect(page.getByRole('button', { name: 'Switch to Chinese' })).toBeVisible();
});

test('shareable English URLs keep research and methods cards in English', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('quant-market-research-locale', 'zh-CN'));

  await page.goto('research/?lang=en-US');
  await expect(page.locator('html')).toHaveAttribute('lang', 'en-US');
  await expect(page.locator('main h1')).toHaveText('Explore data and charts by research question');
  await expect(page.getByRole('heading', { name: 'Cash-flow index research' })).toBeVisible();
  await expect(page.getByText('View topic →').first()).toBeVisible();

  await page.goto('docs/?lang=en-US');
  await expect(page.locator('html')).toHaveAttribute('lang', 'en-US');
  await expect(page.locator('main h1')).toHaveText('Charts show what happened; documentation explains how to read them');
  await expect(page.getByRole('heading', { name: 'Methods and dictionary' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Low-turnover Method' })).toBeVisible();
});
