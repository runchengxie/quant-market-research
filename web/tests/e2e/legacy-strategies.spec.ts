import { expect, test } from '@playwright/test';

for (const id of ['etf-rotation', 'hotsector']) {
  test(`${id} direct route shows reviewed aggregate results in both languages`, async ({ page }) => {
    await page.goto(`research/${id}/`);
    await expect(page.locator('main h1')).toBeVisible();
    await expect(page.locator('main')).toContainText('Historical diagnostic; not investment validation');
    await page.locator('details.results summary').click();
    await expect(page.locator('main table tbody tr')).toHaveCount(id === 'etf-rotation' ? 66 : 6);
    if (id === 'etf-rotation') await expect(page.locator('main')).toContainText('Interval lower bound');
    else {
      await expect(page.locator('main')).toContainText('Mean event uplift');
      await expect(page.locator('main')).toContainText('percentage points');
    }
    await page.getByRole('button', { name: 'Switch to Chinese' }).click();
    await expect(page.locator('main')).toContainText('历史诊断，尚非投资有效性验证');
    await expect(page.locator('main table tbody tr')).toHaveCount(id === 'etf-rotation' ? 66 : 6);
    if (id === 'etf-rotation') await expect(page.locator('main')).toContainText('区间下界');
    else {
      await expect(page.locator('main')).toContainText('事件平均增量');
      await expect(page.locator('main')).toContainText('百分点');
    }
    await page.reload();
    await expect(page.locator('main')).toContainText('这些诊断结果不能证明策略盈利');
  });
}
