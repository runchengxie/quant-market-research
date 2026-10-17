import test from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { mkdtemp, readFile, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
  canonical,
  validateShape,
  selectComparison,
  selectReplay,
  selectAttribution,
} from "./content/rotation-evidence.ts";
import { validateRotationEvidence } from "./content/rotation-evidence.server.ts";
import { importRotationEvidence } from "../scripts/import-rotation-evidence.mjs";
const sha = (value) => createHash("sha256").update(value).digest("hex");
function fixture() {
  const asset = {
    schema_version: "research.rotation_evidence_public.v1",
    evidence_id: "fixture",
    producer_commit: "a".repeat(40),
    generated_at: "2026-10-17T00:00:00+00:00",
    reviewed_source_digest: "b".repeat(64),
    units: {
      returns: "decimal",
      sharpe: "ratio",
      contributions: "decimal_nav",
    },
    protocols: [
      {
        id: "p",
        price_convention: "adjusted_price_valuation",
        execution_convention: "next_observed_session_close",
        cost_bps: 5,
        annualization_sessions: 252,
        risk_budget_policy: "declared_cap_intervention",
      },
    ],
    sources: [
      {
        id: "core",
        status: "historical_replay",
        panel_start: "2020-01-01",
        panel_end: "2020-01-03",
        availability: "unverified",
      },
    ],
    experiments: [
      {
        id: "fixed-base",
        group_id: "risk",
        allocator: "fixed_slots",
        source_id: "core",
        protocol_id: "p",
        evidence_stage: "rerun_original_in_archive",
        original_period: null,
        original_metrics: null,
      },
    ],
    comparisons: [],
    replay: [],
    attribution: [],
    theme_status: {
      status: "blocked",
      reasons: [
        "missing_historical_theme_mapping_and_independent_availability",
      ],
      registration_id: null,
      metrics: null,
    },
    limitations: ["historical_diagnostic_not_forward_validation"],
  };
  const review = {
    status: "approved",
    source_sha256: asset.reviewed_source_digest,
    content_sha256: sha(canonical(asset)),
    asset_sha256: sha(canonical(asset) + "\n"),
    reviewer: "fixture-review",
    reviewed_at: asset.generated_at,
  };
  return { asset, review };
}
test("admission is deterministic and binds all three digests", () => {
  const { asset, review } = fixture();
  assert.deepEqual(validateRotationEvidence(asset, review), asset);
  assert.equal(canonical([1, 1e-7, -0]), "[1,0.0000001,0]");
  for (const key of ["source_sha256", "content_sha256", "asset_sha256"])
    assert.throws(() =>
      validateRotationEvidence(asset, { ...review, [key]: "c".repeat(64) }),
    );
});
test("rejects unknown/private fields, nonfinite metrics and blocked performance", () => {
  for (const mutate of [
    (a) => (a.scores = []),
    (a) => (a.evidence_id = "/home/private"),
    (a) => (a.protocols[0].cost_bps = Infinity),
    (a) => (a.theme_status.metrics = {}),
    (a) => (a.sources[0].panel_end = "2019-01-01"),
    (a) => (a.units.returns = "percent"),
    (a) => (a.protocols[0].price_convention = { holdings: { 510300: 0.45 } }),
  ]) {
    const { asset, review } = fixture();
    mutate(asset);
    assert.throws(() => validateRotationEvidence(asset, review));
  }
});
test("atomic import failure preserves release and successful reimport is deterministic", async () => {
  const root = await mkdtemp(join(tmpdir(), "rotation-import-"));
  const { asset, review } = fixture();
  const assetPath = join(root, "asset.json"),
    reviewPath = join(root, "review.json");
  await writeFile(assetPath, JSON.stringify(asset));
  await writeFile(reviewPath, JSON.stringify(review));
  await importRotationEvidence({
    assetPath,
    reviewPath,
    outputDirectory: root,
  });
  const before = await readFile(join(root, "rotation-evidence-release.json"));
  await assert.rejects(
    importRotationEvidence({
      assetPath,
      reviewPath,
      outputDirectory: root,
      beforeRename: () => {
        throw Error("interrupted");
      },
    }),
  );
  assert.deepEqual(
    await readFile(join(root, "rotation-evidence-release.json")),
    before,
  );
  await importRotationEvidence({
    assetPath,
    reviewPath,
    outputDirectory: root,
  });
  assert.deepEqual(
    await readFile(join(root, "rotation-evidence-release.json")),
    before,
  );
});
test("unavailable selectors never substitute full metrics or future replay", () => {
  const { asset } = fixture();
  assert.equal(
    selectComparison(asset, {
      groupId: "risk",
      windowId: "last_252",
      allocator: "fixed_slots",
    }).status,
    "unavailable",
  );
  asset.replay = [
    { experiment_id: "fixed-base", signal_date: "2020-01-02" },
    { experiment_id: "fixed-base", signal_date: "2020-01-04" },
  ];
  assert.equal(
    selectReplay(asset, { date: "2019-01-01", experimentId: "fixed-base" })
      .status,
    "unavailable",
  );
  assert.equal(
    selectReplay(asset, { date: "bad", experimentId: "fixed-base" }).status,
    "unavailable",
  );
  assert.equal(
    selectReplay(asset, { date: "2020-01-03", experimentId: "fixed-base" })
      .record.signal_date,
    "2020-01-02",
  );
});
test("window selection retains precomputed negative values and missing contributions", () => {
  const { asset } = fixture();
  const metrics = {
    total_return: -0.2,
    cagr: -0.1,
    sharpe_zero_rf: -0.5,
    max_drawdown: -0.3,
  };
  const member = {
    experiment_id: "fixed-base",
    metrics,
    avg_bond_weight: 0.5,
    gross_traded_notional: 1,
    one_way_turnover: 0.5,
    status_counts: { EXECUTED: 1 },
  };
  const base = {
    id: "risk-common",
    group_id: "risk",
    window_id: "common",
    allocator: "fixed_slots",
    protocol_id: "p",
    period: { start: "2020-01-01", end: "2020-01-03", sessions: 3 },
    status: "available",
    reasons: [],
    members: [member],
  };
  asset.comparisons = [
    base,
    {
      ...base,
      id: "risk-short",
      window_id: "last_252",
      members: [{ ...member, metrics: { ...metrics, cagr: -0.25 } }],
    },
  ];
  assert.equal(
    selectComparison(asset, {
      groupId: "risk",
      windowId: "common",
      allocator: "fixed_slots",
    }).members[0].metrics.cagr,
    -0.1,
  );
  assert.equal(
    selectComparison(asset, {
      groupId: "risk",
      windowId: "last_252",
      allocator: "fixed_slots",
    }).members[0].metrics.cagr,
    -0.25,
  );
  assert.equal(
    selectComparison(asset, {
      groupId: "risk",
      windowId: "last_252",
      allocator: "growth",
    }).status,
    "unavailable",
  );
});
test("reviewer metadata is part of the public privacy boundary", () => {
  const { asset, review } = fixture();
  assert.throws(() =>
    validateRotationEvidence(asset, {
      ...review,
      reviewer: "/home/private/API_KEY",
    }),
  );
  assert.throws(() =>
    validateRotationEvidence(asset, { ...review, reviewer: { holdings: [] } }),
  );
});

test("missing contribution evidence remains an explicit unavailable view", () => {
  const { asset } = fixture();
  assert.equal(
    selectAttribution(asset, { comparisonId: "missing", windowId: "common" })
      .status,
    "unavailable",
  );
});
for (const failure of [
  "status_field",
  "review_path",
  "short_window",
  "same_day",
  "attribution_reference",
])
  test(`review regression: ${failure}`, async () => {
    const { asset, review } = JSON.parse(
      await readFile(
        new URL(
          "../public/data/rotation-evidence-release.json",
          import.meta.url,
        ),
        "utf8",
      ),
    );
    if (failure === "status_field")
      asset.comparisons[0].members[0].status_counts.private_holding_510300 = 12345;
    if (failure === "review_path")
      review.reviewer = "/mnt/private/research/owner";
    if (failure === "short_window") {
      const r = asset.comparisons.find((r) => r.window_id === "last_252");
      r.period = { start: "2026-08-21", end: "2026-08-24", sessions: 2 };
    }
    if (failure === "same_day")
      asset.replay[0].execution_date = asset.replay[0].signal_date;
    if (failure === "attribution_reference") {
      asset.attribution[0].risk += 1;
      asset.attribution[0].total_return += 1;
    }
    review.content_sha256 = sha(canonical(asset));
    review.asset_sha256 = sha(canonical(asset) + "\n");
    assert.throws(() => validateRotationEvidence(asset, review));
  });
test("source archive does not deny the page current reproduced runs", async () => {
  const { rotationPageCopy } = await import("./content/rotation-research.ts");
  assert.doesNotMatch(
    rotationPageCopy.theSourceReviewCoversTheWeeklyStrategy[0],
    /This page adds no new backtest/,
  );
  assert.doesNotMatch(
    rotationPageCopy.theSourceReviewCoversTheWeeklyStrategy[1],
    /本页没有新增回测/,
  );
});
