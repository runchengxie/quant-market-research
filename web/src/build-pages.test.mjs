import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

test("pages build orchestrates Astro, MkDocs, nojekyll, and static verification", () => {
  const source = readFileSync(new URL("../scripts/build-pages.mjs", import.meta.url), "utf8");
  assert.ok(source.indexOf('["run", "build"]') < source.indexOf('"mkdocs"'));
  assert.match(source, /\.nojekyll/);
  assert.match(source, /verify:static/);
});
