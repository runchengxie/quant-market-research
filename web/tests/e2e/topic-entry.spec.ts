import { test, expect } from '@playwright/test';
test('home and topic URLs expose one complete research entry', async ({ page }) => {
  for (const route of ['./?lang=en-US', 'research/?lang=en-US']) {
    await page.goto(route);
    const nav = page.getByRole('navigation', { name: 'Primary navigation' });
    await expect(nav.getByRole('link', { name: 'Research overview', exact: true })).toHaveCount(0);
    await expect(nav.getByRole('link', { name: 'Research topics', exact: true })).toHaveClass(/active/);
    await expect(page.locator('[data-research-id]')).toHaveCount(9);
    await page.locator('[data-research-id]').first().locator('summary').click();
    await expect(page.locator('[data-research-id]').first().locator('details a').first()).toBeVisible();
    await expect(page).toHaveTitle(/Research topics/);
  }
});
