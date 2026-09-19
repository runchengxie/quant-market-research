import { expect, test } from "@playwright/test";

const routes = [
  ["", "从主要发现开始了解这些研究"],
  ["research/cashflow/", "现金流历史研究"],
  ["research/cashflow/recovery/", "现金流回撤与回本时间"],
  ["research/microcap/", "A 股微盘历史研究"],
  ["research/microcap/cross-market-liquidity/", "跨市场小微盘流动性"],
  ["research/indices/", "指数与 ETF 历史表现"],
  ["research/style-factors-18y/", "18 年 A 股风格因子研究"],
  ["research/liquidity/", "跨市场流动性"],
  ["research/factors/low-turnover/", "低换手因子：它保留了什么信息？"],
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

test("low-turnover report links to its full methodology", async ({ page }) => {
  await page.goto("research/factors/low-turnover/");
  await expect(page.getByRole("link", { name: /阅读完整方法说明/ })).toHaveAttribute("href", /\/docs\/research\/factors\/low-turnover\//);
});

test("microcap research loads its public data and theme control works", async ({ page }) => {
  const summaryResponse = page.waitForResponse((response) => response.url().endsWith("/data/index/microcap/summary.json"));
  await page.goto("research/microcap/");
  await page.locator("astro-island[component-export='MicrocapPage']").scrollIntoViewIfNeeded();
  expect((await summaryResponse).ok()).toBeTruthy();
  await expect(page.locator(".sub-tabs")).toBeVisible();

  await page.locator(".theme-toggle").click();
  await page.locator(".theme-toggle").click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
});

test("recovery research loads the snapshot from the GitHub Pages base path", async ({ page }) => {
  await page.goto("research/cashflow/recovery/", { waitUntil: "domcontentloaded" });
  await page.locator("astro-island[component-export='CashflowPage']").scrollIntoViewIfNeeded();
  const recoveryResponse = await page.request.get("data/research/recovery.json");
  expect(recoveryResponse.ok()).toBeTruthy();
  await expect(page.locator(".recovery-section")).toBeVisible();
});

test("replication data loads from the GitHub Pages base path", async ({ page }) => {
  await page.goto("research/microcap/", { waitUntil: "domcontentloaded" });
  await page.locator("astro-island[component-export='MicrocapPage']").scrollIntoViewIfNeeded();
  const replicationResponse = await page.request.get("data/research/replication.json");
  expect(replicationResponse.ok()).toBeTruthy();
  await expect(page.getByRole("heading", { name: "自行计算的结果与官方指数有多接近？" })).toBeVisible();
});

for (const width of [1280, 390]) {
  test(`Barra explorer switches all 19 factors at width ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("research/style-factors-18y/");
    await expect(page.locator("#barra-annual canvas")).toBeVisible();
    const buttons = page.locator("button[data-factor]");
    await expect(buttons).toHaveCount(19);
    const detail = page.getByRole("region", { name: "所选因子详情" });
    for (let i = 0; i < 19; i++) {
      const button = buttons.nth(i);
      const factor = await button.getAttribute("data-factor");
      await button.click();
      await expect(button).toHaveAttribute("aria-pressed", "true");
      await expect(detail.locator(".section-kicker").first()).toContainText(factor!);
      await expect(detail).toContainText("历史页面记录的多空方向");
      await expect(detail).toContainText("怎么计算");
      await expect(detail.getByRole("heading", { name: "Quality 子因子诊断" })).toHaveCount(factor === "quality" ? 1 : 0);
    }
    await page.locator('button[data-factor="quality"]').click();
    const leverage = detail.getByRole("row").filter({ hasText: "低杠杆 · Debt / Assets" });
    await expect(leverage).toContainText("1.2%");
    await expect(leverage).toContainText("10.5%");
    await expect(detail.locator(".quality-method-grid > div")).toHaveCount(4);
    const chart = page.locator(".panel").filter({ has: page.getByRole("heading", { name: "逐年合成收益与阶段表现" }) });
    await expect(chart.locator("canvas")).toHaveCount(1);
    expect(await chart.evaluate((el) => el.getBoundingClientRect().bottom)).toBeLessThanOrEqual(await detail.evaluate((el) => el.getBoundingClientRect().top));
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)).toBeTruthy();
    await page.getByText("补充研究：市值十分组与稳定性诊断", { exact: true }).click();
    await expect(page.getByRole("heading", { name: "补充研究：市值十分组", exact: true })).toBeVisible();
    await page.getByText("补充研究：市值十分组与稳定性诊断", { exact: true }).click();
    await page.screenshot({ path: `test-results/barra-${width}.png`, fullPage: true });
  });
}
