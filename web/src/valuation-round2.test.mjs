import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { buildRound2Evidence, assertPublicRound2, buildAttributionEvidence, buildControlEvidence, validateControlReceiptChain, buildCaseEvidence } from './lib/valuation-round2.ts';
function fixture() {
 const rulesHash='a'.repeat(64);
 const portfolios=['pb_parent','pe_deducted_proxy'].flatMap(metric=>['touch10','close10','touch0','touch30'].flatMap(scenario=>[1,2,3,4,5].map(quintile=>({metric,scenario,quintile,unresolved_lots:1,strict_total_change:null}))));
 portfolios.at(-1).unresolved_lots=0;portfolios.at(-1).strict_total_change=.2;
 const unresolved={portfolios:portfolios.map(r=>({...r,unpriced_lots:r.unresolved_lots,valued_but_unexited_lots:0,raw_share_ready:false,revision_safe:false}))};
 const sensitivities=portfolios.flatMap(r=>['A_unpriced_only','B_all_remaining'].flatMap(scope=>[0,.5,1].map(reference_fraction=>({...r,scope,reference_fraction,valuation_only:true,cash_change:0,units_changed:false,not_recovery_probability_or_bound:true,reference_complete:true,unknown_reference_lots:0,scenario_change_from_initial:.2+reference_fraction*.01,symbol:'PRIVATE_ID',cash:999999,private_path:'/home/private'}))));
 return {rulesHash,sourceHashes:{source:'b'.repeat(64)},rules:{schema:'valuation_round2_rules.v1',primary_scenario:'touch10',attribution:{initial_capital:1000000},design_id:'grouped-valuation-round2-20261021',primary_contrasts:[['pb_parent',1,2],['pe_deducted_proxy',1,3]],forward_validation:{status:'protocol_only_not_started',earliest_formation_month:'2026-11',minimum_monthly_cohorts:12}},
 freeze:{status:'rules_frozen_before_new_analysis',design_id:'grouped-valuation-round2-20261021',inputs:{rules:rulesHash},genuine_holdout_admitted:false,forward_validation_started:false,previous_history_explored:true,frozen_at_utc:'2026-10-21T14:38:06Z',baseline_commit:'c'.repeat(40)},checkpoint:{portfolios,raw_share_ready:false,revision_safe:false},unresolved,sensitivities};
}
test('explicit projection keeps 240 supported rows and drops private source details',()=>{
 const data=buildRound2Evidence(fixture());assert.equal(data.sensitivities.length,240);
 assert.equal(data.scope.strict_terminal_unavailable,39);assert.equal(data.freeze.genuine_holdout_admitted,false);
 assert.equal(data.sensitivities[0].strict_total_change,null);
 assert.ok(!/PRIVATE_ID|999999|private_path|\/home\//.test(JSON.stringify(data)));
});
test('malformed fractions, duplicate rows, partial support and cash creation fail closed',()=>{
 for(const mutate of [i=>i.sensitivities[0].reference_fraction=.25,i=>i.sensitivities[0].cash_change=1,i=>i.sensitivities[0].units_changed=true,i=>i.sensitivities.pop(),i=>i.sensitivities[1]=i.sensitivities[0],i=>i.sensitivities[0].unknown_reference_lots=1]){
 const input=fixture();mutate(input);assert.throws(()=>buildRound2Evidence(input));}
});
test('strict and validation promotion, unbound rules and private public data are rejected',()=>{
 for(const mutate of [i=>i.checkpoint.portfolios[0].strict_total_change=.2,i=>i.freeze.genuine_holdout_admitted=true,i=>i.freeze.forward_validation_started=true,i=>i.rulesHash='d'.repeat(64),i=>i.unresolved.portfolios.pop()]){
 const input=fixture();mutate(input);assert.throws(()=>buildRound2Evidence(input));}
 for(const item of [{symbol:'abc'},{cash:1},{note:'/home/private'},{note:'600000.SH'},{note:'C:\\data\\private'}]) assert.throws(()=>assertPublicRound2(item));
});
test('unknown references keep scenario and strict results unavailable',()=>{
 const input=fixture();const row=input.sensitivities[0];row.reference_complete=false;row.unknown_reference_lots=1;row.scenario_change_from_initial=null;
 assert.equal(buildRound2Evidence(input).sensitivities[0].total_change,null);
});

function attributionFixture() {
 const input=fixture(), projected=buildRound2Evidence(input);
 const summary={schema_version:'grouped_valuation_attribution.v1',status:'completed_readonly_attribution',raw_share_ready:false,revision_safe:false,portfolios:input.checkpoint.portfolios.map(r=>({...r,raw_share_ready:false,revision_safe:false,planned_members:10,filled_buys:8,failed_buys:2,zero_budget_members:0,terminal_unpriced_lots:r.unresolved_lots,unknown_reference_lots:0,strict_unknown_days:10,contribution_initial_0:.2,contribution_initial_50:.205,contribution_initial_100:.21,contribution_initial_strict:r.strict_total_change,buy_fees:10000,sell_fees:10000,gross_pnl_0_same_path:220000,terminal_lot_net_pnl_0:-50000,closed_lot_net_pnl:250000,cash_year_exposure:100000,interest_per_1pct_simple:1000,daily_mean_cash_fraction_initial:.1,budget_reconstruction_max_error:1e-8,cash_max_error:1e-8,net_pnl_max_error:1e-8,symbol:'PRIVATE_ID'}))};
 const reconciliation={passed:true,portfolios:40,strict_unknown_portfolios:39,all_members_retained:true,budgets_verified:true,zero_and_reference_sensitivities_reconciled:true,annual_lot_and_portfolio_identities_reconciled:true};
 return {summary,reconciliation,sensitivities:projected.sensitivities};
}
test('contributions normalize amounts and independently reconcile net and strict evidence',()=>{
 const f=attributionFixture(),data=buildAttributionEvidence(f.summary,f.reconciliation,f.sensitivities);
 assert.equal(data.portfolios[0].buy_fee_fraction_initial,.01);assert.equal(data.portfolios[0].gross_pnl_initial_0,.22);
 assert.equal(data.portfolios[0].contribution_initial_strict,null);assert.ok(!/10000|PRIVATE_ID|buy_fees/.test(JSON.stringify(data)));
 for(const mutate of [f=>f.summary.portfolios[0].gross_pnl_0_same_path=230000,f=>f.summary.portfolios[0].contribution_initial_strict=.2,f=>f.summary.portfolios[0].filled_buys=9,f=>f.reconciliation.budgets_verified=false,f=>f.summary.portfolios[0].cash_max_error=.01]){
  const input=attributionFixture();mutate(input);assert.throws(()=>buildAttributionEvidence(input.summary,input.reconciliation,input.sensitivities));
 }
});
function controlsFixture() {
 return {schema_version:'valuation_controls_summaries.v1',outcome_units:'lifetime_cohort_net_pnl_per_intended_budget',contrast_direction:'q1_minus_comparator',genuine_holdout_admitted:false,revision_safe:false,rows:['pb_parent','pe_deducted_proxy'].flatMap(metric=>['all_frozen','common_five'].flatMap(sample_basis=>['report_size','report_size_profitability','secondary_quality','secondary_leverage'].flatMap(layer=>['full_frozen','feature_complete','overlap'].flatMap(stage=>['strict','reference_0','reference_50','reference_100'].map(outcome=>{
 const supported=outcome==='strict'?0:36;
 return {metric,comparison_quintile:metric==='pb_parent'?2:3,primary_contrast:true,sample_basis,layer,stage,outcome,scheduled_months:36,supported_months:supported,supported_formation_months:supported?['202212',...Array.from({length:12},(_,i)=>'2023'+String(i+1).padStart(2,'0')),...Array.from({length:12},(_,i)=>'2024'+String(i+1).padStart(2,'0')),...Array.from({length:11},(_,i)=>'2025'+String(i+1).padStart(2,'0'))]:[],q1_member_slots:100,comparison_member_slots:100,q1_unknown_slots:supported?0:1,comparison_unknown_slots:supported?0:1,mean_q1_retention:.8,mean_comparison_retention:.7,equal_month_mean_contrast:supported?.01:null,positive_month_share:supported?.6:null,yearly:Object.entries({2022:1,2023:12,2024:12,2025:11}).map(([formation_year,scheduled_months])=>({formation_year,scheduled_months,supported_months:supported?scheduled_months:0,equal_month_mean_contrast:supported?.01:null,positive_month_share:supported?.6:null})),leave_one_year_out:[],bootstrap:{status:supported?'available':'insufficient_support',low:supported?-.01:null,high:supported?.02:null,valid_replications:supported?2000:0,invalid_replications:0,supported_month_range:supported?['202212','202511']:[]}};
 })))))};
}
test('control projection retains original formation support and refuses fabricated stability evidence',()=>{
 const data=buildControlEvidence(controlsFixture());assert.equal(data.rows.length,192);assert.equal(data.rows[0].supported_month_mean_contrast,null);
 assert.deepEqual(data.rows[1].yearly.map(y=>y.scheduled_months),[1,12,12,11]);
 for(const mutate of [i=>i.rows[0].bootstrap.low=-.1,i=>i.rows[0].equal_month_mean_contrast=.01,i=>i.rows[1].yearly[0].scheduled_months=12,i=>i.rows[1].supported_formation_months.pop(),i=>i.rows.pop()]){
  const input=controlsFixture();mutate(input);assert.throws(()=>buildControlEvidence(input));
 }
});

test('calendar-year contributions retain original capital and cannot omit a carry year',()=>{
 const f=attributionFixture();
 const annual=f.summary.portfolios.flatMap(r=>['2023','2024','2025','2026'].map(year=>({metric:r.metric,quintile:r.quintile,scenario:r.scenario,year,start_date:year+'0103',end_date:year+'1201',net_pnl_0:'50000',net_pnl_strict:r.contribution_initial_strict==null?'':'50000',contribution_initial_0:'.05',buy_fees:'2500',sell_fees:'2500',strict_unknown_days:'10',reconciliation_error:'0'})));
 assert.equal(buildAttributionEvidence(f.summary,f.reconciliation,f.sensitivities,annual).annual.length,160);
 for(const mutate of [rows=>rows.pop(),rows=>rows[0].net_pnl_0='60000',rows=>rows[0].buy_fees='',rows=>rows[0].reconciliation_error='.001']) {
  const rows=structuredClone(annual);mutate(rows);assert.throws(()=>buildAttributionEvidence(f.summary,f.reconciliation,f.sensitivities,rows));
 }
});

test('strict 16/36 support cannot become a complete scheduled-batch mean',()=>{
 const input=controlsFixture(),row=input.rows[0];
 row.supported_months=16;row.supported_formation_months=input.rows[1].supported_formation_months.slice(0,16);row.equal_month_mean_contrast=.01;row.positive_month_share=.5;
 const counts=[1,12,3,0];row.yearly.forEach((y,i)=>{y.supported_months=counts[i];y.equal_month_mean_contrast=counts[i]?.01:null;y.positive_month_share=counts[i]?.5:null;});
 row.bootstrap.supported_month_range=['202212','202403'];
 const result=buildControlEvidence(input).rows[0];
 assert.equal(result.full_schedule_complete,false);assert.equal(result.missing_month_count,20);
 assert.equal(result.full_schedule_mean_contrast,null);assert.equal(result.supported_month_mean_contrast,.01);
 assert.equal(result.yearly[2].full_schedule_mean_contrast,null);assert.equal(result.yearly[2].supported_month_mean_contrast,.01);
 assert.equal(result.yearly[0].full_schedule_complete,true);assert.equal(result.yearly[0].scheduled_months,1);
});

test('actual normal producer receipt omits recovery metadata and requires the independent frozen chain',()=>{
 const hashes={rules:'1'.repeat(64),freeze_receipt:'2'.repeat(64),attribution_receipt:'3'.repeat(64),controls_receipt:'4'.repeat(64),controls_summary:'5'.repeat(64)};
 // Mirrors the normal producer dict, without any seal_recovery/frozen_design_receipt fields.
 const receipt={schema_version:'valuation_controls_receipt.v1',status:'completed_unpublished_exploration',generated_at_utc:'2026-10-21T14:58:02Z',rules_sha256:hashes.rules,
  inputs:{'/source/receipt.json':'a'.repeat(64),'/attribution/receipt.json':hashes.attribution_receipt,'/repo/rules.json':hashes.rules},
  source_hashes:{'scripts/analyze_grouped_valuation_controls.py':'b'.repeat(64)},outputs:{'summaries.json':hashes.controls_summary},
  source_member_rows:323072,periods:27648,summaries:768,no_backtest_rerun:true,outcome_independent_matching:true,genuine_holdout_admitted:false,
  resource_policy:{threads:2,working_memory_target:'512MB_to_1GB',openblas_threads:1}};
 const inputs={'/freeze/receipt.json':hashes.freeze_receipt,'/controls/receipt.json':hashes.controls_receipt,'/controls/summaries.json':hashes.controls_summary};
 const supplemental={status:'passed_independent_post_run_audits',inputs:structuredClone(inputs),no_outcomes_recomputed:true};
 const semantic={status:'passed_semantic_addendum_without_reestimation',inputs:structuredClone(inputs),no_analysis_rerun:true};
 const cross={status:'passed',controls_receipt_sha256:hashes.controls_receipt,attribution_receipt_sha256:hashes.attribution_receipt,frozen_design_receipt_sha256:hashes.freeze_receipt,
  same_original_member_bytes:true,same_derived_outcome_bytes:true,checks:Array.from({length:3},()=>({frozen_design_and_controls_match:true}))};
 assert.doesNotThrow(()=>validateControlReceiptChain(receipt,supplemental,semantic,cross,hashes));
 assert.equal('frozen_design_receipt_sha256' in receipt,false);assert.equal('seal_recovery' in receipt,false);
 for(const mutate of [
  f=>f.receipt.frozen_design_receipt_sha256='f'.repeat(64),
  f=>f.cross.frozen_design_receipt_sha256='f'.repeat(64),
  f=>f.semantic.inputs['/freeze/receipt.json']='f'.repeat(64),
  f=>f.supplemental.inputs['/controls/summaries.json']='f'.repeat(64),
  f=>f.receipt.status='completed_readonly_controls',
 ]) {
  const f=structuredClone({receipt,supplemental,semantic,cross});mutate(f);
  assert.throws(()=>validateControlReceiptChain(f.receipt,f.supplemental,f.semantic,f.cross,hashes));
 }
});

function caseFixture() {
 const kinds=['pb_positive_gap','pb_negative_gap','pb_unresolved_reference','pe_positive_gap','pe_negative_gap','pe_unresolved_reference'];
 const copies=Object.fromEntries(kinds.map(kind=>[kind,{company:['Case '+kind,'案例'+kind],facts:[['Reviewed fact','已核对事实']],gaps:[['Recovery remains unknown','回收仍未知']]}]));
 const source={schema:'valuation_round2_cases.v1',status:'bounded_primary_evidence_checkpoint_with_gaps',revision_safe:false,selection_changed:false,no_ledger_recalculation:true,cases:kinds.map((kind,i)=>({
  case_key:kind,name:'案例'+kind,symbol:'PRIVATE_ID',historical_symbol:'00000'+i+'.SZ',metric:kind.startsWith('pb_')?'pb_parent':'pe_deducted_proxy',role:kind.slice(3),disposal_status:'no_terminal_unresolved_lot',revision_safe:false,gap_contribution_initial:.001,unresolved_reference_initial:0,formation_date:'20230131',entry_date:'20230201',exit_date:null,financial_report_period:'20220930',official_publication_date:'2022-10-28',vendor_ann_date:'20221028',nonrecurring_share_of_reported_profit:.1,verified_facts:['PRIVATE_AMOUNT 999999'],sources:[{url:'https://static.cninfo.com.cn/finalpage/2022-10-28/123.PDF',title:'Official report',publication_date:'2022-10-28',evidence_role:'formation_financial_report'}],
 }))};
 const audit={status:'passed',selection_cases:6,selection_gap_checks:6,reference_checks:6,official_financial_value_checks:12,official_pdfs_hashed:16,revision_counterexample_verified:true,revision_counterexample_earliest_selected_buy_failed:true,source_data_changed:false,ledger_changed:false,cash_recovery_booked:false};
 return {source,copies,audit};
}
test('reviewed case projection retains public facts and rejects unapproved sources or evidence promotion',()=>{
 const f=caseFixture(),data=buildCaseEvidence(f.source,f.copies,f.audit);
 assert.equal(data.cases.length,6);assert.equal(data.revision_safe,false);assert.equal(data.causal_investigation_complete,false);
 assert.ok(!/PRIVATE_AMOUNT|999999|PRIVATE_ID|000000\.SZ/.test(JSON.stringify(data)));
 for(const mutate of [f=>f.source.selection_changed=true,f=>f.audit.cash_recovery_booked=true,f=>f.source.cases.pop(),f=>f.source.cases[0].sources[0].url='https://unapproved.example/report',f=>f.source.cases[0].name='wrong company']){
  const input=caseFixture();mutate(input);assert.throws(()=>buildCaseEvidence(input.source,input.copies,input.audit));
 }
});
test('prepared final public evidence binds every layer without promoting partial strict results',()=>{
 const data=JSON.parse(readFileSync(new URL('../public/data/valuation_round2_draft.json',import.meta.url),'utf8'));
 assert.equal(data.sensitivities.length,240);assert.equal(data.attribution.portfolios.length,40);assert.equal(data.attribution.annual.length,160);
 assert.equal(data.controls.rows.length,192);assert.equal(data.controls.audit.bucket_aggregate_rows,151589);assert.equal(data.case_progress.cases.length,6);
 const partial=data.controls.rows.find(r=>r.metric==='pb_parent'&&r.sample_basis==='all_frozen'&&r.layer==='report_size_profitability'&&r.stage==='overlap'&&r.outcome==='strict');
 assert.equal(partial.supported_months,16);assert.equal(partial.full_schedule_mean_contrast,null);assert.equal(partial.full_schedule_complete,false);
 assert.notEqual(partial.supported_month_mean_contrast,null);assert.equal(partial.missing_months.length,20);
 for(const row of data.controls.rows) for(const year of row.yearly) if(['2022','2025'].includes(year.formation_year)) assert.equal(year.full_calendar_year_mean_contrast,null);
 for(const hash of Object.values(data.source_sha256))assert.match(hash,/^[a-f0-9]{64}$/);
 assertPublicRound2(data);assert.equal(data.freeze.forward_validation_started,false);
});
