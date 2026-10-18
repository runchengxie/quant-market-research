import { expect, test } from '@playwright/test';

test('approved sell-policy replay leads the page and retains the historical rejection across locales', async ({ page }) => {
 await page.goto('research/microcap/?lang=en-US');
 await expect(page.locator('main > section.theme-heading')).toContainText('21-session constructed replay now passes');
 await expect(page.locator('main > section.theme-heading')).toContainText('Full-history strategy capacity remains uncertified');
 const status=page.locator('#microcap-current-status [data-status-live] [data-claim="MC-C03"]');
 await expect(status).toContainText('79 fills pass');
 await expect(status).toContainText('full-history capacity is not established');
 const nav=page.locator('.topic-nav a[href="#microcap-raw-sell"]');
 await expect(nav).toContainText('Sell-policy review');await nav.click();
 await expect(page).toHaveURL(/#microcap-raw-sell$/);
 const live=page.locator('#microcap-raw-sell [data-raw-sell-live]');
 await expect(live.locator('[data-raw-sell-block="gates"] tbody tr')).toHaveCount(4);
 await expect(live.locator('[data-raw-sell-block="gates"] tbody tr').nth(2)).toContainText('NAV withheld');
 await expect(live.locator('[data-raw-sell-block="gates"] tbody tr').nth(2)).toContainText('Passed for the reviewed slice');
 await expect(live.locator('[data-raw-sell-block="scope"] tbody tr td')).toHaveText(['21','2','40','46','2230','1','1','79','73','6']);
 await expect(live.locator('[data-raw-sell-block="errors"] tbody tr').first().locator('td')).toHaveText(['1.455e-10','1.000e-7']);
 await expect(page.locator('#microcap-chain h2')).toContainText('Version 1.0.7 snapshot');
 const data=await(await page.request.get('data/microcap_raw_sell_review.json')).json();
 const earlier=await(await page.request.get('data/microcap_chain_review.json')).json();
 expect(data.raw_share_strategy_ready).toBe(false);expect(data.new_prospective_observations).toBe(0);
 expect(data.source_sha256.prior_failed_receipt).toBe(earlier.source_sha256.slice);
 expect(earlier.target_slice.accepted_nav).toBe(false);
 await live.locator('summary').first().click();
 await expect(live).toContainText('sell_round_lot=None');await expect(live).toContainText('provider regression tests');
 await page.evaluate(()=>{document.documentElement.lang='zh-CN';});
 await expect(live).toHaveAttribute('lang','zh-CN');await expect(live.locator('details').first()).toHaveAttribute('open','');
 await page.evaluate(()=>{document.documentElement.lang='en-US';});
 await expect(live).toHaveAttribute('lang','en-US');
 await page.getByRole('button',{name:'Switch to Chinese'}).click();
 await expect(live).toContainText('完整历史策略仍未达到就绪标准');
 await expect(live).toContainText('拒绝明确声明为复权价格');
 await expect(live).toContainText('容量／权重账本路径也拒绝此规则');
 await expect(page.locator('#microcap-chain h2')).toContainText('1.0.7 版快照');
 for(const locale of ['en-US','zh-CN']){
  const latest=await(await page.request.get(`downloads/microcap-research.${locale}.md`)).text();
  const frozen=await(await page.request.get(`downloads/archive/microcap-research.v1.0.8.${locale}.md`)).text();
  expect(latest).toBe(frozen);expect(latest).toContain(data.source_sha256.account_manifest);
  expect(latest).toContain('1.455e-10');expect(latest).toContain('79');
 }
 await page.evaluate(()=>{document.documentElement.dataset.theme='dark';});
 await page.setViewportSize({width:390,height:844});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 await expect(live.locator('td').first()).toHaveCSS('white-space','normal');
 await page.locator('#microcap-raw-sell').screenshot({path:'/tmp/microcap-raw-sell-dark-mobile.png'});
});

test('online report exposes the same bounded pass before its historical evidence', async ({ page }) => {
 await page.goto('research/microcap/report/?lang=en-US');
 await expect(page.locator('main')).toContainText('21-session constructed replay now passes');
 await expect(page.locator('main')).toContainText('57 noncode inputs + 4 captured artifacts matched');
 await expect(page.locator('main')).toContainText('Version 1.0.7 snapshot');
 await expect(page.locator('main')).toContainText('1.455e-10');
});
