import test from "node:test";
import assert from "node:assert/strict";
import { parseCsv, publicDataUrl } from "./lib/public-data.ts";

test("public snapshot URLs work on GitHub Pages and root deployments", () => {
  assert.equal(publicDataUrl("index/microcap/nav.csv", "/quant-market-research/"), "/quant-market-research/data/index/microcap/nav.csv");
  assert.equal(publicDataUrl("/smallcap_turnover.json", "/"), "/data/smallcap_turnover.json");
});

test("shared CSV parser preserves quoted commas and escaped quotes", () => {
  assert.deepEqual(parseCsv('name,note\n"自由现金流,指数","a ""quoted"" note"\n'), [
    { name: "自由现金流,指数", note: 'a "quoted" note' },
  ]);
});
