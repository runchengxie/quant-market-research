import schema from './rotation-foundation-schema.json';
import {validateDescriptor} from './rotation-extension';
import {canonical} from './rotation-evidence';
import {foundationCopy} from './rotation-foundation-copy';
export type FoundationMetric={total_return:number;cagr:number;max_drawdown:number;volatility:number;total_cost:number;turnover:number;mean_risky_exposure:number};
export type FoundationRow={case_id:string;left:string;right:string;status:'available'|'unavailable';expected_sessions:number;weekly_pairs:number;period:{start:string;end:string};reasons:string[];metrics:{left:FoundationMetric;right:FoundationMetric}|null;uncertainty:{estimate:number;interval:number[];weekly_pairs:number;expected_block_weeks:number;replicates:number;seed:number;sensitivity:{expected_block_weeks:number;interval:number[]}[]}|null};
export type RotationFoundation={schema_version:'research.rotation_foundation.v1';release_id:string;producer_commit:string;created_at:string;reviewed_source_digest:string;registration_sha256:string;
 sample:{status:string;candidate_start:string;first_signal:string;last_signal:string;retained_end:string;expected_signals:number;historical_availability:string};
 causes:{cells:number;blocked_decisions:number;distinct_events:number;categories:{code:string;cells:number;decisions:number}[];events:{symbol:string;effective_from:string;effective_to:string;publisher:string;url:string;published_at:string|null;retrieved_at:string;sha256:string}[]};
 case_calendars:{case_id:string;cost_bps:number;execution_delay_sessions:number;start:string;end:string;sessions:number;expected_signals:number}[];
 comparisons:FoundationRow[];theme:{status:string;required_signals:number;admitted_signals:number;metrics:FoundationMetric|null};
 readiness:{status:string;capture_state:string;settled_pairs:number;source_session:string|null;observed_at:string};
 policy:{minimum_pairs:number;review_every_pairs:number;expected_block_weeks:number;replicates:number;seed:number;interval_level:number;economic_boundary_net_annual_log_return:number};decision:string;};
const same=(a:unknown,b:unknown)=>canonical(a)===canonical(b);
export function validateFoundationShape(value:unknown):RotationFoundation{
 validateDescriptor(value,schema);const a=value as RotationFoundation;
 if(a.schema_version!=='research.rotation_foundation.v1'||!/^[A-Za-z0-9][A-Za-z0-9_-]{0,95}$/.test(a.release_id)||!/^[0-9a-f]{40}$/.test(a.producer_commit))throw Error('Invalid foundation identity');
 const s=a.sample;
 if(s.status!=='inspected_retained_universe_retrospective'||s.historical_availability!=='unverified'||!(s.candidate_start<=s.first_signal&&s.first_signal<=s.last_signal&&s.last_signal<s.retained_end)||s.expected_signals<1)throw Error('Invalid retrospective sample');
 if(!same(a.policy,{minimum_pairs:104,review_every_pairs:52,expected_block_weeks:13,replicates:10000,seed:20261018,interval_level:.95,economic_boundary_net_annual_log_return:0}))throw Error('Invalid foundation policy');
 const c=a.causes;
 if(!same(c.categories.map(v=>v.code),['prelisting','suspension','unresolved'])||c.categories.reduce((n,v)=>n+v.cells,0)!==c.cells||c.categories.reduce((n,v)=>n+v.decisions,0)!==c.blocked_decisions||c.events.length!==c.distinct_events||new Set(c.events.map(v=>[v.symbol,v.effective_from,v.effective_to].join(':'))).size!==c.events.length)throw Error('Invalid cause reconciliation');
 c.events.forEach(e=>{const u=new URL(e.url);if(u.protocol!=='https:'||e.effective_from>e.effective_to)throw Error('Invalid source URL or interval');});
 if(!a.comparisons.length||new Set(a.comparisons.map(r=>[r.case_id,r.left,r.right].join(':'))).size!==a.comparisons.length)throw Error('Invalid comparison identities');
 validateCalendars(a);
 a.comparisons.forEach(validateRow);
 const t=a.theme;
 if(!['admitted','unavailable'].includes(t.status)||t.metrics!==null||t.required_signals!==s.expected_signals||t.admitted_signals!==(t.status==='admitted'?t.required_signals:0))throw Error('Invalid theme coverage');
 if(t.status!=='admitted'&&a.comparisons.some(r=>r.left==='theme-overlay'&&r.status==='available'))throw Error('Unavailable theme cannot have returns');
 if(!['awaiting_weekday_evidence','ready_for_future_registration'].includes(a.readiness.status)||!['armed','unarmed'].includes(a.readiness.capture_state)||!['descriptive_only','unavailable','paused','inconclusive'].includes(a.decision))throw Error('Invalid evidence stage');
 return a;
}
function validateRow(r:FoundationRow){
 if(!['primary','cost-zero','cost-ten','delay-two'].includes(r.case_id)||!['combined:passive','selection-only:passive','timing-only:passive','combined:selection-only','theme-overlay:combined'].includes(`${r.left}:${r.right}`))throw Error('Unknown component comparison');
 if(!['available','unavailable'].includes(r.status)||[r.metrics,r.uncertainty].some(v=>(v!==null)!==(r.status==='available'))||r.expected_sessions<2||r.period.start>r.period.end||r.reasons.some(v=>!/^[a-z][a-z0-9_]{0,95}$/.test(v)))throw Error('Invalid unavailable metrics or calendar');
 const u=r.uncertainty;
 if(u&&(u.weekly_pairs!==r.weekly_pairs||u.expected_block_weeks!==13||u.replicates!==10000||u.seed!==20261018||!same(u.sensitivity.map(v=>v.expected_block_weeks),[8,26])||[u.interval,...u.sensitivity.map(v=>v.interval)].some(v=>v.length!==2||v[0]>v[1])))throw Error('Invalid uncertainty');
}
export function validateFoundationReview(asset:RotationFoundation,review:unknown,hashes:{content:string;asset:string}){
 const r=review as Record<string,unknown>;
 if(!r||Object.keys(r).sort().join()!==['status','source_sha256','content_sha256','asset_sha256','reviewer','reviewed_at'].sort().join()||r.status!=='approved'||r.source_sha256!==asset.reviewed_source_digest||r.content_sha256!==hashes.content||r.asset_sha256!==hashes.asset||typeof r.reviewer!=='string'||!/^[A-Za-z0-9][A-Za-z0-9_-]{0,95}$/.test(r.reviewer)||typeof r.reviewed_at!=='string'||!/(Z|[+-]\d{2}:\d{2})$/.test(r.reviewed_at)||!Number.isFinite(Date.parse(r.reviewed_at))||Date.parse(r.reviewed_at)<Date.parse(asset.created_at))throw Error('Invalid foundation review binding');
}
export function foundationComparison(a:RotationFoundation,caseId:string,left:string,right:string){return a.comparisons.find(r=>r.case_id===caseId&&r.left===left&&r.right===right);}
export function foundationPercent(value:number|null,locale='en-US'){return value===null?foundationCopy.unavailable[locale==='zh-CN'?1:0]:new Intl.NumberFormat(locale,{style:'percent',minimumFractionDigits:2,maximumFractionDigits:2}).format(value);}

const caseDefinitions:Record<string,number[]>={primary:[5,1],'cost-zero':[0,1],'cost-ten':[10,1],'delay-two':[5,2]};
const componentPairs=['combined:passive','selection-only:passive','timing-only:passive','combined:selection-only','theme-overlay:combined'];
function validateCalendars(a:RotationFoundation){
 const cases=a.case_calendars;
 if(cases.length!==4||new Set(cases.map(c=>c.case_id)).size!==4||cases.some(c=>!same(caseDefinitions[c.case_id],[c.cost_bps,c.execution_delay_sessions])||c.end!==a.sample.retained_end||!(a.sample.first_signal<c.start&&c.start<=c.end)||c.expected_signals!==a.sample.expected_signals||c.sessions<2))throw Error('Invalid registered case calendars');
 const expected=Object.keys(caseDefinitions).flatMap(id=>componentPairs.map(pair=>id+':'+pair)).sort();
 if(!same(a.comparisons.map(r=>r.case_id+':'+r.left+':'+r.right).sort(),expected))throw Error('Incomplete registered matrix');
 for(const row of a.comparisons){const c=cases.find(c=>c.case_id===row.case_id)!;const max=Math.floor((Date.parse(c.end)-Date.parse(c.start))/604800000)+1;if(row.expected_sessions!==c.sessions||row.period.start!==c.start||row.period.end!==c.end||row.weekly_pairs>max)throw Error('Comparison calendar mismatch');}
}
