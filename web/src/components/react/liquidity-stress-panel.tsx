import {useState} from 'react';
import {liquidityStressCopy as copy} from '../../content/liquidity-stress-copy';
import {stressBudgets,scaleWindowBudget} from '../../lib/liquidity-stress';
import {formatNumber as num} from '../../lib/format';
import {withBase} from '../../lib/routes';
import {BarChart,Panel,SimpleTable,Loading,ResourceState,useJson,englishLocale} from './research-shared';
const text=(key:keyof typeof copy)=>copy[key][englishLocale()?0:1];
const money=(value:number|null|undefined)=>value==null?text('missing'):`$${num(value)}`;
const pct=(value:number|null|undefined)=>value==null?text('missing'):`${num(value*100)}%`;
type Stress={year:number;bucket:number;months:number;min_daily_stocks:number;stress_months:string[];normal_median_usd:number|null;stress_median_usd:number|null;retained_budget_fraction:number|null};
type Cohort={year:number;bucket:number;formations:number;formation_stock_observations:number;retained_fraction:number;migrated_fraction:number;ineligible_fraction:number;missing_fraction:number;continuous_fraction:number;usable_continuous_fraction:number;frozen_valid_formations:number;frozen_min_ratio_median:number|null;min_coverage:number};
type Window={year:number;bucket:number;window:string;dates:number;observations:number;missing_window_observations:number;p25:number|null;median:number|null;p75:number|null};
type Evidence={buckets:string[];stress:Stress[];cohorts:Cohort[];windows:Window[];minute_quality:Array<{date:string;eligible_candidates:number;accepted:number;reasons:Record<string,number>}>};
export function LiquidityStressPanel(){
 const resource=useJson<Evidence>('liquidity/stress-persistence.json');
 const [year,setYear]=useState('2025');const [bucket,setBucket]=useState('2');const [window,setWindow]=useState('open30');
 const [participation,setParticipation]=useState('3');const [days,setDays]=useState('5');const [holdings,setHoldings]=useState('20');const [fullBudget,setFullBudget]=useState('1000000');
 if(resource.error)return <ResourceState error={resource.error} retry={resource.retry} label={text('title')}/>;
 if(!resource.data)return <Loading/>;
 const data=resource.data;const years=[...new Set(data.stress.map(row=>row.year))].sort((a,b)=>a-b);
 const selectedYear=years.includes(Number(year))?Number(year):years[years.length-1];const b=Number(bucket);
 const stress=data.stress.find(row=>row.year===selectedYear&&row.bucket===b);const cohort=data.cohorts.find(row=>row.year===selectedYear&&row.bucket===b);
 const w=data.windows.find(row=>row.year===selectedYear&&row.bucket===b&&row.window===window);
 const budget=stress?stressBudgets(stress.normal_median_usd,stress.stress_median_usd,Number(participation)/100,Number(days),Number(holdings),stress.min_daily_stocks):null;
 const scaled=w&&fullBudget.trim()!==''?scaleWindowBudget(Number(fullBudget),[w.p25,w.median,w.p75]):null;
 const phases=[{label:text('normal'),baseline:stress?.normal_median_usd,budget:budget?.normal},{label:text('stress'),baseline:stress?.stress_median_usd,budget:budget?.stress}];
 const cohortBars=cohort?([{key:'retained',value:cohort.retained_fraction},{key:'migrated',value:cohort.migrated_fraction},{key:'ineligible',value:cohort.ineligible_fraction},{key:'absent',value:cohort.missing_fraction}] as const):[];
 return <section id="liquidity-stress" className="report-section"><h2>{text('title')}</h2><p>{text('intro')}</p>
  <div className="liquidity-filters"><label>{text('year')}<select aria-label={text('year')} value={selectedYear} onChange={event=>setYear(event.target.value)}>{years.map(value=><option key={value}>{value}</option>)}</select></label><label>{text('bucket')}<select aria-label={text('bucket')} value={bucket} onChange={event=>setBucket(event.target.value)}>{data.buckets.map((label,index)=><option key={label} value={index}>{label}</option>)}</select></label></div>
  <Panel title={text('stressTitle')} tag={`${selectedYear} · ${data.buckets[b]}`}><p>{text('stressMethod')}</p>
   {stress?.retained_budget_fraction!=null?<><BarChart rows={phases.map(row=>({phase:row.label,value:String(row.baseline)}))} labelKey="phase" valueKey="value" formatter={money}/><p>{text('months')}: {num(stress.months)} · {text('stressMonths')}: {stress.stress_months.join(', ')} · {text('fraction')}: {pct(stress.retained_budget_fraction)}</p></>:<p role="status">{text('insufficient')}</p>}
   <h3>{text('scenarioTitle')}</h3><p className="panel-note">{text('scenarioNote')}</p><p>{text('minimumStocks')}: {num(stress?.min_daily_stocks)}</p><div className="liquidity-filters"><label>{text('participation')}<input type="number" min="0.01" max="100" value={participation} onChange={e=>setParticipation(e.target.value)}/></label><label>{text('days')}<input type="number" min="1" max="252" value={days} onChange={e=>setDays(e.target.value)}/></label><label>{text('holdings')}<input type="number" min="1" max="1000" value={holdings} onChange={e=>setHoldings(e.target.value)}/></label></div>
   {!budget&&<p role="status">{text('unavailable')}</p>}<SimpleTable rows={phases.map(row=>({phase:row.label,baseline:money(row.baseline),budget:money(row.budget)}))} columns={[["phase",text('phase')],["baseline",text('baseline')],["budget",text('budget')]]}/>
  </Panel>
  <Panel title={text('cohortTitle')} tag="20"><p>{text('cohortNote')}</p>{cohort?<><BarChart rows={cohortBars.map(row=>({state:text(row.key),value:String(row.value)}))} labelKey="state" valueKey="value" formatter={pct}/><SimpleTable rows={[
   {metric:text('formations'),value:num(cohort.formations)},{metric:text('cohortStocks'),value:num(cohort.formation_stock_observations)},{metric:text('usableContinuous'),value:pct(cohort.usable_continuous_fraction)},{metric:text('continuous'),value:pct(cohort.continuous_fraction)},{metric:text('frozen'),value:pct(cohort.frozen_min_ratio_median)},{metric:text('frozenCount'),value:`${num(cohort.frozen_valid_formations)} / ${num(cohort.formations)}`},{metric:text('coverage'),value:pct(cohort.min_coverage)},
  ]} columns={[["metric",text('metric')],["value",text('value')]]}/><p className="panel-note">{text('frozenNote')}</p></>:<p role="status">{text('noCohort')}</p>}</Panel>
  <Panel title={text('windowTitle')} tag={String(selectedYear)}><p>{text('windowNote')}</p><div className="liquidity-filters"><label>{text('clock')}<select aria-label={text('clock')} value={window} onChange={e=>setWindow(e.target.value)}>{(['open30','late_morning','afternoon','close30','core'] as const).map(value=><option key={value} value={value}>{text(value)}</option>)}</select></label><label>{text('fullBudget')}<input type="number" min="0" max="1000000000000000" value={fullBudget} onChange={e=>setFullBudget(e.target.value)}/></label></div>
   {w?<>{!scaled&&<p role="status">{text('budgetInvalid')}</p>}<p>{text('dates')}: {num(w.dates)} · {text('observations')}: {num(w.observations)} · {text('missingWindows')}: {num(w.missing_window_observations)}</p><SimpleTable rows={[w.p25,w.median,w.p75].map((value,index)=>({quantile:['P25','P50','P75'][index],share:pct(value),budget:money(scaled?.[index])}))} columns={[["quantile",text('quantile')],["share",text('share')],["budget",text('scaled')]]}/></>:<p role="status">{text('noWindows')}</p>}
   <p className="panel-note">{text('windowBudgetNote')}</p><p className="data-notice" role="note">{text('clockCaveat')}</p>
   <details><summary>{text('quality')}</summary><SimpleTable rows={data.minute_quality.filter(row=>row.date.startsWith(String(selectedYear))).map(row=>({date:row.date,candidates:num(row.eligible_candidates),accepted:num(row.accepted),short:num(row.reasons.short_day??0),mismatch:num(row.reasons.amount_mismatch??0),missing:num(row.reasons.missing_minute??0),other:num((row.reasons.missing_daily??0)+(row.reasons.nonpositive_total??0))}))} columns={[["date",text('date')],["candidates",text('candidates')],["accepted",text('accepted')],["short",text('short')],["mismatch",text('mismatch')],["missing",text('missingMinute')],["other",text('other')]]}/></details>
  </Panel><p className="report-links"><a download href={withBase('/data/liquidity/stress-persistence.json',import.meta.env.BASE_URL)}>{text('aggregates')}</a><a download href={withBase('/data/liquidity/stress-review.json',import.meta.env.BASE_URL)}>{text('receipt')}</a></p>
 </section>;
}
