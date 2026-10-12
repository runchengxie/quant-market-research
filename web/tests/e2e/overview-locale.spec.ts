import { expect, test } from '@playwright/test';

test('overview translates all study cards and puts the reading note after the library', async ({ page }) => {
  await page.goto('?lang=zh-CN');
  await expect(page.locator('.featured-study h2')).toHaveText('18 年 A 股风格因子动态：收益、稳定性与市场阶段');
  await expect(page.locator('.library-heading h2')).toHaveText('按关心的问题进入报告');
  const cards = page.locator('.overview-evidence-grid .evidence-card');
  await expect(cards).toHaveCount(5);
  await expect(cards.locator('h3')).toHaveText(['现金流', '小微盘', '长期风格', '低换手因子', 'A股交易成本与策略容量']);
  await expect(page.locator('.fine-print .section-kicker')).toHaveText('阅读提示');
  expect(await page.locator('.fine-print').evaluate(node => {
    const library = document.querySelector('.overview-evidence-grid')!;
    return Boolean(library.compareDocumentPosition(node) & Node.DOCUMENT_POSITION_FOLLOWING);
  })).toBe(true);
  await expect(page.locator('.freshness-status')).toHaveText('衍生汇总');
  await expect(page.locator('.freshness-source')).toContainText('已审核的公开研究快照');
  const chineseText = await page.locator('main').innerText();
  expect(chineseText).not.toMatch(/Featured study|Research library|Coverage|Reading note|calendar days|reviewed public research snapshots|derived/);
  await page.getByRole('button', { name: '切换到英文' }).click();
  await expect(page.locator('.featured-study h2')).toHaveText('18-year A-share style factors: returns, stability, and market regimes');
  await expect(cards.first().locator('h3')).toHaveText('Cash flow');
  await expect(page.locator('.featured-facts strong').nth(1)).toHaveText('19');
  await expect(cards.first().locator('dd').first()).toHaveText('2015-01-05 to 2026-09-04');
  await page.getByRole('button', { name: 'Switch to Chinese' }).click();
  await page.reload();
  await expect(cards.first().locator('h3')).toHaveText('现金流');
  await page.goto('');
  await expect(page.locator('.featured-study h2')).toHaveText('18 年 A 股风格因子动态：收益、稳定性与市场阶段');
});
