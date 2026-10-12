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
  await expect(page.locator('#pilot-audit')).toContainText('65,673,625');
  await expect(page.locator('#pilot-results')).toContainText('8.48');
  await expect(page.locator('#pilot-results')).toContainText('64.41%');
  await expect(page.locator('#pilot-results svg')).toHaveCount(3);
  await page.reload();
  await expect(page.locator('h1')).toHaveText('A股交易成本与策略容量');
});

test('expanded evidence leads the page and translates diagnostic boundaries', async ({ page }) => {
  await page.goto('research/execution-costs/');
  const expanded = page.locator('#expanded-results');
  await expect(expanded.getByRole('heading').first()).toHaveText('Expanded snapshot evidence and strategy diagnostics');
  await expect(expanded.locator('#daily-evidence table').locator('tbody tr')).toHaveCount(20);
  await expect(expanded).toContainText('Order-flow association has not passed the dynamic replay gate');
  await expect(page.locator('.prior-evidence')).not.toHaveAttribute('open', '');
  await page.goto('research/execution-costs/?lang=zh-CN');
  await expect(page.locator('#expanded-results h2')).toHaveText('扩展盘口证据与策略诊断');
  await expect(page.getByRole('link', {name: '完整研究报告与复现记录 ↗'})).toHaveAttribute('href', /execution-cost-expansion-20261012\.zh-CN\.md$/);
  await expect(page.locator('#strategy-diagnostic')).toContainText('这些结果不能证明真实容量或净超额收益');
  await expect(page.locator('#strategy-evidence table').first().locator('tbody tr')).toHaveCount(18);
  await expect(page.locator('[data-execution-chart="daily"] a[download]')).toHaveAttribute('href', /expanded-daily\.zh\.svg$/);
  await page.setViewportSize({ width: 320, height: 700 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.locator('#strategy-diagnostic details').last().locator('summary').click();
  await expect(page.locator('#strategy-diagnostic details').last()).toContainText('线性成本比例');
  await expect(page.locator('#strategy-diagnostic details').last()).toContainText('复利成本比例');
  await page.reload();
  await expect(page.locator('#expanded-results h2')).toHaveText('扩展盘口证据与策略诊断');
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
 await staticPage.goto('http://127.0.0.1:4321/quant-market-research/research/execution-costs/');
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
 await expect(workflow).toContainText('参与率约束模式暂不可用');
 await expect(workflow.locator('tbody tr')).toHaveCount(3);
 await expect(workflow.getByRole('link',{name:'回放协议与假设 ↗'})).toHaveAttribute('href',/execution-cost-replay\.zh-CN\.md$/);
});
