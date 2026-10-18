import { useState } from 'react';
import { withBase } from '../../lib/routes';
import { liquidityResearchCopy as copy } from '../../content/liquidity-research-copy';
import { formatNumber as num } from '../../lib/format';
import { englishLocale, Loading, ResourceState, SimpleTable, useJson, type LiquidityPeriodMarket } from './research-shared';

const text = (key: keyof typeof copy) => copy[key][englishLocale() ? 0 : 1];
type View = {period:string;common_start:string;common_end:string;common_dates:number;base:LiquidityPeriodMarket;lifecycle:LiquidityPeriodMarket};
type Evidence = {periods:View[];scope_changes:Array<{period:string;previous_including_bse:LiquidityPeriodMarket;sh_sz:LiquidityPeriodMarket}>};

export function LiquidityUniversePanel() {
 const {data,error,retry}=useJson<Evidence>('liquidity/universe-sensitivity.json');
 const [period,setPeriod]=useState('2020-2024');const [bucket,setBucket]=useState(1);
 if(error) return <ResourceState error={error} retry={retry} label={text('universeTitle')}/>;
 if(!data) return <Loading/>;
 const selected=data.periods.find(row=>row.period===period)??data.periods[0];
 if(!selected) return null;
 const scope=data.scope_changes.find(row=>row.period===selected.period);
 const variants=[{label:text('oldScope'),item:scope?.previous_including_bse},{label:text('shszScope'),item:selected.base},{label:text('lifecycleScope'),item:selected.lifecycle}];
 const base=selected.base.buckets[bucket];
 const rows=variants.flatMap(({label,item})=>{
  if(!item) return [];
  const b=item.buckets[bucket];
  const delta=b.median_usd==null||base.median_usd==null||base.median_usd===0?null:(b.median_usd/base.median_usd-1)*100;
  return [{scope:label,stocks:num(b.count),observations:num(b.observations),median:b.median_usd==null?text('noObservations'):`$${num(b.median_usd)}`,delta:delta==null?text('missing'):`${num(delta)}%`}];
 });
 return <section className="report-section" id="liquidity-universe-sensitivity"><h3>{text('universeTitle')}</h3><p>{text('universeIntro')}</p>
  <div className="liquidity-filters"><label>{text('period')}<select aria-label={text('universePeriod')} value={selected.period} onChange={e=>setPeriod(e.target.value)}>{data.periods.map(row=><option key={row.period} value={row.period}>{row.period==='latest'?text('latest'):row.period==='common snapshot'?text('common'):row.period}</option>)}</select></label><label>{text('bucket')}<select aria-label={text('universeBucket')} value={bucket} onChange={e=>setBucket(Number(e.target.value))}>{selected.base.buckets.map((b,index)=><option key={b.label} value={index}>{b.label}</option>)}</select></label></div>
  <p className="panel-note">{selected.common_start} — {selected.common_end} · {num(selected.common_dates)} {text('commonDays')}</p>
  <SimpleTable rows={rows} columns={[["scope",text('scopeVariant')],["stocks",text('stocks')],["observations",text('observations')],["median",text('median_usd')],["delta",text('changeFromShsz')]]}/>
  <p className="data-notice" role="note">{text('universeCaveat')}</p><p className="report-links"><a download href={withBase('/data/liquidity/universe-sensitivity.json',import.meta.env.BASE_URL)}>{text('universeDownload')}</a><a download href={withBase('/data/liquidity/universe-review.json',import.meta.env.BASE_URL)}>{text('receipt')}</a></p>
 </section>;
}
