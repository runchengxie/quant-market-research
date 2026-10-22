import { validateRotationEvidence } from "../src/content/rotation-evidence.server.ts";
import fs from "node:fs";
import {createHash} from "node:crypto";
import {validateIndexedBinding,validateReleaseIndex} from "../src/content/rotation-extension.ts";
import {validateReviewedRotationEnvelope} from "../src/content/rotation-operations.server.ts";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { publicDocs } from "../src/content/public-registry.ts";
import { englishCopy } from "../src/content/locale-copy.ts";

const repository = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");

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
  ["research/factors/low-turnover/index.html", "Low-turnover stocks and subsequent returns"],
  ["research/factors/pb-roe/index.html", "PB and ROE: historical comparison and evidence boundary"],
  ["research/index.html", "Current findings by topic"],
  ["data-sources/index.html", "Every public snapshot has its own dates and boundaries"],
  ["search/index.html", "Search research, methods, and factor definitions"],
  ...publicDocs.map((doc) => [
    `docs/${doc.slug ? `${doc.slug}/` : ""}index.html`,
    doc.id.endsWith("-zh-CN") ? doc.title : englishCopy(doc).title,
  ]),
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
  try {
    const release=JSON.parse(fs.readFileSync(path.join(dist,"data/rotation-evidence-release.json"),"utf8"));
    if(Object.keys(release).sort().join(',')!=='asset,review')throw Error('Invalid envelope');
    validateRotationEvidence(release.asset,release.review);
  } catch(error) { errors.push(`Missing or invalid reviewed rotation evidence: ${error.message}`); }


  try {
    const index=validateReleaseIndex(JSON.parse(fs.readFileSync(path.join(dist,"data/rotation-release-index.json"),"utf8")));
    for(const entry of index.releases){
      const raw=fs.readFileSync(path.join(dist,"data",entry.path));
      if(createHash('sha256').update(raw).digest('hex')!==entry.sha256)throw Error('Indexed release hash mismatch');
      const envelope=JSON.parse(raw.toString());
      validateIndexedBinding(entry,envelope);
      if(Object.keys(envelope).sort().join()!=='asset,review')throw Error('Invalid indexed envelope');
      validateReviewedRotationEnvelope(envelope);
      if(envelope.review.content_sha256!==entry.content_sha256||envelope.review.reviewer!==entry.reviewer)throw Error('Index review binding mismatch');
    }
  } catch(error){errors.push(`Missing or invalid rotation release registry: ${error.message}`);}


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
      .replace(/<template\b[^>]*>[\s\S]*?<\/template>/gi, " ")
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

  const publicText = filesBelow(dist).filter((file) => /\.(?:html|js|css|json|csv|txt|xml|svg|md)$/i.test(file))
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
