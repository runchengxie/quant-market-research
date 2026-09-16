import test from "node:test";
import assert from "node:assert/strict";
import { parseCsv } from "../scripts/csv.mjs";

test("shared publisher CSV parser handles quoted fields and embedded newlines", () => {
  assert.deepEqual(parseCsv('name,note\n"现金流,指数","第一行\n第二行"\n'), [
    { name: "现金流,指数", note: "第一行\n第二行" },
  ]);
});
