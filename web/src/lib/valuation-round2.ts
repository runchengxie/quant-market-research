type Row = Record<string, any>;
const metrics = ['pb_parent', 'pe_deducted_proxy'];
const scenarios = ['touch10', 'close10', 'touch0', 'touch30'];
const scopes = ['A_unpriced_only', 'B_all_remaining'];
const fractions = [0, .5, 1];
export function aggregateCount(value: unknown): number {
  if (typeof value !== 'number' || !Number.isSafeInteger(value) || value < 0) throw new Error('Invalid aggregate count');
  return value;
}
export function aggregateNumber(value: unknown): number {
  if (typeof value !== 'number' || !Number.isFinite(value)) throw new Error('Invalid aggregate number');
  return value;
}
export function assertPublicRound2(value: unknown) {
  const bannedKey = /^(?:ts_code|symbol|securities|security_id|name|private_path|cash|market_value|denominator|buy_notional|sell_notional|scenario_value|current_marked_value)$/;
  function walk(item: any): void {
    if (typeof item === 'string' && (/\d{6}\.(?:SZ|SH|BJ)|(?:\/home\/|[A-Z]:\\)/i.test(item))) throw new Error('Private identity or machine path in public evidence');
    if (Array.isArray(item)) item.forEach(walk);
    else if (item && typeof item === 'object') for (const [key, val] of Object.entries(item)) {
      if (bannedKey.test(key)) throw new Error('Raw amount or private identity in public evidence');
      walk(val);
    }
  }
  walk(value);
}
export function buildRound2Evidence(input: { sensitivities: Row[]; unresolved: Row; checkpoint: Row; rules: Row; freeze: Row; rulesHash: string; sourceHashes: Record<string,string>; attribution?: {summary: Row; reconciliation: Row; annual?: Row[]}; controls?: Row; controlsSemantics?: Row; controlsAudit?: {cross_receipt_passed:boolean;bucket_distribution_audited:boolean;bucket_aggregate_rows:number;semantics_checked:boolean;recovered_seal:boolean}; cases?:Row; caseCopy?:Row; caseAudit?:Row }) {
  const { checkpoint, rules, freeze } = input;
  if (!/^\d{4}-\d{2}-\d{2}T/.test(freeze.frozen_at_utc) || !Number.isFinite(Date.parse(freeze.frozen_at_utc)) || !/^[a-f0-9]{40}$/.test(freeze.baseline_commit) ||
      JSON.stringify(rules.primary_contrasts) !== JSON.stringify([['pb_parent',1,2],['pe_deducted_proxy',1,3]]) || rules.primary_scenario !== 'touch10' || rules.attribution?.initial_capital !== 1_000_000) throw new Error('Malformed frozen design');
  if (checkpoint.raw_share_ready !== false || checkpoint.revision_safe !== false || checkpoint.portfolios.length !== 40 ||
      checkpoint.portfolios.filter((r: Row) => r.strict_total_change === null).length !== 39 ||
      checkpoint.portfolios.filter((r: Row) => r.scenario === 'touch10' && r.strict_total_change === null).length !== 10) throw new Error('Unsupported strict result promotion');
  if (rules.schema !== 'valuation_round2_rules.v1' || rules.design_id !== 'grouped-valuation-round2-20261021' ||
      freeze.status !== 'rules_frozen_before_new_analysis' || freeze.design_id !== rules.design_id ||
      freeze.genuine_holdout_admitted !== false || freeze.forward_validation_started !== false ||
      freeze.previous_history_explored !== true || rules.forward_validation.status !== 'protocol_only_not_started') throw new Error('Unsupported validation promotion');
  if (!/^[a-f0-9]{64}$/.test(input.rulesHash) || !Object.values(freeze.inputs).includes(input.rulesHash) ||
      Object.values(input.sourceHashes).some(hash => !/^[a-f0-9]{64}$/.test(hash))) throw new Error('Unbound source hash');
  if(input.controls && (!input.controlsSemantics || !input.controlsAudit || input.controlsAudit.cross_receipt_passed!==true || input.controlsAudit.bucket_distribution_audited!==true || input.controlsAudit.semantics_checked!==true || !Number.isSafeInteger(input.controlsAudit.bucket_aggregate_rows) || input.controlsAudit.bucket_aggregate_rows<=0)) throw new Error('Controls require reviewed audit addenda');
  const seen = new Set<string>();
  const sensitivities = input.sensitivities.map(r => {
    if (!metrics.includes(r.metric) || !scenarios.includes(r.scenario) || ![1,2,3,4,5].includes(r.quintile) ||
        !scopes.includes(r.scope) || !fractions.includes(r.reference_fraction) ||
        r.valuation_only !== true || r.cash_change !== 0 || r.units_changed !== false || r.not_recovery_probability_or_bound !== true) throw new Error('Malformed sensitivity or cash creation');
    const key = [r.metric,r.quintile,r.scenario,r.scope,r.reference_fraction].join(':');
    if (seen.has(key)) throw new Error('Duplicate sensitivity');
    seen.add(key);
    const support = input.unresolved.portfolios.find((p: Row) => p.metric === r.metric && p.quintile === r.quintile && p.scenario === r.scenario);
    const ledger = checkpoint.portfolios.find((p: Row) => p.metric === r.metric && p.quintile === r.quintile && p.scenario === r.scenario);
    if (!support || !ledger || support.raw_share_ready !== false || support.revision_safe !== false ||
        aggregateCount(support.unpriced_lots) !== ledger.unresolved_lots ||
        typeof r.reference_complete !== 'boolean' || (r.unknown_reference_lots === 0) !== r.reference_complete ||
        (r.reference_complete ? r.scenario_change_from_initial == null : r.scenario_change_from_initial != null)) throw new Error('Incomplete reference falsely promoted');
    if (ledger.unresolved_lots > 0 && ledger.strict_total_change !== null) throw new Error('Unsupported strict result');
    return { metric: String(r.metric), quintile: aggregateCount(r.quintile), scenario: String(r.scenario), scope: String(r.scope),
      reference_fraction: aggregateNumber(r.reference_fraction), reference_complete: r.reference_complete as boolean,
      unknown_reference_lots: aggregateCount(r.unknown_reference_lots), unresolved_lots: aggregateCount(ledger.unresolved_lots),
      valued_unexited_lots: aggregateCount(support.valued_but_unexited_lots),
      total_change: r.scenario_change_from_initial == null ? null : aggregateNumber(r.scenario_change_from_initial),
      strict_total_change: ledger.strict_total_change == null ? null : aggregateNumber(ledger.strict_total_change) };
  });
  if (sensitivities.length !== 240) throw new Error('Incomplete sensitivity matrix');
  const data = { schema_version: 'valuation_round2.v1', evidence_status: 'unpublished_retrospective_diagnostics',
    raw_share_ready: false, revision_safe: false, not_realized_returns: true,
    scope: { portfolios: 40, sensitivity_rows: 240, strict_terminal_unavailable: 39, primary_strict_unavailable: 10, terminal_date: '20260202' },
    freeze: { design_id: rules.design_id as string, frozen_at_utc: String(freeze.frozen_at_utc), baseline_commit: String(freeze.baseline_commit), rules_sha256: input.rulesHash,
      existing_history_explored: true, genuine_holdout_admitted: false, forward_validation_started: false,
      earliest_formation_month: String(rules.forward_validation.earliest_formation_month), minimum_monthly_cohorts: aggregateCount(rules.forward_validation.minimum_monthly_cohorts),
      primary_scenario: 'touch10', primary_contrasts: (rules.primary_contrasts as any[][]).map((r: any[]) => ({ metric: String(r[0]), first: aggregateCount(r[1]), comparator: aggregateCount(r[2]) })) },
    sensitivities, attribution: input.attribution ? buildAttributionEvidence(input.attribution.summary, input.attribution.reconciliation, sensitivities, input.attribution.annual) : null, controls: input.controls ? {...buildControlEvidence(input.controls, input.controlsSemantics),audit:input.controlsAudit??null} : null, case_progress: input.cases && input.caseCopy && input.caseAudit ? buildCaseEvidence(input.cases,input.caseCopy,input.caseAudit) : null, source_sha256: input.sourceHashes };
  assertPublicRound2(data);
  return data;
}
export type Round2Evidence = ReturnType<typeof buildRound2Evidence>;

/** Monetary source fields are normalized by the frozen initial capital, never copied. */
export function buildAttributionEvidence(summary: Row, reconciliation: Row, sensitivities: {metric:string;quintile:number;scenario:string;scope:string;reference_fraction:number;total_change:number|null;strict_total_change:number|null}[], annualInput?: Row[]) {
  if (summary.schema_version !== 'grouped_valuation_attribution.v1' || summary.status !== 'completed_readonly_attribution' || summary.raw_share_ready !== false || summary.revision_safe !== false || reconciliation.passed !== true || reconciliation.portfolios !== 40 || reconciliation.strict_unknown_portfolios !== 39 || reconciliation.all_members_retained !== true || reconciliation.budgets_verified !== true || reconciliation.zero_and_reference_sensitivities_reconciled !== true || reconciliation.annual_lot_and_portfolio_identities_reconciled !== true) throw new Error('Unreviewed attribution');
  const seen = new Set<string>();
  const portfolios = (summary.portfolios as Row[]).map(r => {
    if (!metrics.includes(r.metric) || !scenarios.includes(r.scenario) || ![1,2,3,4,5].includes(r.quintile)) throw new Error('Unknown attribution portfolio');
    if (r.raw_share_ready !== false || r.revision_safe !== false) throw new Error('Attribution evidence promotion');
    const key = [r.metric,r.quintile,r.scenario].join(':');
    if (seen.has(key)) throw new Error('Duplicate attribution portfolio'); seen.add(key);
    const money = (key:string) => aggregateNumber(r[key]) / 1_000_000;
    const planned=aggregateCount(r.planned_members), filled=aggregateCount(r.filled_buys), failed=aggregateCount(r.failed_buys);
    if (planned !== filled + failed) throw new Error('Attribution member counts do not reconcile');
    const changes = [0,50,100].map((fraction,index) => {
      const value = r['contribution_initial_'+fraction] == null ? null : aggregateNumber(r['contribution_initial_'+fraction]);
      const reference=sensitivities.find(s=>s.metric===r.metric && s.quintile===r.quintile && s.scenario===r.scenario && s.scope==='A_unpriced_only' && s.reference_fraction===[0,.5,1][index]);
      if (!reference || (value==null)!==(reference.total_change==null) || value!=null && Math.abs(value-reference.total_change!)>1e-12) throw new Error('Attribution differs from reference sensitivity');
      return value;
    });
    const strict=r.contribution_initial_strict==null ? null : aggregateNumber(r.contribution_initial_strict);
    const reference=sensitivities.find(s=>s.metric===r.metric && s.quintile===r.quintile && s.scenario===r.scenario);
    if (!reference || (strict==null)!==(reference.strict_total_change==null) || strict!=null && Math.abs(strict-reference.strict_total_change!)>1e-12) throw new Error('Strict attribution promoted');
    if (changes[0]!=null && Math.abs(money('gross_pnl_0_same_path')-money('buy_fees')-money('sell_fees')-changes[0])>1e-12) throw new Error('Gross and net attribution do not reconcile');
    if (changes[0]!=null && Math.abs(money('terminal_lot_net_pnl_0')+money('closed_lot_net_pnl')-changes[0])>1e-12) throw new Error('Lot attribution does not reconcile');
    const errors=['budget_reconstruction_max_error','cash_max_error','net_pnl_max_error'].map(key=>money(key));
    if (errors.some(error=>error<0 || error>1e-12)) throw new Error('Attribution reconciliation outside frozen tolerance');
    return {metric:String(r.metric),quintile:aggregateCount(r.quintile),scenario:String(r.scenario),
      planned_members:planned,filled_buys:filled,failed_buys:failed,zero_budget_members:aggregateCount(r.zero_budget_members),
      terminal_unpriced_lots:aggregateCount(r.terminal_unpriced_lots),unknown_reference_lots:aggregateCount(r.unknown_reference_lots),strict_unknown_days:aggregateCount(r.strict_unknown_days),
      contribution_initial_0:changes[0],contribution_initial_50:changes[1],contribution_initial_100:changes[2],contribution_initial_strict:strict,
      gross_pnl_initial_0:money('gross_pnl_0_same_path'),buy_fee_fraction_initial:money('buy_fees'),sell_fee_fraction_initial:money('sell_fees'),
      closed_lot_contribution_initial:money('closed_lot_net_pnl'),terminal_lot_contribution_initial_0:money('terminal_lot_net_pnl_0'),
      cash_year_exposure_initial:money('cash_year_exposure'),interest_1pct_fraction_initial:money('interest_per_1pct_simple'),
      daily_mean_cash_fraction_initial:aggregateNumber(r.daily_mean_cash_fraction_initial),max_reconciliation_error_initial:Math.max(...errors)};
  });
  if (portfolios.length!==40) throw new Error('Incomplete attribution matrix');
  const annual=(annualInput??[]).map(r=>{
    const portfolio=portfolios.find(p=>p.metric===r.metric && p.quintile===Number(r.quintile) && p.scenario===r.scenario);
    const year=String(r.year);
    if(!portfolio || !['2023','2024','2025','2026'].includes(year) || !/^\d{8}$/.test(r.start_date) || !/^\d{8}$/.test(r.end_date)) throw new Error('Unknown annual accounting scope');
    const n=(key:string)=>{if(r[key]==='') throw new Error('Missing annual aggregate');return aggregateNumber(typeof r[key]==='string'?Number(r[key]):r[key]);};
    if(Math.abs(n('net_pnl_0')/1_000_000-n('contribution_initial_0'))>1e-12 || Math.abs(n('reconciliation_error'))>1e-6) throw new Error('Annual accounting does not reconcile');
    return {metric:String(r.metric),quintile:Number(r.quintile),scenario:String(r.scenario),calendar_year:year,start_date:String(r.start_date),end_date:String(r.end_date),
      contribution_initial_0:n('contribution_initial_0'),contribution_initial_strict:r.net_pnl_strict==null||r.net_pnl_strict===''?null:n('net_pnl_strict')/1_000_000,
      buy_fee_fraction_initial:n('buy_fees')/1_000_000,sell_fee_fraction_initial:n('sell_fees')/1_000_000,
      strict_unknown_days:aggregateCount(typeof r.strict_unknown_days==='string'?Number(r.strict_unknown_days):r.strict_unknown_days)};
  });
  if(annualInput) {
    if(annual.length!==160 || new Set(annual.map(r=>[r.metric,r.quintile,r.scenario,r.calendar_year].join(':'))).size!==160) throw new Error('Incomplete annual accounting');
    for(const portfolio of portfolios) {
      const rows=annual.filter(r=>r.metric===portfolio.metric && r.quintile===portfolio.quintile && r.scenario===portfolio.scenario);
      if(Math.abs(rows.reduce((sum,r)=>sum+r.contribution_initial_0,0)-portfolio.contribution_initial_0!)>1e-12) throw new Error('Annual contributions do not sum to portfolio');
    }
  }
  const result={evidence_status:'checked_accounting_under_scenarios',reference_scope:'A_unpriced_only',portfolios,annual};
  assertPublicRound2(result);return result;
}

function nullable(value: unknown) { return value == null ? null : aggregateNumber(value); }
export function buildControlEvidence(summary: Row, semantics?: Row) {
  if(summary.schema_version!=='valuation_controls_summaries.v1' || summary.outcome_units!=='lifetime_cohort_net_pnl_per_intended_budget' || summary.contrast_direction!=='q1_minus_comparator' || summary.genuine_holdout_admitted!==false || summary.revision_safe!==false) throw new Error('Unsupported control interpretation');
  const schedule=['202212',...['2023','2024'].flatMap(year=>Array.from({length:12},(_,i)=>year+String(i+1).padStart(2,'0'))),...Array.from({length:11},(_,i)=>'2025'+String(i+1).padStart(2,'0'))];
  const rows=(summary.rows as Row[]).filter(r=>r.primary_contrast===true).map(r=>{
    if(!metrics.includes(r.metric) || ![2,3,4,5].includes(r.comparison_quintile) || r.comparison_quintile!==(r.metric==='pb_parent'?2:3) ||
       !['all_frozen','common_five'].includes(r.sample_basis) ||
       !['report_size','report_size_profitability','secondary_quality','secondary_leverage'].includes(r.layer) ||
       !['full_frozen','feature_complete','overlap'].includes(r.stage) ||
       !['strict','reference_0','reference_50','reference_100'].includes(r.outcome)) throw new Error('Unexpected control dimension');
    const scheduled=aggregateCount(r.scheduled_months), supported=aggregateCount(r.supported_months);
    if(scheduled!==36 || supported>scheduled || r.supported_formation_months.length!==supported ||
       new Set(r.supported_formation_months).size!==supported ||
       r.supported_formation_months.some((date:string)=>!schedule.includes(date))) throw new Error('Control month support differs');
    const estimate=nullable(r.equal_month_mean_contrast), positive=nullable(r.positive_month_share);
    if((supported===0)!==(estimate===null) || positive!=null && (positive<0 || positive>1)) throw new Error('Unsupported control estimate');
    const bootstrap=r.bootstrap;
    const low=nullable(bootstrap.low),high=nullable(bootstrap.high);
    if((low===null)!==(high===null) || supported<12 && low!==null || low!=null && low>high!) throw new Error('Unsupported bootstrap interval');
    const yearly=(r.yearly as Row[]).map(y=>{
      const year=String(y.formation_year),scheduledYear=aggregateCount(y.scheduled_months),supportedYear=aggregateCount(y.supported_months);
      if(!['2022','2023','2024','2025'].includes(year) || scheduledYear!==({2022:1,2023:12,2024:12,2025:11} as Row)[year] || supportedYear>scheduledYear) throw new Error('Calendar-year support differs');
      return {formation_year:year,scheduled_months:scheduledYear,supported_months:supportedYear,missing_months:schedule.filter(date=>date.startsWith(year)&&!r.supported_formation_months.includes(date)),missing_month_count:scheduledYear-supportedYear,calendar_year_fully_sampled:scheduledYear===12,full_calendar_year_mean_contrast:scheduledYear===12&&supportedYear===12?nullable(y.equal_month_mean_contrast):null,full_schedule_complete:supportedYear===scheduledYear,full_schedule_mean_contrast:supportedYear===scheduledYear?nullable(y.equal_month_mean_contrast):null,supported_month_mean_contrast:nullable(y.equal_month_mean_contrast),supported_month_positive_share:nullable(y.positive_month_share)};
    });
    if(yearly.length!==4 || new Set(yearly.map(y=>y.formation_year)).size!==4) throw new Error('Incomplete year inventory');
    return {metric:String(r.metric),comparison_quintile:aggregateCount(r.comparison_quintile),sample_basis:String(r.sample_basis),layer:String(r.layer),stage:String(r.stage),outcome:String(r.outcome),
      scheduled_months:scheduled,supported_months:supported,supported_formation_months:r.supported_formation_months.map(String),
      q1_member_slots:aggregateCount(r.q1_member_slots),comparison_member_slots:aggregateCount(r.comparison_member_slots),
      q1_unknown_slots:aggregateCount(r.q1_unknown_slots),comparison_unknown_slots:aggregateCount(r.comparison_unknown_slots),
      mean_q1_retention:nullable(r.mean_q1_retention),mean_comparison_retention:nullable(r.mean_comparison_retention),
      missing_months:schedule.filter(date=>!r.supported_formation_months.includes(date)),missing_month_count:scheduled-supported,full_schedule_complete:supported===scheduled,full_schedule_mean_contrast:supported===scheduled?estimate:null,supported_month_mean_contrast:estimate,supported_month_positive_share:positive,yearly,
      leave_one_year_out:(r.leave_one_year_out as Row[]).map(y=>{
        const omitted=String(y.excluded_formation_year),planned=36-({2022:1,2023:12,2024:12,2025:11} as Row)[omitted],support=aggregateCount(y.supported_months);
        if(!Number.isSafeInteger(planned)||support>planned) throw new Error('Invalid leave-year-out support');
        return {omitted_formation_year:omitted,scheduled_months:planned,supported_months:support,missing_month_count:planned-support,full_schedule_complete:support===planned,full_schedule_mean_contrast:support===planned?nullable(y.equal_month_mean_contrast):null,supported_month_mean_contrast:nullable(y.equal_month_mean_contrast)};
      }),
      bootstrap:{status:String(bootstrap.status),low,high,valid_replications:aggregateCount(bootstrap.valid_replications),invalid_replications:aggregateCount(bootstrap.invalid_replications),
        supported_month_range:bootstrap.supported_month_range.map((date:unknown)=>{if(typeof date!=='string'||!/^20(?:22|23|24|25)\d{2}$/.test(date)) throw new Error('Invalid bootstrap date range');return date;})}};
  });
  if(rows.length!==192 || new Set(rows.map(r=>[r.metric,r.sample_basis,r.layer,r.stage,r.outcome].join(':'))).size!==192) throw new Error('Incomplete primary control matrix');
  if(semantics) {
    if(semantics.no_outcomes_recomputed!==true || semantics.original_summaries_unchanged!==true || semantics.rows.length!==768) throw new Error('Unsupported control semantics receipt');
    const key=(r:Row)=>[r.metric,r.comparison_quintile,r.primary_contrast??true,r.sample_basis,r.layer,r.stage,r.outcome].join(':');
    const indexed=new Map((semantics.rows as Row[]).map(r=>[key(r),r]));
    if(indexed.size!==768) throw new Error('Duplicate semantic row');
    for(const row of rows) {
      const expected=indexed.get(key(row));
      if(!expected || ['full_schedule_complete','full_schedule_mean_contrast','supported_month_mean_contrast'].some(field=>expected[field]!==row[field as keyof typeof row]) ||
         JSON.stringify(expected.missing_months)!==JSON.stringify(row.missing_months)) throw new Error('Control semantics differ');
      for(const year of row.yearly) {
        const y=expected.yearly.find((y:Row)=>String(y.formation_year)===year.formation_year);
        if(!y || ['full_schedule_complete','full_schedule_mean_contrast','supported_month_mean_contrast','calendar_year_fully_sampled','full_calendar_year_mean_contrast'].some(field=>y[field]!==year[field as keyof typeof year]) ||
           JSON.stringify(y.missing_months)!==JSON.stringify(year.missing_months)) throw new Error('Annual semantics differ');
      }
    }
  }
  const result={evidence_status:'exploratory_formation_batch_contribution' ,outcome_basis:'full_holding_period_pnl_over_original_intended_slot_budget',rows};
  assertPublicRound2(result);return result;
}

/** Normal producers do not carry recovery-only metadata; addenda bind every run. */
export function validateControlReceiptChain(receipt: Row, supplemental: Row, semanticsReceipt: Row, crossAudit: Row, hashes: Record<string,string>) {
  if(receipt.schema_version!=='valuation_controls_receipt.v1' || !['completed_unpublished_exploration','recovered_after_receipt_only_failure'].includes(receipt.status) ||
     receipt.rules_sha256!==hashes.rules || receipt.no_backtest_rerun!==true || receipt.outcome_independent_matching!==true || receipt.genuine_holdout_admitted!==false ||
     receipt.frozen_design_receipt_sha256!==undefined && receipt.frozen_design_receipt_sha256!==hashes.freeze_receipt ||
     !Object.values(receipt.inputs).includes(hashes.attribution_receipt) || !Object.values(receipt.inputs).includes(hashes.rules)) throw new Error('Control receipt differs from frozen source chain');
  for(const auditReceipt of [supplemental,semanticsReceipt]) {
    if(!Object.values(auditReceipt.inputs).includes(hashes.controls_receipt) || !Object.values(auditReceipt.inputs).includes(hashes.freeze_receipt) ||
       !Object.values(auditReceipt.inputs).includes(hashes.controls_summary)) throw new Error('Control addendum source chain differs');
  }
  if(supplemental.status!=='passed_independent_post_run_audits' || supplemental.no_outcomes_recomputed!==true ||
     semanticsReceipt.status!=='passed_semantic_addendum_without_reestimation' || semanticsReceipt.no_analysis_rerun!==true ||
     crossAudit.status!=='passed' || crossAudit.controls_receipt_sha256!==hashes.controls_receipt || crossAudit.attribution_receipt_sha256!==hashes.attribution_receipt ||
     crossAudit.frozen_design_receipt_sha256!==hashes.freeze_receipt || crossAudit.same_original_member_bytes!==true || crossAudit.same_derived_outcome_bytes!==true ||
     !Array.isArray(crossAudit.checks) || crossAudit.checks.length!==3 || crossAudit.checks.some((row:Row)=>row.frozen_design_and_controls_match!==true)) throw new Error('Control independent audit failed');
}

export function buildCaseEvidence(source: Row, copies: Row, audit: Row) {
  const kinds=['pb_positive_gap','pb_negative_gap','pb_unresolved_reference','pe_positive_gap','pe_negative_gap','pe_unresolved_reference'];
  if(source.schema!=='valuation_round2_cases.v1' || source.status!=='bounded_primary_evidence_checkpoint_with_gaps' || source.revision_safe!==false ||
     source.selection_changed!==false || source.no_ledger_recalculation!==true || source.cases.length!==6 || new Set(source.cases.map((r:Row)=>r.case_key)).size!==6 ||
     audit.status!=='passed' || audit.selection_cases!==6 || audit.selection_gap_checks!==6 || audit.reference_checks!==6 || audit.official_financial_value_checks!==12 ||
     audit.official_pdfs_hashed!==16 || audit.revision_counterexample_verified!==true || audit.revision_counterexample_earliest_selected_buy_failed!==true ||
     audit.source_data_changed!==false || audit.ledger_changed!==false || audit.cash_recovery_booked!==false) throw new Error('Unreviewed case checkpoint');
  const date=(value:unknown,nullable=false)=>{if(value===null&&nullable)return null;if(typeof value!=='string'||!/^\d{4}-?\d{2}-?\d{2}$/.test(value))throw new Error('Invalid case date');return value;};
  const cases=kinds.map(kind=>{
    const r=(source.cases as Row[]).find(r=>r.case_key===kind),copy=copies[kind];
    if(!r || !copy || !r.name.startsWith(copy.company[1]) || r.revision_safe!==false ||
       r.metric!==(kind.startsWith('pb_')?'pb_parent':'pe_deducted_proxy') || !['positive_gap','negative_gap','unresolved_reference'].includes(r.role) ||
       !['no_terminal_unresolved_lot','delisted_recovery_unverified','merger_conversion_known_ledger_bridge_missing'].includes(r.disposal_status)) throw new Error('Unexpected reviewed case');
    if(!/^\d{6}\.(?:SH|SZ|BJ)$/.test(r.historical_symbol)) throw new Error('Invalid dated ticker');
    const bilingual=(value:unknown)=>{if(!Array.isArray(value)||value.length!==2||value.some(x=>typeof x!=='string'||!x.trim()))throw new Error('Missing case translation');return value.map(String);};
    return {case_key:kind,company_label:bilingual(copy.company),historical_ticker:String(r.historical_symbol).split('.')[0],
      metric:String(r.metric),role:String(r.role),gap_contribution_initial:aggregateNumber(r.gap_contribution_initial),unresolved_reference_initial:aggregateNumber(r.unresolved_reference_initial),
      formation_date:date(r.formation_date),entry_date:date(r.entry_date),exit_date:date(r.exit_date,true),financial_report_period:date(r.financial_report_period),
      official_publication_date:date(r.official_publication_date),vendor_announcement_date:date(r.vendor_ann_date),disposal_status:String(r.disposal_status),
      nonrecurring_share_of_reported_profit:nullable(r.nonrecurring_share_of_reported_profit),nonrecurring_ratio_basis:'reported_period_not_TTM',
      facts:(copy.facts as unknown[]).map(bilingual),gaps:(copy.gaps as unknown[]).map(bilingual),
      sources:(r.sources as Row[]).map(item=>{
        const url=new URL(item.url);
        if(url.protocol!=='https:' || url.hostname!=='static.cninfo.com.cn' || url.search || url.hash || !['formation_financial_report','dated_case_context'].includes(item.evidence_role)) throw new Error('Unapproved primary-source URL');
        return {url:url.href,publication_date:date(item.publication_date),evidence_role:String(item.evidence_role),title_zh:String(item.title)};
      })};
  });
  const result={evidence_status:'bounded_primary_facts_with_open_gaps',revision_safe:false,causal_investigation_complete:false,raw_share_bridge_complete:false,
    audit:{selection_checks:6,official_financial_checks:12,official_documents:16,revision_counterexample_verified:true,earlier_counterexample_buy_failed:true},cases};
  assertPublicRound2(result);return result;
}
