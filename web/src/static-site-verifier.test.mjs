import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { verifyStaticSite } from "../scripts/verify-static-site.mjs";
import { publicDocs } from "./content/public-registry.ts";
import { englishCopy } from "./content/locale-copy.ts";

const routes = [
  ["research/overseas-leadlag/index.html", "Overseas signals and the A-share open"],
  ["index.html", "Research overview"],
  ["research/style-theme-rotation/index.html", "Style and theme rotation: from signals to ETF portfolios"],
  ["research/etf-rotation/index.html", "Style and theme rotation"],
  ["research/hotsector/index.html", "Style and theme rotation"],
  ["research/cashflow/index.html", "Cash-flow index research"],
  ["research/cashflow/recovery/index.html", "Cash-flow index research"],
  ["research/microcap/index.html", "A-share micro-cap history"],
  ["research/microcap/cross-market-liquidity/index.html", "Cross-market micro-cap liquidity"],
  ["research/indices/index.html", "Long-run index and ETF performance"],
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
  await fs.copyFile(new URL('../public/data/rotation-evidence-release.json',import.meta.url),path.join(root,'data/rotation-evidence-release.json'));
  await fs.copyFile(new URL('../public/data/rotation-release-index.json',import.meta.url),path.join(root,'data/rotation-release-index.json'));
  await fs.cp(new URL('../public/data/rotation/',import.meta.url),path.join(root,'data/rotation'),{recursive:true});
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
  await fs.writeFile(path.join(root, "index.html"), "<html>/home/example private output</html>");
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

test('inert translation templates do not count as visible English copy, but still undergo private-path scans', async (t) => {
  const root = await makeSite();
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  const file = path.join(root, 'index.html');
  await fs.appendFile(file, '<template data-document-translation><h1>中文正文</h1></template>');
  assert.deepEqual(verifyStaticSite(root), []);
  await fs.appendFile(file, '<template>/home/private/report</template>');
  assert.match(verifyStaticSite(root).join('\n'), /forbidden local path/);
});


test('downloadable Markdown is included in public-boundary scanning', async (t) => {
  const root = await makeSite();
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  await fs.mkdir(path.join(root, 'downloads'));
  await fs.writeFile(path.join(root, 'downloads/report.md'), '# Report\n/home/private/generated-report');
  assert.match(verifyStaticSite(root).join('\n'), /forbidden local path/);
});

 test('static verifier rejects a missing or corrupt rotation release',async(t)=>{const root=await makeSite();t.after(()=>fs.rm(root,{recursive:true,force:true}));await fs.writeFile(path.join(root,'data/rotation-evidence-release.json'),'{}');assert.match(verifyStaticSite(root).join('\n'),/invalid reviewed rotation evidence/);});

test('static verifier rejects a missing release registry',async(t)=>{
 const root=await makeSite();t.after(()=>fs.rm(root,{recursive:true,force:true}));
 await fs.rm(path.join(root,'data/rotation-release-index.json'),{force:true});
 assert.match(verifyStaticSite(root).join('\n'),/rotation release registry/);
});
