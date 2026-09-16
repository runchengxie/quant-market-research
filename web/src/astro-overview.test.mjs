import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const page = await readFile(new URL("./pages/index.astro", import.meta.url), "utf8");

test("Astro overview statically renders reviewed recovery and Barra evidence", () => {
  assert.match(page, /OverviewContent recovery=\{recovery\} barra=\{barra\}/);
  assert.match(page, /public\/data\/research\/recovery\.json/);
  assert.match(page, /public\/data\/barra\/barra_summary\.json/);
  assert.doesNotMatch(page, /client:(load|visible|idle)/);
});
