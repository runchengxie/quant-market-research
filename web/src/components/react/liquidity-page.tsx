import { useState } from 'react';
import { liquidityCaveats } from '../../liquidity-copy';
import { liquidityResearchCopy as copy } from '../../content/liquidity-research-copy';
import { formatNumber as num } from '../../lib/format';
import { auditLiquidityMarket, liquidityComparison, marketsForPeriod, mechanicalOrderBudget, type LiquidityMetric } from '../../lib/liquidity-quality';
import { Panel, BarChart, ControlBar, Choice, SimpleTable, Loading, ResourceState, useJson, englishLocale } from './research-shared';
import type { LiquiditySummary } from './research-shared';

const text = (key: keyof typeof copy) => copy[key][englishLocale() ? 0 : 1];
const money = (value: number | null | undefined) => value == null ? text('missing') : `$${num(value)}`;
export function LiquidityPage({ embedded = false }: { embedded?: boolean }) {
 return <LiquidityPeriodPanel embedded={embedded}/>;
}

export function LiquidityPeriodPanel({ embedded = false }: { embedded?: boolean }) {
 const { data: summary, error, retry } = useJson<LiquiditySummary>('liquidity/summary.json');
 const [period,setPeriod]=useState('latest');
 const [market,setMarket]=useState('all');
 const [bucket,setBucket]=useState(0);
 const [metric,setMetric]=useState<LiquidityMetric>('median_usd');
 const [log,setLog]=useState(true);
 if(error) return <ResourceState error={error} retry={retry} label={text('explorer')}/>;
 if(!summary) return <Loading/>;
 const markets=marketsForPeriod(summary,period);
 const visible=markets.filter(item=>market==='all'||item.market===market);
 const rows=liquidityComparison(markets,bucket,metric).filter(item=>market==='all'||item.market===market);
 const buckets=summary.markets[0]?.buckets??[];
 const issueText=(item: typeof summary.markets[number])=>auditLiquidityMarket(item).map(issue=>`${text(issue.code)}: ${num(issue.reported)} / ${num(issue.grouped)}`).join('; ');
 const rawRows=visible.flatMap(item=>item.buckets.map(row=>({market:item.market,date:item.as_of??item.coverage_end??text('missing'),bucket:row.label,stocks:row.count==null?text('missing'):num(row.count),observations:row.observations==null?text('missing'):num(row.observations),median:money(row.median_usd),mean:money(row.mean_usd),p90:money(row.p90_usd)})));
 return <>
  <section className={`period-panel ${embedded?'embedded':''}`} id="market-profiles">
   <div className="period-heading"><div><span className="section-kicker">{text('explorer')}</span><h2>{text('profile')}</h2><p>{text('dates')}</p></div><span className="status-badge mixed">{englishLocale()?'Dates differ':'日期不一致'}</span></div>
   <p className="panel-note">{text('method')}</p>
   <ControlBar><span className="control-label">{text('period')}</span>{['latest',...(summary.periods??[]).map(item=>item.period)].map(value=><Choice key={value} active={period===value} onClick={()=>setPeriod(value)}>{value==='latest'?text('latest'):value}{summary.periods?.find(item=>item.period===value)?.status==='pending'?` · ${text('pending')}`:''}</Choice>)}</ControlBar>
   {markets.length ? <>
    <div className="liquidity-filters">
     <label>{text('market')}<select aria-label={text('market')} value={market} onChange={e=>setMarket(e.target.value)}><option value="all">{text('all')}</option>{summary.markets.map(item=><option key={item.market}>{item.market}</option>)}</select></label>
     <label>{text('bucket')}<select aria-label={text('bucket')} value={bucket} onChange={e=>setBucket(Number(e.target.value))}>{buckets.map((item,index)=><option key={item.label} value={index}>{item.label}</option>)}</select></label>
     <label>{text('metric')}<select aria-label={text('metric')} value={metric} onChange={e=>setMetric(e.target.value as LiquidityMetric)}>{(['median_usd','mean_usd','p90_usd'] as const).map(value=><option key={value} value={value}>{text(value)}</option>)}</select></label>
     <Choice active={log} onClick={()=>setLog(!log)}>{log?text('log'):text('linear')}</Choice>
    </div>
    <p className="period-meta">{visible.map(item=>`${item.market} ${item.as_of??item.coverage_end??text('missing')}`).join(' · ')}</p>
    <p className="panel-note">{text('chartNote')}</p>
    {visible.filter(item=>auditLiquidityMarket(item).length).map(item=><p key={item.market} className="data-notice" role="status">{item.market}: {text('quarantined')}. {issueText(item)}</p>)}
    <Panel title={`${text('comparison')} · ${buckets[bucket]?.label??''}`} tag={`${text(metric)} · USD`}>
     {rows.length ? <BarChart rows={rows.map(item=>({market:item.market,value:item.value==null?'':String(item.value)}))} labelKey="market" valueKey="value" formatter={value=>money(value)} logScale={log}/> : <p className="panel-note">{text('quarantined')}</p>}
     <SimpleTable rows={rows.map(item=>({market:item.market,value:money(item.value)}))} columns={[["market",text('market')],["value",text(metric)]]}/>
    </Panel>
    <details><summary>{text('raw')}</summary><p className="panel-note">{text('stockNote')}</p><SimpleTable rows={rawRows} columns={[["market",text('market')],["date",text('date')],["bucket",text('bucket')],["stocks",text('stocks')],["observations",text('observations')],["median",text('median_usd')],["mean",text('mean_usd')],["p90",text('p90_usd')]]}/></details>
   </>:<p className="data-notice" role="status">{text('noPeriod')}</p>}
  </section>
  <section id="liquidity-quality" className="report-section"><h2>{text('quality')}</h2>
   <SimpleTable rows={summary.markets.map(item=>({market:item.market,date:item.as_of??text('missing'),status:auditLiquidityMarket(item).length?text('quarantined'):text('historical'),issues:issueText(item)||text('consistent'),p90:item.buckets.every(row=>row.p90_usd!=null)?text('p90_usd'):text('noP90')}))} columns={[["market",text('market')],["date",text('date')],["status",text('status')],["issues",text('issue')],["p90",text('p90_usd')]]}/>
   <p className="panel-note">{text('jp')}</p><p className="panel-note">{liquidityCaveats(summary.caveats,englishLocale()?'en-US':'zh-CN')}</p>
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
