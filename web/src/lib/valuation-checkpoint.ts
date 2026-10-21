type RecordValue = Record<string, any>;
const metrics = ['pb_parent', 'pe_deducted_proxy'] as const;
const allMetrics = ['pe_ttm', 'pe_deducted_proxy', 'pb_parent', 'pb_ex_goodwill_proxy', 'pb_ex_intangibles_proxy'];
const scenarios = ['touch10', 'close10', 'touch0', 'touch30'] as const;
const conditionNames = ['persistent_cheap', 'one_off_cheap', 'other_cheap', 'history_insufficient'];
const caseNames = ['latest_minimum_pb', 'historical_non_st_minimum_pb', 'positive_pe_nonpositive_deducted'];

function count(value: unknown): number {
  const n = typeof value === 'string' && value !== '' ? Number(value) : value;
  if (typeof n !== 'number' || !Number.isSafeInteger(n) || n < 0) throw new Error('invalid aggregate count');
  return n;
}
function finite(value: unknown): number {
  const n = typeof value === 'string' && value !== '' ? Number(value) : value;
  if (typeof n !== 'number' || !Number.isFinite(n)) throw new Error('invalid aggregate number');
  return n;
}
function optionalNumber(value: unknown): number | null {
  return value == null || value === '' ? null : finite(value);
}
function limitedFlags(value: RecordValue) {
  if (value.raw_share_ready !== false || value.revision_safe !== false) throw new Error('unsupported evidence promotion');
}

/** Explicit projection: private holdings, identities, amounts and paths never pass through. */
export function buildCheckpointEvidence(input: {
  ledger: RecordValue; actions: RecordValue; conditions: RecordValue; limitations: RecordValue;
  coverage: RecordValue[]; strata: RecordValue[]; cases: RecordValue[];
}) {
  const { ledger, actions, conditions, limitations } = input;
  limitedFlags(ledger); limitedFlags(actions); limitedFlags(limitations);
  if (ledger.status !== 'completed_unpublished_proxy_checkpoint' || ledger.pilot !== false ||
      conditions.revision_safe !== false || conditions.endpoint_selection_conditioned !== true ||
      conditions.not_executable_returns !== true || limitations.financial_history_not_repaired !== true ||
      limitations.st_small_sample_warning !== true) throw new Error('unreviewed checkpoint source');
  const seen = new Set<string>();
  const portfolios = (ledger.portfolios as RecordValue[]).map((r: RecordValue) => {
    limitedFlags(r);
    if (!metrics.includes(r.metric) || !scenarios.includes(r.scenario) || ![1, 2, 3, 4, 5].includes(r.quintile)) throw new Error('unexpected portfolio');
    const id = `${r.metric}:${r.quintile}:${r.scenario}`;
    if (seen.has(id)) throw new Error('duplicate portfolio');
    seen.add(id);
    if (r.cohorts !== 36 || r.sessions !== 748 || r.entry_date !== '20230103' ||
        r.liquidation_date !== '20260105' || r.last_date !== '20260202' ||
        r.max_cash_replay_error !== 0) throw new Error('checkpoint scope or cash reconciliation differs');
    const unresolved = count(r.final.unresolved_lots);
    const strict = optionalNumber(r.strict_total_return);
    if ((unresolved > 0) !== (strict === null)) throw new Error('unresolved asset has a fabricated strict result or missing status');
    if (count(r.strict_nav_days) > r.sessions) throw new Error('strict marked sessions exceed ledger scope');
    return { metric: r.metric as typeof metrics[number], quintile: count(r.quintile), scenario: r.scenario as typeof scenarios[number],
      strict_nav_days: count(r.strict_nav_days), unresolved_lots: unresolved,
      pending_exit_lots: count(r.final.pending_exit_lots), delayed_sales: count(r.delayed_sales),
      max_exit_delay_sessions: count(r.max_exit_delay_sessions),
      zero_unresolved_total_change: finite(r.zero_unresolved_total_return), strict_total_change: strict,
      expired_buy_orders: Object.entries(r.reasons).filter(([reason]) => reason.startsWith('buy:')).reduce((sum, [, n]) => sum + count(n), 0) };
  });
  if (portfolios.length !== 40) throw new Error('incomplete portfolio matrix');
  const conditionRows = (conditions.rows as RecordValue[]).map((r: RecordValue) => {
    if (!metrics.includes(r.metric) || !conditionNames.includes(r.condition)) throw new Error('unexpected condition');
    const selected = count(r.stock_months), resolved = count(r.endpoint_resolved), unresolved = count(r.unresolved);
    if (selected !== resolved + unresolved) throw new Error('condition support does not reconcile');
    return { metric: r.metric as typeof metrics[number], condition: String(r.condition), months: count(r.months),
      stock_months: selected, endpoint_resolved: resolved, unresolved,
      equal_month_conditional_mean: finite(r.equal_month_conditional_mean), months_with_at_least_20: count(r.months_with_at_least_20) };
  });
  if (conditionRows.length !== 8 || new Set(conditionRows.map((r: RecordValue) => `${r.metric}:${r.condition}`)).size !== 8) throw new Error('incomplete condition matrix');
  const latest = input.coverage.map(r => String(r.date)).sort().at(-1);
  if (latest !== '20261016') throw new Error('unexpected coverage endpoint');
  const coverage = input.coverage.filter(r => String(r.date) === latest && r.status === 'all_market').map(r => {
    if (!allMetrics.includes(r.metric)) throw new Error('unexpected coverage metric');
    const quoted = count(r.quoted), valid = count(r.valid), nonpositive = count(r.nonpositive), missing = count(r.missing_other);
    if (valid + nonpositive + missing !== quoted) throw new Error('coverage does not reconcile');
    return { metric: String(r.metric), quoted, valid, nonpositive, missing_other: missing, common_five: count(r.common_five) };
  });
  if (coverage.length !== 5 || new Set(coverage.map(r => r.metric)).size !== 5) throw new Error('missing coverage metric');
  const latestStrata = input.strata.filter(r => String(r.date) === latest);
  const strata = latestStrata.filter(r => ['size_bucket', 'reporting_group'].includes(r.dimension)).map(r => {
    if (!['pb_parent', 'pe_deducted_proxy', 'pb_ex_intangibles_proxy'].includes(r.metric)) throw new Error('unexpected stratum metric');
    if (!(r.dimension === 'size_bucket' ? ['1', '2', '3', '4', '5'] : ['general_reporting', 'financial_reporting']).includes(String(r.stratum))) throw new Error('unexpected stratum');
    return { dimension: String(r.dimension), stratum: String(r.stratum), metric: String(r.metric),
      quoted: count(r.quoted), valid: count(r.valid), median: optionalNumber(r.median), p05: optionalNumber(r.p05), small_sample: count(r.valid) < 20 };
  });
  const industries = metrics.map(metric => {
    const rows = latestStrata.filter(r => r.dimension === 'industry_snapshot_proxy' && r.metric === metric);
    const usable = rows.filter(r => r.median !== '' && r.median != null);
    return { metric, strata: rows.length, usable_strata: usable.length, small_sample_strata: rows.filter(r => count(r.valid) < 20).length };
  });
  if (input.cases.length !== 3 || caseNames.some(name => !input.cases.some(r => r.case === name))) throw new Error('unexpected case inventory');
  return { schema_version: 'valuation_checkpoint.v1', evidence_status: 'unpublished_adjusted_unit_diagnostic',
    raw_share_ready: false, revision_safe: false, st_small_sample_warning: true,
    scope: { portfolios: 40, cohorts: 36, sessions: 748, start: '20230103', liquidation: '20260105', end: '20260202', exit_tail_sessions: 20, cash_replay_error: 0 },
    portfolios, actions: { signal_names: count(actions.signal_names), snapshot_names: count(actions.snapshot_names),
      names_without_snapshot_rows: count(actions.signal_names_without_snapshot_rows),
      implemented_window_rows: count(actions.implemented_window_rows),
      implemented_missing_ex_date_rows: count(actions.implemented_missing_ex_date_rows),
      missing_cash_field_rows: count(actions.missing_fields.cash_div_tax),
      stock_events_missing_listing_date: count(actions.positive_stock_missing_listing_date),
      repeated_symbol_ex_date_rows: count(actions.repeated_symbol_ex_date_rows), independent_event_completeness: false },
    conditions: conditionRows, coverage: { date: latest, rows: coverage }, strata,
    industries: { snapshot_date: '20260928', point_in_time: false, rows: industries },
    cases: caseNames.map(kind => ({ kind, causal_investigation_complete: false })) };
}
export type CheckpointEvidence = ReturnType<typeof buildCheckpointEvidence>;

/** The two independent audits must cover exactly the frozen ledger portfolios. */
export function buildAuditEvidence(fillAudit: RecordValue, persistedAudit: RecordValue, receiptHash: string, portfolios: CheckpointEvidence['portfolios']) {
  for (const audit of [fillAudit, persistedAudit]) {
    if (audit.status !== 'passed' || audit.run_receipt_sha256 !== receiptHash || audit.portfolios.length !== 40 ||
        new Set(audit.portfolios.map((r: RecordValue) => r.portfolio)).size !== 40) throw new Error('Independent audit scope differs');
  }
  const expectedIds = new Set(portfolios.map(r => `${r.metric}_q${r.quintile}_${r.scenario}`));
  if (fillAudit.portfolios.some((r: RecordValue) => !expectedIds.has(r.portfolio) || r.violations !== 0 || !Number.isSafeInteger(r.filled_orders) || r.filled_orders < 0) ||
      persistedAudit.portfolios.some((r: RecordValue) => !expectedIds.has(r.portfolio) || r.passed !== true || r.days !== 748 || !Number.isFinite(r.max_cash_error) || r.max_cash_error < 0 || r.max_cash_error > 1e-7)) throw new Error('Independent audit did not pass');
  return { filled_orders_checked: count(fillAudit.portfolios.reduce((sum: number, r: RecordValue) => sum + r.filled_orders, 0)), fill_violations: 0,
    persisted_cash_tolerance: 1e-7, persisted_max_cash_error: Math.max(...persistedAudit.portfolios.map((r: RecordValue) => r.max_cash_error)) };
}
