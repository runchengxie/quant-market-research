import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { verifyStaticSite } from "../scripts/verify-static-site.mjs";

const routes = [
  ["index.html", "研究总览"],
  ["research/cashflow/index.html", "现金流历史研究"],
  ["research/cashflow/recovery/index.html", "现金流回撤与回本时间"],
  ["research/microcap/index.html", "A 股微盘历史研究"],
  ["research/microcap/cross-market-liquidity/index.html", "跨市场小微盘流动性"],
  ["research/indices/index.html", "指数与 ETF 历史表现"],
  ["research/style-factors-18y/index.html", "18 年 A 股风格因子研究"],
  ["research/liquidity/index.html", "跨市场流动性"],
];

async function makeSite() {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "qmr-site-"));
  for (const [file, marker] of routes) {
    const destination = path.join(root, file);
    await fs.mkdir(path.dirname(destination), { recursive: true });
    await fs.writeFile(destination, `<html><h1>${marker}</h1></html>`);
  }
  for (const file of ["404.html", "docs/index.html", "docs/assets/docs.css", "docs/assets/theme-tokens.css", "data/manifest.json", "data/research/recovery.json", ".nojekyll"]) {
    const destination = path.join(root, file);
    await fs.mkdir(path.dirname(destination), { recursive: true });
    await fs.writeFile(destination, file.endsWith(".html") ? "<html>Docs</html>" : "{}");
  }
  return root;
}

test("static site verifier accepts all routes and required public artifacts", async (t) => {
  const root = await makeSite();
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  assert.deepEqual(verifyStaticSite(root), []);
});

test("static site verifier reports missing routes and private material", async (t) => {
  const root = await makeSite();
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  await fs.rm(path.join(root, "research/microcap/index.html"));
  await fs.writeFile(path.join(root, "index.html"), "<html>/home/richard private output</html>");
  const errors = verifyStaticSite(root).join("\n");
  assert.match(errors, /Missing route output: research\/microcap\/index\.html/);
  assert.match(errors, /forbidden local path or credential marker/);
});
