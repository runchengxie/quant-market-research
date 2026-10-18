import { expect, test } from '@playwright/test';

for (const theme of ['dark','light']) {
 test(`liquidity panels, badges and accented statistics follow ${theme} theme`, async ({page}) => {
  await page.addInitScript(value => localStorage.setItem('market-research-theme', value), theme);
  await page.goto('research/liquidity/?lang=zh-CN');
  await page.locator('astro-island[component-export="LiquidityPage"]').scrollIntoViewIfNeeded();
  const panel=page.locator('.period-panel');
  await expect(panel).toBeVisible();
  const stability=page.locator('#liquidity-stability');
  await expect(stability).toBeVisible();
  await expect(stability).toContainText('P25–P75');
  const stabilityBackground=await stability.locator('.panel').evaluate(el=>getComputedStyle(el).backgroundColor);
  if(theme==='dark') expect(stabilityBackground).not.toBe('rgb(255, 255, 255)');
  const colors=await panel.evaluate(el=>{
   const s=getComputedStyle(el);
   const probe=document.createElement('span');probe.style.background='var(--surface)';document.body.append(probe);
   const surface=getComputedStyle(probe).backgroundColor;probe.remove();
   return {background:s.backgroundColor,surface};
  });
  expect(colors.background).toBe(colors.surface);
  const accent=page.locator('.stat.accent').first();
  if(await accent.count()) {
   const color=await accent.evaluate(el=>getComputedStyle(el).backgroundColor);
   expect(color).not.toBe('rgb(232, 217, 200)');
  }
  if(theme==='dark') {
   const badge=page.locator('.status-badge').first();
   expect(await badge.evaluate(el=>getComputedStyle(el).backgroundColor)).not.toBe('rgb(250, 244, 221)');
  }
 });
}

test('shared dates, real historical windows and distinct turnover measures remain explicit', async ({page}) => {
 await page.goto('research/liquidity/?lang=en-US');
 await expect(page.locator('#market-profiles')).toBeVisible();
 await expect(page.locator('#market-profiles .period-meta').first()).toContainText('2025-09-30');
 await page.getByRole('combobox',{name:'Market-cap bucket (USD)',exact:true}).selectOption('1');
 await page.getByRole('combobox',{name:'Turnover statistic',exact:true}).selectOption('p90_usd');
 const table=page.locator('#market-profiles .panel table');
 await expect(table).toContainText('1,987,948');
 await expect(table).toContainText('133,538');
 await expect(table).toContainText('790,350');
 await expect(table).toContainText('A-share');
 await expect(table).toContainText('No observations');
 await page.getByRole('combobox',{name:'Rolling turnover measure',exact:true}).selectOption('median20');
 await expect(table).not.toContainText('1,987,948');
 await page.getByRole('button',{name:'2025',exact:true}).click();
 await expect(page.locator('#market-profiles .period-meta').first()).toContainText('2025-01-06');
 await expect(page.locator('#market-profiles .period-meta').first()).toContainText('161');
 await expect(table.locator('tbody tr')).toHaveCount(4);
 await page.getByRole('button',{name:'2026 YTD',exact:true}).click();
 await expect(page.locator('#market-profiles')).toContainText('Markets without data: US');
 await expect(table.locator('tbody tr')).toHaveCount(3);
 await expect(page.locator('#liquidity-evidence')).toContainText('960');
 await expect(page.locator('#liquidity-quality')).toContainText('Historical PIT is not established', {ignoreCase:true});
});

test('ADV-based scenario uses the selected market group and rejects invalid inputs', async ({page}) => {
 await page.goto('research/liquidity/?lang=en-US');
 const row=page.locator('#order-budget table tbody tr').filter({hasText:'A-share'});
 await expect(row).toContainText('$');
 const initial=await row.innerText();
 await page.getByLabel('Execution days',{exact:true}).fill('10');
 await expect(row).not.toHaveText(initial);
 await page.getByLabel('Participation rate (%)',{exact:true}).fill('0');
 await expect(row).toContainText('Enter a participation rate');
});

test('coverage panel distinguishes daily overlap, A-share minute and sampled Level 2 evidence', async ({page})=>{
 await page.goto('research/liquidity/?lang=en-US');
 const panel=page.locator('#capacity-data-coverage');
 await expect(panel).toContainText('2020-01-06');
 await expect(panel).toContainText('2026-04-30');
 await expect(panel).toContainText('5,411,206');
 await expect(panel).toContainText('2,084');
 await expect(panel).toContainText('306,483');
 await expect(panel).toContainText('1,019');
 await page.getByRole('button',{name:'P90',exact:true}).click();
 await expect(panel.locator('.research-chart')).toBeVisible();
});

test('one directory entry and preserved old routes lead to the unified study', async ({page}) => {
 await page.goto('research/?lang=en-US');
 await expect(page.locator('.directory-grid a[href$="/research/liquidity/"]')).toHaveCount(1);
 await expect(page.locator('.directory-grid a[href$="/research/execution-costs/"]')).toHaveCount(0);
 await expect(page.locator('.directory-grid a[href$="/cross-market-liquidity/"]')).toHaveCount(0);
 await page.goto('research/microcap/cross-market-liquidity/?lang=zh-CN');
 await page.locator('#unified-entry a').click();
 await expect(page.locator('h1')).toHaveText('流动性、交易成本与策略容量');
 await expect(page.locator('#expanded-results')).toHaveCount(1);
 await expect(page.locator('#minute-execution')).toHaveCount(1);
 await expect(page.locator('#research-notes')).toHaveCount(1);
});

for(const width of [390,1280]) {
 test(`unified charts and table fit ${width}px and switch locale`,async({page})=>{
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  await page.setViewportSize({width,height:900});
  await page.goto('research/liquidity/?lang=en-US');
  await expect(page.locator('#market-profiles')).toBeVisible();
  await page.locator('#market-profiles details summary').click();
  await expect(page.locator('#market-profiles details table')).toContainText('Security-day observations');
  await expect(page.locator('h1')).toHaveCount(1);
  if(await page.locator('.nav-toggle').isVisible()) await page.locator('.nav-toggle').click();
  await page.getByRole('button',{name:'Switch to Chinese',exact:true}).click();
  await expect(page.locator('h1')).toHaveText('流动性、交易成本与策略容量');
  await expect(page.getByRole('combobox',{name:'市值区间（美元）',exact:true})).toBeVisible();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBeTruthy();
  expect(errors).toEqual([]);
 });
}

for(const route of ['research/microcap/','research/cashflow/']) {
 test(`accented summary cards follow the dark theme on ${route}`,async({page})=>{
  await page.addInitScript(()=>localStorage.setItem('market-research-theme','dark'));
  await page.goto(`${route}?lang=zh-CN`);
  await page.locator('#topic-content').scrollIntoViewIfNeeded();
  const card=page.locator('.stat.accent').first();
  await expect(card).toBeVisible();
  expect(await card.evaluate(el=>getComputedStyle(el).backgroundColor)).not.toBe('rgb(232, 217, 200)');
 });
}

test('default size bucket includes A-share and empty buckets retain universe context', async ({page})=>{
 await page.goto('research/liquidity/?lang=en-US');
 const bucket=page.getByRole('combobox',{name:'Market-cap bucket (USD)',exact:true});
 await expect(bucket).toHaveValue('2');
 const table=page.locator('#market-profiles .panel table');
 const a=table.locator('tbody tr').filter({hasText:'A-share'});
 await expect(a).toContainText('2,501');
 await expect(a).not.toContainText('No observations');
 await bucket.selectOption('0');
 await expect(page.locator('.empty-bucket-notice')).toContainText('4,949 stocks and 4,949 security-days');
 await expect(page.locator('.empty-bucket-notice')).toContainText('not missing market data');
 await page.getByRole('button',{name:'2020-2024',exact:true}).click();
 await expect(page.locator('.empty-bucket-notice')).toContainText('4,710,463 security-days');
});

test('relative quintiles preserve periods, show A-share and distinguish actual dollar sizes', async ({page})=>{
 await page.setViewportSize({width:390,height:900});
 await page.addInitScript(()=>localStorage.setItem('market-research-theme','dark'));
 await page.goto('research/liquidity/?lang=en-US');
 await page.getByRole('combobox',{name:'Size grouping',exact:true}).selectOption('relative');
 await expect(page.getByRole('combobox',{name:'Size rank within each market',exact:true})).toHaveValue('0');
 const table=page.locator('#market-profiles .panel table');
 await expect(table).toContainText('Observed market-cap range (USD)');
 await expect(table.locator('tbody tr').filter({hasText:'A-share'})).toContainText('990');
 await expect(table).not.toContainText('No observations');
 await expect(page.locator('#market-profiles')).toContainText('not the same dollar size');
 await page.getByRole('button',{name:'2026 YTD',exact:true}).click();
 await expect(table.locator('tbody tr')).toHaveCount(3);
 await expect(page.locator('#market-profiles')).toContainText('Markets without data: US');
 await page.getByRole('combobox',{name:'Size grouping',exact:true}).selectOption('absolute');
 await expect(page.getByRole('combobox',{name:'Market-cap bucket (USD)',exact:true})).toHaveValue('2');
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBeTruthy();
});

test('relative source failure can retry while the absolute comparison remains usable',async({page})=>{
 await page.route('**/data/liquidity/relative-summary.json',route=>route.fulfill({status:503,body:'temporary failure'}));
 await page.goto('research/liquidity/?lang=en-US');
 await expect(page.getByRole('combobox',{name:'Market-cap bucket (USD)',exact:true})).toHaveValue('2');
 await page.getByRole('combobox',{name:'Size grouping',exact:true}).selectOption('relative');
 await expect(page.locator('#market-profiles')).toContainText('503');
 await page.unroute('**/data/liquidity/relative-summary.json');
 await page.locator('#market-profiles').getByRole('button',{name:/Retry/i}).click();
 await expect(page.getByRole('combobox',{name:'Size rank within each market',exact:true})).toBeVisible();
});


test('scope sensitivity separates BSE exclusions from lifecycle checks and constrains budgets',async({page})=>{
 await page.goto('research/liquidity/?lang=en-US');
 const evidence=page.locator('#liquidity-universe-sensitivity');
 await expect(evidence).toContainText('34,947');
 await expect(evidence).toContainText('500');
 await expect(evidence).toContainText('not an independent historical membership archive');
 await expect(page.locator('#liquidity-stability')).toContainText('2015');
 await expect(page.locator('#order-budget')).toContainText('P25–P75');
 await page.getByRole('button',{name:'2020-2024',exact:true}).click();
 await page.getByRole('combobox',{name:'Market-cap bucket (USD)',exact:true}).selectOption('1');
 await expect(page.locator('#order-budget table tbody tr').filter({hasText:'A-share'})).toContainText('Holdings exceed minimum daily group stock count');
});
