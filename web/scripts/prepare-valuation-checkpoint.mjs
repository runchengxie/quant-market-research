import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { createHash } from 'node:crypto';
import { parseCsv } from './csv.mjs';
import { buildAuditEvidence, buildCheckpointEvidence } from '../src/lib/valuation-checkpoint.ts';

const args = Object.fromEntries(process.argv.slice(2).reduce((pairs, item, i, all) => i % 2 ? pairs : [...pairs, [item, all[i + 1]]], []));
for (const key of ['--ledger-root', '--followup-root', '--fill-audit', '--persisted-audit', '--output', '--receipt']) if (!args[key]) throw new Error(`Missing ${key}`);
const ledgerRoot = resolve(args['--ledger-root']), followupRoot = resolve(args['--followup-root']);
const output = resolve(args['--output']), receiptPath = resolve(args['--receipt']);
if (existsSync(receiptPath)) throw new Error('Refusing to overwrite prepared receipt');
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const inputs = {}, hashes = {};
function read(path, key) { const bytes = readFileSync(path); inputs[key] = path; hashes[key] = sha(bytes); return bytes; }
const ledgerReceipt = JSON.parse(read(resolve(ledgerRoot, 'receipt.json'), 'ledger_receipt'));
const followupReceipt = JSON.parse(read(resolve(followupRoot, 'receipt.json'), 'followup_receipt'));
if (ledgerReceipt.status !== 'completed_unpublished_proxy_checkpoint' || followupReceipt.status !== 'completed_unpublished_exploratory_diagnostics') throw new Error('Incomplete source receipt');
function verified(root, receipt, file, key, csv = false) {
  const bytes = read(resolve(root, file), key);
  if (sha(bytes) !== receipt.outputs[file]) throw new Error(`Source hash mismatch: ${key}`);
  return csv ? parseCsv(bytes.toString('utf8')) : JSON.parse(bytes);
}
const payload = buildCheckpointEvidence({
  ledger: verified(ledgerRoot, ledgerReceipt, 'summary.json', 'ledger_summary'),
  actions: verified(ledgerRoot, ledgerReceipt, 'action_audit.json', 'action_audit'),
  conditions: verified(followupRoot, followupReceipt, 'conditions.json', 'condition_comparison'),
  limitations: verified(followupRoot, followupReceipt, 'limitations.json', 'followup_limitations'),
  coverage: verified(followupRoot, followupReceipt, 'coverage_all_dates.csv', 'coverage', true),
  strata: verified(followupRoot, followupReceipt, 'annual_strata.csv', 'strata', true),
  cases: verified(followupRoot, followupReceipt, 'private_cases.json', 'case_inventory'),
});
const fillAudit = JSON.parse(read(resolve(args['--fill-audit']), 'fill_audit'));
const persistedAudit = JSON.parse(read(resolve(args['--persisted-audit']), 'persisted_audit'));
if (payload.portfolios.filter(r => r.strict_total_change === null).length !== 39 ||
    payload.portfolios.filter(r => r.scenario === 'touch10' && r.strict_total_change === null).length !== 10) throw new Error('Checkpoint support differs from reviewed disclosure');
const data = { ...payload, audits: buildAuditEvidence(fillAudit, persistedAudit, hashes.ledger_receipt, payload.portfolios), source_sha256: hashes };
const bytes = Buffer.from(JSON.stringify(data, null, 2) + '\n');
if (/"(?:ts_code|symbol|securities|denominator|market_value|private_path)"|\d{6}\.(?:SZ|SH|BJ)|\/home\//.test(bytes.toString('utf8'))) throw new Error('Private source detail escaped projection');
mkdirSync(dirname(receiptPath), { recursive: true });
if (existsSync(output)) {
  if (!readFileSync(output).equals(bytes)) throw new Error('Refusing to overwrite different prepared evidence');
} else writeFileSync(output, bytes, { flag: 'wx' });
writeFileSync(receiptPath, JSON.stringify({ status: 'prepared_unpublished_allowlisted_aggregate', inputs, input_sha256: hashes,
  output, output_sha256: sha(bytes), source_sha256: {
    'web/scripts/prepare-valuation-checkpoint.mjs': sha(readFileSync(new URL(import.meta.url))),
    'web/src/lib/valuation-checkpoint.ts': sha(readFileSync(new URL('../src/lib/valuation-checkpoint.ts', import.meta.url))),
  } }, null, 2) + '\n', { flag: 'wx' });
console.log(`Prepared ${payload.portfolios.length} ledger scenarios, ${payload.conditions.length} condition rows; ${bytes.length} bytes`);
