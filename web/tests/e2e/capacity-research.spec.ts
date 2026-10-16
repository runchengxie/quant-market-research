import { expect, test } from '@playwright/test';

for (const theme of ['dark','light']) {
 test(`liquidity panels, badges and accented statistics follow ${theme} theme`, async ({page}) => {
  await page.addInitScript(value => localStorage.setItem('market-research-theme', value), theme);
  await page.goto('research/liquidity/?lang=zh-CN');
  await page.locator('astro-island[component-export="LiquidityPage"]').scrollIntoViewIfNeeded();
  const panel=page.locator('.period-panel');
  await expect(panel).toBeVisible();
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

test('bucket and metric controls retain missing P90 and exclude contradictory counts', async ({page}) => {
 await page.goto('research/liquidity/?lang=en-US');
 await expect(page.locator('#market-profiles')).toBeVisible();
 await page.getByRole('combobox',{name:'Market-cap bucket (USD)',exact:true}).selectOption('1');
 await page.getByRole('combobox',{name:'Turnover statistic',exact:true}).selectOption('p90_usd');
 const table=page.locator('#market-profiles .panel table');
 await expect(table).toContainText('1,983,502');
 await expect(table).toContainText('Not reported');
 await expect(table).not.toContainText('A-share');
 await expect(page.locator('#liquidity-quality')).toContainText('5,321 / 5,461');
 await expect(page.locator('#liquidity-quality')).toContainText('125 / 177');
 await page.getByRole('button',{name:'2025 · Pending generation',exact:true}).click();
 await expect(page.locator('#market-profiles')).toContainText('Latest snapshots are not substituted');
 await expect(page.locator('#market-profiles table')).toHaveCount(0);
});

test('arithmetic controls recompute and reject invalid inputs', async ({page}) => {
 await page.goto('research/liquidity/?lang=en-US');
 await expect(page.locator('#order-budget output')).toHaveText('$25,000');
 await page.getByLabel('Execution days',{exact:true}).fill('10');
 await expect(page.locator('#order-budget output')).toHaveText('$50,000');
 await page.getByLabel('Participation rate (%)',{exact:true}).fill('0');
 await expect(page.locator('#order-budget output')).toContainText('Enter finite');
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
  await expect(page.locator('#market-profiles details table')).toContainText('511');
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
