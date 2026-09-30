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
  const visibleHanCount = await page.locator('.recovery-section, .replication-section').evaluateAll((sections) => {
    return sections.map((section) => section.textContent ?? '').join('').match(/[\u4e00-\u9fff]/g)?.length ?? 0;
  });
  expect(visibleHanCount).toBe(0);
});
