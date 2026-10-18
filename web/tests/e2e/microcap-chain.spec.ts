import { expect, test } from '@playwright/test';

test('account-chain navigation, locale changes, downloads and dark mobile preserve evidence states', async ({ page }) => {
 await page.goto('research/microcap/?lang=en-US');
 const live = page.locator('#microcap-chain [data-chain-live]');
 const nav = page.locator('a[href="#microcap-chain"]').first();
 await expect(nav).toContainText('1.0.7 snapshot');
 await nav.click();
 await expect(page).toHaveURL(/#microcap-chain$/);
 await expect(live.locator('[data-chain-block="primary"] tbody tr td')).toHaveText(['7', '7', '6', '1', '3']);
 await expect(live.locator('[data-chain-block="trace"] tbody tr td')).toHaveText(['6', '6', '63', '1']);
 await expect(live).toContainText('null, not zero');
 await expect(live.locator('[data-chain-block="target"] tbody tr td')).toHaveText(['2', '40', '46', '21', '2230', '1', '1', 'Withheld']);
 await expect(live).toContainText('no NAV is accepted');
 await expect(live).toContainText('cannot be transferred to minimum-45');
 const data = await (await page.request.get('data/microcap_chain_review.json')).json();
 await expect(live).toContainText(data.prospective.actual_review_utc);
 await expect(live.locator('[data-chain-block="prospective"] tbody tr td').last()).toHaveText('0');
 await live.locator('summary').first().click();
 await expect(live.locator('details').first()).toHaveAttribute('open', '');
 await page.evaluate(() => { document.documentElement.lang = 'zh-CN'; });
 await expect(live).toHaveAttribute('lang', 'zh-CN');
 await expect(live.locator('details').first()).toHaveAttribute('open', '');
 await expect(live).toContainText('不能填作零');
 await page.evaluate(() => { document.documentElement.lang = 'en-US'; });
 await expect(live).toHaveAttribute('lang', 'en-US');
 await page.getByRole('button', { name: 'Switch to Chinese' }).click();
 await expect(live).toHaveAttribute('lang', 'zh-CN');
 await expect(live).toContainText('不能据此判断底层历史数据不存在');
 for (const locale of ['en-US', 'zh-CN']) {
  const latest = await (await page.request.get(`downloads/microcap-research.${locale}.md`)).text();
  const fixed = await (await page.request.get(`downloads/archive/microcap-research.v1.0.8.${locale}.md`)).text();
  expect(latest).toBe(fixed);
  expect(latest).toContain(data.prospective.actual_review_utc);
  expect(latest).toContain(data.source_sha256.primary);
 }
 await page.evaluate(() => { document.documentElement.dataset.theme = 'dark'; });
 await page.setViewportSize({ width: 390, height: 844 });
 expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
 await expect(live.locator('td').first()).toHaveCSS('white-space', 'normal');
 await page.locator('#microcap-chain').screenshot({ path: '/tmp/microcap-chain-dark-mobile.png' });
});
