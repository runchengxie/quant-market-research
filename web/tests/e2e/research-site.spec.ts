import { expect, test } from "@playwright/test";

const routes = [
  ["", "研究到了哪一步，有哪些发现？"],
  ["research/cashflow/", "现金流历史研究"],
  ["research/cashflow/recovery/", "现金流回撤与回本时间"],
  ["research/microcap/", "A 股微盘历史研究"],
  ["research/microcap/cross-market-liquidity/", "跨市场小微盘流动性"],
  ["research/indices/", "指数与 ETF 历史表现"],
  ["research/style-factors-18y/", "18 年 A 股风格因子研究"],
  ["research/liquidity/", "跨市场流动性"],
] as const;

test.beforeEach(async ({ page }) => {
  await page.route(/fonts\.(?:googleapis|gstatic)\.com/, (route) => route.abort());
});

for (const [route, heading] of routes) {
  test(`${route || "overview"} opens directly and survives a refresh`, async ({ page }) => {
    await page.goto(route, { waitUntil: "domcontentloaded" });
    await expect(page.locator("main h2").first()).toContainText(heading);
    await page.reload({ waitUntil: "domcontentloaded" });
    await expect(page.locator("main h2").first()).toContainText(heading);
  }
  );
}

test("legacy hash links redirect to the new research URL", async ({ page }) => {
  await page.goto("#microcap");
  await expect(page).toHaveURL(/\/research\/microcap\/$/);
  await expect(page.locator("main h2").first()).toContainText("A 股微盘历史研究");
});

test("microcap research loads its public data and theme control works", async ({ page }) => {
  const summaryResponse = page.waitForResponse((response) => response.url().endsWith("/data/index/microcap/summary.json"));
  await page.goto("research/microcap/");
  expect((await summaryResponse).ok()).toBeTruthy();
  await expect(page.locator(".sub-tabs")).toBeVisible();

  await page.locator(".theme-toggle").click();
  await page.locator(".theme-toggle").click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
});

test("recovery research loads the snapshot from the GitHub Pages base path", async ({ page }) => {
  const recoveryResponse = page.waitForResponse((response) => response.url().endsWith("/data/research/recovery.json"));
  await page.goto("research/cashflow/recovery/", { waitUntil: "domcontentloaded" });
  expect((await recoveryResponse).ok()).toBeTruthy();
  await expect(page.locator(".recovery-section")).toBeVisible();
});

test("replication data loads from the GitHub Pages base path", async ({ page }) => {
  const replicationResponse = page.waitForResponse((response) => response.url().endsWith("/data/research/replication.json"));
  await page.goto("research/microcap/", { waitUntil: "domcontentloaded" });
  expect((await replicationResponse).ok()).toBeTruthy();
  await expect(page.getByRole("heading", { name: "我们自己算出的结果，跟指数有多接近？" })).toBeVisible();
});
