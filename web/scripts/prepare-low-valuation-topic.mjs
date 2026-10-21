import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { resolve, relative } from 'node:path';
import { createHash } from 'node:crypto';
import { buildTopicEvidence } from '../src/lib/valuation-topic.ts';

const args = Object.fromEntries(process.argv.slice(2).reduce((pairs, item, i, all) => i % 2 ? pairs : [...pairs, [item, all[i + 1]]], []));
if (!args['--gap-audit'] || !args['--output'] || !args['--receipt']) throw new Error('Specify --gap-audit --output --receipt');
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const sources = {
  valuation_panel: resolve('public/data/valuation_panel_reviewed.json'),
  historical_factors: resolve('public/data/barra/historical_factor_summary.json'),
  historical_manifest: resolve('public/data/barra/barra_source_manifest.json'),
  endpoint_gap_audit: resolve(args['--gap-audit']),
};
const raw = Object.fromEntries(Object.entries(sources).map(([key, path]) => [key, readFileSync(path)]));
const parsed = Object.fromEntries(Object.entries(raw).map(([key, bytes]) => [key, JSON.parse(bytes.toString('utf8'))]));
const data = { ...buildTopicEvidence(parsed.valuation_panel, parsed.historical_factors, parsed.historical_manifest, parsed.endpoint_gap_audit),
  source_sha256: Object.fromEntries(Object.entries(raw).map(([key, bytes]) => [key, sha(bytes)])) };
const output = resolve(args['--output']);
const receipt = resolve(args['--receipt']);
if (existsSync(output) || existsSync(receipt)) throw new Error('Refusing to overwrite topic output or receipt');
const bytes = Buffer.from(JSON.stringify(data, null, 2) + '\n');
writeFileSync(output, bytes, { flag: 'wx' });
writeFileSync(receipt, JSON.stringify({ status: 'derived_aggregates_only_no_research_rerun', inputs: sources,
  input_sha256: data.source_sha256, output, output_sha256: sha(bytes), source_files: {
    [relative(resolve('..'), resolve('scripts/prepare-low-valuation-topic.mjs'))]: sha(readFileSync('scripts/prepare-low-valuation-topic.mjs')),
    [relative(resolve('..'), resolve('src/lib/valuation-topic.ts'))]: sha(readFileSync('src/lib/valuation-topic.ts')),
  } }, null, 2) + '\n', { flag: 'wx' });
console.log(`Prepared aggregate topic evidence: ${bytes.length} bytes`);
