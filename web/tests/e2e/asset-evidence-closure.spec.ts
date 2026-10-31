import { test, expect } from '@playwright/test';

for (const width of [1280, 390]) {
  test(`closure evidence, cost basis and download at ${width}px`, async ({ page, request }) => {
    await page.setViewportSize({ width, height: 844 });
    await page.goto('research/cashflow/?lang=en-US');
    const section = page.locator('#cashflow-robustness');
    await expect(section).toContainText('Cost bases differ');
    await expect(section).toContainText('Not admitted; zero completed windows');
    await expect(section).toContainText('Strict report-rounding checks still fail for 2018 and 2019');
    await page.goto('research/cashflow/?lang=zh-CN');
    await expect(section).toContainText('两种参数不能互换');
    await expect(section).toContainText('尚未准入，完成窗口为0');
    await expect(page.locator('body')).toHaveJSProperty('scrollWidth', width);
    const link = section.getByRole('link', { name: '已核查的派生汇总' });
    const response = await request.get((await link.getAttribute('href'))!);
    expect(response.ok()).toBe(true);
    const data = await response.json();
    expect(data.cohorts['000300_SH'].classifications.delisted_by_fiscal_end).toBe(8);
    expect(data.etf_years.find((row: {year: number}) => row.year === 2019).disclosed_return_matches).toBe(false);
    expect(data).not.toHaveProperty('member_details');
  });
}
