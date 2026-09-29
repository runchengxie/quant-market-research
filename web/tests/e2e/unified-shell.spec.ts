import { expect, test } from '@playwright/test';

test('one heading and a compact shared navigation', async ({ page }) => {
  for (const route of ['./', 'research/', 'data-sources/', 'research/style-factors-18y/', '404.html']) {
    await page.goto(route);
    await expect(page.locator('main h1')).toHaveCount(1);
    await expect(page.locator('header h1')).toHaveCount(0);
    await expect(page.getByRole('navigation', { name: 'Primary navigation' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Methods & dictionary', exact: true })).toHaveAttribute('href', /\/docs\/$/);
  }
});

test('mobile navigation can be closed with Escape', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('./');
  const toggle = page.locator('.nav-toggle');
  await toggle.click();
  await expect(toggle).toHaveAttribute('aria-expanded', 'true');
  await page.keyboard.press('Escape');
  await expect(toggle).toHaveAttribute('aria-expanded', 'false');
  await expect(toggle).toBeFocused();
});
