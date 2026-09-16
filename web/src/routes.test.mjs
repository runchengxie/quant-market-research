import test from "node:test";
import assert from "node:assert/strict";
import { LEGACY_HASH_ROUTES, PUBLIC_ROUTES, legacyHashTarget, withBase } from "./lib/routes.ts";

test("public routes and legacy hashes preserve every existing research entry", () => {
  assert.deepEqual(Object.values(PUBLIC_ROUTES), [
    "/",
    "/research/cashflow/",
    "/research/cashflow/recovery/",
    "/research/microcap/",
    "/research/microcap/cross-market-liquidity/",
    "/research/indices/",
    "/research/style-factors-18y/",
    "/research/liquidity/",
  ]);

  for (const hash of ["", "#overview", "#cashflow", "#cashflow-recovery", "#microcap", "#microcap-recovery", "#cross-market", "#style", "#style-factors-18y", "#indices", "#liquidity"]) {
    assert.ok(LEGACY_HASH_ROUTES[hash], `missing legacy entry for ${hash}`);
  }
  assert.equal(LEGACY_HASH_ROUTES["#microcap-recovery"], "/research/microcap/#microcap-recovery");
});

test("withBase adds a GitHub Pages subpath once and keeps root deployments clean", () => {
  assert.equal(withBase("/research/microcap/", "/quant-market-research/"), "/quant-market-research/research/microcap/");
  assert.equal(withBase("/", "/"), "/");
});

test("the canonical root URL does not redirect itself while old hashes still map", () => {
  assert.equal(legacyHashTarget("", "/quant-market-research/"), null);
  assert.equal(legacyHashTarget("#overview", "/quant-market-research/"), "/quant-market-research/");
  assert.equal(legacyHashTarget("#microcap-recovery", "/quant-market-research/"), "/quant-market-research/research/microcap/#microcap-recovery");
});
