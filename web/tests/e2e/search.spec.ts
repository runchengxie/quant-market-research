import { expect, test } from '@playwright/test';
test('search route restores query and returns factor results', async ({ page }) => {
  await page.goto('search/?q=quality');
  await expect(page.getByRole('searchbox')).toHaveValue('quality');
  await expect(page.getByRole('link', { name: /quality/i }).first()).toBeVisible();
  await page.getByRole('searchbox').fill('unmatched term');
  await page.getByRole('button', { name: 'Search', exact: true }).click();
  await expect(page.getByText('No matches found.')).toBeVisible();
});


test('method search matches text beyond character 200 and opens the complete report', async ({ page }) => {
  await page.goto('search/?q=quarantined');
  const result = page.getByRole('link', { name: 'Financial statement template coverage diagnosis', exact: true });
  await expect(result).toBeVisible();
  await expect(page.getByText(/first 1,200 characters/)).toBeVisible();
  await result.click();
  await expect(page.locator('main')).toContainText('The provider repair was merged before this consumer diagnosis');
});
