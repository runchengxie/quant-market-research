import { expect, test } from '@playwright/test';
test('cost topic exposes scenario arithmetic and persists Chinese locale', async ({ page }) => {
  await page.goto('research/');
  await page.getByRole('link').filter({ hasText: 'A-share Trading Costs and Capacity' }).click();
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
