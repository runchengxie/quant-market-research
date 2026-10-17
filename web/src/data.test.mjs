import test from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
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
    for (const bucket of market.buckets) {
      assert.ok(bucket.zero_adv20_observations >= 0 && bucket.zero_adv20_observations <= bucket.observations);
      assert.equal(bucket.zero_adv20_share, bucket.observations ? bucket.zero_adv20_observations / bucket.observations : null);
      if (bucket.observations) assert.ok(bucket.p10_usd <= bucket.p25_usd && bucket.p25_usd <= bucket.median_usd && bucket.median_usd <= bucket.p75_usd && bucket.p75_usd <= bucket.p90_usd);
    }
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

test("relative quintiles bind to the reviewed absolute release and retain every denominator",()=>{
 const absoluteRaw=fs.readFileSync(path.join(root,"liquidity/summary.json"));
 const base=JSON.parse(absoluteRaw);
 const raw=fs.readFileSync(path.join(root,"liquidity/relative-summary.json"));
 const relative=JSON.parse(raw);
 const review=JSON.parse(fs.readFileSync(path.join(root,"liquidity/relative-review.json")));
 assert.equal(relative.absolute_summary_sha256,createHash('sha256').update(absoluteRaw).digest('hex'));
 assert.equal(review.reviewed_summary_sha256,createHash('sha256').update(raw).digest('hex'));
 assert.equal(review.aggregate_cells_reconciled,1710);
 assert.equal(review.absolute_aggregate_cells_reconciled,1520);
 assert.equal(review.feature_checksums_verified,true);
 for(const [views,originals] of [[relative.markets,base.markets],...relative.periods.map((p,i)=>[p.markets,base.periods[i].markets])]) {
  assert.deepEqual(views.map(m=>m.market),originals.map(m=>m.market));
  views.forEach((m,i)=>{
   assert.equal(m.eligible_observations,originals[i].eligible_observations);
   assert.equal(m.buckets.reduce((n,b)=>n+b.observations,0),m.eligible_observations);
   assert.equal(m.buckets.length,5);
  });
 }
});

test("absolute liquidity aggregates bind to the expanded independent review",()=>{
 const absoluteRaw=fs.readFileSync(path.join(root,"liquidity/summary.json"));
 const summary=JSON.parse(absoluteRaw);
 const review=JSON.parse(fs.readFileSync(path.join(root,"liquidity/independent-review.json")));
 assert.equal(review.reviewed_summary_sha256,createHash("sha256").update(absoluteRaw).digest("hex"));
 assert.equal(review.aggregate_cells_reconciled,1520);
 assert.equal(review.count_and_reason_conservation,true);
 assert.equal(review.strict_prior_fx_checked,true);
 assert.equal(review.full_raw_warehouse_audited,false);
 assert.ok(summary.generated_on >= "2026-10-17");
});

test("publishes identifier-free targeted minute/daily checks with an explicit missing universe denominator",()=>{
 const raw=fs.readFileSync(path.join(root,"liquidity/followup-audit.json"));
 const audit=JSON.parse(raw);
 assert.equal(audit.schema_version,"liquidity_followup_audit.v1");
 assert.equal(audit.universe_denominator.status,"unavailable");
 assert.equal(audit.universe_denominator.zero_turnover_rate,null);
 assert.equal(audit.observed_rows.daily_rows,31761);
 assert.equal(audit.observed_rows.daily_zero_turnover_rows,0);
 assert.ok(audit.dates.some(day=>day.date==="20241128"&&day.exchanges.some(row=>row.exchange==="BJ"&&row.daily_only===257)));
 assert.doesNotMatch(raw.toString(),/\b[A-Z0-9]{6}\.(SH|SZ|BJ)\b|\/home\/|source_path/);
});

test("publishes aggregate-only daily, minute and Level 2 coverage checks",()=>{
 const raw=fs.readFileSync(path.join(root,"liquidity/capacity-data-quality.json"));
 const quality=JSON.parse(raw);
 assert.equal(quality.schema_version,"capacity-data-quality.v1");
 assert.deepEqual(quality.markets.map(row=>row.market),["US","HK","A-share","JP"]);
 assert.deepEqual(quality.daily_periods.find(row=>row.period==="2026 YTD").markets,["HK","A-share","JP"]);
 const ashare=quality.markets.find(row=>row.market==="A-share");
 assert.equal(ashare.minute.sessions,1019);
 assert.equal(ashare.minute.calendar_gaps,9);
 assert.equal(ashare.level2.snapshot_dates,10);
 assert.equal(ashare.level2.snapshot_rows,311395);
 assert.equal(ashare.level2.usable_snapshot_rows,306483);
 assert.equal(quality.minute_daily_reconciliation.matched_security_days,5411206);
 assert.equal(quality.minute_daily_reconciliation.daily_only_security_days,2084);
 assert.equal(quality.minute_daily_reconciliation.minute_duplicate_keys,0);
 assert.ok(quality.minute_daily_reconciliation.median_daily_total_ratio > 0.99);
 assert.equal(quality.audit_receipts.full_minute_semantic_rebaseline_complete,false);
 assert.equal(quality.audit_receipts.l2_actual_order_calibrated,false);
 assert.doesNotMatch(raw.toString(),/\/home\/|\/mnt\/|ts_code|security_id|source_path/);
});
