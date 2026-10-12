import { expansionCopy as c } from '../content/execution-expansion-copy';
import { surfaceChartRows, strategyChartRows } from '../lib/execution-chart';
import { formatEvidenceNumber as n, formatEvidenceFraction as pct, formatEvidenceNav as nav } from '../lib/execution-expansion';
import { readChartTheme } from '../theme';
import { baseChartOptions } from '../lib/chart-presentation';
export function mountExecutionCharts() {
 document.querySelectorAll<HTMLElement>('[data-execution-chart]').forEach(root => {
  const kind=root.dataset.executionChart!;
  const data=JSON.parse(root.querySelector('.chart-data')!.textContent!);
  let chart: import('echarts').ECharts | undefined;
  const stateKey=`execution-chart-${kind}`;
  try {
   const stored=JSON.parse(sessionStorage.getItem(stateKey)??'{}');
   root.querySelectorAll<HTMLSelectElement>('select').forEach(select=>{
    const saved=stored[select.dataset.chartControl!];
    if(Array.from(select.options).some(option=>option.value===saved))select.value=saved;
   });
  } catch { /* Tables and controls remain usable when browser storage is unavailable. */ }

  const locale=()=>document.documentElement.lang==='zh-CN'?1:0;
  const text=(key:string)=>(c[key as keyof typeof c]??[key,key])[locale()];
  const label=(key:string)=>/^\d{8}$/.test(key)?`${key.slice(0,4)}-${key.slice(4,6)}-${key.slice(6)}`:text(key);
  const control=(key:string)=>root.querySelector<HTMLSelectElement>(`[data-chart-control="${key}"]`)?.value;
  const values=()=>kind==='strategy'?strategyChartRows(data,Number(control('capital'))):surfaceChartRows(kind==='daily'?data:data[control('group')!],control('side')!,Number(control('notional')));
  const updateTable=(rows:any[])=>{
   const body=root.querySelector('tbody')!; body.replaceChildren();
   rows.forEach(r=>{
    const tr=document.createElement('tr');
    const cells=kind==='strategy'?[text(r.scenario),nav(r.terminal_nav),n(r.transaction_cost_cny)]:[label(r.key),n(r.p50),n(r.p90),pct(r.coverage),n(r.books),n(r.filled)];
    cells.forEach(value=>{const td=document.createElement('td');td.textContent=value;tr.append(td)});body.append(tr);
   });
  };
  const paint=()=>{
   const rows=values(); updateTable(rows);
   root.querySelectorAll<HTMLSelectElement>('select').forEach(select=>{const span=select.previousElementSibling;select.setAttribute('aria-label',span?.textContent??'')});
   if(!chart)return;
   const theme=readChartTheme(); const coverage=control('metric')==='coverage';
   const strategy=kind==='strategy';
   root.querySelector<HTMLElement>('.chart-key')!.hidden=strategy||coverage;
   const series=strategy?[{name:text('nav'),data:rows.map(r=>r.terminal_nav)}]:coverage?[{name:text('chartCoverageValue'),data:rows.map(r=>r.coverage===null?null:r.coverage*100)}]:[{name:text('chartP50'),data:rows.map(r=>r.p50)},{name:text('chartP90'),data:rows.map(r=>r.p90)}];
   chart.setOption({...baseChartOptions(theme,matchMedia('(prefers-reduced-motion: reduce)').matches),grid:{left:8,right:12,top:28,bottom:28,containLabel:true},tooltip:{...baseChartOptions(theme,true).tooltip,trigger:'axis',confine:true,valueFormatter:(v:any)=>v==null?'—':strategy?nav(v):`${n(v)}${coverage?'%':` ${text('chartUnit')}`}`},xAxis:{type:'value',name:strategy?text('nav'):coverage?'%':text('chartUnit'),nameLocation:'middle',nameGap:22,scale:false,axisLabel:{color:theme.label},splitLine:{lineStyle:{color:theme.grid}}},yAxis:{type:'category',data:rows.map(r=>strategy?text(r.scenario):label(r.key)),axisLabel:{color:theme.label,width:strategy?100:85,overflow:'truncate',fontSize:11},axisLine:{lineStyle:{color:theme.axis}}},series:series.map((s,i)=>({...s,type:'bar',barMaxWidth:16,itemStyle:{color:i===0?'#3677bd':'#ba7953'}}))},true);
   root.dataset.chartReady='true';
  };
  root.querySelectorAll('select').forEach(select=>select.addEventListener('change',()=>{
   try {sessionStorage.setItem(stateKey,JSON.stringify(Object.fromEntries(Array.from(root.querySelectorAll<HTMLSelectElement>('select')).map(s=>[s.dataset.chartControl,s.value]))));} catch { /* Storage is optional. */ }
   paint();
  }));
  const observer=new MutationObserver(paint);observer.observe(document.documentElement,{attributes:true,attributeFilter:['lang','data-theme']});
  const intersection=new IntersectionObserver(async entries=>{
   if(!entries.some(e=>e.isIntersecting))return;intersection.disconnect();
   const {echarts}=await import('./echarts');chart=echarts.init(root.querySelector<HTMLElement>('.chart-canvas')!);paint();
   const resize=new ResizeObserver(()=>chart?.resize());resize.observe(root);
  },{rootMargin:'200px'});intersection.observe(root);
  paint();
 });
}
