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
  ["research/factors/low-turnover/index.html", "低换手因子：它保留了什么信息？"],
  ["research/index.html", "从研究问题进入数据与图表"],
  ["data-sources/index.html", "每份公开快照都有自己的日期和边界"],
  ["search/index.html", "搜索研究、方法与因子定义"],
  ["docs/research-closeout-status/index.html", "研究收口状态"],
  ["docs/research/factors/low-turnover/index.html", "低换手：它可能反映哪些特征"],
  ["docs/research/factors/pb-roe/index.html", "PB 与 ROE：怎样比较估值和盈利能力"],
  ["docs/research/factors/microcap/index.html", "微盘股：收益证据与水下时间"],
  ["docs/research/factors/smallcap-turnover-history/index.html", "小市值成交活跃度补充"],
  ["docs/research/factors/barra-factor-dictionary/index.html", "Barra 风格因子字典"],
  ["docs/research/factors/barra-source-inventory/index.html", "Barra 风格研究资料清单"],
];

async function makeSite() {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "qmr-site-"));
  for (const [file, marker] of routes) {
    const destination = path.join(root, file);
    await fs.mkdir(path.dirname(destination), { recursive: true });
    await fs.writeFile(destination, `<html><h1>${marker}</h1></html>`);
  }
  for (const file of ["404.html", "docs/index.html", "search-index.json", "data/manifest.json", "data/research/recovery.json", ".nojekyll"]) {
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

test("static site verifier rejects NUL bytes in generated HTML", async (t) => {
  const root = await makeSite();
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  await fs.appendFile(path.join(root, "research/style-factors-18y/index.html"), "<small>同一\u0000\u0000历史序列</small>");
  assert.match(verifyStaticSite(root).join("\n"), /research\/style-factors-18y\/index\.html: HTML contains NUL bytes/);
});

test("static site verifier rejects malformed UTF-8 but accepts multibyte text", async (t) => {
  const root = await makeSite();
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  await fs.appendFile(path.join(root, "docs/index.html"), "<p>完整中文、🧪与 café</p>");
  assert.deepEqual(verifyStaticSite(root), []);
  await fs.appendFile(path.join(root, "docs/index.html"), Buffer.from([0xe4, 0xb8]));
  assert.match(verifyStaticSite(root).join("\n"), /docs\/index\.html: HTML is not valid UTF-8/);
});
