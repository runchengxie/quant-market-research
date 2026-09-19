import { expect, test } from '@playwright/test';
test('search route restores query and returns factor results', async ({ page }) => {
  await page.goto('search/?q=quality');
  await expect(page.getByRole('searchbox')).toHaveValue('quality');
  await expect(page.getByRole('link', { name: /复合质量/ }).first()).toBeVisible();
  await page.getByRole('searchbox').fill('不存在的指标');
  await page.getByRole('button', { name: '搜索' }).click();
  await expect(page.getByText('没有匹配内容。')).toBeVisible();
});
