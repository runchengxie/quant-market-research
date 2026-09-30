import { expect, test } from '@playwright/test';

for (const route of [
  'research/factors/low-turnover/',
  'research/factors/pb-roe/',
  'research/microcap/',
  'research/cashflow/',
  'research/indices/',
  'research/liquidity/',
  'research/microcap/cross-market-liquidity/',
  'research/cashflow/recovery/',
  'research/',
  'data-sources/',
  'search/',
]) {
  test(`${route} keeps visible report text English in the default locale`, async ({ page }) => {
    await page.goto(route);
    await expect(page.locator('main h1')).toBeVisible();
    await page.waitForLoadState('networkidle');
    if (route.includes('low-turnover')) {
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
