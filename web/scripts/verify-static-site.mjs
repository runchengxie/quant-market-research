import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repository = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");

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
  ["docs/research-closeout-status/index.html", "Research closeout status"],
  ["docs/research/factors/low-turnover/index.html", "Low turnover: what might it represent?"],
  ["docs/research/factors/pb-roe/index.html", "PB and ROE: comparing valuation and profitability"],
  ["docs/research/factors/microcap/index.html", "Microcaps: return evidence and underwater periods"],
  ["docs/research/factors/smallcap-turnover-history/index.html", "Small-cap turnover history, 2008–2014"],
  ["docs/research/factors/barra-factor-dictionary/index.html", "Barra factor dictionary"],
  ["docs/research/factors/barra-source-inventory/index.html", "Barra research source inventory"],
  ["docs/index.zh-CN/index.html", "Quant Market Research 研究说明"],
  ["docs/research-closeout-status.zh-CN/index.html", "研究收口状态"],
  ["docs/research/factors/low-turnover.zh-CN/index.html", "低换手：它可能反映哪些特征"],
  ["docs/research/factors/pb-roe.zh-CN/index.html", "PB 与 ROE：怎样比较估值和盈利能力"],
  ["docs/research/factors/microcap.zh-CN/index.html", "微盘股：收益证据与水下时间"],
  ["docs/research/experiments/microcap-execution-diagnostic-20260928.zh-CN/index.html", "微盘组合公共执行模拟诊断"],
  ["docs/research/factors/smallcap-turnover-history.zh-CN/index.html", "小市值成交活跃度补充"],
  ["docs/research/factors/barra-factor-dictionary.zh-CN/index.html", "Barra 风格因子字典"],
  ["docs/research/factors/barra-source-inventory.zh-CN/index.html", "Barra 风格研究资料清单"],
];

function filesBelow(directory) {
  if (!fs.existsSync(directory)) return [];
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const file = path.join(directory, entry.name);
    return entry.isDirectory() ? filesBelow(file) : [file];
  });
}

function isChineseLocaleRoute(relativePath) {
  return /(?:^|\/)[^/]*\.zh-CN(?:\/|$)/i.test(relativePath)
    || /(?:^|\/)zh-CN(?:\/|$)/i.test(relativePath);
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

  for (const file of filesBelow(dist).filter((candidate) => candidate.endsWith(".html"))) {
    const relative = path.relative(dist, file).split(path.sep).join("/");
    if (isChineseLocaleRoute(relative)) continue;
    if (!fs.existsSync(file)) continue;
    const html = fs.readFileSync(file, "utf8")
      .replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, " ")
      .replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, " ")
      .replace(/<button\b[^>]*class="locale-toggle"[^>]*>[\s\S]*?<\/button>/gi, " ")
      .replace(/<[^>]+>/g, " ");
    if (/[\u4e00-\u9fff]/.test(html)) errors.push(`${relative}: English route contains visible Chinese text`);
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
