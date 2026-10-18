import {operationsCopy,operationCodes} from './rotation-operations-copy';
import {isEnglish} from './rotation-extension-display';
import type {MatchedRow} from './rotation-operations';
export const opText=(key:keyof typeof operationsCopy)=>operationsCopy[key][isEnglish()?0:1];
export const opCode=(key:string)=>operationCodes[key]?.[isEnglish()?0:1]??opText('unavailable');
export const opNumber=(n:number)=>new Intl.NumberFormat(isEnglish()?'en-US':'zh-CN',{maximumFractionDigits:3}).format(n);
export const opPercent=(n:number|null)=>n===null?'—':new Intl.NumberFormat(isEnglish()?'en-US':'zh-CN',{style:'percent',maximumFractionDigits:2}).format(n);
export const opDate=(v:string|null,instant=false)=>v===null?'—':new Intl.DateTimeFormat(isEnglish()?'en-US':'zh-CN',{timeZone:instant?'Asia/Shanghai':'UTC',year:'numeric',month:'short',day:'numeric',...(instant?{hour:'2-digit',minute:'2-digit'} as const:{})}).format(new Date(v.length===10?v+'T00:00:00Z':v));
export function opWindow(id:string){if(id==='common')return opText('common');if(id==='last_252')return opText('last252');if(id==='last_756')return opText('last756');if(id.startsWith('year_'))return `${opText('calendarYear')} ${id.slice(5)}`;const match=/^rolling_(252|756)_(.+)$/.exec(id);return match?`${opText('rolling')} · ${match[1]} · ${opDate(match[2])}`:opText('unavailable');}
export type MatchedSelection={baseline:string;comparison:string;eligibility:string;case:string;window:string};
export function matchedSelection(params:URLSearchParams,windows:string[]):MatchedSelection{
 const allowed={baseline:['fixed-base','pool-core'],comparison:['budget','estimated-risk'],eligibility:['retained_snapshot','historical_prefix'],case:['primary','cost-zero','cost-ten','delay-two'],window:windows};
 const defaults={baseline:'fixed-base',comparison:'budget',eligibility:'retained_snapshot',case:'primary',window:'common'};
 return Object.fromEntries(Object.entries(allowed).map(([key,values])=>{const selected=params.get('ops'+key[0].toUpperCase()+key.slice(1));return [key,selected&&values.includes(selected)?selected:defaults[key as keyof typeof defaults]];})) as MatchedSelection;
}
export function selectionParams(params:URLSearchParams,selected:MatchedSelection){const result=new URLSearchParams(params);Object.entries(selected).forEach(([key,value])=>result.set('ops'+key[0].toUpperCase()+key.slice(1),value));return result;}
export function matchedRow(rows:MatchedRow[],s:MatchedSelection){return rows.find(r=>r.baseline===s.baseline&&r.comparison===s.comparison&&r.eligibility_case===s.eligibility&&r.case_id===s.case&&r.window_id===s.window);}
export function matchedCsv(row:MatchedRow){
 const columns=['id','status','baseline','comparison','eligibility_case','case_id','window_id','start','end','reference_cagr','comparator_cagr','reasons'];
 const values=[row.id,row.status,row.baseline,row.comparison,row.eligibility_case,row.case_id,row.window_id,row.period?.start??'',row.period?.end??'',row.metrics?.reference.cagr??'',row.metrics?.comparator.cagr??'',row.reasons.join('|')];
 const quote=(value:unknown)=>'"'+String(value).replaceAll('"','""')+'"';return columns.join(',')+'\n'+values.map(quote).join(',')+'\n';
}
