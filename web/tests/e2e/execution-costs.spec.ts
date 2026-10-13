import { expect, test } from '@playwright/test';
test('cost topic exposes scenario arithmetic and persists Chinese locale', async ({ page }) => {
  await page.goto('research/');
  await page.getByRole('link').filter({ hasText: 'A-share Trading Costs and Capacity' }).click();
  await page.waitForURL('**/research/execution-costs/');
  await expect(page.locator('h1')).toHaveText('A-share trading costs and capacity');
  await expect(page.locator('#baseline tbody tr').first()).toContainText('10.50%');
  await expect(page.locator('#baseline tbody tr').first()).toContainText('5.25%');
  await page.goto('research/execution-costs/?lang=zh-CN');
  await expect(page.locator('h1')).toHaveText('A股交易成本与策略容量');
  await expect(page.locator('.research-verdict')).toContainText('真实委托与动态冲击仍待校准');
  await expect(page.locator('#pilot-audit')).toHaveCount(0);
  await expect(page.locator('#pilot-results')).toHaveCount(0);
  await expect(page.locator('#baseline')).toBeVisible();
  await page.reload();
  await expect(page.locator('h1')).toHaveText('A股交易成本与策略容量');
});

test('expanded evidence leads the page and translates diagnostic boundaries', async ({ page }) => {
  await page.goto('research/execution-costs/');
  const expanded = page.locator('#expanded-results');
  await expect(expanded.getByRole('heading').first()).toHaveText('Expanded snapshot evidence and strategy diagnostics');
  await expect(expanded.locator('#daily-evidence table').locator('tbody tr')).toHaveCount(20);
  await expect(expanded).toContainText('Order-flow association has not passed the dynamic replay gate');
  await expect(page.locator('.prior-evidence')).toHaveCount(0);
  await page.goto('research/execution-costs/?lang=zh-CN');
  await expect(page.locator('#expanded-results h2')).toHaveText('按挂单试算，要多花多少钱');
  await expect(page.getByRole('link', {name: '完整研究报告与复现记录 ↗'})).toHaveAttribute('href', /execution-cost-expansion-20261012\.zh-CN\.md$/);
  await expect(page.locator('#strategy-diagnostic')).toContainText('不能证明真实容量或净超额收益');
  await expect(page.locator('#strategy-evidence table').first().locator('tbody tr')).toHaveCount(18);
  await expect(page.locator('[data-execution-chart="daily"] a[download]')).toHaveAttribute('href', /expanded-daily\.zh\.svg$/);
  await page.setViewportSize({ width: 320, height: 700 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await expect(page.locator('#baseline')).toBeVisible();
  await expect(page.locator('#evidence')).toContainText('静态基准');
  await expect(page.locator('#roadmap')).toBeVisible();
  await page.reload();
  await expect(page.locator('#expanded-results h2')).toHaveText('按挂单试算，要多花多少钱');
});


test('responsive interactive controls select reviewed values and preserve Chinese', async ({page})=>{
 await page.setViewportSize({width:320,height:700});
 await page.goto('research/execution-costs/?lang=zh-CN');
 const daily=page.locator('[data-execution-chart="daily"]');
 await daily.scrollIntoViewIfNeeded();
 await expect(daily).toHaveAttribute('data-chart-ready','true');
 await daily.locator('[data-chart-control="side"]').selectOption('sell');
 await daily.locator('[data-chart-control="notional"]').selectOption('10000000');
 await daily.locator('[data-chart-control="metric"]').selectOption('coverage');
 await expect(daily.locator('select').first()).toHaveAttribute('aria-label','订单方向');
 await expect(daily.locator('tbody tr')).toHaveCount(10);
 await expect(daily.locator('tbody tr').first()).toContainText('2021-01-04');
 const groups=page.locator('[data-execution-chart="groups"]');
 await groups.locator('[data-chart-control="group"]').selectOption('by_volatility_group');
 await expect(groups.locator('tbody')).toContainText('不可用');
 const strategy=page.locator('[data-execution-chart="strategy"]');
 await strategy.locator('[data-chart-control="capital"]').selectOption('100000000');
 await expect(strategy.locator('tbody tr')).toHaveCount(4);
 await expect(strategy.locator('tbody')).toContainText('扩展样本');
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 await page.reload();
 await expect(daily.locator('select').first()).toHaveAttribute('aria-label','订单方向');
 await expect(daily.locator('[data-chart-control="side"]')).toHaveValue('sell');
 await expect(daily.locator('[data-chart-control="notional"]')).toHaveValue('10000000');
});

test('English charts have no visible Han text and no-JS tables retain evidence',async({page,browser})=>{
 await page.goto('research/execution-costs/?lang=en-US');
 await page.locator('[data-execution-chart="groups"]').scrollIntoViewIfNeeded();
 await expect(page.locator('[data-execution-chart="groups"]')).toHaveAttribute('data-chart-ready','true');
 const visible=await page.locator('[data-execution-chart]').evaluateAll(nodes=>nodes.map(n=> (n as HTMLElement).innerText).join(' '));
 expect(visible).not.toMatch(/[\p{Script=Han}]/u);
 const context=await browser.newContext({javaScriptEnabled:false});
 const staticPage=await context.newPage();
 await staticPage.goto(page.url(), {waitUntil:'domcontentloaded'});
 await expect(staticPage.locator('[data-execution-chart="daily"] tbody tr')).toHaveCount(10);
 await expect(staticPage.locator('[data-execution-chart="daily"] tbody tr').first()).toContainText('9.18');
 await staticPage.locator('#daily-evidence summary').click();
 await expect(staticPage.locator('#daily-evidence table tbody tr')).toHaveCount(20);
 await expect(staticPage.locator('#daily-evidence')).toHaveAttribute('open','');
 await context.close();
});

test('execution workflow separates blocked replay and synthetic entry from actual calibration',async({page})=>{
 await page.goto('research/execution-costs/?lang=zh-CN');
 const workflow=page.locator('#calibration-workflow');
 await expect(workflow).toContainText('真实订单入口已实现；实盘校准仍待完成');
 await workflow.locator('summary').click();
 await expect(workflow).toContainText('还不能按成交量比例限制下单');
 await expect(workflow.locator('tbody tr')).toHaveCount(3);
 await expect(workflow.locator('tbody tr').last()).toContainText('7 / 12');
 await expect(workflow).toContainText('旧版本混入其他日期盘口');
 await expect(workflow.getByRole('link',{name:'回放协议与假设 ↗'})).toHaveAttribute('href',/execution-cost-replay\.zh-CN\.md$/);
});

test('data fitness preserves missing benchmarks and explains flat costs',async({page})=>{
 await page.goto('research/execution-costs/?lang=zh-CN');
 const fitness=page.locator('#data-fitness');
 await expect(fitness).toContainText('这些数字核查到哪一步了');
 await expect(fitness.locator('table').first().locator('tbody tr')).toHaveCount(2);
 await expect(fitness.locator('table').first()).toContainText('960');
 await fitness.locator('summary').last().click();
 await expect(fitness).toContainText('43');
 await expect(fitness).toContainText('120%');
 await expect(fitness).toContainText('不是实际净值损失');
 await page.setViewportSize({width:320,height:700});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});


test('execution report keeps detailed values available without opening them by default',async({page})=>{
 await page.goto('research/execution-costs/?lang=zh-CN');
 await expect(page.locator('.research-verdict .reading-lead')).toContainText('约90元');
 const values=page.locator('[data-execution-chart="daily"] .selected-values');
 await expect(values).not.toHaveAttribute('open','');
 await values.locator('summary').click();
 await expect(values.locator('tbody tr')).toHaveCount(10);
});


test('minute study preserves independent windows, boundaries and mobile locale', async ({page,browser})=>{
 await page.goto('research/execution-costs/?lang=en-US');
 const section=page.locator('#minute-execution');
 await expect(section).toHaveAttribute('data-minute-schema','execution-minute-public.v1');
 await expect(section).toContainText('40 main-board securities');
 await expect(section).toContainText('21 unresolved');
 await expect(section).toContainText('not causal own-order impact');
 await expect(section).toContainText('weighted by each order’s target notional');
 expect(await section.innerText()).not.toMatch(/[\p{Script=Han}]/u);
 if(await section.getAttribute('data-minute-published')==='true'){
  await expect(section.locator('[data-minute-window]')).toHaveCount(2);
  await expect(section.locator('[data-minute-window="2024h2"]')).toContainText('2024-07');
  await expect(section.locator('[data-minute-window="2025"]')).toContainText('2025-01');
  for(const id of ['2024h2','2025']){
   const window=section.locator(`[data-minute-window="${id}"]`);
   await expect(window.locator('table').nth(1).locator('tbody tr')).toHaveCount(9);
   await expect(window.locator('.minute-staleness')).toBeVisible();
  }
 }
 const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:320,height:700}});
 const staticPage=await context.newPage();
 await staticPage.goto(page.url(), {waitUntil:'domcontentloaded'});
 await expect(staticPage.locator('#minute-execution [data-minute-window]')).toHaveCount(2);
 await expect(staticPage.locator('#minute-execution [data-minute-window="2024h2"] table').nth(1).locator('tbody tr')).toHaveCount(9);
 expect(await staticPage.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 await context.close();
 await page.goto('research/execution-costs/?lang=zh-CN');
 await expect(section).toContainText('40只主板股票');
 await expect(section).toContainText('不能证明冲击是主要损耗');
 await page.setViewportSize({width:320,height:700});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});
