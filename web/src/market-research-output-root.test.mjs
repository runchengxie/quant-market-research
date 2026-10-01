import assert from "node:assert/strict";
import test from "node:test";
import { resolveMarketResearchOutputRoot } from "../scripts/market-research-output-root.mjs";

test("uses the canonical per-project data root by default", () => {
  assert.equal(
    resolveMarketResearchOutputRoot({ env: {}, home: "/home/example" }),
    "/home/example/data/quant/quant-market-research/outputs",
  );
});

test("uses QUANT_DATA_ROOT when configured", () => {
  assert.equal(
    resolveMarketResearchOutputRoot({
      env: { QUANT_DATA_ROOT: "/mnt/research" },
      home: "/home/example",
    }),
    "/mnt/research/quant-market-research/outputs",
  );
});

test("lets the dedicated output variable override the canonical root", () => {
  assert.equal(
    resolveMarketResearchOutputRoot({
      env: {
        QUANT_DATA_ROOT: "/mnt/research",
        MARKET_RESEARCH_OUTPUT_ROOT: "/srv/results",
      },
      home: "/home/example",
    }),
    "/srv/results",
  );
});
