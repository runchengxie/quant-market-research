import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.dirname(fileURLToPath(import.meta.url));

test("research and documentation directories render English-first localized copy", async () => {
  const research = await fs.readFile(path.join(root, "pages/research/index.astro"), "utf8");
  const docs = await fs.readFile(path.join(root, "pages/docs/index.astro"), "utf8");
  const copy = await fs.readFile(path.join(root, "content/locale-copy.ts"), "utf8");

  assert.match(research, /titleEn="Research topics"/);
  assert.match(research, /data-en="Explore data and charts by research question"/);
  assert.match(research, /data-zh="从研究问题进入数据与图表"/);
  assert.match(docs, /titleEn="Methods and dictionary"/);
  assert.match(docs, /data-en="Public documentation"/);
  assert.match(docs, /filter\(\(doc\) => !doc\.id\.endsWith\('-zh-CN'\)\)/);
  for (const pageId of ["cashflow", "microcap", "indices", "style", "pb-roe", "low-turnover-method", "barra-factor-dictionary"]) {
    assert.ok(copy.includes(pageId), `missing English copy for ${pageId}`);
  }
});
