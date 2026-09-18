import test from "node:test";
import assert from "node:assert/strict";
import { formatFreshness, snapshotFreshness } from "./lib/freshness.ts";

test("freshness keeps generated time separate from data coverage", () => {
  const value = snapshotFreshness({ snapshots: { sample: {
    generated_at: "2026-09-18T08:00:00+08:00",
    coverage_start: "2020-01-01",
    coverage_end: "2026-09-17",
    source: "reviewed snapshot",
    quality_status: "derived",
  }}}, "sample");
  assert.deepEqual(value, {
    generatedAt: "2026-09-18T08:00:00+08:00",
    coverageStart: "2020-01-01",
    coverageEnd: "2026-09-17",
    asOf: "2026-09-17",
    source: "reviewed snapshot",
    qualityStatus: "derived",
  });
  assert.match(formatFreshness(value), /数据截至 2026-09-17/);
  assert.match(formatFreshness(value), /快照生成于 2026-09-18/);
});

test("missing freshness dates are explicit rather than called latest", () => {
  const value = snapshotFreshness({ snapshots: { sample: { source: "pending", quality_status: "pending" } } }, "sample");
  assert.equal(value.asOf, null);
  assert.match(formatFreshness(value), /日期待补/);
  assert.doesNotMatch(formatFreshness(value), /最新/);
});

test("market freshness preserves each market's own as-of date", () => {
  const value = snapshotFreshness({ snapshots: { liquidity: {
    generated_at: "2026-09-18",
    markets: { us: { as_of: "2026-09-07" }, hk: { as_of: "2026-05-26" } },
    source: "liquidity snapshot", quality_status: "incomplete",
  }}}, "liquidity");
  assert.deepEqual(value.markets, { us: "2026-09-07", hk: "2026-05-26" });
});
