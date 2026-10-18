import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {buildMicrocapReport} from './content/microcap-report.server.ts';

// Synthetic review; these fills and residuals are not published study results.
export function syntheticRawSellReview() {
 return {
  schema_version: 1, reviewed_on: '2000-02-01', status: 'bounded_account_reconciled',
  raw_share_strategy_ready: false, new_prospective_observations: 0,
  comparison: {noncode_inputs_matched: 57, captured_artifacts_matched: 4,
   window_targets_calendar_match: true, inputs_unchanged: true, prior_failure_retained: true},
  policy: {explicit_sell_round_lot: 100, buy_lot_independent: true,
   sell_round_lot_default_is_continuous: true, default_compatibility_scope: 'provider_regression_tests',
   full_integer_liquidation_allowed: true, adjusted_price_basis_allowed: false,
   capacity_weight_ledger_allowed: false, fraction_tolerance_cap: 1e-8,
   tiny_float_residue_preserved: true, capacity_expansion: false},
  account: {sessions: 21, formations: 2, targets_per_formation: 40, distinct_target_names: 46,
   query_rows_scanned: 2230, included_actions: 1, excluded_pre_entry_actions: 1,
   fills: 5, buy_fills: 4, sell_fills: 1, all_inventory_integral: true,
   max_errors_cny: {cash: 1e-11, marked_value: 1e-10, fees: 0, identity: 1e-10}, tolerance_cny: 1e-7},
  certification: {full_period: false, historical_account: false, tax: false,
   registrar_holder: false, historical_information_set: false},
  source_sha256: {account_manifest: 'a'.repeat(64), independent_review: 'b'.repeat(64),
   prior_failed_receipt: 'c'.repeat(64)},
 };
}

for (const locale of ['en-US', 'zh-CN']) {
 test(`bounded replay tables derive fills and residuals without exposing account value in ${locale}`, async () => {
  const { rawSellTables, rawSellMarkdown } = await import('./content/microcap-raw-sell.ts');
  const value = syntheticRawSellReview();
  const tables = rawSellTables(value, locale);
  assert.deepEqual(tables.scope.rows.slice(-3).map(row => row[1]), ['5', '4', '1']);
  assert.equal(tables.errors.rows[2][1], '0');
  assert.equal(tables.errors.rows[0][2], '1.000e-7');
  const markdown = rawSellMarkdown(value, locale);
  assert.ok(markdown.includes(value.source_sha256.account_manifest));
  assert.doesNotMatch(markdown, /undefined|NaN|\/home\/|PRIVATE|002729|20211012|ending_value_cny/);
  if (locale === 'en-US') assert.doesNotMatch(markdown, /[\u3400-\u9fff]/);
 });
}

for (const [name, mutate] of [
 ['false certification', value => {value.certification.full_period = true;}],
 ['mismatched fills', value => {value.account.sell_fills++;}],
 ['relaxed tolerance', value => {value.account.tolerance_cny = 1e-6;}],
 ['unreviewed compatibility', value => {value.policy.default_compatibility_scope = 'assumed_from_replay';}],
 ['private field', value => {value.account.symbol = 'PRIVATE';}],
 ['nonfinite residual', value => {value.account.max_errors_cny.cash = Infinity;}],
 ['unmatched inputs', value => {value.comparison.inputs_unchanged = false;}],
 ['new prospective observation', value => {value.new_prospective_observations = 1;}],
]) test(`raw-sell publication rejects ${name}`, async () => {
 const { rawSellMarkdown } = await import('./content/microcap-raw-sell.ts');
 const value = syntheticRawSellReview(); mutate(value);
 assert.throws(() => rawSellMarkdown(value, 'en-US'));
});

for (const locale of ['en-US', 'zh-CN']) test(`approved replay is source-bound and shared by the ${locale} report`, async () => {
 const {rawSellMarkdown, validateRawSellReview}=await import('./content/microcap-raw-sell.ts');
 const bytes=await readFile('public/data/microcap_raw_sell_review.json');
 assert.equal(createHash('sha256').update(bytes).digest('hex'), 'c68a62c1226be40fd17a393c479b425f3c5838117b50722ce5673f73177e95f6');
 const value=validateRawSellReview(JSON.parse(bytes));
 const previous=JSON.parse(await readFile('public/data/microcap_chain_review.json', 'utf8'));
 assert.equal(value.source_sha256.prior_failed_receipt, previous.source_sha256.slice);
 assert.equal(value.account.fills, 79);
 assert.equal(value.account.buy_fills, 73);
 assert.equal(value.account.sell_fills, 6);
 assert.ok((await buildMicrocapReport(locale)).markdown.includes(rawSellMarkdown(value,locale)));
 assert.doesNotMatch(bytes.toString(), /PRIVATE|\/home\/|symbol|source_path|ending_value|target_date/);
});
