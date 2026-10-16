import { useState } from 'react';
import { liquidityCaveats } from '../../liquidity-copy';
import { liquidityResearchCopy as copy } from '../../content/liquidity-research-copy';
import { formatNumber as num } from '../../lib/format';
import { withBase } from '../../lib/routes';
import { auditLiquidityMarket, liquidityComparison, marketsForPeriod, mechanicalOrderBudget, type LiquidityMetric } from '../../lib/liquidity-quality';
import { Panel, BarChart, ControlBar, Choice, SimpleTable, Loading, ResourceState, useJson, englishLocale } from './research-shared';
import type { LiquiditySummary, LiquidityRelativeSummary, LiquidityCoverageSummary } from './research-shared';

const text = (key: keyof typeof copy) => copy[key][englishLocale() ? 0 : 1];
const money = (value: number | null | undefined) => value == null ? text('missing') : `$${num(value)}`;
export function LiquidityPage({ embedded = false }: { embedded?: boolean }) {
 return <LiquidityPeriodPanel embedded={embedded}/>;
}

export function LiquidityPeriodPanel({ embedded = false }: { embedded?: boolean }) {
 const { data: summary, error, retry } = useJson<LiquiditySummary>('liquidity/summary.json');
 const coverageResource=useJson<LiquidityCoverageSummary>('liquidity/capacity-data-quality.json');
 const [chosenPeriod,setPeriod]=useState<string|null>(null);
 const [market,setMarket]=useState('all');
 const [absoluteBucket,setAbsoluteBucket]=useState(2);
 const [relativeBucket,setRelativeBucket]=useState(0);
 const [grouping,setGrouping]=useState<'absolute'|'relative'>('absolute');
 const relativeResource=useJson<LiquidityRelativeSummary>('liquidity/relative-summary.json');
 const [metric,setMetric]=useState<LiquidityMetric>('median_usd');
 const [basis,setBasis]=useState<'adv20'|'median20'>('adv20');
 const [log,setLog]=useState(true);
 if(error) return <ResourceState error={error} retry={retry} label={text('explorer')}/>;
 if(!summary) return <Loading/>;
 const period=chosenPeriod??(summary.periods?.some(item=>item.period==='common snapshot')?'common snapshot':'latest');
 const source=grouping==='relative'?relativeResource.data:summary;
 const bucket=grouping==='relative'?relativeBucket:absoluteBucket;
 const setBucket=grouping==='relative'?setRelativeBucket:setAbsoluteBucket;
 const selected=source?.periods?.find(item=>item.period===period);
 const markets=source?marketsForPeriod({...summary,markets:source.markets,periods:source.periods},period):[];
 const visible=markets.filter(item=>market==='all'||item.market===market);
 const rows=liquidityComparison(markets,bucket,metric,basis).filter(item=>market==='all'||item.market===market);
 const buckets=source?.markets[0]?.buckets??[];
 const bucketLabel=grouping==='relative'?text('relativeBucket'):text('bucket');
 const displayCount=(value:number|undefined)=>value==null?text('missing'):num(value);
 const issueText=(item: typeof summary.markets[number])=>auditLiquidityMarket(item).map(issue=>`${text(issue.code)}: ${num(issue.reported)} / ${num(issue.grouped)}`).join('; ');
 const valueFor=(row: typeof buckets[number], key: LiquidityMetric)=>row[basis==='adv20'?key:(`median20_${key}` as const)];
 const rawRows=visible.flatMap(item=>item.buckets.map(row=>({market:item.market,date:item.coverage_start===item.coverage_end?item.as_of??'':`${item.coverage_start} — ${item.coverage_end}`,bucket:row.label,stocks:row.count==null?text('missing'):num(row.count),observations:row.observations==null?text('missing'):num(row.observations),median:row.observations===0?text('noObservations'):money(valueFor(row,'median_usd')),mean:money(valueFor(row,'mean_usd')),p90:money(valueFor(row,'p90_usd'))})));
 const periodLabel=(value:string)=>value==='latest'?text('latest'):value==='common snapshot'?text('common'):value;
 return <>
  <section className={`period-panel ${embedded?'embedded':''}`} id="market-profiles">
   <div className="period-heading"><div><span className="section-kicker">{text('explorer')}</span><h2>{text('profile')}</h2><p>{period==='latest'?text('dates'):text('aligned')}</p></div><span className={`status-badge ${period==='latest'?'mixed':selected?.status==='incomplete'?'incomplete':'verified'}`}>{period==='latest'?(englishLocale()?'Dates differ':'日期不一致'):selected?.status==='incomplete'?text('incomplete'):text('aligned')}</span></div>
   <p className="panel-note">{text('method')}</p>
   <ControlBar><span className="control-label">{text('period')}</span>{['latest',...(summary.periods??[]).map(item=>item.period)].map(value=><Choice key={value} active={period===value} onClick={()=>setPeriod(value)}>{periodLabel(value)}{summary.periods?.find(item=>item.period===value)?.status==='pending'?` · ${text('pending')}`:''}</Choice>)}</ControlBar>
   {selected&&<div className="period-meta"><p>{text('range')}: {selected.common_start??text('missing')} — {selected.common_end??text('missing')} · {text('commonDays')}: {num(selected.common_dates)}</p>{!!selected.missing_markets?.length&&<p>{text('absent')}: {selected.missing_markets.join(', ')}</p>}</div>}
   {selected&&selected.common_dates!==1&&<p className="panel-note">{text('pooled')}</p>}
   <div className="liquidity-filters"><label>{text('grouping')}<select aria-label={text('grouping')} value={grouping} onChange={e=>setGrouping(e.target.value as 'absolute'|'relative')}><option value="absolute">{text('absolute')}</option><option value="relative">{text('relative')}</option></select></label></div>
   {grouping==='relative'&&<><p className="panel-note">{text('relativeNote')}</p><p className="panel-note">{text('capRangeNote')}</p>{relativeResource.error?<ResourceState error={relativeResource.error} retry={relativeResource.retry} label={text('relative')}/>:!relativeResource.data?<p role="status">{text('relativeLoading')}</p>:null}</>}
   {markets.length ? <>
    <div className="liquidity-filters">
     <label>{text('market')}<select aria-label={text('market')} value={market} onChange={e=>setMarket(e.target.value)}><option value="all">{text('all')}</option>{summary.markets.map(item=><option key={item.market}>{item.market}</option>)}</select></label>
     <label>{bucketLabel}<select aria-label={bucketLabel} value={bucket} onChange={e=>setBucket(Number(e.target.value))}>{buckets.map((item,index)=><option key={item.label} value={index}>{item.label}</option>)}</select></label>
     <label>{text('basis')}<select aria-label={text('basis')} value={basis} onChange={e=>setBasis(e.target.value as 'adv20'|'median20')}><option value="adv20">{text('adv20')}</option><option value="median20">{text('median20')}</option></select></label>
     <label>{text('metric')}<select aria-label={text('metric')} value={metric} onChange={e=>setMetric(e.target.value as LiquidityMetric)}>{(['median_usd','mean_usd','p90_usd'] as const).map(value=><option key={value} value={value}>{text(value)}</option>)}</select></label>
     <Choice active={log} onClick={()=>setLog(!log)}>{log?text('log'):text('linear')}</Choice>
    </div>
    <p className="period-meta">{visible.map(item=>`${item.market} ${item.as_of??item.coverage_end??text('missing')}`).join(' · ')}</p>
    <p className="panel-note">{text(grouping==='relative'?'relativeChartNote':'chartNote')}</p>
    {rows.filter(row=>row.observations===0).map(row=><p className="data-notice empty-bucket-notice" key={row.market} role="status">{row.market}: {text('emptyBucket').replace('{stocks}',displayCount(row.totalStocks)).replace('{observations}',displayCount(row.totalObservations))} {grouping==='absolute'&&text('emptyHint')}</p>)}
    {visible.filter(item=>auditLiquidityMarket(item).length).map(item=><p key={item.market} className="data-notice" role="status">{item.market}: {text('quarantined')}. {issueText(item)}</p>)}
    <Panel title={`${text('comparison')} · ${buckets[bucket]?.label??''}`} tag={`${text(basis)} · ${text(metric)} · USD`}>
     {rows.length ? <BarChart rows={rows.map(item=>({market:item.market,value:item.value==null?'':String(item.value)}))} labelKey="market" valueKey="value" formatter={value=>money(value)} logScale={log}/> : <p className="panel-note">{text('noMarket')}</p>}
     <SimpleTable rows={rows.map(item=>({market:item.market,value:item.observations===0?text('noObservations'):money(item.value),stocks:displayCount(item.stocks),totalStocks:displayCount(item.totalStocks),observations:displayCount(item.observations),totalObservations:displayCount(item.totalObservations),capRange:item.capMin==null?text('missing'):`${money(item.capMin)} — ${money(item.capMax)}`}))} columns={[["market",text('market')],["value",text(metric)],["stocks",text('bucketStocks')],["totalStocks",text('universeStocks')],["observations",text('bucketObservations')],["totalObservations",text('universeObservations')],...(grouping==='relative'?[["capRange",text('capRange')]]:[])]}/>
    </Panel>
    <details><summary>{text('raw')}</summary><p className="panel-note">{selected?.common_dates!==1&&selected?text('pooled'):text('stockNote')}</p><SimpleTable rows={rawRows} columns={[["market",text('market')],["date",text('range')],["bucket",bucketLabel],["stocks",text('stocks')],["observations",text('observations')],["median",text('median_usd')],["mean",text('mean_usd')],["p90",text('p90_usd')]]}/></details>
   </>:source&&<p className="data-notice" role="status">{text('noPeriod')}</p>}
  </section>
  <section id="liquidity-quality" className="report-section"><h2>{text('quality')}</h2>
   <SimpleTable rows={markets.map(item=>({market:item.market,date:item.coverage_start===item.coverage_end?item.as_of??text('missing'):`${item.coverage_start} — ${item.coverage_end}`,status:auditLiquidityMarket(item).length?text('quarantined'):text('historical'),issues:issueText(item)||text('consistent'),fx:`${item.fx_start??''} — ${item.fx_end??''}`}))} columns={[["market",text('market')],["date",text('range')],["status",text('status')],["issues",text('issue')],["fx",text('fx')]]}/>
   <p className="panel-note">{text('jp')}</p><p className="panel-note">{text('sourceNote')}</p><p className="panel-note">{liquidityCaveats(summary.caveats,englishLocale()?'en-US':'zh-CN')}</p>
   <details><summary>{text('panelProfile')}</summary><SimpleTable rows={Object.entries(summary.source_profiles??{}).map(([name,p])=>({market:name,source:num(p.source_rows),included:num(p.eligible_observations)}))} columns={[["market",text('market')],["source",text('sourceRows')],["included",text('includedRows')]]}/></details>
   <p><a href={withBase('/data/liquidity/inherited-summary.json',import.meta.env.BASE_URL)}>{text('archive')}</a></p>
   <LiquidityCoveragePanel data={coverageResource.data} error={coverageResource.error} retry={coverageResource.retry} market={market}/>
  </section>
  <OrderBudget rows={rows} period={periodLabel(period)} bucket={buckets[bucket]?.label??''} basis={text(basis)} metric={text(metric)}/>
 </>;
}

function LiquidityCoveragePanel({data,error,retry,market}:{data:LiquidityCoverageSummary|null;error:string|null;retry:()=>void;market:string}) {
 const [quantile,setQuantile]=useState('0.5');
 if(error) return <div className="report-section"><h3>{text('coverageTitle')}</h3><ResourceState error={error} retry={retry} label={text('coverageTitle')}/></div>;
 if(!data) return <div className="report-section"><h3>{text('coverageTitle')}</h3><Loading/></div>;
 const visible=data.markets.filter(row=>market==='all'||row.market===market);
 const concentration=data.intraday_concentration.quantiles[quantile];
 const pct=(value:number)=>`${(value*100).toFixed(1)}%`;
 const dailyBasis:Record<string,string>={US:text('dailyBasisUS'),HK:text('dailyBasisHK'),'A-share':text('dailyBasisA'),JP:text('dailyBasisJP')};
 const rows:Array<{market:string;granularity:string;coverage:string;status:string}> = [];
 for(const row of visible) {
  const minuteCoverage=row.minute.status==='available'?`${row.minute.start} – ${row.minute.end} · ${num(row.minute.sessions)} ${text('sessions')}`:text('notAvailable');
  const minuteStatus=row.minute.status==='available'?`${num(row.minute.rows)} ${text('rows')}; ${num(row.minute.security_days)} ${text('securityDays')}; ${num(row.minute.calendar_gaps)} ${text('calendarGaps')}`:text('notAvailable');
  const level2Coverage=row.level2.status==='sampled'?`${num(row.level2.snapshot_dates)} ${text('selectedDates')} · ${num(row.level2.usable_snapshot_rows)} / ${num(row.level2.snapshot_rows)} ${text('validQuotes')}`:text('notAvailable');
  rows.push({market:row.market,granularity:text('daily'),coverage:`${row.daily.start} – ${row.daily.end} · ${text('latest')}: ${row.daily.latest}`,status:dailyBasis[row.market]??text('missing')});
  rows.push({market:row.market,granularity:text('minute'),coverage:minuteCoverage,status:minuteStatus});
  rows.push({market:row.market,granularity:'Level 2',coverage:level2Coverage,status:row.level2.status==='sampled'?text('level2Sampled'):text('notAvailable')});
 }
 return <div className="report-section" id="capacity-data-coverage">
  <h3>{text('coverageTitle')}</h3><p>{text('coverageIntro')}</p>
  <SimpleTable rows={rows} columns={[["market",text('market')],["granularity",text('granularity')],["coverage",text('coverageRange')],["status",text('coverageStatus')]]}/>
  <p className="panel-note">{text('commonWindows')}: {data.daily_periods.map(row=>`${row.period}: ${row.start} – ${row.end} · ${num(row.common_dates)} ${text('sessions')}${row.markets.length<4?` · ${text('missing')}: ${['US','HK','A-share','JP'].filter(item=>!row.markets.includes(item)).join(', ')}`:''}`).join(' · ')}</p>
  {visible.filter(row=>row.minute.status==='available').map(row=><p className="data-notice" role="note" key={`${row.market}-minute-note`}>{text('minuteCaveat')}</p>)}
  {visible.filter(row=>row.level2.status==='sampled').map(row=><p className="panel-note" key={`${row.market}-level2-note`}>{text('level2Caveat')}</p>)}
  <p className="panel-note">{text('minuteDailyMethod')}</p>
  <SimpleTable rows={[
   {metric:text('matchedSecurityDays'),value:num(data.minute_daily_reconciliation.matched_security_days)},
   {metric:text('dailyOnlySecurityDays'),value:num(data.minute_daily_reconciliation.daily_only_security_days)},
   {metric:text('duplicateMinuteKeys'),value:num(data.minute_daily_reconciliation.minute_duplicate_keys)},
   {metric:text('matchWithin1Cny'),value:pct(data.minute_daily_reconciliation.abs_diff_le_1_cny)},
   {metric:text('matchWithin100Cny'),value:pct(data.minute_daily_reconciliation.abs_diff_le_100_cny)},
   {metric:text('matchWithin01Pct'),value:pct(data.minute_daily_reconciliation.rel_diff_le_0_1pct)},
   {metric:text('mismatchOver1Pct'),value:pct(data.minute_daily_reconciliation.rel_diff_over_1pct)},
   {metric:text('mismatchOver5Pct'),value:pct(data.minute_daily_reconciliation.rel_diff_over_5pct)},
   {metric:text('mismatchOver10Pct'),value:pct(data.minute_daily_reconciliation.rel_diff_over_10pct)},
   {metric:text('dailyTotalRatio'),value:num(data.minute_daily_reconciliation.median_daily_total_ratio)},
   {metric:text('dailyZeroRate'),value:pct(data.minute_daily_reconciliation.daily_zero_turnover_rate)},
  ]} columns={[["metric",text('diagnostic')],["value",text('result')]]}/>
  <p className="panel-note">{text('zeroTurnoverNote')}</p>
  <p>{text('yearlyMismatchTitle')}</p>
  <SimpleTable rows={Object.entries(data.minute_daily_reconciliation.yearly).map(([year,row])=>({year:year==='2022'?`${year}*`:year,matched:num(row.matched_security_days),dailyOnly:num(row.daily_only_security_days),over1:pct(row.relative_diff_over_1pct/row.matched_security_days),over5:pct(row.relative_diff_over_5pct/row.matched_security_days),over10:pct(row.relative_diff_over_10pct/row.matched_security_days)}))} columns={[["year",text('year')],["matched",text('matchedSecurityDays')],["dailyOnly",text('dailyOnlySecurityDays')],["over1",text('mismatchOver1Pct')],["over5",text('mismatchOver5Pct')],["over10",text('mismatchOver10Pct')]]}/>
  <p className="panel-note">{text('yearlyMismatchNote')}</p>
  <p className="data-notice" role="note">{text('tailMismatchNote')}</p>
  <p>{text('concentrationTitle')}</p>
  <ControlBar><span className="control-label">{text('quantile')}</span>{[['0.5','P50'],['0.9','P90'],['0.99','P99']].map(([value,label])=><Choice key={value} active={quantile===value} onClick={()=>setQuantile(value)}>{label}</Choice>)}</ControlBar>
  <BarChart rows={[
   {window:text('top5Min'),share:String(concentration.top_5min_share)},
   {window:text('open30Min'),share:String(concentration.open_30min_share)},
   {window:text('close30Min'),share:String(concentration.close_30min_share)},
  ]} labelKey="window" valueKey="share" formatter={pct}/>
  <p className="panel-note">{text('concentrationNote').replace('{days}',num(data.intraday_concentration.days))}</p>
 </div>;
}

function OrderBudget({rows,period,bucket,basis,metric}:{rows:ReturnType<typeof liquidityComparison>;period:string;bucket:string;basis:string;metric:string}) {
 const [participation,setParticipation]=useState('3');const [days,setDays]=useState('5');const [holdings,setHoldings]=useState('20');
 const p=Number(participation)/100;const d=Number(days);const n=Number(holdings);
 const valid=Number.isFinite(p)&&p>0&&p<=1&&Number.isInteger(d)&&d>0&&Number.isInteger(n)&&n>0&&n<=1000;
 const scenarioRows=rows.map(row=>{
  const enoughStocks=row.stocks==null||n<=row.stocks;
  const benchmark=row.value;
  const singleStockBudget=valid&&enoughStocks&&typeof benchmark==='number'?mechanicalOrderBudget(benchmark,p,d):null;
  const oneWay=singleStockBudget==null?null:singleStockBudget*n;
  return {market:row.market,baseline:row.value==null?text('missing'):money(row.value),holdings:row.stocks==null?text('missing'):`${num(n)} / ${num(row.stocks)}`,budget:oneWay==null?(enoughStocks?text('invalid'):text('holdingsExceedSample')):money(oneWay)};
 });
 return <section id="order-budget" className="report-section"><h2>{text('budget')}</h2><p>{text('budgetNote')}</p><p className="panel-note">{period} · {bucket} · {basis} · {metric}</p><div className="liquidity-filters">
  <label>{text('participation')}<input type="number" min="0.01" max="100" step="0.1" value={participation} onChange={e=>setParticipation(e.target.value)}/></label>
  <label>{text('days')}<input type="number" min="1" max="252" step="1" value={days} onChange={e=>setDays(e.target.value)}/></label>
  <label>{text('holdings')}<input type="number" min="1" max="1000" step="1" value={holdings} onChange={e=>setHoldings(e.target.value)}/></label>
 </div><SimpleTable rows={scenarioRows} columns={[["market",text('market')],["baseline",text('selectedGroupBaseline')],["holdings",text('scenarioHoldings')],["budget",text('scenarioBudget')]]}/></section>;
}
