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
  ["research/factors/pb-roe/", "PB 与 ROE：历史对照与证据边界"],
] as const;

test.beforeEach(async ({ page }) => {
  await page.route(/fonts\.(?:googleapis|gstatic)\.com/, (route) => route.abort());
});

test("research HTML preserves UTF-8 text before hydration", async ({ request }) => {
  for (const [route] of routes) {
    const response = await request.get(route || "./");
    expect(response.ok()).toBeTruthy();
    const bytes = await response.body();
    expect(bytes.includes(0), `${route} contains NUL bytes`).toBe(false);
    const html = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
    if (route === "research/style-factors-18y/") expect(html).toContain("同一历史序列");
  }
});

test("Barra hydration preserves pagination ARIA references", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error" && /React|hydrat|did not match/i.test(message.text())) errors.push(message.text());
  });
  await page.goto("research/style-factors-18y/");
  await expect(page.locator("#barra-annual canvas")).toBeVisible();
  await page.getByText("补充研究：市值十分组与稳定性诊断", { exact: true }).click();
  const pagination = page.getByRole("navigation", { name: "表格分页" });
  await expect(pagination.first()).toBeVisible();
  for (const nav of await pagination.all()) {
    const target = await nav.getAttribute("aria-describedby");
    expect(target).toBeTruthy();
    expect(await page.evaluate((id) => Array.from(document.querySelectorAll("[id]")).filter((element) => element.id === id).length, target)).toBe(1);
  }
  await pagination.first().getByRole("button", { name: "下一页", exact: true }).click();
  await expect(pagination.first()).toContainText("第 2 /");
  expect(errors).toEqual([]);
});

for (const [route, heading] of routes) {
  test(`${route || "overview"} opens directly and survives a refresh`, async ({ page }) => {
    await page.goto(route, { waitUntil: "domcontentloaded" });
    await expect(page.getByRole("heading", { name: heading, exact: true }).first()).toBeVisible();
    await page.reload({ waitUntil: "domcontentloaded" });
    await expect(page.getByRole("heading", { name: heading, exact: true }).first()).toBeVisible();
  }
  );
}

test("legacy hash links redirect to the new research URL", async ({ page }) => {
  await page.goto("#microcap");
  await expect(page).toHaveURL(/\/research\/microcap\/$/);
  await expect(page.getByRole("heading", { name: "A 股微盘历史研究", exact: true }).first()).toBeVisible();
});

test("low-turnover report links to its full methodology", async ({ page }) => {
  await page.goto("research/factors/low-turnover/");
  await expect(page.getByRole("link", { name: /阅读完整方法说明/ })).toHaveAttribute("href", /\/docs\/research\/factors\/low-turnover\//);
});

test("PB/ROE topic links to the reviewed evidence and discloses its scope", async ({ page }) => {
  await page.goto("research/");
  await page.getByRole("link", { name: /PB 与 ROE 历史对照/ }).click();
  await expect(page.locator(".theme-heading p")).toContainText("数据截至 2026-08-31");
  await expect(page.getByText("不能当作严格纯 PB 组合", { exact: false })).toBeVisible();
  await expect(page.getByRole("link", { name: /阅读完整数据与方法/ })).toHaveAttribute("href", /\/docs\/research\/factors\/pb-roe\//);
});

test("PB/ROE charts separate the shared pool from the quality audit", async ({ page }) => {
  await page.goto("research/factors/pb-roe/");
  const ranking = page.locator('figure[aria-labelledby="ranking-chart-title"]');
  const quality = page.locator('figure[aria-labelledby="quality-chart-title"]');
  await expect(ranking.locator(".evidence-chart-row")).toHaveCount(5);
  await expect(ranking).toContainText("12.05%");
  await expect(ranking).toContainText("46.74%");
  await expect(quality.locator(".evidence-chart-row")).toHaveCount(2);
  await expect(quality).toContainText("48.26%");
  await expect(page.locator('figure[aria-labelledby="universe-chart-title"]')).toContainText("658,311");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBeTruthy();
});

test("low-turnover charts show uncertainty and snapshot-driven execution limits", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("research/factors/low-turnover/");
  const controls = page.locator('figure[aria-labelledby="control-chart-title"]');
  await expect(controls.locator(".interval-row")).toHaveCount(4);
  await expect(controls).toContainText("0.57–1.18%");
  await expect(page.locator('figure[aria-labelledby="capacity-chart-title"]')).toBeVisible();
  await expect(page.locator('figure[aria-labelledby="window-chart-title"] .evidence-chart-row')).toHaveCount(3);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBeTruthy();
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
    const workspace = page.locator('[aria-label="当前因子诊断工作区"]');
    await expect(workspace).toBeVisible();
    await expect(workspace.locator("#barra-annual")).toBeVisible();
    await expect(workspace.locator("#barra-factor-detail")).toBeVisible();
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
      await expect(workspace.locator(".workspace-context strong")).toHaveText(await button.textContent() ?? "");
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
