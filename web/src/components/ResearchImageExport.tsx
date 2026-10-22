import {useEffect,useState} from 'react';
import {createResearchImage} from '../lib/research-image';
import {readerToolsCopy as c} from '../content/reader-tools-copy';
import {lowTurnoverEvidence} from '../content/low-turnover-copy';
import {createSummaryImage} from '../lib/summary-image';
import type {ReadingSummary} from '../content/research-reading';
export default function ResearchImageExport({summary}:{summary?:ReadingSummary}={}){
  const [locale,setLocale]=useState<'en-US'|'zh-CN'>('en-US');
  const [busy,setBusy]=useState(false),[error,setError]=useState(false),[url,setUrl]=useState('');
  useEffect(()=>{setLocale(document.documentElement.lang==='zh-CN'?'zh-CN':'en-US');},[]);
  useEffect(()=>()=>{if(url)URL.revokeObjectURL(url);},[url]);
  const n=locale==='zh-CN'?1:0;
  async function download(){
    setBusy(true);setError(false);
    try{
      const blob=await (summary?createSummaryImage(summary,locale):createResearchImage(locale));const next=URL.createObjectURL(blob);setUrl(next);
      const link=document.createElement('a');link.href=next;link.download=`${summary?.id??'low-turnover'}-${summary?(summary.date??'undated'):lowTurnoverEvidence.evidenceDate}.${locale}.png`;document.body.append(link);link.click();link.remove();
    }catch{setError(true);}finally{setBusy(false);}
  }
  return <div className="research-image-export"><button type="button" className="button-link secondary" data-testid="download-research-image" disabled={busy} onClick={download}>{(busy?c.preparing:c.download)[n]}</button><p className="panel-note">{c.note[n]}</p><p role="status">{error?c.error[n]:busy?c.preparing[n]:''}</p>{url&&<details open><summary>{c.preview[n]}</summary><img data-testid="research-image-preview" src={url} alt={c.preview[n]} style={{display:'block',width:'100%',maxWidth:540,height:'auto',marginTop:16}} /></details>}</div>;
}
