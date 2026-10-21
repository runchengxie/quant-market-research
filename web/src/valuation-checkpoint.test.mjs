import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { buildAuditEvidence, buildCheckpointEvidence } from './lib/valuation-checkpoint.ts';

function fixture() {
  const metrics = ['pb_parent', 'pe_deducted_proxy'];
  const portfolios = metrics.flatMap(metric => ['touch10', 'close10', 'touch0', 'touch30'].flatMap(scenario => [1, 2, 3, 4, 5].map(quintile => ({ metric, scenario, quintile, raw_share_ready: false, revision_safe: false, cohorts: 36, sessions: 748, entry_date: '20230103', liquidation_date: '20260105', last_date: '20260202', max_cash_replay_error: 0, strict_nav_days: 10, delayed_sales: 3, max_exit_delay_sessions: 4, zero_unresolved_total_return: .2, strict_total_return: null, final: { unresolved_lots: 2, pending_exit_lots: 2, cash: 999999 }, reasons: { 'buy:upper_limit': 7 }, ts_code: 'PRIVATE_ID' }))));
  return {
    ledger: { status: 'completed_unpublished_proxy_checkpoint', pilot: false, raw_share_ready: false, revision_safe: false, portfolios, private_path: '/private/example' },
    actions: { raw_share_ready: false, revision_safe: false, signal_names: 5565, snapshot_names: 4295, signal_names_without_snapshot_rows: 1390, implemented_window_rows: 10357, implemented_missing_ex_date_rows: 29, missing_fields: { cash_div_tax: 102 }, positive_stock_missing_listing_date: 1, repeated_symbol_ex_date_rows: 817 },
    conditions: { revision_safe: false, endpoint_selection_conditioned: true, not_executable_returns: true, rows: metrics.flatMap(metric => ['persistent_cheap', 'one_off_cheap', 'other_cheap', 'history_insufficient'].map(condition => ({ metric, condition, months: 36, stock_months: 100, endpoint_resolved: 90, unresolved: 10, equal_month_conditional_mean: .01, months_with_at_least_20: 32 }))) },
    limitations: { raw_share_ready: false, revision_safe: false, financial_history_not_repaired: true, st_small_sample_warning: true },
    coverage: ['pe_ttm', 'pe_deducted_proxy', 'pb_parent', 'pb_ex_goodwill_proxy', 'pb_ex_intangibles_proxy'].map(metric => ({ date: '20261016', status: 'all_market', metric, quoted: 10, valid: 8, nonpositive: 1, missing_other: 1, common_five: 6 })),
    strata: [{ date: '20261016', dimension: 'size_bucket', stratum: '1', metric: 'pb_parent', quoted: '10', valid: '8', median: '.6', p05: '.2' }],
    cases: ['latest_minimum_pb', 'historical_non_st_minimum_pb', 'positive_pe_nonpositive_deducted'].map(kind => ({ case: kind, ts_code: 'PRIVATE_ID', market_value: 999999 })),
  };
}

test('projection excludes private identities, raw amounts and paths, retaining unresolved status', () => {
  const data = buildCheckpointEvidence(fixture());
  assert.equal(data.portfolios.length, 40);
  assert.equal(data.portfolios[0].strict_total_change, null);
  assert.equal(data.portfolios[0].unresolved_lots, 2);
  assert.equal(data.actions.names_without_snapshot_rows, 1390);
  assert.equal(data.industries.point_in_time, false);
  assert.ok(!/PRIVATE_ID|private_path|market_value|999999|\/private\//.test(JSON.stringify(data)));
});

test('unresolved positions cannot be promoted into a strict terminal result', () => {
  const input = fixture(); input.ledger.portfolios[0].strict_total_return = .2;
  assert.throws(() => buildCheckpointEvidence(input), /fabricated strict/);
});

test('partial matrices, failed reconciliation and evidence promotion fail closed', () => {
  for (const change of [input => input.ledger.portfolios.pop(), input => { input.ledger.portfolios[0].max_cash_replay_error = 1; }, input => { input.ledger.portfolios[0].strict_nav_days = 749; }, input => { input.ledger.portfolios[0].final.unresolved_lots = 0; }, input => { input.ledger.raw_share_ready = true; }, input => { input.conditions.not_executable_returns = false; }, input => { input.coverage[0].valid = 9; }]) {
    const input = fixture(); change(input); assert.throws(() => buildCheckpointEvidence(input));
  }
});

test('prepared checkpoint preserves complete scenario support and source receipts', () => {
  const data = JSON.parse(readFileSync(new URL('../public/data/valuation_ledger_checkpoint_draft.json', import.meta.url), 'utf8'));
  assert.equal(data.portfolios.length, 40);
  assert.equal(data.scope.sessions, 748);
  assert.equal(data.raw_share_ready, false);
  assert.equal(data.revision_safe, false);
  assert.equal(data.st_small_sample_warning, true);
  assert.equal(data.portfolios.filter(r => r.strict_total_change === null).length, 39);
  assert.equal(data.portfolios.filter(r => r.scenario === 'touch10' && r.strict_total_change === null).length, 10);
  assert.equal(data.audits.filled_orders_checked, 2507510);
  assert.equal(data.audits.fill_violations, 0);
  assert.ok(data.audits.persisted_max_cash_error <= data.audits.persisted_cash_tolerance);
  for (const row of data.portfolios) if (row.unresolved_lots) assert.equal(row.strict_total_change, null);
  assert.equal(data.conditions.length, 8);
  assert.equal(data.cases.length, 3);
  assert.match(data.source_sha256.ledger_receipt, /^[a-f0-9]{64}$/);
  assert.match(data.source_sha256.followup_receipt, /^[a-f0-9]{64}$/);
  assert.match(data.source_sha256.fill_audit, /^[a-f0-9]{64}$/);
  assert.match(data.source_sha256.persisted_audit, /^[a-f0-9]{64}$/);
  assert.ok(!/"(?:ts_code|symbol|securities|denominator|market_value|private_path)"|\d{6}\.(?:SZ|SH|BJ)|\/home\//.test(JSON.stringify(data)));
});

test('audit binding rejects mismatched runs, missing portfolios, negative and overflowing fills', () => {
  const portfolios = buildCheckpointEvidence(fixture()).portfolios;
  const make = () => {
    const rows = portfolios.map(r => ({ portfolio: `${r.metric}_q${r.quintile}_${r.scenario}`, filled_orders: 10, violations: 0, passed: true, days: 748, max_cash_error: 2e-10 }));
    return [{ status: 'passed', run_receipt_sha256: 'a'.repeat(64), portfolios: structuredClone(rows) }, { status: 'passed', run_receipt_sha256: 'a'.repeat(64), portfolios: structuredClone(rows) }];
  };
  assert.equal(buildAuditEvidence(...make(), 'a'.repeat(64), portfolios).filled_orders_checked, 400);
  for (const change of [a => { a[0].run_receipt_sha256 = 'b'.repeat(64); }, a => { a[0].portfolios.pop(); }, a => { a[0].portfolios[0].filled_orders = -1; }, a => { for (const r of a[0].portfolios) r.filled_orders = Number.MAX_SAFE_INTEGER; }, a => { a[1].portfolios[0].max_cash_error = 1e-4; }]) {
    const audits = make(); change(audits); assert.throws(() => buildAuditEvidence(...audits, 'a'.repeat(64), portfolios));
  }
});
