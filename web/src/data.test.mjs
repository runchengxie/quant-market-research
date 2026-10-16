import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../public/data");

test("publishes reviewed four-market liquidity with real common-date periods", () => {
  const summary = JSON.parse(fs.readFileSync(path.join(root, "liquidity/summary.json"), "utf8"));
  assert.deepEqual(summary.markets.map(m => m.market), ["US", "HK", "A-share", "JP"]);
  assert.equal(summary.method.roll_days, 20);
  assert.deepEqual(summary.markets.map(m => m.as_of), ["2025-10-03", "2026-05-26", "2026-10-15", "2026-05-01"]);
  const common = summary.periods.find(p => p.period === "common snapshot");
  assert.equal(common.common_end, "2025-09-30");
  assert.equal(common.common_dates, 1);
  for (const period of summary.periods) for (const market of period.markets) {
    assert.equal(market.buckets.reduce((n,b) => n+b.observations,0), market.eligible_observations);
  }
  const ytd = summary.periods.find(p => p.period === "2026 YTD");
  assert.deepEqual(ytd.missing_markets, ["US"]);
  assert.equal(ytd.common_dates, 71);
  assert.equal(summary.periods.find(p => p.period === "2025").common_end, "2025-09-30");
});

test("publishes the Barra market-evidence snapshot", () => {
  const summary = JSON.parse(fs.readFileSync(path.join(root, "barra/barra_summary.json"), "utf8"));
  const quantiles = fs.readFileSync(path.join(root, "barra/barra_size_quantiles.csv"), "utf8");
  assert.equal(summary.legacy_barra_result.factor_count, 19);
  assert.equal(summary.size_monotonicity.quantiles, 10);
  assert.match(quantiles, /formation_date,bucket,mean_forward_return/);
});

test("publishes the historical Barra report datasets", () => {
  const factors = JSON.parse(fs.readFileSync(path.join(root, "barra/historical_factor_summary.json"), "utf8"));
  const yearly = fs.readFileSync(path.join(root, "barra/factor_yearly.csv"), "utf8");
  const correlations = JSON.parse(fs.readFileSync(path.join(root, "barra/factor_correlation.json"), "utf8"));
  const reportPath = path.join(root, "barra/historical_report.md");
  const report = fs.readFileSync(reportPath, "utf8");
  assert.equal(factors.length, 19);
  assert.match(yearly, /year,factor,days,period_start/);
  assert.ok(correlations.size);
  for (const [, imagePath] of report.matchAll(/!\[[^\]]*\]\(([^)]+)\)/g)) {
    assert.ok(fs.existsSync(path.resolve(path.dirname(reportPath), imagePath)), `missing report image: ${imagePath}`);
  }
});

test("publishes the explicitly scoped Quality component diagnostic", () => {
  const rows = fs
    .readFileSync(path.join(root, "barra/quality_component_summary.csv"), "utf8")
    .trim()
    .split("\n");
  assert.equal(rows.length, 5);
  assert.match(rows[0], /factor,days,years,cumulative_ret,annual_ret,geometric_annual_ret/);
  assert.match(rows.slice(1).join("\n"), /quality_profitability/);
  assert.match(rows.slice(1).join("\n"), /quality_earnings_quality/);
});

test("publishes complete multi-period rows for representative ETFs", () => {
  const rows = fs
    .readFileSync(path.join(root, "index/linked_indices/etf_multi_period_returns.csv"), "utf8")
    .trim()
    .split("\n");
  assert.equal(rows.length, 101);
  assert.match(rows[0], /ts_code,period,start,end/);
  for (const period of ["1Y", "3Y", "5Y", "10Y"]) {
    assert.equal(rows.filter((row) => row.split(",")[1] === period).length, 25);
  }
});

test("does not publish the retired animal index dataset", () => {
  assert.equal(fs.existsSync(path.join(root, "animal")), false);
  assert.equal(fs.existsSync(path.join(root, "plant")), false);
});

test("publishes a lightweight smallcap turnover research snapshot", () => {
  const summary = JSON.parse(fs.readFileSync(path.join(root, "smallcap_turnover.json"), "utf8"));
  assert.equal(summary.schema_version, "smallcap_turnover_ui.v2");
  assert.deepEqual(summary.clean.rank_counts, [1, 10, 50, 100, 200, 400, 1000]);
  assert.equal(summary.clean.quality_status, "verified");
  assert.equal(summary.historical.quality_status, "incomplete");
  assert.ok(summary.clean.annual.length >= 60);
  assert.ok(summary.historical.annual.length >= 100);
  assert.equal(summary.overlap_audit.length, 7);
  assert.ok(summary.clean.monthly.length >= 700);
  assert.ok(summary.historical.monthly.length >= 1_200);
});
