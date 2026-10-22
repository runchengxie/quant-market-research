import { expect, test } from '@playwright/test';
import { readFile } from 'node:fs/promises';
for (const locale of ['en-US', 'zh-CN']) {
  test(`single PNG preserves evidence and limits in ${locale}`, async ({ page }, testInfo) => {
    await page.goto(`research/factors/low-turnover/?lang=${locale}`);
    const downloadEvent = page.waitForEvent('download');
    await page.getByTestId('download-research-image').click();
    const download = await downloadEvent;
    expect(download.suggestedFilename()).toBe(`low-turnover-2026-09-16.${locale}.png`);
    await download.saveAs(testInfo.outputPath('summary.png'));
    const bytes = await readFile((await download.path())!);
    expect([...bytes.subarray(0, 8)]).toEqual([137,80,78,71,13,10,26,10]);
    expect(bytes.readUInt32BE(16)).toBe(1080);
    expect(bytes.readUInt32BE(20)).toBeGreaterThan(1500);
    expect(bytes.readUInt32BE(20)).toBeLessThan(6500);
    await expect(page.getByTestId('research-image-preview')).toBeVisible();
    await expect(page.getByTestId('research-image-preview')).toHaveJSProperty('naturalWidth', 1080);
    await expect(page.getByTestId('claim-review')).toContainText('LT-C01');
    await expect(page.getByTestId('forward-review').locator('a').first()).toHaveAttribute('href', /microcap\/#microcap-research-agenda/);
  });
  test(`compact mobile header keeps navigation usable in ${locale}`, async ({ page }) => {
    await page.setViewportSize({width:390,height:844});
    await page.goto(`research/factors/low-turnover/?lang=${locale}`);
    expect((await page.locator('.site-header').boundingBox())!.height).toBeLessThan(180);
    await page.locator('.nav-toggle').click();
    await expect(page.locator('#primary-nav')).toBeVisible();
    await expect(page.locator('[data-locale-toggle]')).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(page.locator('.nav-toggle')).toBeFocused();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  });
}
test('valuation review preserves draft and forward status', async ({page}) => {
  await page.goto('research/valuation-groups/?lang=zh-CN');
  await expect(page.getByTestId('claim-review')).toContainText('VG-C01');
  await expect(page.getByTestId('forward-review')).toContainText('尚未开始');
});

test('PNG encoding failure is reported and the next attempt downloads successfully', async ({page}) => {
  await page.goto('research/factors/low-turnover/?lang=zh-CN');
  await page.evaluate(() => {
    const original = HTMLCanvasElement.prototype.toBlob;
    HTMLCanvasElement.prototype.toBlob = function(callback) {
      HTMLCanvasElement.prototype.toBlob = original;
      callback(null);
    };
  });
  const button=page.getByTestId('download-research-image');
  await button.click();
  await expect(page.getByRole('status')).toContainText('图片生成失败');
  await expect(button).toBeEnabled();
  const event=page.waitForEvent('download');
  await button.click();
  expect((await event).suggestedFilename()).toContain('zh-CN.png');
  await expect(page.getByRole('status')).toBeEmpty();
});
