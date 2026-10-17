import { test, expect } from "@playwright/test";
const route = "research/style-theme-rotation/";
test("common windows, URL history, replay eligibility and attribution use admitted data", async ({
  page,
}) => {
  await page.goto(route + "?lang=en-US");
  const panel = page.locator("#rotation-evidence");
  await expect(
    panel.getByRole("heading", { name: "Reproduced weekly rotation evidence" }),
  ).toBeVisible();
  await expect(panel.getByTestId("comparison-period")).toContainText("2182");
  await panel
    .getByLabel("Evaluation window", { exact: true })
    .selectOption("last_252");
  await expect(panel.getByTestId("comparison-period")).toContainText(
    "252 sessions",
  );
  await expect(page).toHaveURL(/rotationWindow=last_252/);
  await panel
    .getByLabel("Evidence group", { exact: true })
    .selectOption("pool");
  await expect(panel).toContainText("Missing required price columns");
  await expect(
    panel.getByRole("heading", { name: "Where cumulative return came from" }),
  ).toBeVisible();
  await panel
    .getByRole("button", { name: "Load historical replay", exact: true })
    .click();
  await expect(panel.getByTestId("replay-status")).toBeVisible();
  await expect(panel).toContainText("Unverified");
  await panel
    .getByRole("button", { name: "Previous signal", exact: true })
    .click();
  await expect(page).toHaveURL(/rotationDate=/);
  await expect(page).toHaveURL(/lang=en-US/);
  const before = await panel.getByTestId("replay-status").innerText();
  await panel
    .getByRole("button", { name: "Previous signal", exact: true })
    .click();
  await expect(panel.getByTestId("replay-status")).not.toHaveText(before);
  await page.goBack();
  await expect(panel.getByTestId("replay-status")).toHaveText(before);
  await panel
    .getByLabel("Eligibility filter", { exact: true })
    .selectOption("eligible");
  await expect(panel).toContainText("Theme-to-ETF incremental test: blocked");
});
test("hash mismatch shows retry without exposing replay", async ({ page }) => {
  await page.route("**/data/rotation-evidence-release.json", (r) =>
    r.fulfill({ status: 200, body: "{}" }),
  );
  await page.goto(route);
  const p = page.locator("#rotation-evidence");
  await p
    .getByRole("button", { name: "Load historical replay", exact: true })
    .click();
  await expect(p.getByRole("alert")).toContainText("could not be verified");
  await expect(p.getByTestId("replay-status")).toHaveCount(0);
});
test("invalid dates never choose future observations and Chinese mobile remains usable", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(route + "?lang=zh-CN&rotationDate=1900-01-01");
  const p = page.locator("#rotation-evidence");
  await p.getByRole("button", { name: "载入历史回放", exact: true }).click();
  await expect(p).toContainText("所选日期不在已准入范围内");
  await p.getByRole("button", { name: "恢复最近的有效日期" }).click();
  await expect(p.getByTestId("replay-status")).toBeVisible();
  await expect(p).toContainText("上市证据");
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBeTruthy();
});
test("static fallback exposes current comparison, replay and contribution evidence", async ({
  browser,
}) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto(
    "http://127.0.0.1:" +
      (process.env.PORT ?? "4321") +
      "/quant-market-research/" +
      route,
  );
  const p = page.locator("#rotation-evidence");
  await expect(p).toContainText("21 reproduced");
  await expect(p).toContainText("Cumulative return");
  await expect(p).toContainText("First observed price");
  await expect(p).toContainText("Theme-to-ETF incremental test: blocked");
  await context.close();
});
for (const locale of ["en-US", "zh-CN"])
  for (const width of [390, 1280, 1440]) {
    test(`evidence is readable with blocked storage and dark theme ${locale} ${width}`, async ({
      page,
    }) => {
      const errors: string[] = [];
      page.on("pageerror", (e) => errors.push(e.message));
      await page.setViewportSize({ width, height: 900 });
      await page.emulateMedia({ colorScheme: "dark" });
      await page.addInitScript(() => {
        Object.defineProperty(window, "localStorage", {
          get() {
            throw new Error("storage blocked");
          },
        });
      });
      await page.goto(route + `?lang=${locale}`);
      const p = page.locator("#rotation-evidence");
      const control = p.getByLabel(
        locale === "en-US" ? "Evaluation window" : "评价窗口",
        { exact: true },
      );
      await control.focus();
      await control.selectOption("last_756");
      await expect(p.getByTestId("comparison-period")).toContainText("756");
      await expect(p.getByRole("img").first()).toBeVisible();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBeTruthy();
      expect(errors).toEqual([]);
    });
  }
test("negative numeric sorting and keyboard window changes retain reviewed units", async ({
  page,
}) => {
  await page.goto(route + "?lang=en-US");
  const p = page.locator("#rotation-evidence");
  const drawdown = p.getByRole("button", { name: /Maximum drawdown \(%\)/ });
  await drawdown.click();
  await expect(
    p.locator("table").first().locator("tbody tr").first().locator("td").nth(4),
  ).toContainText("-11.61");
  await drawdown.click();
  await expect(
    p.locator("table").first().locator("tbody tr").first().locator("td").nth(4),
  ).toContainText("-22.86");
  const window = p.getByLabel("Evaluation window", { exact: true });
  await window.focus();
  await window.press("Home");
  await window.press("ArrowDown");
  await window.press("Enter");
  await expect(p.getByTestId("comparison-period")).toContainText(
    "252 sessions",
  );
});
test("mobile numeric tables scroll horizontally without stacking digits", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 900 });
  await page.goto(route + "?lang=zh-CN");
  const table = page.locator("#rotation-evidence table").first();
  await expect(table.locator("tbody tr")).toHaveCount(3);
  await expect(table).toBeVisible();
  await table.scrollIntoViewIfNeeded();
  const row = await table.locator("tbody tr").first().boundingBox();
  expect(row!.height).toBeLessThan(150);
  expect(
    await table.evaluate(
      (t) =>
        t.getBoundingClientRect().width >
        t.parentElement!.getBoundingClientRect().width,
    ),
  ).toBeTruthy();
});
