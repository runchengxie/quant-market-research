import { expect, test } from '@playwright/test';

for (const route of [
  '',
  'research/recovery.html',
  '404.html',
  'research/factors/low-turnover/',
  'research/factors/pb-roe/',
  'research/style-factors-18y/',
  'research/microcap/',
  'research/cashflow/',
  'research/indices/',
  'research/liquidity/',
  'research/microcap/cross-market-liquidity/',
  'research/cashflow/recovery/',
  'research/',
  'docs/',
  'docs/research-closeout-status/',
  'docs/research/factors/low-turnover/',
  'docs/research/factors/pb-roe/',
  'docs/research/factors/microcap/',
  'docs/research/factors/smallcap-turnover-history/',
  'docs/research/factors/barra-factor-dictionary/',
  'docs/research/factors/barra-source-inventory/',
  'docs/research/experiments/microcap-execution-diagnostic-20260928/',
  'data-sources/',
  'search/',
]) {
  test(`${route} keeps visible report text English in the default locale`, async ({ page }) => {
    await page.goto(route);
    await expect(page.locator('main h1')).toBeVisible();
    await page.waitForLoadState('networkidle');
    if (route === 'research/factors/low-turnover/') {
      await expect(page.getByRole('region', { name: 'Low-turnover execution validation' })).toBeVisible();
    }
    const hanText = await page.locator('body').evaluate((body) => {
      const copy = body.cloneNode(true) as HTMLElement;
      copy.querySelectorAll('script, style, .locale-toggle').forEach((node) => node.remove());
      const walker = document.createTreeWalker(copy, NodeFilter.SHOW_TEXT);
      const fragments: string[] = [];
      while (walker.nextNode()) {
        const value = walker.currentNode.textContent?.trim() ?? '';
        if (/[\u4e00-\u9fff]/.test(value)) fragments.push(value.slice(0, 260));
      }
      return { count: fragments.join('').match(/[\u4e00-\u9fff]/g)?.length ?? 0, fragments: fragments.slice(0, 100) };
    });
    expect(hanText.count, `default English page ${route} contains visible Chinese: ${JSON.stringify(hanText.fragments)}`).toBe(0);
  });
}

test('style-factor language switch preserves the selected factor and its metrics', async ({ page }) => {
  await page.goto('research/style-factors-18y/?factor=quality');
  const metrics = page.locator('.factor-stats');
  await expect(metrics).toBeVisible();
  const englishValues = await metrics.locator('.stat strong').allInnerTexts();
  await page.getByRole('button', { name: 'Switch to Chinese' }).click();
  await expect(page.locator('html')).toHaveAttribute('lang', 'zh-CN');
  await expect(page.locator('main h1')).toHaveText('18 年 A 股风格因子研究');
  await expect(page.locator('button[data-factor="quality"]')).toHaveText('复合质量');
  await expect(metrics.locator('.stat strong')).toHaveText(englishValues);
});

test('recovery reports localize source labels and expanded methodology in English', async ({ page }) => {
  await page.goto('research/cashflow/recovery/');
  await page.locator('astro-island[component-export="CashflowPage"]').scrollIntoViewIfNeeded();
  const recovery = page.getByRole('region', { name: 'Recovery and holding-period risk' });
  await expect(recovery).toContainText('CSI 800 Cash Flow');
  await recovery.getByText('Method and reading notes', { exact: true }).click();
  await expect(recovery.getByText(
    'The gain needed to recover is the prior high divided by the current level, minus one. For example, a 50% loss requires a 100% gain to break even.',
    { exact: true },
  )).toBeVisible();

  await page.goto('research/microcap/#microcap-recovery');
  await page.locator('astro-island[component-export="MicrocapPage"]').scrollIntoViewIfNeeded();
  const microcapRecovery = page.getByRole('region', { name: 'Recovery and holding-period risk' });
  await expect(microcapRecovery).toContainText('Tonghuashun Micro-cap');
  await page.getByRole('button', { name: 'Monthly', exact: true }).click();
  await page.getByRole('button', { name: 'N = 1', exact: true }).click();
  await expect(page.getByText('N = 1 · cleaned basis')).toBeVisible();
  const visibleHanCount = await page.locator('body').evaluate((body) => {
    const copy = body.cloneNode(true) as HTMLElement;
    copy.querySelectorAll('script, style, .locale-toggle').forEach((node) => node.remove());
    const walker = document.createTreeWalker(copy, NodeFilter.SHOW_TEXT);
    const fragments: string[] = [...copy.querySelectorAll('[aria-label], [title], [placeholder], img[alt]')]
      .flatMap((node) => ['aria-label', 'title', 'placeholder', 'alt'].map((name) => node.getAttribute(name) ?? ''));
    while (walker.nextNode()) {
      const value = walker.currentNode.textContent?.trim() ?? '';
      if (/[\u4e00-\u9fff]/.test(value)) fragments.push(value.slice(0, 200));
    }
    return fragments.filter((fragment) => /[\u4e00-\u9fff]/.test(fragment));
  });
  expect(visibleHanCount, `Visible Chinese text remains: ${visibleHanCount.slice(0, 50).join(' | ')}`).toEqual([]);

  const recoveryMetrics = await microcapRecovery.locator('.recovery-stats strong').allInnerTexts();
  const englishMetricFacts = recoveryMetrics.map((value) => value.match(/[\d.]+%?/g) ?? []);
  await page.getByRole('button', { name: 'Switch to Chinese' }).click();
  await expect(page.locator('html')).toHaveAttribute('lang', 'zh-CN');
  await expect(page.getByRole('heading', { name: '自行计算的结果与官方指数有多接近？' })).toBeVisible();
  const chineseRecovery = page.locator('.recovery-section');
  await expect(chineseRecovery).toContainText('回本与持有期风险');
  const chineseMetricFacts = (await chineseRecovery.locator('.recovery-stats strong').allInnerTexts()).map((value) => value.match(/[\d.]+%?/g) ?? []);
  expect(chineseMetricFacts).toEqual(englishMetricFacts);
  await page.getByRole('button', { name: '切换到英文' }).click();
  await expect(page.locator('html')).toHaveAttribute('lang', 'en-US');
  await expect(page.locator('.replication-section h2')).toHaveText('How closely do local reconstructions track official indices?');
});
