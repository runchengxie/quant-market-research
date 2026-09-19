import { expect, test } from '@playwright/test';

test('selected factor survives methodology round trip and history', async ({ page }) => {
  await page.goto('research/style-factors-18y/?factor=quality');
  await page.getByRole('link', { name: '阅读完整因子定义', exact: true }).click();
  await expect(page).toHaveURL(/barra-factor-dictionary\/\?factor=quality/);
  await page.getByRole('link', { name: '回到因子图表', exact: true }).click();
  await expect(page.locator('button[data-factor="quality"]')).toHaveAttribute('aria-pressed', 'true');
  await page.goBack();
  await expect(page).toHaveURL(/barra-factor-dictionary\/\?factor=quality/);
  await page.goForward();
  await expect(page.locator('button[data-factor="quality"]')).toHaveAttribute('aria-pressed', 'true');
});
