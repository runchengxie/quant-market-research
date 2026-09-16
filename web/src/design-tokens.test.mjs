import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const [tokens, webStyles, docsStyles, mkdocs] = await Promise.all([
  readFile(new URL("../../docs/assets/theme-tokens.css", import.meta.url), "utf8"),
  readFile(new URL("./styles.css", import.meta.url), "utf8"),
  readFile(new URL("../../docs/assets/docs.css", import.meta.url), "utf8"),
  readFile(new URL("../../mkdocs.yml", import.meta.url), "utf8"),
]);

test("shared design tokens are the single source for the research and docs palettes", () => {
  for (const token of ["--paper", "--surface", "--ink", "--muted", "--rule", "--accent", "--accent-soft", "--font-body", "--font-heading", "--font-mono"]) {
    assert.match(tokens, new RegExp(`${token}:`));
  }
  assert.match(webStyles, /\.\.\/\.\.\/docs\/assets\/theme-tokens\.css/);
  assert.match(docsStyles, /theme-tokens\.css/);
  assert.match(mkdocs, /- assets\/theme-tokens\.css[\s\S]*- assets\/docs\.css/);
  assert.match(mkdocs, /!\/assets\/theme-tokens\.css/);
});
