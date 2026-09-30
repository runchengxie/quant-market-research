import { expect, test } from '@playwright/test';
test('search route restores query and returns factor results', async ({ page }) => {
  await page.goto('search/?q=quality');
  await expect(page.getByRole('searchbox')).toHaveValue('quality');
  await expect(page.getByRole('link', { name: /quality/i }).first()).toBeVisible();
  await page.getByRole('searchbox').fill('unmatched term');
  await page.getByRole('button', { name: 'Search', exact: true }).click();
  await expect(page.getByText('No matches found.')).toBeVisible();
});
