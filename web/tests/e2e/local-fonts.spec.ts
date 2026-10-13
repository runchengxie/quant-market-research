import { expect, test } from '@playwright/test';

for (const locale of ['en-US', 'zh-CN']) {
  test(`research typography loads from the site in ${locale}`, async ({ page, baseURL }) => {
    const externalFonts: string[] = [];
    const fontOrigins: string[] = [];
    page.on('request', (request) => {
      const url = new URL(request.url());
      if (url.hostname.endsWith('googleapis.com') || url.hostname.endsWith('gstatic.com')) {
        externalFonts.push(request.url());
      }
      if (request.resourceType() === 'font') fontOrigins.push(url.origin);
    });
    await page.goto(`research/style-factors-18y/?lang=${locale}`);
    await expect(page.locator('main h1')).toBeVisible();
    await page.evaluate(() => document.fonts.ready);
    expect(externalFonts).toEqual([]);
    expect(fontOrigins.length).toBeGreaterThan(0);
    expect(fontOrigins.every(origin => origin === new URL(baseURL!).origin)).toBe(true);
    const loaded = await page.evaluate(() => Array.from(document.fonts)
      .filter(font => font.status === 'loaded').map(font => font.family));
    expect(loaded.some(family => family.includes('Manrope Variable'))).toBe(true);
  });
}
