import { createHash } from 'node:crypto';
import { readFile, readdir, stat, writeFile, access } from 'node:fs/promises';
import { join, relative, resolve } from 'node:path';
import process from 'node:process';
import { chromium } from 'playwright';

export const LEGACY_ROUTES = [
  '/',
  '/research/cashflow/',
  '/research/cashflow/recovery/',
  '/research/microcap/',
  '/research/microcap/cross-market-liquidity/',
  '/research/indices/',
  '/research/style-factors-18y/',
  '/research/liquidity/',
  '/research/factors/low-turnover/',
  '/docs/',
  '/docs/research-closeout-status/',
  '/docs/research/factors/low-turnover/',
  '/docs/research/factors/microcap/',
  '/docs/research/factors/smallcap-turnover-history/',
  '/docs/research/factors/barra-factor-dictionary/',
  '/docs/research/factors/barra-source-inventory/',
  '/404.html',
];

function mainSelector(html) {
  if (/<main\b/i.test(html)) return /<main\b[^>]*>([\s\S]*?)<\/main>/i.exec(html)?.[1] ?? '';
  return /<[^>]+role=["']main["'][^>]*>([\s\S]*?)<\/[^>]+>/i.exec(html)?.[1] ?? '';
}

export async function collectHeadingAnchors(html) {
  const body = mainSelector(html);
  const anchors = [];
  const headingPattern = /<h([1-6])\b([^>]*)>([\s\S]*?)<\/h\1>/gi;
  for (const match of body.matchAll(headingPattern)) {
    const attrs = match[2];
    const id = /\bid=["']([^"']+)["']/i.exec(attrs)?.[1];
    if (!id || /^:R[^:]*:/.test(id)) continue;
    const text = match[3].replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
    anchors.push({ id, text, level: Number(match[1]) });
  }
  const named = /\b(?:span|a|div)\b[^>]*\bid=["']([^"']+)["'][^>]*>/gi;
  for (const match of body.matchAll(named)) {
    const id = match[1];
    if (/^:R[^:]*:/.test(id) || anchors.some((item) => item.id === id)) continue;
    anchors.push({ id, text: '', level: 0 });
  }
  return anchors;
}

async function filesUnder(root) {
  const output = [];
  async function walk(dir) {
    for (const entry of await readdir(dir, { withFileTypes: true })) {
      const full = join(dir, entry.name);
      if (entry.isDirectory()) await walk(full);
      else output.push(full);
    }
  }
  try { await walk(root); } catch (error) { if (error.code !== 'ENOENT') throw error; }
  return output.sort();
}

export async function hashPublicFiles(root) {
  const dataRoot = resolve(root, 'data');
  const files = await filesUnder(dataRoot);
  const hashes = {};
  for (const file of files) {
    const key = relative(resolve(root), file).replaceAll('\\', '/');
    hashes[key] = createHash('sha256').update(await readFile(file)).digest('hex');
  }
  return hashes;
}

async function contractForPage(page, route) {
  await page.goto(`http://127.0.0.1:4321/quant-market-research${route}`, { waitUntil: 'domcontentloaded' });
  return { route, anchors: await page.evaluate(() => {
    const main = document.querySelector('main,[role="main"]');
    if (!main) return [];
    return [...main.querySelectorAll('h1,h2,h3,h4,h5,h6,[id]')]
      .filter((node) => !/^:R[^:]*:/.test(node.id))
      .map((node) => ({ id: node.id, text: node.matches('h1,h2,h3,h4,h5,h6') ? node.textContent.trim().replace(/\s+/g, ' ') : '', level: node.matches('h1,h2,h3,h4,h5,h6') ? Number(node.tagName.slice(1)) : 0 }))
      .filter((item, index, all) => item.id && all.findIndex((candidate) => candidate.id === item.id) === index);
  }) };
}

export async function captureSiteContract(dist) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ javaScriptEnabled: false });
  const routes = [];
  try {
    for (const route of LEGACY_ROUTES) routes.push(await contractForPage(page, route));
  } finally { await browser.close(); }
  return { version: 1, routes, data: await hashPublicFiles(dist) };
}

async function readJson(path) { return JSON.parse(await readFile(path, 'utf8')); }
async function exists(path) { try { await access(path); return true; } catch { return false; } }

export async function checkSiteContract(dist, contractPath, hashPath) {
  const expected = await readJson(contractPath);
  const actual = await captureSiteContract(dist);
  const shape = (routes) => routes.map((route) => ({ route: route.route, anchors: route.anchors.map(({ id, level }) => ({ id, level })) }));
  if (JSON.stringify(shape(expected.routes)) !== JSON.stringify(shape(actual.routes))) throw new Error('legacy route or anchor contract changed');
  const expectedHashes = await readJson(hashPath);
  if (JSON.stringify(expectedHashes) !== JSON.stringify(actual.data)) throw new Error('public data snapshot hashes changed');
  return true;
}

async function main() {
  const [command, dist, contractPath, hashPath] = process.argv.slice(2);
  if (!['capture', 'check'].includes(command) || !dist || !contractPath || !hashPath) throw new Error('usage: site-contract.mjs <capture|check> <dist> <contract-file> <hash-file>');
  if (command === 'capture' && (await exists(contractPath) || await exists(hashPath))) throw new Error('refusing to overwrite an existing site contract');
  if (command === 'capture') {
    const contract = await captureSiteContract(dist);
    await writeFile(contractPath, `${JSON.stringify({ version: contract.version, routes: contract.routes }, null, 2)}\n`);
    await writeFile(hashPath, `${JSON.stringify(contract.data, null, 2)}\n`);
  } else await checkSiteContract(dist, contractPath, hashPath);
}

if (import.meta.url === `file://${process.argv[1]}`) main().catch((error) => { console.error(error.stack || error); process.exitCode = 1; });
