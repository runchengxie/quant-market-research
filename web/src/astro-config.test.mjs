import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

test("Astro build configuration targets static GitHub Pages and React islands", () => {
  const config = readFileSync(new URL("../astro.config.mjs", import.meta.url), "utf8");

  assert.match(config, /output:\s*["']static["']/);
  assert.match(config, /site:\s*["']https:\/\/runchengxie\.github\.io["']/);
  assert.match(config, /base:\s*["']\/quant-market-research["']/);
  assert.match(config, /react\(\)/);
  assert.match(config, /outDir:\s*["']\.\/dist["']/);
});
