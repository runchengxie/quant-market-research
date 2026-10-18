import {useEffect,useState} from 'react';
import type {MatchedRow} from '../content/rotation-operations';
import {validateOperationsShape} from '../content/rotation-operations';
import {loadIndexedRelease,type ReleaseEntry} from '../content/rotation-extension';
import {opText as t,opCode,opNumber,opPercent,opDate,opWindow,matchedSelection,matchedRow,selectionParams,matchedCsv,type MatchedSelection} from '../content/rotation-operations-display';
type Overview={row_count:number;available_rows:number;window_ids:string[];rows:MatchedRow[]};
export default function RotationMatchedExplorer({overview,releaseEntry,dataBase}:{overview:Overview;releaseEntry:ReleaseEntry;dataBase:string}){
 const read=()=>matchedSelection(new URLSearchParams(location.search),overview.window_ids);
 const [selected,setSelected]=useState(read),[rows,setRows]=useState(overview.rows),[loaded,setLoaded]=useState(false),[status,setStatus]=useState<'idle'|'loading'|'error'>('idle');
 const row=matchedRow(rows,selected);
 async function load(){setStatus('loading');try{const asset=validateOperationsShape(await loadIndexedRelease(releaseEntry,new URL(dataBase,location.href).href));setRows(asset.comparisons.rows);setLoaded(true);setStatus('idle');}catch{setStatus('error');}}
 useEffect(()=>{const restore=()=>setSelected(read());addEventListener('popstate',restore);return()=>removeEventListener('popstate',restore);},[]);
 useEffect(()=>{if(!row&&!loaded&&status==='idle')void load();},[selected]);
 function change(key:keyof MatchedSelection,value:string){const next={...selected,[key]:value};setSelected(next);const url=new URL(location.href);url.search=selectionParams(url.searchParams,next).toString();history.pushState({},'',url);}
 function download(){if(!row)return;const url=URL.createObjectURL(new Blob([matchedCsv(row)],{type:'text/csv;charset=utf-8'}));const link=document.createElement('a');link.href=url;link.download=`${row.id}.csv`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 const caseOptions=[['primary','primary'],['cost-zero','zero'],['cost-ten','ten'],['delay-two','delay']] as const;
 const metrics=['total_return','cagr','max_drawdown','volatility','target_risky_weight','realized_risky_weight','turnover','cost_drag'] as const;
 return <section id="rotation-matched" className="panel rotation-operations"><h2>{t('matched')}</h2><p>{t('matchedNote')}</p><p className="panel-note">{t('interpretation')}</p>
  <div className="rotation-facts"><div><strong>{opNumber(overview.row_count)}</strong>{t('rowCount')}</div><div><strong>{opNumber(overview.available_rows)}</strong>{t('availableCount')}</div></div>
  <div className="extension-controls operations-controls">
   <label>{t('baseline')}<select aria-label={t('baseline')} value={selected.baseline} onChange={e=>change('baseline',e.target.value)}><option value="fixed-base">{t('fixed')}</option><option value="pool-core">{t('defensive')}</option></select></label>
   <label>{t('comparison')}<select aria-label={t('comparison')} value={selected.comparison} onChange={e=>change('comparison',e.target.value)}><option value="budget">{t('budget')}</option><option value="estimated-risk">{t('risk')}</option></select></label>
   <label>{t('eligibility')}<select aria-label={t('eligibility')} value={selected.eligibility} onChange={e=>change('eligibility',e.target.value)}><option value="retained_snapshot">{t('snapshot')}</option><option value="historical_prefix">{t('prefix')}</option></select></label>
   <label>{t('case')}<select aria-label={t('case')} value={selected.case} onChange={e=>change('case',e.target.value)}>{caseOptions.map(([value,key])=><option key={value} value={value}>{t(key)}</option>)}</select></label>
   <label>{t('window')}<select aria-label={t('window')} value={selected.window} onChange={e=>change('window',e.target.value)}>{overview.window_ids.map(id=><option key={id} value={id}>{opWindow(id)}</option>)}</select></label>
  </div>
  {!loaded&&<button type="button" onClick={()=>void load()} disabled={status==='loading'}>{status==='loading'?t('loading'):status==='error'?t('retry'):t('load')}</button>}
  {status==='error'&&<p role="alert">{t('loadError')}</p>}<p aria-live="polite">{status==='loading'?t('loading'):''}</p>
  {row?<div data-testid="matched-result" data-status={row.status}>
   {row.status==='unavailable'?<><h3>{t('unavailable')}</h3><ul>{row.reasons.map(reason=><li key={reason}>{opCode(reason)}</li>)}</ul></>:<>
    <p>{t('period')}: {opDate(row.period!.start)} – {opDate(row.period!.end)} · {opNumber(row.period!.sessions)} {t('sessions')}</p>
    <div className="table-scroll"><table><thead><tr><th>{t('metric')}</th><th>{t('reference')}</th><th>{t('comparator')}</th></tr></thead><tbody>{metrics.map(key=><tr key={key}><td>{t(key)}</td><td>{key==='turnover'?opNumber(row.metrics!.reference[key]):opPercent(row.metrics!.reference[key])}</td><td>{key==='turnover'?opNumber(row.metrics!.comparator[key]):opPercent(row.metrics!.comparator[key])}</td></tr>)}</tbody></table></div>
    <figure><svg viewBox="0 0 600 130" role="img" aria-label={t('realized_risky_weight')} style={{width:'100%',maxWidth:600}}>{(['reference','comparator'] as const).map((arm,i)=><g key={arm}><text x="0" y={i*55+20} fill="currentColor" fontSize="13">{t(arm)}</text><rect x="0" y={i*55+29} width={600*row.metrics![arm].realized_risky_weight} height="14" fill={i?'#b58a43':'#168574'}/></g>)}</svg><figcaption>{t('realized_risky_weight')}</figcaption></figure>
   </>}
   <dl className="operations-details"><div><dt>{t('targetError')}</dt><dd>{row.target_budget_error===null?'—':opNumber(row.target_budget_error)}</dd></div><div><dt>{t('exposureGap')}</dt><dd>{opPercent(row.realized_exposure_gap)}</dd></div><div><dt>{t('riskMissing')}</dt><dd>{opNumber(row.unavailable_count)}</dd></div><div><dt>{t('inactive')}</dt><dd>{opNumber(row.inactive_count)}</dd></div><div><dt>{t('breaches')}</dt><dd>{opNumber(row.ceiling_breaches)}</dd></div></dl>
   <button type="button" onClick={download}>{t('download')}</button>
  </div>:<p>{loaded?t('noRow'):t('loadNeeded')}</p>}
 </section>;
}
