import {useState} from 'react';
import {liquidityExitCopy as copy} from '../../content/liquidity-exit-copy';
import {formatNumber as num} from '../../lib/format';
import {withBase} from '../../lib/routes';
import {BarChart,Panel,SimpleTable,Loading,ResourceState,useJson,englishLocale} from './research-shared';
const text=(key:keyof typeof copy)=>copy[key][englishLocale()?0:1];
const pct=(v:number|null|undefined)=>v==null?text('missing'):`${num(v*100)}%`;
type Row={year:number;bucket:number;position_usd:number;participation:number;horizon:number;mode:string;formations:number;stocks:number;covered:number;not_covered:number;unresolved:number;static_covered:number;covered_day_p50:number|null;covered_day_p95:number|null;all_names_day_max:number|null;uncredited_fraction:number;top_decile_uncredited_share:number|null};
type Evidence={buckets:string[];rows:Row[]};
type Minute={dates:number;accepted_stock_days:number;boundary_difference:{open_absolute_p95:number};statistics:Record<string,{observations:number;median:number}>};
type Revision={baseline:{rows:number;end:string}};
export function LiquidityExitPanel(){
 const resource=useJson<Evidence>('liquidity/exit-exploration.json');
 const minute=useJson<Minute>('liquidity/minute-clock-probe.json');
 const revision=useJson<Revision>('liquidity/revision-baseline.json');
 const [year,setYear]=useState('2025');const [bucket,setBucket]=useState('2');const [position,setPosition]=useState('1000000');const [participation,setParticipation]=useState('0.03');const [horizon,setHorizon]=useState('5');const [mode,setMode]=useState('guarded');
 if(resource.error)return <ResourceState error={resource.error} retry={resource.retry} label={text('title')}/>;
 if(!resource.data)return <Loading/>;
 const data=resource.data;
 const choices=data.rows.filter(r=>r.year===Number(year)&&r.bucket===Number(bucket)&&r.position_usd===Number(position)&&r.participation===Number(participation)&&r.horizon===Number(horizon));
 const row=choices.find(r=>r.mode===mode);const raw=choices.find(r=>r.mode==='raw');const guarded=choices.find(r=>r.mode==='guarded');
 const count=(n:number)=>`${num(n)} · ${pct(row?n/row.stocks:null)}`;
 const windows={open_a:'09:30 ≤ t < 10:00',open_b:'09:30 < t ≤ 10:00',close_a:'14:30 ≤ t ≤ 15:00',close_b:'14:30 < t ≤ 15:00'};
 return <section id="liquidity-exit" className="report-section"><h2>{text('title')}</h2><p>{text('intro')}</p>
 <Panel title={text('chart')} tag={`${year} · ${data.buckets[Number(bucket)]}`}>
 <div className="liquidity-filters">
 <label>{text('year')}<select value={year} onChange={e=>setYear(e.target.value)}>{[2024,2025].map(v=><option key={v}>{v}</option>)}</select></label>
 <label>{text('bucket')}<select value={bucket} onChange={e=>setBucket(e.target.value)}>{data.buckets.map((v,i)=><option value={i} key={v}>{v}</option>)}</select></label>
 <label>{text('position')}<select value={position} onChange={e=>setPosition(e.target.value)}>{[100000,1000000].map(v=><option value={v} key={v}>{num(v)}</option>)}</select></label>
 <label>{text('participation')}<select value={participation} onChange={e=>setParticipation(e.target.value)}>{[.01,.03,.05].map(v=><option value={v} key={v}>{pct(v)}</option>)}</select></label>
 <label>{text('horizon')}<select value={horizon} onChange={e=>setHorizon(e.target.value)}>{[1,5,20].map(v=><option key={v}>{v}</option>)}</select></label>
 <label>{text('mode')}<select value={mode} onChange={e=>setMode(e.target.value)}>{(['guarded','raw'] as const).map(v=><option value={v} key={v}>{text(v)}</option>)}</select></label>
 </div><p>{text('rules')}</p><p className="panel-note">{text('scope')}</p>
 {row&&raw&&guarded?<>
 {(row.stocks<100||row.formations<6)&&<p className="data-notice">{text('sparse')}</p>}
 <BarChart rows={[{label:text('static'),value:String(row.static_covered/row.stocks)},{label:text('raw'),value:String(raw.covered/raw.stocks)},{label:text('guarded'),value:String(guarded.covered/guarded.stocks)}]} labelKey="label" valueKey="value" formatter={pct}/>
 <SimpleTable rows={[
 {metric:text('formations'),value:num(row.formations)},{metric:text('stocks'),value:num(row.stocks)},
 {metric:text('covered'),value:count(row.covered)},{metric:text('notCovered'),value:count(row.not_covered)},{metric:text('unresolved'),value:count(row.unresolved)},
 {metric:text('p50'),value:row.covered_day_p50==null?text('missing'):num(row.covered_day_p50)},
 {metric:text('p95'),value:row.covered_day_p95==null?text('missing'):num(row.covered_day_p95)},
 {metric:text('maximum'),value:row.all_names_day_max==null?text('censored'):num(row.all_names_day_max)},
 {metric:text('residual'),value:pct(row.uncredited_fraction)},{metric:text('tail'),value:pct(row.top_decile_uncredited_share)}
 ]} columns={[["metric",text('metric')],["value",text('value')]]}/>
 </>:<p role="status">{text('empty')}</p>}
 <p className="data-notice">{text('caveat')}</p></Panel>
 <details><summary>{text('audits')}</summary><p>{text('independent')}</p><h3>{text('minute')}</h3><p>{text('minuteNote')}</p>
 {minute.error?<ResourceState error={minute.error} retry={minute.retry} label={text('minute')}/>:minute.data?<><p>{text('dates')}: {num(minute.data.dates)} · {text('observations')}: {num(minute.data.accepted_stock_days)}</p><p>{text('boundaryP95')}: {num(minute.data.boundary_difference.open_absolute_p95*100)}</p><SimpleTable rows={Object.entries(windows).map(([key,label])=>({window:label,median:pct(minute.data?.statistics[key]?.median)}))} columns={[["window",text('window')],["median",text('median')]]}/></>:<Loading/>}
 <p className="data-notice">{text('semantics')}</p><h3>{text('revision')}</h3><p>{text('revisionNote')}</p>
 {revision.error?<ResourceState error={revision.error} retry={revision.retry} label={text('revision')}/>:revision.data?<p>{text('baselineRows')}: {num(revision.data.baseline.rows)} · {text('baselineEnd')}: {revision.data.baseline.end}</p>:<Loading/>}
 <p className="report-links">{([['minute-clock-probe.json','minuteDownload'],['revision-baseline.json','revisionDownload']] as const).map(([file,label])=><a key={file} download href={withBase(`/data/liquidity/${file}`,import.meta.env.BASE_URL)}>{text(label)}</a>)}</p>
 </details>
 <p className="report-links">{([['exit-exploration.json','download'],['exit-review.json','receipt']] as const).map(([file,label])=><a key={file} download href={withBase(`/data/liquidity/${file}`,import.meta.env.BASE_URL)}>{text(label)}</a>)}</p>
 </section>;
}
