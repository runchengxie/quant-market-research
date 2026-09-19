import { expect, test } from "@playwright/test";

test("unknown URL factor cannot crash the explorer", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("research/style-factors-18y/?factor=toString");
  await expect(page.locator('button[data-factor="size"]')).toHaveAttribute("aria-pressed", "true");
  expect(errors).toEqual([]);
});

test("factor search, family filter and shared link preserve selected evidence", async ({ page }) => {
  await page.goto("research/style-factors-18y/?factor=quality");
  const detail = page.getByRole("region", { name: "所选因子详情" });
  await expect(page.locator('button[data-factor="quality"]')).toHaveAttribute("aria-pressed", "true");
  await expect(detail).toContainText("ROE");
  await page.getByRole("searchbox", { name: "搜索因子" }).fill("beta");
  await expect(page.locator("button[data-factor]")).toHaveCount(1);
  await page.locator('button[data-factor="beta"]').click();
  await expect(detail).toContainText("beta");
  await expect(page).toHaveURL(/factor=beta/);
  await page.getByRole("searchbox", { name: "搜索因子" }).fill("没有这个因子");
  await expect(page.getByText("没有匹配的因子")).toBeVisible();
  await page.getByRole("button", { name: "清除筛选" }).click();
  await expect(page.locator("button[data-factor]")).toHaveCount(19);
  await page.getByRole("combobox", { name: "因子家族" }).selectOption("价值");
  await expect(page.locator('button[data-factor="value"]')).toBeVisible();
  await expect(page.locator('button[data-factor="beta"]')).toHaveCount(0);
  await expect(detail).toContainText("beta");
  await page.reload();
  await expect(page.locator('button[data-factor="beta"]')).toHaveAttribute("aria-pressed", "true");
});

test("optional dataset failure stays local and can be retried", async ({ page }) => {
  let fail = true;
  await page.route("**/data/barra/quality_component_summary.csv", route => fail
    ? route.fulfill({ status: 503, body: "unavailable" }) : route.continue());
  await page.goto("research/style-factors-18y/?factor=quality");
  await expect(page.locator("button[data-factor]")).toHaveCount(19);
  await expect(page.locator("#barra-annual canvas")).toBeVisible();
  const quality = page.getByRole("region", { name: "Quality 子因子数据" });
  await expect(quality.getByRole("alert")).toContainText("加载失败");
  fail = false;
  await quality.getByRole("button", { name: /重试/ }).click();
  await expect(quality.getByRole("row").filter({ hasText: "低杠杆 · Debt / Assets" })).toContainText("1.2%");
});

test("required dataset failure has recovery instead of an endless spinner", async ({ page }) => {
  let fail = true;
  await page.route("**/data/barra/factor_yearly.csv", route => fail
    ? route.fulfill({ status: 503, body: "unavailable" }) : route.continue());
  await page.goto("research/style-factors-18y/");
  const annual = page.locator("#barra-annual");
  await expect(annual.getByRole("alert")).toContainText("加载失败");
  fail = false;
  await annual.getByRole("button", { name: /重试/ }).click();
  await expect(annual.locator("canvas")).toBeVisible();
});

test("size data is lazy, shows revision limits and can page through all records", async ({ page }) => {
  let sizeRequests = 0;
  await page.route("**/data/barra/barra_size_quantiles.csv", route => { sizeRequests++; return route.continue(); });
  await page.goto("research/style-factors-18y/");
  await expect(page.locator("#barra-annual canvas")).toBeVisible();
  expect(sizeRequests).toBe(0);
  const diagnostic = page.locator(".size-diagnostic");
  await diagnostic.locator(":scope > summary").click();
  await expect(diagnostic).toContainText("输入版本 2026-09-18");
  await expect(diagnostic).toContainText("10,544");
  expect(sizeRequests).toBe(1);
  const table = diagnostic.getByRole("table").first();
  await expect(table.getByRole("row")).toHaveCount(51);
  await diagnostic.getByRole("button", { name: "最后一页", exact: true }).click();
  await expect(table.getByRole("row")).toHaveCount(31);
  await expect(diagnostic.getByRole("button", { name: "下一页", exact: true })).toBeDisabled();
  await diagnostic.getByRole("button", { name: "第一页", exact: true }).click();
  await expect(table.getByRole("row")).toHaveCount(51);
  await diagnostic.getByRole("button", { name: "阶段收益差", exact: true }).click();
  await expect(diagnostic.getByRole("table").nth(1)).toContainText("共同分组日期数");
});

for (const width of [390, 1280]) {
  test(`workbench readable layout and selected metrics at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("research/style-factors-18y/?factor=quality");
    const annual = page.locator("#barra-annual");
    await expect(annual.locator("canvas")).toBeVisible();
    expect(await annual.evaluate(el => el.getBoundingClientRect().top)).toBeLessThan(width > 800 ? 600 : 850);
    await expect(page.getByRole("region", { name: "所选因子关键指标" })).toContainText("4.0%");
    await expect(page.getByRole("region", { name: "因子相关性" })).toContainText("正相关");
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBeTruthy();
    await page.screenshot({ path: `test-results/workbench-light-${width}.png`, fullPage: true });
    await page.locator(".theme-toggle").click();
    await page.locator(".theme-toggle").click();
    await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
    await page.locator('button[data-factor="size"]').click();
    await expect(page.getByRole("region", { name: "所选因子关键指标" })).not.toContainText("4.0%");
    await page.screenshot({ path: `test-results/workbench-dark-${width}.png`, fullPage: true });
  });
}
