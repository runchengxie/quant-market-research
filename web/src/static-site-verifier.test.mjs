import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { verifyStaticSite } from "../scripts/verify-static-site.mjs";
import { publicDocs } from "./content/public-registry.ts";
import { englishCopy } from "./content/locale-copy.ts";

const routes = [
  ["index.html", "Research overview"],
  ["research/cashflow/index.html", "Cash-flow history"],
  ["research/cashflow/recovery/index.html", "Cash-flow drawdowns and recovery time"],
  ["research/microcap/index.html", "A-share micro-cap history"],
  ["research/microcap/cross-market-liquidity/index.html", "Cross-market micro-cap liquidity"],
  ["research/indices/index.html", "Index and ETF history"],
  ["research/style-factors-18y/index.html", "18-year A-share style factors"],
  ["research/liquidity/index.html", "Cross-market liquidity"],
  ["research/factors/low-turnover/index.html", "Low-turnover factor: what information remains?"],
  ["research/factors/pb-roe/index.html", "PB and ROE: historical comparison and evidence boundary"],
  ["research/index.html", "Explore data and charts by research question"],
  ["data-sources/index.html", "Every public snapshot has its own dates and boundaries"],
  ["search/index.html", "Search research, methods, and factor definitions"],
  ...publicDocs.map((doc) => [
    `docs/${doc.slug ? `${doc.slug}/` : ""}index.html`,
    doc.id.endsWith("-zh-CN") ? doc.title : englishCopy(doc).title,
  ]),
];

async function makeSite() {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "qmr-site-"));
  for (const [file, marker] of routes) {
    const destination = path.join(root, file);
    await fs.mkdir(path.dirname(destination), { recursive: true });
    await fs.writeFile(destination, `<html><h1>${marker}</h1></html>`);
  }
  for (const file of ["404.html", "search-index.json", "data/manifest.json", "data/research/recovery.json", ".nojekyll"]) {
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

test("static site verifier checks English HTML routes outside the required-route list", async (t) => {
  const root = await makeSite();
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  const newRoute = path.join(root, "research/new-topic/index.html");
  await fs.mkdir(path.dirname(newRoute), { recursive: true });
  await fs.writeFile(newRoute, "<html><body><main>历史实验</main></body></html>");

  assert.match(
    verifyStaticSite(root).join("\n"),
    /research\/new-topic\/index\.html: English route contains visible Chinese text/,
  );
});

test("static site verifier rejects NUL bytes in generated HTML", async (t) => {
  const root = await makeSite();
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  await fs.appendFile(path.join(root, "research/style-factors-18y/index.html"), "<small>同一\u0000\u0000历史序列</small>");
  assert.match(verifyStaticSite(root).join("\n"), /research\/style-factors-18y\/index\.html: HTML contains NUL bytes/);
});

test("static site verifier rejects malformed UTF-8 but accepts multibyte Chinese routes", async (t) => {
  const root = await makeSite();
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  await fs.appendFile(path.join(root, "docs/index.zh-CN/index.html"), "<p>完整中文、🧪与 café</p>");
  assert.deepEqual(verifyStaticSite(root), []);
  await fs.appendFile(path.join(root, "docs/index.zh-CN/index.html"), Buffer.from([0xe4, 0xb8]));
  assert.match(verifyStaticSite(root).join("\n"), /docs\/index\.zh-CN\/index\.html: HTML is not valid UTF-8/);
});
