import { expect, test } from '@playwright/test';

for (const id of ['etf-rotation', 'hotsector']) {
  test(`${id} direct route preserves its evidence state when switching language`, async ({ page }) => {
    await page.goto(`research/${id}/`);
    await expect(page.locator('main h1')).toBeVisible();
    await expect(page.locator('main')).toContainText('No real-data comparative return evidence');
    await page.getByRole('button', { name: 'Switch to Chinese' }).click();
    await expect(page.locator('main')).toContainText('尚未纳入真实数据的收益对照证据');
    await page.reload();
    await expect(page.locator('main')).toContainText('缺少收益数据不代表收益为零');
  });
}
