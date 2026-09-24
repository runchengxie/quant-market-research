import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repository = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");

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

function filesBelow(directory) {
  if (!fs.existsSync(directory)) return [];
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const file = path.join(directory, entry.name);
    return entry.isDirectory() ? filesBelow(file) : [file];
  });
}

function resolveLocalReference(reference, htmlFile, dist) {
  if (/^(?:[a-z]+:|\/\/|#|data:|javascript:|mailto:)/i.test(reference)) return null;
  const withoutSuffix = reference.split(/[?#]/, 1)[0];
  const pageBase = "/quant-market-research";
  let localPath;
  if (withoutSuffix.startsWith("/")) {
    if (withoutSuffix !== pageBase && !withoutSuffix.startsWith(`${pageBase}/`)) return `URL is outside the GitHub Pages base: ${reference}`;
    localPath = withoutSuffix.slice(pageBase.length).replace(/^\//, "");
  } else {
    localPath = path.relative(dist, path.resolve(path.dirname(htmlFile), withoutSuffix));
  }
  const target = path.resolve(dist, localPath || ".");
  if (!target.startsWith(`${dist}${path.sep}`) && target !== dist) return `URL escapes build directory: ${reference}`;
  const candidates = [target, path.join(target, "index.html"), path.join(target, "404.html")];
  return candidates.some((candidate) => fs.existsSync(candidate)) ? null : `Missing local URL target: ${reference}`;
}

export function verifyStaticSite(distDirectory) {
  const dist = path.resolve(distDirectory);
  const errors = [];

  for (const [relative, marker] of routes) {
    const file = path.join(dist, relative);
    if (!fs.existsSync(file)) {
      errors.push(`Missing route output: ${relative}`);
      continue;
    }
    const html = fs.readFileSync(file, "utf8");
    if (!html.includes(marker)) errors.push(`Route output is missing its title marker: ${relative}`);
  }

  for (const relative of ["404.html", "docs/index.html", "search-index.json", "data/manifest.json", "data/research/recovery.json"]) {
    if (!fs.existsSync(path.join(dist, relative))) errors.push(`Missing required public artifact: ${relative}`);
  }

  for (const htmlFile of filesBelow(dist).filter((file) => file.endsWith(".html"))) {
    const bytes = fs.readFileSync(htmlFile);
    const relative = path.relative(dist, htmlFile);
    if (bytes.includes(0)) errors.push(`${relative}: HTML contains NUL bytes`);
    let html;
    try {
      html = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
    } catch {
      errors.push(`${relative}: HTML is not valid UTF-8`);
      continue;
    }
    const references = [...html.matchAll(/(?:href|src|component-url|renderer-url)="([^"]+)"/g)].map((match) => match[1]);
    for (const reference of references) {
      const error = resolveLocalReference(reference, htmlFile, dist);
      if (error) errors.push(`${path.relative(dist, htmlFile)}: ${error}`);
    }
  }

  const publicText = filesBelow(dist).filter((file) => /\.(?:html|js|css|json|csv|txt|xml|svg)$/i.test(file))
    .map((file) => fs.readFileSync(file, "utf8")).join("\n");
  if (/\/home\/|\/Users\/|\/mnt\/|TUSHARE_TOKEN=|API_KEY=|SECRET_KEY=/.test(publicText)) {
    errors.push("Public build contains a forbidden local path or credential marker");
  }
  if (!fs.existsSync(path.join(dist, ".nojekyll"))) errors.push("Missing .nojekyll marker");
  return errors;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const dist = process.argv[2] ? path.resolve(process.argv[2]) : path.join(repository, "dist");
  const errors = verifyStaticSite(dist);
  if (errors.length) {
    console.error(errors.map((error) => `- ${error}`).join("\n"));
    process.exitCode = 1;
  } else {
    console.log(`Verified public static site: ${dist}`);
  }
}
