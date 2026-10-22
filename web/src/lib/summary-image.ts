import { readingCopy as c, type ReadingSummary } from '../content/research-reading';
export async function createSummaryImage(summary: ReadingSummary, locale: 'en-US'|'zh-CN'): Promise<Blob> {
  const n=locale==='zh-CN'?1:0;
  const blocks:[string,number,boolean][]=[['Quant Market Research',24,false],[summary.title[n],46,true],[c[summary.stage][n],26,false],[summary.conclusion[n],32,true],[c.coverage[n],26,true],[summary.coverage[n],28,false],[c.scope[n],26,true],[summary.scope[n],28,false],[c.limit[n],26,true],[summary.limit[n],28,false],[c.date[n],24,true],[summary.date??c.missing[n],24,false]];
  const family='"Noto Sans SC Variable", sans-serif';
  await document.fonts.load(`400 28px ${family}`,blocks.map(b=>b[0]).join(''));
  await document.fonts.load(`700 46px ${family}`,blocks.map(b=>b[0]).join(''));
  await document.fonts.ready;
  const canvas=document.createElement('canvas');canvas.width=1080;canvas.height=6500;
  const ctx=canvas.getContext('2d');if(!ctx)throw Error('Canvas unavailable');
  ctx.fillStyle='#f8f5ef';ctx.fillRect(0,0,1080,6500);ctx.textBaseline='top';let y=64;
  for(const [value,size,bold] of blocks){
    ctx.font=`${bold?700:400} ${size}px ${family}`;ctx.fillStyle=bold?'#252525':'#514b43';
    let line='';const flush=()=>{ctx.fillText(line.trimEnd(),64,y);y+=size*1.6;line='';};
    for(const token of (locale==='zh-CN'?Array.from(value):value.match(/\S+\s*|\s+/g)??[])){
      if(ctx.measureText(line+token).width>952&&line)flush();
      if(ctx.measureText(token).width>952){for(const ch of Array.from(token)){if(ctx.measureText(line+ch).width>952&&line)flush();line+=ch;}}
      else line+=token;
    }
    if(line)flush();y+=24;
  }
  if(y>6400)throw Error('Summary exceeds safe image height');
  const output=document.createElement('canvas');output.width=1080;output.height=Math.ceil(y+40);
  const out=output.getContext('2d');if(!out)throw Error('Canvas unavailable');out.drawImage(canvas,0,0);
  return new Promise((resolve,reject)=>output.toBlob(blob=>blob?resolve(blob):reject(Error('PNG encoding failed')),'image/png'));
}
