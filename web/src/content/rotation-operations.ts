import schema from './rotation-operations-schema.json';
import {canonical, validatePublicText} from './rotation-evidence';
import {validateDescriptor, type Metrics, type Period} from './rotation-extension';
export type MatchedMetrics = Metrics & {
  volatility:number; target_risky_weight:number; realized_risky_weight:number;
  turnover:number; cost_drag:number;
  attribution:{risk:number;bond:number;costs:number;residual:number;total_return:number};
};
export type MatchedRow = {
  id:string; baseline:string; eligibility_case:string; comparison:string; case_id:string;
  cost_bps:number; execution_delay_sessions:number; window_id:string; protocol_sha256:string;
  status:'available'|'unavailable'; reasons:string[]; period:Period|null;
  reference_period:Period|null; comparator_period:Period|null;
  metrics:{reference:MatchedMetrics;comparator:MatchedMetrics}|null;
  differences:{total_return:number;cagr:number;max_drawdown:number;volatility:number}|null;
  target_budget_error:number|null;realized_exposure_gap:number|null;
  ceiling_breaches:number;inactive_count:number;unavailable_count:number;
};
export type RotationOperations = {
 schema_version:'research.rotation_operations.v1';release_id:string;created_at:string;
 producer_commit:string;base_evidence_id:string;reviewed_source_digest:string;
 health:{state:string;preparation_status:string;capture_state:'armed'|'unarmed';readiness:'met'|'pending';
  cutoff_local:string;timezone:string;observed_at:string;source_session:string|null;
  source_observed_by:string|null;reviewed_at:string|null;captured_weeks:number;settled_weeks:number;
  pending_settlement:number;missing_weeks:number;calendar_valid_through:string|null;
  preparation_timer:'enabled'|'disabled';forward_timer:'enabled'|'disabled';metrics:Metrics|null;reasons:string[]};
 audit:{historical_availability:string;panel_start:string;panel_end:string;sessions:number;symbols:number;
  symbol_week_records:number;changed_records:number;affected_weeks:number;audit_sha256:string;registration_sha256:string;
  rules:{minimum_history:number;amount_sessions:number;minimum_median_amount:number;amount_unit:string};
  dimensions:{rule:string;state:string;records:number;reason:string;admitted:number;unknown:number;rejected:number}[];
  panels:{id:string;symbols:number;changed_records:number;affected_weeks:number}[];
  baseline_gaps:{baseline:string;unavailable_weeks:number;first_week:string|null;last_week:string|null;reasons:{code:string;count:number}[]}[];
  monthly:{month:string;changed_records:number;unavailable_baseline_weeks:number}[];
  source_hashes:{id:string;sha256:string}[];reasons:string[]};
 comparisons:{protocol_sha256:string;report_sha256:string;historical_availability:string;
  budget_definition:string;risk_definition:string;
  risk:{target_vol:number;lookback:number;annualization:number;ddof:number;max_risky_weight:number;bond_above_ceiling:string};
  cases:{id:string;cost_bps:number;execution_delay_sessions:number}[];row_count:number;available_rows:number;rows:MatchedRow[]};
 changes:{kind:string;code:string}[];
};
const same=(a:unknown,b:unknown)=>canonical(a)===canonical(b);
function code(value:string){if(!/^[a-z][a-z0-9_]{0,95}$/.test(value))throw Error('Invalid public reason code');}
function period(value:Period){if(value.start>value.end||value.sessions<2||value.sessions>(Date.parse(value.end)-Date.parse(value.start))/86400000+1)throw Error('Invalid paired period');}
export function validateOperationsShape(value:unknown):RotationOperations{
 validateDescriptor(value,schema);const a=value as RotationOperations;
 if(a.schema_version!=='research.rotation_operations.v1'||!/^[A-Za-z0-9][A-Za-z0-9_-]{0,95}$/.test(a.release_id)||!/^[0-9a-f]{40}$/.test(a.producer_commit))throw Error('Invalid operations identity');
 const h=a.health;
 if(h.timezone!=='Asia/Shanghai'||!/^(?:1[5-9]|2[0-3]):[0-5][0-9]$/.test(h.cutoff_local)||h.metrics!==null)throw Error('Invalid operational health');
 if(!['armed','unarmed'].includes(h.capture_state)||!['met','pending'].includes(h.readiness)||[h.preparation_timer,h.forward_timer].some(v=>!['enabled','disabled'].includes(v))||h.settled_weeks>h.captured_weeks||(h.capture_state==='armed'&&h.readiness!=='met'))throw Error('Invalid operational readiness');
 if(h.source_observed_by&&h.reviewed_at&&Date.parse(h.source_observed_by)>Date.parse(h.reviewed_at))throw Error('Review precedes source');h.reasons.forEach(code);
 const u=a.audit;
 if(u.historical_availability!=='unverified'||!same(u.rules,{minimum_history:252,amount_sessions:252,minimum_median_amount:10000,amount_unit:'thousand_cny'})||u.panel_start>u.panel_end||u.changed_records>u.symbol_week_records)throw Error('Invalid prefix audit');
 u.dimensions.forEach(d=>{code(d.rule);const count=d.admitted+d.unknown+d.rejected;const state=!count||d.unknown?'unknown':d.rejected?'rejected':'admitted';if(d.records!==count||d.state!==state||d.reason!==(count?'see_rule_records':'missing_evidence'))throw Error('Invalid audit dimension state');});u.monthly.forEach(d=>{if(!/^\d{4}-(?:0[1-9]|1[0-2])$/.test(d.month))throw Error('Invalid audit month');});
 u.baseline_gaps.forEach(g=>{if(!['fixed-base','pool-core'].includes(g.baseline))throw Error('Unknown baseline');g.reasons.forEach(r=>code(r.code));});u.reasons.forEach(code);
 validateComparisons(a.comparisons);a.changes.forEach(c=>{code(c.kind);code(c.code);});return a;
}
function validateComparisons(c:RotationOperations['comparisons']){
 if(c.historical_availability!=='unverified'||c.budget_definition!=='selection_conditional_on_reference_target_budget'||c.risk_definition!=='common_estimated_ceiling_not_equal_realized_risk'||!same(c.risk,{target_vol:0.08,lookback:60,annualization:252,ddof:1,max_risky_weight:1,bond_above_ceiling:'unavailable'}))throw Error('Invalid comparison protocol');
 if(c.row_count!==c.rows.length||new Set(c.rows.map(r=>r.id)).size!==c.rows.length||c.available_rows!==c.rows.filter(r=>r.status==='available').length)throw Error('Duplicate pairs or wrong counts');
 const definitions:Record<string,number[]>={primary:[5,1],'cost-zero':[0,1],'cost-ten':[10,1],'delay-two':[5,2]};
 if(new Set(c.cases.map(v=>v.id)).size!==c.cases.length)throw Error('Duplicate cases');
 for(const v of c.cases)if(!same(definitions[v.id],[v.cost_bps,v.execution_delay_sessions]))throw Error('Unregistered case');
 for(const r of c.rows){
  const v=c.cases.find(v=>v.id===r.case_id);
  if(!v||r.protocol_sha256!==c.protocol_sha256||r.cost_bps!==v.cost_bps||r.execution_delay_sessions!==v.execution_delay_sessions||!['fixed-base','pool-core'].includes(r.baseline)||!['budget','estimated-risk'].includes(r.comparison)||!['retained_snapshot','historical_prefix'].includes(r.eligibility_case))throw Error('Invalid paired protocol');
  if(r.id!==[r.eligibility_case,r.baseline,r.case_id,r.comparison,r.window_id].join('-'))throw Error('Invalid pair identity');
  const available=r.status==='available';if(!['available','unavailable'].includes(r.status)||[r.period,r.reference_period,r.comparator_period,r.metrics,r.differences].some(v=>(v!==null)!==available))throw Error('Unavailable metrics or calendar');r.reasons.forEach(code);
  validateWindow(r);
  if(available)validateAvailable(r);
 }
}
function validateWindow(r:MatchedRow){
 const name=r.window_id;if(name==='common')return;
 const last=/^last_(252|756)$/.exec(name),rolling=/^rolling_(252|756)_(\d{4}-\d{2}-\d{2})$/.exec(name),year=/^year_(\d{4})$/.exec(name);
 if(!last&&!rolling&&!year)throw Error('Unknown comparison window');
 if(year&&Number(year[1])<1)throw Error('Invalid window year');
 if(rolling){const date=new Date(rolling[2]+'T00:00:00Z');if(Number(rolling[2].slice(0,4))<1||!Number.isFinite(date.valueOf())||date.toISOString().slice(0,10)!==rolling[2])throw Error('Invalid window date');}
 const p=r.period;if(!p)return;
 if((last||rolling)&&p.sessions!==Number((last||rolling)![1]))throw Error('Incomplete named window');
 if(rolling&&p.end!==rolling[2])throw Error('Rolling window endpoint mismatch');
 if(year&&(!p.start.startsWith(year[1]+'-01-')||!p.end.startsWith(year[1]+'-12-')))throw Error('Incomplete calendar-year window');
}
function validateAvailable(r:MatchedRow){
 if(!same(r.period,r.reference_period)||!same(r.period,r.comparator_period))throw Error('Unequal paired calendars');period(r.period!);
 for(const m of Object.values(r.metrics!)){
  const t=m.attribution;
  if(m.max_drawdown< -1||m.max_drawdown>0||m.volatility<0||m.target_risky_weight<0||m.target_risky_weight>1||m.realized_risky_weight<0||m.realized_risky_weight>1||Math.abs(t.total_return-m.total_return)>1e-10||Math.abs(t.risk+t.bond+t.costs+t.residual-m.total_return)>1e-10)throw Error('Invalid paired attribution');
 }
 for(const [k,d] of Object.entries(r.differences!))if(Math.abs(r.metrics!.reference[k as keyof NonNullable<MatchedRow['differences']>]-r.metrics!.comparator[k as keyof NonNullable<MatchedRow['differences']>]-d)>1e-10)throw Error('Invalid paired difference');
 if(r.comparison==='budget'&&(r.target_budget_error===null||r.target_budget_error>1e-10))throw Error('Budget mismatch');
}
export function validateOperationsReview(a:RotationOperations,value:unknown,hashes:{content:string;asset:string}):void{
 if(!value||typeof value!=='object'||Array.isArray(value))throw Error('Missing operations review');
 const r=value as Record<string,string>;
 if(Object.keys(r).sort().join()!==['status','source_sha256','content_sha256','asset_sha256','reviewer','reviewed_at'].sort().join())throw Error('Unknown review fields');
 Object.values(r).forEach(validatePublicText);
 if(Object.values(r).some(v=>typeof v!=='string'||!v)||r.status!=='approved'||r.source_sha256!==a.reviewed_source_digest||r.content_sha256!==hashes.content||r.asset_sha256!==hashes.asset||!/(Z|[+-]\d{2}:\d{2})$/.test(r.reviewed_at)||!Number.isFinite(Date.parse(r.reviewed_at))||Date.parse(r.reviewed_at)<Date.parse(a.created_at))throw Error('Operations review mismatch');
}
