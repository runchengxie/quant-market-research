import {commoditySelection} from '../lib/commodity-view';
import {commodityCopy as c} from '../content/commodity-copy';
import {readChartTheme} from '../theme';
export function mountCommodityExplorer(){
 const root=document.querySelector<HTMLElement>('[data-commodity-explorer]');
 if(!root||root.dataset.mounted)return;root.dataset.mounted='true';
 const cases=JSON.parse(root.querySelector('[data-commodity-payload]')!.textContent!);
 const selects=[...root.querySelectorAll<HTMLSelectElement>('select')];
 let chart:import('echarts').ECharts|undefined;
 const locale=()=>document.documentElement.lang==='zh-CN'?1:0;
 const text=(key:keyof typeof c)=>c[key][locale()];
 const pct=(v:number)=>new Intl.NumberFormat(locale()?'zh-CN':'en-US',{style:'percent',maximumFractionDigits:2}).format(v);
 const paint=()=>{
  const state=Object.fromEntries(selects.map(s=>[s.dataset.commodityControl!,s.value])) as {policy:string;weight:string;horizon:string};
  const selected=commoditySelection<any>(cases,state);
  const values:Record<string,string>={count:String(selected.completed_windows),returnBetter:pct(selected.improves_return.fraction),drawdownBetter:pct(selected.improves_drawdown.fraction),both:pct(selected.improves_both.fraction),median:pct(selected.portfolio_cagr.median),worst:pct(selected.portfolio_cagr.minimum),worstDrawdown:pct(selected.portfolio_max_drawdown.minimum)};
  for(const [id,value]of Object.entries(values))root.querySelector(`[data-commodity-metric="${id}"]`)!.textContent=value;
  const row=selected.worst_return_difference_windows?.[0];
  root.querySelector('[data-commodity-failure]')!.textContent=row?`${row.start} — ${row.end} · ${text('commodity_20')} ${pct(row.portfolio_cagr)} / ${text('equity')} ${pct(row.equity_cagr)}`:text('none');
  root.querySelector('[data-commodity-status]')!.textContent=`${text('count')} ${selected.completed_windows} · ${Number(state.horizon)/12} ${locale()?'年':'years'} · ${state.weight}% · ${text(state.policy as 'monthly'|'annual')}`;
  root.dataset.selection=JSON.stringify(state);root.dataset.reviewedValues=JSON.stringify(values);
  const names=['returnBetter','drawdownBetter','both'] as const;
  const canvas=root.querySelector<HTMLElement>('[data-commodity-chart]')!;
  canvas.setAttribute('aria-label',names.map(id=>`${text(id)} ${values[id]}`).join(' · '));
  if(chart){const theme=readChartTheme();chart.setOption({animation:!matchMedia('(prefers-reduced-motion: reduce)').matches,grid:{left:8,right:35,top:20,bottom:35,containLabel:true},tooltip:{trigger:'axis',confine:true,valueFormatter:(v:unknown)=>`${Number(v).toFixed(2)}%`},xAxis:{type:'value',min:0,max:100,axisLabel:{color:theme.label,formatter:'{value}%'},splitLine:{lineStyle:{color:theme.grid}}},yAxis:{type:'category',inverse:true,data:names.map(text),axisLabel:{color:theme.label,width:150,overflow:'truncate'}},series:[{type:'bar',barMaxWidth:28,itemStyle:{color:'#3677bd'},data:[selected.improves_return.fraction*100,selected.improves_drawdown.fraction*100,selected.improves_both.fraction*100]}]},true);root.dataset.chartReady='true';}
 };
 try{const saved=JSON.parse(sessionStorage.getItem('commodity-selection')??'{}');for(const s of selects)if([...s.options].some(o=>o.value===saved[s.dataset.commodityControl!]))s.value=saved[s.dataset.commodityControl!];}catch{/* Optional storage. */}
 selects.forEach(s=>s.addEventListener('change',()=>{paint();try{sessionStorage.setItem('commodity-selection',root.dataset.selection!);}catch{/* Optional storage. */}}));
 new MutationObserver(paint).observe(document.documentElement,{attributes:true,attributeFilter:['lang','data-theme']});
 const observer=new IntersectionObserver(async entries=>{if(!entries.some(e=>e.isIntersecting))return;observer.disconnect();try{const {echarts}=await import('./echarts');chart=echarts.init(root.querySelector<HTMLElement>('[data-commodity-chart]')!);paint();new ResizeObserver(()=>chart?.resize()).observe(root);}catch{root.querySelector('[data-commodity-status]')!.textContent=text('fallback');}},{rootMargin:'150px'});observer.observe(root);paint();
}
