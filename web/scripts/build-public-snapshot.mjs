import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { parseArgs } from "node:util";
import { parseCsv } from "./csv.mjs";
import { resolveMarketResearchOutputRoot } from "./market-research-output-root.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const repository = path.resolve(here, "../..");
const sourceLabel = "market-research A-share rule reconstruction";

// Resolve existing ancestors as well, so a staged directory under a symlink
// cannot disguise an alias of the source directory.
function realDirectory(directory) {
  const resolved = path.resolve(directory);
  if (fs.existsSync(resolved)) return fs.realpathSync(resolved);
  const parent = path.dirname(resolved);
  return parent === resolved ? resolved : path.join(realDirectory(parent), path.basename(resolved));
}

export function buildPublicSnapshot({
  outputRoot = resolveMarketResearchOutputRoot(),
  targetRoot = path.resolve(here, "../public/data"),
} = {}) {
  const output = fs.realpathSync(path.resolve(outputRoot));
  const target = realDirectory(targetRoot);
  const relative = path.relative(repository, output);
  if (relative === "" || (!relative.startsWith(`..${path.sep}`) && relative !== ".." && !path.isAbsolute(relative))) {
    throw new Error("Research input must be outside the code repository");
  }
  if (output === target) throw new Error("Public target must differ from research input");

  // Read every input before modifying public output. Publication still requires review.
  const summary = JSON.parse(fs.readFileSync(path.join(output, "microcap_summary.json"), "utf8"));
  if (!summary || typeof summary !== "object" || Array.isArray(summary)) {
    throw new Error("Microcap summary must be an object");
  }
  const rows = parseCsv(fs.readFileSync(path.join(output, "microcap_nav.csv"), "utf8"));
  const nav = rows.map((row) => {
    // The Python producer names this column `return`; public JSON keeps `daily_return`.
    const dailyReturn = row.return ?? row.daily_return;
    const values = [row.nav, dailyReturn, row.constituents];
    if (!/^\d{4}-\d{2}-\d{2}$/.test(row.date) || values.some((value) => !value?.trim() || !Number.isFinite(Number(value)))) {
      throw new Error("Microcap NAV rows require a date and finite numeric values");
    }
    if (row.return !== undefined && row.daily_return !== undefined &&
        (!row.daily_return.trim() || !Number.isFinite(Number(row.daily_return)) || Number(row.return) !== Number(row.daily_return))) {
      throw new Error("Conflicting return and daily_return values");
    }
    return { date: row.date, nav: Number(row.nav), daily_return: Number(dailyReturn), constituents: Number(row.constituents) };
  });
  if (!nav.length) throw new Error("Microcap NAV must contain at least one observation");

  const manifestPath = path.join(target, "manifest.json");
  const existing = fs.existsSync(manifestPath) ? JSON.parse(fs.readFileSync(manifestPath, "utf8")) : {};
  if (!existing || typeof existing !== "object" || Array.isArray(existing)) throw new Error("Public manifest must be an object");
  if ((existing.sources !== undefined && (!Array.isArray(existing.sources) || existing.sources.some((value) => typeof value !== "string"))) ||
      [existing.markets, existing.snapshots].some((value) => value !== undefined && (!value || typeof value !== "object" || Array.isArray(value)))) {
    throw new Error("Public manifest sources, markets and snapshots have invalid structure");
  }
  const generatedAt = new Date().toISOString();
  const manifest = {
    ...existing,
    generated_at: generatedAt,
    sources: [...new Set([...(existing.sources ?? []), sourceLabel])],
    markets: {
      hk: "pending local refresh", us: "pending local refresh", jp: "pending local refresh",
      ...existing.markets, a_share: "published",
    },
    privacy: "Derived snapshot only; raw market data and local paths are excluded.",
    snapshots: {
      ...existing.snapshots,
      microcap: {
        // The current CLI summary has no reviewed eligibility/quality receipt.
        // Importing new results cannot inherit an older snapshot's validation.
        generated_at: generatedAt, coverage_start: nav[0].date, coverage_end: nav.at(-1).date,
        source: summary.source_label ?? sourceLabel, quality_status: "incomplete",
        caveats: summary.caveats ?? [],
      },
    },
  };
  fs.mkdirSync(target, { recursive: true });
  for (const [name, value] of Object.entries({ microcap_summary: summary, microcap_nav: nav, manifest })) {
    fs.writeFileSync(path.join(target, `${name}.json`), `${JSON.stringify(value, null, 2)}\n`);
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  const { values } = parseArgs({ options: { "target-root": { type: "string" } } });
  buildPublicSnapshot({ targetRoot: values["target-root"] });
}
