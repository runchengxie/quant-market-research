import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, readFileSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";

const script = new URL("../scripts/build-public-snapshot.mjs", import.meta.url);

function fixture() {
  const root = mkdtempSync(path.join(os.tmpdir(), "microcap-snapshot-import-"));
  const input = path.join(root, "external-results");
  const target = path.join(root, "public");
  mkdirSync(input);
  mkdirSync(target);
  writeFileSync(path.join(input, "microcap_summary.json"), JSON.stringify({
    source_label: "Reviewed synthetic rule reconstruction", observations: 2,
    caveats: ["Synthetic test data; no investment result."],
  }));
  writeFileSync(path.join(input, "microcap_nav.csv"),
    "date,nav,return,constituents\n2026-01-02,1,0,400\n2026-01-05,1.01,0.01,399\n");
  const manifest = { generated_at: "2026-01-01", sources: ["Other reviewed study"],
    markets: { hk: "published" }, included_snapshots: { index_research_files: 22 },
    snapshots: { liquidity: { coverage_end: "2026-01-01", quality_status: "derived" },
      microcap: { coverage_end: "2025-12-31", quality_status: "verified" } } };
  writeFileSync(path.join(target, "manifest.json"), JSON.stringify(manifest));
  return { root, input, target, manifest };
}

function run(input, target, extra = {}) {
  return spawnSync(process.execPath, [script.pathname, "--target-root", target], {
    env: { ...process.env, MARKET_RESEARCH_OUTPUT_ROOT: input, ...extra }, encoding: "utf8",
  });
}

test("snapshot CLI reads external results and preserves unrelated public manifest records", () => {
  const f = fixture();
  try {
    const result = run(f.input, f.target);
    assert.equal(result.status, 0, result.stderr);
    const nav = JSON.parse(readFileSync(path.join(f.target, "microcap_nav.json"), "utf8"));
    assert.deepEqual(nav, [
      { date: "2026-01-02", nav: 1, daily_return: 0, constituents: 400 },
      { date: "2026-01-05", nav: 1.01, daily_return: 0.01, constituents: 399 },
    ]);
    const manifest = JSON.parse(readFileSync(path.join(f.target, "manifest.json"), "utf8"));
    assert.deepEqual(manifest.included_snapshots, f.manifest.included_snapshots);
    assert.deepEqual(manifest.snapshots.liquidity, f.manifest.snapshots.liquidity);
    assert.equal(manifest.markets.hk, "published");
    assert.equal(manifest.markets.us, "pending local refresh");
    assert.ok(manifest.sources.includes("Other reviewed study"));
    assert.equal(manifest.snapshots.microcap.coverage_end, "2026-01-05");
    assert.equal(manifest.snapshots.microcap.quality_status, "incomplete");
    assert.ok(!JSON.stringify(manifest).includes(f.root));
  } finally { rmSync(f.root, { recursive: true }); }
});

test("missing source leaves existing public files unchanged", () => {
  const f = fixture();
  try {
    rmSync(path.join(f.input, "microcap_nav.csv"));
    const before = readFileSync(path.join(f.target, "manifest.json"), "utf8");
    const result = run(f.input, f.target);
    assert.notEqual(result.status, 0);
    assert.equal(readFileSync(path.join(f.target, "manifest.json"), "utf8"), before);
    assert.throws(() => readFileSync(path.join(f.target, "microcap_summary.json")));
  } finally { rmSync(f.root, { recursive: true }); }
});


test("malformed numeric input fails before publishing a partial snapshot", () => {
  const f = fixture();
  try {
    writeFileSync(path.join(f.input, "microcap_nav.csv"),
      "date,nav,daily_return,constituents\n2026-01-02,1,not-a-return,400\n");
    const before = readFileSync(path.join(f.target, "manifest.json"), "utf8");
    const result = run(f.input, f.target);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /finite numeric values/);
    assert.equal(readFileSync(path.join(f.target, "manifest.json"), "utf8"), before);
  } finally { rmSync(f.root, { recursive: true }); }
});

test("checkout-local inputs are rejected without altering reviewed output", () => {
  const f = fixture();
  try {
    const repository = path.resolve(path.dirname(script.pathname), "../..");
    const result = run(repository, f.target);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /outside the code repository/);
    assert.deepEqual(JSON.parse(readFileSync(path.join(f.target, "manifest.json"), "utf8")), f.manifest);
  } finally { rmSync(f.root, { recursive: true }); }
});


test("legacy daily_return inputs retain the public numeric value", () => {
  const f = fixture();
  try {
    const file = path.join(f.input, "microcap_nav.csv");
    writeFileSync(file, readFileSync(file, "utf8").replace("date,nav,return,", "date,nav,daily_return,"));
    const result = run(f.input, f.target);
    assert.equal(result.status, 0, result.stderr);
    assert.equal(JSON.parse(readFileSync(path.join(f.target, "microcap_nav.json"), "utf8"))[1].daily_return, 0.01);
  } finally { rmSync(f.root, { recursive: true }); }
});

test("conflicting producer and legacy return columns stop publication", () => {
  const f = fixture();
  try {
    writeFileSync(path.join(f.input, "microcap_nav.csv"),
      "date,nav,return,daily_return,constituents\n2026-01-02,1,0,0.5,400\n");
    const before = readFileSync(path.join(f.target, "manifest.json"), "utf8");
    const result = run(f.input, f.target);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /Conflicting return/);
    assert.equal(readFileSync(path.join(f.target, "manifest.json"), "utf8"), before);
  } finally { rmSync(f.root, { recursive: true }); }
});


test("invalid existing manifest stops import without replacing reviewed metadata", () => {
  const f = fixture();
  try {
    const before = JSON.stringify({ ...f.manifest, sources: "not-a-source-list" });
    writeFileSync(path.join(f.target, "manifest.json"), before);
    const result = run(f.input, f.target);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /invalid structure/);
    assert.equal(readFileSync(path.join(f.target, "manifest.json"), "utf8"), before);
    assert.throws(() => readFileSync(path.join(f.target, "microcap_summary.json")));
  } finally { rmSync(f.root, { recursive: true }); }
});


test("aliased public target cannot overwrite the external source directory", () => {
  const f = fixture();
  try {
    const alias = path.join(f.root, "input-alias");
    symlinkSync(f.input, alias, process.platform === "win32" ? "junction" : "dir");
    const before = readFileSync(path.join(f.input, "microcap_summary.json"), "utf8");
    const result = run(f.input, alias);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /Public target must differ/);
    assert.equal(readFileSync(path.join(f.input, "microcap_summary.json"), "utf8"), before);
    assert.throws(() => readFileSync(path.join(f.input, "manifest.json")));
    assert.throws(() => readFileSync(path.join(f.input, "microcap_nav.json")));
  } finally { rmSync(f.root, { recursive: true }); }
});
