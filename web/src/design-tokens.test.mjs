import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const [tokens, webStyles] = await Promise.all([
  readFile(new URL("./theme-tokens.css", import.meta.url), "utf8"),
  readFile(new URL("./styles.css", import.meta.url), "utf8"),
]);

test("shared design tokens are the single source for the research and docs palettes", () => {
  for (const token of ["--paper", "--surface", "--ink", "--muted", "--rule", "--accent", "--accent-soft", "--font-body", "--font-heading", "--font-mono"]) {
    assert.match(tokens, new RegExp(`${token}:`));
  }
  assert.match(webStyles, /\.\/theme-tokens\.css/);
  assert.match(webStyles, /\.article-content/);
  assert.match(webStyles, /var\(--font-body\)/);
  assert.match(webStyles, /var\(--font-heading\)/);
});
