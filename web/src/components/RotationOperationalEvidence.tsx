import {useEffect,useState} from 'react';
import type {RotationOperations} from '../content/rotation-operations';
import {opText as t,opCode,opDate,opNumber} from '../content/rotation-operations-display';
export default function RotationOperationalEvidence({evidence:a}:{evidence:Pick<RotationOperations,'health'|'audit'>}){
 const h=a.health,u=a.audit;
 const years=[...new Set(u.monthly.map(m=>m.month.slice(0,4)))];
 const readYear=()=>{const requested=new URLSearchParams(location.search).get('opsAuditYear');return requested&&years.includes(requested)?requested:'all';};
 const [year,setYear]=useState(readYear);
 useEffect(()=>{const restore=()=>setYear(readYear());addEventListener('popstate',restore);return()=>removeEventListener('popstate',restore);},[]);
 const months=u.monthly.filter(m=>year==='all'||m.month.startsWith(year));
 const max=Math.max(1,...months.map(m=>m.changed_records));
 const label=(id:string)=>t(id==='pool-core'?'defensive':'fixed');
 function selectYear(value:string){setYear(value);const url=new URL(location.href);url.searchParams.set('opsAuditYear',value);history.pushState({},'',url);}
 return <section id="rotation-operations" className="panel rotation-operations">
  <h2>{t('title')}</h2><p className="extension-callout">{t('conclusion')}</p><p>{t('intro')}</p>
  <p className="panel-note">{t('asOf')}: <time dateTime={h.observed_at}>{opDate(h.observed_at,true)}</time> · {h.timezone}</p><p className="panel-note">{t('freshness')}</p>
  <section aria-labelledby="operations-readiness"><h3 id="operations-readiness">{t('health')}</h3>
   <ol className="operations-timeline">
    <li data-ready={h.preparation_status==='prepared'||h.preparation_status==='already_prepared'}><strong>{t('preparation')}</strong><span>{opCode(h.preparation_status)}</span></li>
    <li data-ready={h.state!=='awaiting_registration'}><strong>{t('registration')}</strong><span>{opCode(h.state)}</span></li>
    <li data-ready={h.captured_weeks>0}><strong>{t('capture')}</strong><span>{t(h.capture_state)}</span></li>
    <li data-ready={h.settled_weeks>0}><strong>{t('settlement')}</strong><span>{opNumber(h.settled_weeks)}</span></li>
   </ol>
   <div className="rotation-facts"><div><strong>{opNumber(h.captured_weeks)}</strong>{t('captured')}</div><div><strong>{opNumber(h.settled_weeks)}</strong>{t('settled')}</div><div><strong>{opNumber(h.pending_settlement)}</strong>{t('pending')}</div><div><strong>{opNumber(h.missing_weeks)}</strong>{t('missing')}</div></div>
   <dl className="operations-details"><div><dt>{t('sourceSession')}</dt><dd>{opDate(h.source_session)}</dd></div><div><dt>{t('received')}</dt><dd>{opDate(h.source_observed_by,true)}</dd></div><div><dt>{t('reviewed')}</dt><dd>{opDate(h.reviewed_at,true)}</dd></div><div><dt>{t('cutoff')}</dt><dd>{h.cutoff_local} · {h.timezone}</dd></div><div><dt>{t('prepareTimer')}</dt><dd>{t(h.preparation_timer)}</dd></div><div><dt>{t('forwardTimer')}</dt><dd>{t(h.forward_timer)}</dd></div><div><dt>{t('calendar')}</dt><dd>{opDate(h.calendar_valid_through)}</dd></div></dl>
   <p>{t('readinessNote')}</p>{h.reasons.length>0&&<ul>{h.reasons.map(reason=><li key={reason}>{opCode(reason)}</li>)}</ul>}
  </section>
  <section id="rotation-prefix-audit"><h3>{t('audit')}</h3><p>{t('auditNote')}</p><p>{opDate(u.panel_start)} – {opDate(u.panel_end)} · {opNumber(u.sessions)} {t('sessions')}</p>
   <div className="rotation-facts"><div><strong>{opNumber(u.symbols)}</strong>{t('symbols')}</div><div><strong>{opNumber(u.symbol_week_records)}</strong>{t('records')}</div><div><strong>{opNumber(u.changed_records)}</strong>{t('changes')}</div><div><strong>{opNumber(u.affected_weeks)}</strong>{t('affected')}</div></div>
   <div className="operations-panel-bars">{u.panels.map(panel=><div key={panel.id}><span>{t(panel.id==='core'?'core':panel.id==='pool'?'pool':'industry')}</span><div className="operations-bar-track"><i style={{width:`${100*panel.changed_records/Math.max(1,...u.panels.map(p=>p.changed_records))}%`}}/></div><strong>{opNumber(panel.changed_records)}</strong><small>{opNumber(panel.affected_weeks)} {t('affectedWeeks')}</small></div>)}</div>
   <p className="panel-note">{t('panelNote')}</p>
   <label className="operations-year">{t('year')}<select aria-label={t('year')} value={year} onChange={e=>selectYear(e.target.value)}><option value="all">{t('allYears')}</option>{years.map(value=><option key={value}>{value}</option>)}</select></label>
   <figure><svg viewBox="0 0 900 190" role="img" aria-label={t('monthChart')} style={{width:'100%',height:'auto',display:'block'}}><line x1="0" x2="900" y1="164" y2="164" stroke="currentColor" opacity=".2"/>{months.map((month,index)=>{const width=900/Math.max(months.length,1);const height=150*month.changed_records/max;return <g key={month.month}><rect x={index*width+1} y={164-height} width={Math.max(1,width-2)} height={height} fill="var(--accent, #168574)"><title>{month.month}: {opNumber(month.changed_records)}</title></rect>{(index===0||index===months.length-1||months.length<=12)&&<text x={index*width+width/2} y="184" textAnchor="middle" fontSize={months.length<=12?13:11} fill="currentColor">{month.month}</text>}</g>;})}</svg><figcaption>{t('monthChart')} · {opNumber(months.reduce((sum,m)=>sum+m.changed_records,0))}</figcaption></figure>
   <details><summary>{t('dimensions')}</summary><p>{t('dimensionNote')}</p><div className="table-scroll"><table><thead><tr><th>{t('dimension')}</th><th>{t('admitted')}</th><th>{t('unknown')}</th><th>{t('rejected')}</th></tr></thead><tbody>{u.dimensions.map(d=><tr key={d.rule}><td>{opCode(d.rule)}</td><td>{opNumber(d.admitted)}</td><td>{opNumber(d.unknown)}</td><td>{opNumber(d.rejected)}</td></tr>)}</tbody></table></div></details>
   <h4>{t('gaps')}</h4><div className="table-scroll"><table><thead><tr><th>{t('baseline')}</th><th>{t('missing')}</th><th>{t('span')}</th><th>{t('reason')}</th></tr></thead><tbody>{u.baseline_gaps.map(g=><tr key={g.baseline}><td>{label(g.baseline)}</td><td>{opNumber(g.unavailable_weeks)}</td><td>{opDate(g.first_week)} – {opDate(g.last_week)}</td><td><ul>{g.reasons.map(r=><li key={r.code}>{opCode(r.code)}: {opNumber(r.count)}</li>)}</ul></td></tr>)}</tbody></table></div>
   <p className="panel-note">{t('overlap')}</p>
   <details><summary>{t('rules')}</summary><p>{t('ruleNote')}</p><code>SHA-256: {u.audit_sha256}</code></details>
  </section>
 </section>;
}
