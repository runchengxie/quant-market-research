import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const web = process.cwd();
const reference = path.resolve(web, "../.build/mkdocs-reference");
const destination = path.join(web, "dist/docs");
const sharedAssets = ["assets", "css", "img", "js", "search", "webfonts"];
const companions = [
  "index.zh-CN",
  "research-closeout-status.zh-CN",
  "research/factors/low-turnover.zh-CN",
  "research/factors/pb-roe.zh-CN",
  "research/factors/microcap.zh-CN",
  "research/experiments/microcap-execution-diagnostic-20260928.zh-CN",
  "research/factors/smallcap-turnover-history.zh-CN",
  "research/factors/barra-factor-dictionary.zh-CN",
  "research/factors/barra-source-inventory.zh-CN",
];

for (const asset of sharedAssets) {
  const source = path.join(reference, asset);
  const target = path.join(destination, asset);
  if (!fs.existsSync(source)) throw new Error(`MkDocs shared asset missing: ${asset}`);
  fs.cpSync(source, target, { recursive: true });
}

for (const slug of companions) {
  const source = path.join(reference, slug);
  const target = path.join(destination, slug);
  if (!fs.existsSync(source)) throw new Error(`MkDocs locale companion missing: ${slug}`);
  fs.cpSync(source, target, { recursive: true });
}
