import { lowTurnoverCopy as c, lowTurnoverControls as controls, lowTurnoverEvidence as evidence } from '../content/low-turnover-copy';
import { readerToolsCopy as r } from '../content/reader-tools-copy';
export async function createResearchImage(locale: 'en-US'|'zh-CN'): Promise<Blob> {
  const n=locale==='zh-CN'?1:0;
  const family='"Noto Sans SC Variable", sans-serif';
  const paragraphs=[c.kicker[n],c.title[n],c.conclusion[n],c.introduction[n],c.controlsList[n],c.lead[n],r.imageScope[n],r.chartNote[n],r.imageHistory[n],r.imageTrading[n],c.chart[n],r.limits[n],...controls.map(row=>row.label[n])];
  // Load every subset used by the exported text, including material not yet visible on screen.
  await document.fonts.load(`400 30px ${family}`, paragraphs.join(''));
  await document.fonts.load(`700 48px ${family}`, paragraphs.join(''));
  await document.fonts.ready;
  const canvas=document.createElement('canvas');
  canvas.width=1080; canvas.height=6500;
  const ctx=canvas.getContext('2d');
  if (!ctx) throw new Error('Canvas unavailable');
  ctx.fillStyle='#f8f5ef';ctx.fillRect(0,0,1080,6500);
  let y=72;
  const text=(value:string,size=30,color='#34312d',bold=false)=>{
    ctx.font=`${bold?700:400} ${size}px ${family}`;ctx.fillStyle=color;ctx.textBaseline='top';
    // Word boundaries for English, individual graphemes for Chinese, with a long-token fallback.
    const tokens=locale==='zh-CN'?Array.from(value):value.match(/\S+\s*|\s+/g)??[];
    let line='';
    const flush=()=>{ctx.fillText(line.trimEnd(),64,y);y+=size*1.55;line='';};
    for (const token of tokens) {
      if(ctx.measureText(line+token).width>952&&line) flush();
      if(ctx.measureText(token).width>952) {
        for(const ch of Array.from(token)){if(ctx.measureText(line+ch).width>952&&line)flush();line+=ch;}
      } else line+=token;
    }
    if(line)flush();y+=22;
  };
  text(c.kicker[n],23,'#a74730');
  text(c.title[n],48,'#252525',true);
  text(c.conclusion[n],36,'#a74730',true);
  text(c.lead[n]);text(c.introduction[n],26,'#625b52');text(r.imageScope[n],26,'#625b52');
  text(c.chart[n],32,'#252525',true);
  for(const row of controls){
    text(row.label[n],29,'#34312d',true);
    const x=(v:number)=>64+v/2.2*680;
    const chartY=y+18;
    ctx.strokeStyle='#ddd5c9';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(64,chartY);ctx.lineTo(744,chartY);ctx.stroke();
    ctx.strokeStyle='#a74730';ctx.lineWidth=7;ctx.beginPath();ctx.moveTo(x(row.ciLow),chartY);ctx.lineTo(x(row.ciHigh),chartY);ctx.stroke();
    ctx.fillStyle='#a74730';ctx.beginPath();ctx.arc(x(row.spread),chartY,9,0,Math.PI*2);ctx.fill();
    ctx.font=`700 30px ${family}`;ctx.fillStyle='#34312d';ctx.fillText(`+${row.spread.toFixed(2)}`,790,y);
    y+=58;text(`${c.range[n]} ${row.ciLow.toFixed(2)}${c.between[n]}${row.ciHigh.toFixed(2)}`,25,'#625b52');
  }
  text(r.chartNote[n],26,'#625b52');text(c.controlsList[n],25,'#625b52');text(r.limits[n],32,'#252525',true);
  text(r.imageHistory[n],27);text(r.imageTrading[n],27);
  text(`${r.date[n]} ${evidence.evidenceDate} · ${r.reviewDate[n]} ${evidence.reviewedAt}`,23,'#625b52');
  if(y>6400)throw new Error('Image exceeds safe canvas height');
  const output=document.createElement('canvas');output.width=1080;output.height=Math.ceil(y+35);
  const out=output.getContext('2d');if(!out)throw new Error('Canvas unavailable');out.drawImage(canvas,0,0);
  return new Promise((resolve,reject)=>output.toBlob(blob=>blob?resolve(blob):reject(new Error('PNG encoding failed')),'image/png'));
}
