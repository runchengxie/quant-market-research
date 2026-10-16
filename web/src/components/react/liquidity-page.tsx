import { useState } from 'react';
import { liquidityCaveats } from '../../liquidity-copy';
import { liquidityResearchCopy as copy } from '../../content/liquidity-research-copy';
import { formatNumber as num } from '../../lib/format';
import { withBase } from '../../lib/routes';
import { auditLiquidityMarket, liquidityComparison, marketsForPeriod, mechanicalOrderBudget, type LiquidityMetric } from '../../lib/liquidity-quality';
import { Panel, BarChart, ControlBar, Choice, SimpleTable, Loading, ResourceState, useJson, englishLocale } from './research-shared';
import type { LiquiditySummary, LiquidityRelativeSummary } from './research-shared';

const text = (key: keyof typeof copy) => copy[key][englishLocale() ? 0 : 1];
const money = (value: number | null | undefined) => value == null ? text('missing') : `$${num(value)}`;
export function LiquidityPage({ embedded = false }: { embedded?: boolean }) {
 return <LiquidityPeriodPanel embedded={embedded}/>;
}

export function LiquidityPeriodPanel({ embedded = false }: { embedded?: boolean }) {
 const { data: summary, error, retry } = useJson<LiquiditySummary>('liquidity/summary.json');
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
  </section>
  <OrderBudget/>
 </>;
}

function OrderBudget() {
 const [turnover,setTurnover]=useState('100000');const [participation,setParticipation]=useState('5');const [days,setDays]=useState('5');
 let budget:number|null=null;
 try {if(turnover.trim()&&participation.trim()&&days.trim()) budget=mechanicalOrderBudget(Number(turnover),Number(participation)/100,Number(days));} catch { /* Display invalid input without producing a budget. */ }
 return <section id="order-budget" className="report-section"><h2>{text('budget')}</h2><p>{text('budgetNote')}</p><div className="liquidity-filters">
  <label>{text('turnover')}<input type="number" min="0" value={turnover} onChange={e=>setTurnover(e.target.value)}/></label>
  <label>{text('participation')}<input type="number" min="0.01" max="100" step="0.1" value={participation} onChange={e=>setParticipation(e.target.value)}/></label>
  <label>{text('days')}<input type="number" min="1" step="1" value={days} onChange={e=>setDays(e.target.value)}/></label>
 </div><p aria-live="polite"><strong>{text('result')}: <output>{budget==null?text('invalid'):money(budget)}</output></strong></p></section>;
}
