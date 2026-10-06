import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

test("Pages build orchestrates Astro, nojekyll, and static verification", () => {
  const source = readFileSync(new URL("../scripts/build-pages.mjs", import.meta.url), "utf8");
  assert.match(source, /\["run", "build"\]/);
  assert.doesNotMatch(source, /mkdocs/i);
  assert.match(source, /\.nojekyll/);
  assert.match(source, /verify:static/);
});
