import {useState} from 'react';
import type {RotationFoundation,FoundationMetric} from '../content/rotation-foundation';
import {foundationComparison,foundationPercent} from '../content/rotation-foundation';
import {foundationCopy as copy} from '../content/rotation-foundation-copy';
import {isEnglish,dateText} from '../content/rotation-extension-display';
const names:Record<string,keyof typeof copy>={'combined':'combined','passive':'passive','selection-only':'selection','timing-only':'timing','theme-overlay':'theme','prelisting':'prelisting','suspension':'suspension','unresolved':'unresolved'};
export default function RotationFoundationExplorer({evidence:a,notesBase}:{evidence:RotationFoundation;notesBase:string}){
 const locale=isEnglish()?'en-US':'zh-CN';
 const t=(key:keyof typeof copy)=>copy[key][isEnglish()?0:1];
 const label=(value:string)=>t(names[value]??'unavailable');
 const number=(value:number)=>new Intl.NumberFormat(locale,{maximumFractionDigits:3}).format(value);
 const percent=(value:number|null)=>foundationPercent(value,locale);
 const [category,setCategory]=useState('all'),[caseId,setCase]=useState('primary'),[pair,setPair]=useState('combined:passive'),[metric,setMetric]=useState<keyof FoundationMetric>('cagr');
 const primary=foundationComparison(a,'primary','combined','passive');
 const [left,right]=pair.split(':');const row=foundationComparison(a,caseId,left,right);
 const categories=a.causes.categories.filter(c=>category==='all'||c.code===category);
 const comparisons=a.comparisons.filter(r=>r.case_id===caseId);
 const metricKeys:[keyof FoundationMetric,keyof typeof copy][]=[['total_return','return'],['cagr','cagr'],['max_drawdown','drawdown'],['volatility','volatility'],['turnover','turnover'],['total_cost','cost'],['mean_risky_exposure','exposure']];
 const chart=row?.metrics?[{name:label(left),value:row.metrics.left[metric]},{name:label(right),value:row.metrics.right[metric]}]:[];
 const lo=Math.min(0,...chart.map(v=>v.value)),hi=Math.max(0,...chart.map(v=>v.value));const span=hi-lo||1;
 const x=(v:number)=>170+500*(v-lo)/span;
 const format=(v:number)=>metric==='turnover'?number(v):percent(v);
 return <section id="rotation-foundation" className="panel foundation-panel">
  <h2>{t('title')}</h2><p className="extension-callout">{t('conclusion')}</p>
  <section><h3>{t('sample')}</h3><p>{t('sampleNote')}</p>{primary?.uncertainty&&primary.uncertainty.interval[0]<=0&&primary.uncertainty.interval[1]>=0&&<p>{t('crossesZero')}</p>}<dl className="foundation-facts">
   <div><dt>{t('candidate')}</dt><dd>{dateText(a.sample.candidate_start)}</dd></div><div><dt>{t('signals')}</dt><dd>{number(a.sample.expected_signals)}</dd></div><div><dt>{t('first')}</dt><dd>{dateText(a.sample.first_signal)}</dd></div><div><dt>{t('last')}</dt><dd>{dateText(a.sample.last_signal)}</dd></div><div><dt>{t('end')}</dt><dd>{dateText(a.sample.retained_end)}</dd></div>
  </dl></section>
  <section id="rotation-foundation-causes"><h3>{t('causes')}</h3><p>{t('causeNote')}</p>
   <label htmlFor="foundation-cause">{t('causeFilter')}</label><select id="foundation-cause" value={category} onChange={e=>setCategory(e.target.value)}><option value="all">{t('all')}</option>{a.causes.categories.map(c=><option key={c.code} value={c.code}>{label(c.code)}</option>)}</select>
   <div className="foundation-facts" aria-live="polite"><div><strong data-testid="foundation-cell-count">{number(categories.reduce((n,c)=>n+c.cells,0))}</strong><span>{t('cells')}</span></div><div><strong>{number(categories.reduce((n,c)=>n+c.decisions,0))}</strong><span>{t('decisions')}</span></div><div><strong>{number(a.causes.distinct_events)}</strong><span>{t('events')}</span></div></div>
   <div className="foundation-bars">{categories.map(c=><div key={c.code}><span>{label(c.code)}</span><meter min={0} max={Math.max(1,a.causes.cells)} value={c.cells} aria-label={label(c.code)}/><strong>{number(c.cells)}</strong></div>)}</div>
   <details><summary>{t('sources')}</summary><div className="table-scroll"><table><thead><tr><th>ETF</th><th>{t('effective')}</th><th>{t('publication')}</th><th>{t('retrieved')}</th></tr></thead><tbody>{a.causes.events.map(e=><tr key={e.symbol+e.effective_from}><td><a href={e.url} rel="noreferrer">{e.symbol}</a><small>{e.publisher}</small></td><td>{dateText(e.effective_from)} – {dateText(e.effective_to)}</td><td>{e.published_at?dateText(e.published_at):t('unavailable')}</td><td>{new Intl.DateTimeFormat(locale,{timeZone:'Asia/Shanghai',dateStyle:'medium',timeStyle:'short'}).format(new Date(e.retrieved_at))}</td></tr>)}</tbody></table></div></details>
  </section>
  <section id="rotation-foundation-comparison"><h3>{t('compare')}</h3><div className="foundation-controls">
   <div><label htmlFor="foundation-case">{t('case')}</label><select id="foundation-case" value={caseId} onChange={e=>setCase(e.target.value)}>{[['primary','primary'],['cost-zero','zero'],['cost-ten','ten'],['delay-two','delay']].map(([v,k])=><option key={v} value={v}>{t(k as keyof typeof copy)}</option>)}</select></div>
   <div><label htmlFor="foundation-pair">{t('pair')}</label><select id="foundation-pair" value={pair} onChange={e=>setPair(e.target.value)}>{comparisons.map(r=><option key={r.left+':'+r.right} value={r.left+':'+r.right}>{label(r.left)} {t('against')} {label(r.right)}</option>)}</select></div>
  </div>
  <div data-testid="foundation-result" data-status={row?.status??'unavailable'} aria-live="polite">
   <p><strong>{row?.status==='available'?t('available'):t('unavailable')}</strong></p>
   {row&&<p>{dateText(row.period.start)} – {dateText(row.period.end)} · {number(row.expected_sessions)} {t('sessions')} · {number(row.weekly_pairs)} {t('weeks')}</p>}
   {row?.metrics?<><label>{t('compare')}<select aria-label={t('cagr')+' / '+t('drawdown')} value={metric} onChange={e=>setMetric(e.target.value as keyof FoundationMetric)}>{metricKeys.map(([key,title])=><option key={key} value={key}>{t(title)}</option>)}</select></label>
    <figure><svg viewBox="0 0 800 150" role="img" aria-label={t(metricKeys.find(([k])=>k===metric)![1])} className="foundation-metric-chart"><line x1={x(0)} x2={x(0)} y1="12" y2="122" stroke="currentColor" opacity=".5"/>{chart.map((v,i)=><g key={v.name}><text x="8" y={37+i*60} fill="currentColor" fontSize="13">{v.name.length>24?v.name.slice(0,21)+'…':v.name}</text><rect x={Math.min(x(0),x(v.value))} y={15+i*60} width={Math.max(1,Math.abs(x(v.value)-x(0)))} height="32" fill={i?'#7e70ad':'#168574'}><title>{v.name}: {format(v.value)}</title></rect><text x="690" y={37+i*60} fill="currentColor" fontSize="15">{format(v.value)}</text></g>)}</svg></figure>
    <div className="table-scroll"><table><thead><tr><th>{t('compare')}</th><th>{label(left)}</th><th>{label(right)}</th></tr></thead><tbody>{metricKeys.map(([key,title])=><tr key={key}><th>{t(title)}</th><td>{key==='turnover'?number(row.metrics!.left[key]):percent(row.metrics!.left[key])}</td><td>{key==='turnover'?number(row.metrics!.right[key]):percent(row.metrics!.right[key])}</td></tr>)}</tbody></table></div>
    {row.uncertainty&&<><h4>{t('uncertainty')}</h4><p>{percent(row.uncertainty.estimate)} · {t('interval')}: [{percent(row.uncertainty.interval[0])}, {percent(row.uncertainty.interval[1])}]</p><p>{t('intervalNote')}</p><div className="table-scroll"><table><tbody>{[{expected_block_weeks:13,interval:row.uncertainty.interval},...row.uncertainty.sensitivity].map(v=><tr key={v.expected_block_weeks}><th>{number(v.expected_block_weeks)} {t('weeks')}</th><td>[{percent(v.interval[0])}, {percent(v.interval[1])}]</td></tr>)}</tbody></table></div></>}
   </>:<p>{t('unavailableNote')}</p>}
  </div>
  <details><summary>{t('methods')}</summary><p>{t('passiveNote')}</p><p>{t('methodNote')}</p><p>{t('annualization')}</p><p>{t('sampleNote')}</p></details>
  </section>
  <section id="rotation-foundation-progress"><h3>{t('progress')}</h3><ol><li>{a.readiness.status==='ready_for_future_registration'?t('ready'):t('pending')}</li><li>{a.readiness.capture_state==='armed'?t('armed'):t('unarmed')}</li><li>{t('settled')}: {number(a.readiness.settled_pairs)}</li></ol>
   <p>{t('asOf')}: {new Intl.DateTimeFormat(locale,{timeZone:'Asia/Shanghai',dateStyle:'medium',timeStyle:'short'}).format(new Date(a.readiness.observed_at))} · {t('sourceSession')}: {a.readiness.source_session?dateText(a.readiness.source_session):t('unavailable')}</p>
   <p>{t('next')}</p><p>{t('themeNote')}</p><p>{t('policy')}</p><p>{t('prospectiveDifference')}</p><strong>{a.decision==='descriptive_only'?t('descriptive'):t('notEstablished')}</strong>
  </section>
  <p><a href={`${notesBase}rotation-foundation-review${locale==='zh-CN'?'.zh-CN':''}.md`}>{t('reviewNotes')}</a></p>
  <details><summary>{t('hashes')}</summary><p>{a.release_id}</p><code>{a.registration_sha256}</code><p><code>{a.reviewed_source_digest}</code></p></details>
 </section>;
}
