import { expect, test } from '@playwright/test';

const routes = ['./', 'research/style-factors-18y/', 'research/factors/low-turnover/', 'research/microcap/', 'docs/research/factors/barra-factor-dictionary/'];
for (const width of [320, 390, 768, 1280, 1440]) {
  test(`unified layout at ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    for (const route of routes) {
      const errors: string[] = []; page.on('pageerror', (error) => errors.push(error.message));
      await page.goto(route);
      await expect(page.locator('main h1')).toHaveCount(1);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBeTruthy();
      expect(errors).toEqual([]);
    }
  });
}

test('blocked storage does not prevent navigation or readable content', async ({ page }) => {
  await page.addInitScript(() => { Storage.prototype.getItem = () => { throw new DOMException('blocked', 'SecurityError'); }; Storage.prototype.setItem = () => { throw new DOMException('blocked', 'SecurityError'); }; });
  await page.emulateMedia({ colorScheme: 'dark', reducedMotion: 'reduce' });
  await page.goto('./');
  await expect(page.locator('main h1')).toBeVisible();
  await page.getByRole('link', { name: '方法与字典', exact: true }).click();
  await expect(page.locator('main h1')).toBeVisible();
});
