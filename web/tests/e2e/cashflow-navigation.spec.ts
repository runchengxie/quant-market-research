import { expect, test } from '@playwright/test';

const canonical = '/quant-market-research/research/cashflow/';

async function expectRecovery(page: import('@playwright/test').Page) {
  await expect(page.locator('#cashflow-recovery')).toHaveCount(1);
  await expect(page.getByRole('region', { name: 'Recovery and holding-period risk' })).toContainText('CSI 800 Cash Flow');
  await expect.poll(() => page.locator('#cashflow-recovery').evaluate(el => Math.abs(el.getBoundingClientRect().top - 24))).toBeLessThan(10);
}

test('static anchors and the old-route fallback work without JavaScript', async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto('http://127.0.0.1:' + (process.env.PORT ?? '4321') + canonical + 'recovery/');
  await expect(page).toHaveURL(new RegExp(canonical + '#cashflow-recovery$'));
  for (const id of ['cashflow-returns', 'cashflow-recovery', 'cashflow-replication']) {
    await expect(page.locator(`#${id}`)).toHaveCount(1);
    await expect(page.locator(`#${id}`)).toHaveAttribute('aria-labelledby', `${id}-title`);
  }
  await expect(page.locator('#cashflow-recovery')).toContainText('prior investment high');
  await context.close();
});

test('directory, search and overview expose one cashflow topic with independent index and microcap entries', async ({ page, request }) => {
  await page.goto('research/');
  await expect(page.locator('.research-card h2 a[href$="/research/cashflow/"]')).toHaveCount(1);
  await expect(page.locator('a[href*="/cashflow/recovery/"]')).toHaveCount(0);
  await expect(page.locator('.research-card h2 a[href$="/research/indices/"]')).toContainText('Long-run index and ETF performance');
  await expect(page.locator('.research-card h2 a[href$="/research/microcap/"]')).toHaveCount(1);
  await page.goto('./');
  await expect(page.locator('main a[href$="/research/cashflow/"]')).toHaveCount(1);
  await expect(page.locator('main a[href$="/research/indices/"]')).toHaveCount(1);
  const records = await (await request.get('search-index.json')).json();
  const list = Array.isArray(records) ? records : records.records;
  expect(list.filter((r: {id: string}) => r.id === 'cashflow')).toHaveLength(1);
  expect(list.some((r: {id: string}) => r.id === 'cashflow-recovery')).toBe(false);
});

for (const route of ['research/cashflow/recovery/', 'research/recovery.html', './#cashflow-recovery']) {
  test(`legacy ${route} reaches recovery and survives refresh`, async ({ page }) => {
    await page.goto(route);
    await expect(page).toHaveURL(`${canonical}#cashflow-recovery`);
    await expectRecovery(page);
    await page.reload();
    await expectRecovery(page);
  });
}

test('legacy query and existing anchors survive replacement without a history trap', async ({ page }) => {
  await page.goto('research/indices/');
  await page.goto('research/cashflow/recovery/?lang=en-US#cashflow-replication');
  await expect(page).toHaveURL(`${canonical}?lang=en-US#cashflow-replication`);
  await expect(page.getByRole('region', { name: 'Index replication progress' })).toContainText('How closely do local reconstructions track official indices?');
  await page.goBack();
  await expect(page).toHaveURL(/\/research\/indices\/$/);
  await page.goForward();
  await expect(page).toHaveURL(`${canonical}?lang=en-US#cashflow-replication`);
  await page.goto('research/cashflow/recovery/?lang=zh-CN');
  await expect(page).toHaveURL(`${canonical}?lang=zh-CN#cashflow-recovery`);
  await expect(page.locator('main h1')).toHaveText('现金流指数研究');
  await expect(page.locator('.topic-nav a')).toHaveText(['收益与分红口径', '回撤与回本', '指数复刻与可交易性', '数据与方法']);
});

test('topic anchors and cross references work with back/forward on a narrow screen', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('research/cashflow/');
  await page.locator('.topic-nav a[href="#cashflow-recovery"]').click();
  await expectRecovery(page);
  const tableScroll = page.locator('#cashflow-recovery .table-scroll').first();
  await expect.poll(() => tableScroll.evaluate(el => el.scrollWidth - el.clientWidth)).toBeGreaterThan(400);
  await tableScroll.focus();
  await page.keyboard.press('ArrowRight');
  await expect.poll(() => tableScroll.evaluate(el => el.scrollLeft)).toBeGreaterThan(0);
  await page.locator('.topic-nav a[href="#cashflow-replication"]').click();
  await expect(page).toHaveURL(`${canonical}#cashflow-replication`);
  await page.goBack();
  await expectRecovery(page);
  await page.goForward();
  await expect(page).toHaveURL(`${canonical}#cashflow-replication`);
  await expect(page.locator('body')).toHaveJSProperty('scrollWidth', 390);
  await page.locator('.related-topics a[href$="/research/indices/"]').click();
  await expect(page.locator('main h1')).toHaveText('Long-run index and ETF performance');
  await expect(page.locator('.replication-section, #cashflow-recovery')).toHaveCount(0);
  await page.locator('.related-topics a[href$="/research/microcap/"]').click();
  await expect(page.locator('main h1')).toHaveText('A-share micro-cap history');
  await page.locator('.related-topics a[href$="/research/cashflow/"]').click();
  await expect(page.locator('main h1')).toHaveText('Cash-flow index research');
});

test('recovery target remains usable when research data fails', async ({ page }) => {
  await page.route('**/data/research/recovery.json', route => route.fulfill({ status: 503, body: 'unavailable' }));
  await page.goto('research/cashflow/recovery/');
  await expect(page.locator('#cashflow-recovery')).toHaveCount(1);
  await expect(page.locator('#cashflow-recovery [role="alert"]')).toContainText('failed to load');
  await expect(page.locator('#cashflow-replication')).toBeAttached();
});

test('late charts preserve the deep-link position until the reader scrolls', async ({ page }) => {
  let release: () => void = () => {};
  const pending = new Promise<void>(resolve => { release = resolve; });
  await page.route('**/data/research/recovery.json', async route => { await pending; await route.continue(); });
  await page.goto('research/cashflow/#cashflow-replication');
  await expect(page.getByRole('region', { name: 'Index replication progress' })).toBeVisible();
  release();
  await expect(page.getByRole('region', { name: 'Recovery and holding-period risk' })).toContainText('CSI 800 Cash Flow');
  await expect.poll(() => page.locator('#cashflow-replication').evaluate(el => Math.abs(el.getBoundingClientRect().top - 24))).toBeLessThan(10);
  await page.mouse.wheel(0, -600);
  await expect.poll(() => page.locator('#cashflow-replication').evaluate(el => el.getBoundingClientRect().top)).toBeGreaterThan(100);
});

for (const locale of ['en-US', 'zh-CN']) {
  test(`cashflow hydration keeps ${locale} copy aligned without runtime errors`, async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(`research/cashflow/recovery/?lang=${locale}`);
    await expect(page.locator('.recovery-stats')).toBeAttached();
    await page.waitForLoadState('networkidle');
    await expect(page.locator('#cashflow-recovery-title')).toHaveText(locale === 'zh-CN' ? '回撤与回本' : 'Drawdowns and recovery');
    expect(errors).toEqual([]);
  });
}
