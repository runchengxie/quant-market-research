import {assetChartView,type AssetChartData,type ChartState} from '../lib/asset-interactive';
import {assetChartCopy as c} from '../content/asset-chart-copy';
import {assetNames} from '../content/asset-return-copy';
import {portfolioNames,ruleNames,comparisonNames} from '../content/asset-robustness-copy';
import {masks} from '../content/asset-decision-copy';
import {readChartTheme} from '../theme';
import {baseChartOptions} from '../lib/chart-presentation';
const names:Record<string,readonly [string,string]>={...c,...assetNames,...portfolioNames,...ruleNames,...comparisonNames,...masks,gold:['Gold','黄金']};
const colors=['#3677bd','#2f8c7d','#b4833d'];
const escape=(s:string)=>s.replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]!));

export function mountAssetCharts(){
 document.querySelectorAll<HTMLElement>('[data-asset-chart]').forEach(root=>{
  if(root.dataset.assetMounted)return;root.dataset.assetMounted='true';
  const kind=root.dataset.assetChart!;
  const data=JSON.parse(root.querySelector('.asset-chart-data')!.textContent!) as AssetChartData;
  let chart:import('echarts').ECharts|undefined;
  const locale=()=>document.documentElement.lang==='zh-CN'?1:0;
  const t=(key:string)=>names[key]?.[locale()]??key;
  const state=():ChartState=>{
   const selected=Object.fromEntries(Array.from(root.querySelectorAll<HTMLSelectElement>('select')).map(s=>[s.dataset.assetControl!,s.value]));
   if(kind==='spending'){selected.demand=(document.getElementById('decision-demand') as HTMLSelectElement).value;selected.shock=(document.getElementById('decision-shock') as HTMLSelectElement).value;}
   if(kind==='allocation')selected.cost=(document.getElementById('allocation-cost') as HTMLSelectElement).value;
   return selected;
  };
  try{
   const saved=JSON.parse(sessionStorage.getItem(`asset-chart-${kind}`)??'{}');
   root.querySelectorAll<HTMLSelectElement>('select').forEach(s=>{if([...s.options].some(o=>o.value===saved[s.dataset.assetControl!]))s.value=saved[s.dataset.assetControl!];});
  }catch{/* Controls work without browser storage. */}
  const number=(value:number|null,unit:string)=>value===null?t('missing'):new Intl.NumberFormat(locale()?'zh-CN':'en-US',{maximumFractionDigits:2,minimumFractionDigits:unit==='months'?0:2}).format(value*(unit==='percent'||unit==='pp'?100:1))+(unit==='percent'?'%':unit==='pp'?(locale()?'个百分点':' pp'):'');
  const paint=()=>{
   const selected=state();const view=assetChartView(kind,data,selected);
   const sample=view.sample_windows?`${t('windows')} ${view.sample_windows}`:view.sample_months?`${t('sample')} ${view.sample_months}`:view.start?`${t('start')} ${view.start}`:view.draws?`${view.draws}${locale()?'次抽样':' draws'}`:'';
   let summary=sample;
   if(view.start&&view.sample_months)summary+=` · ${t('start')} ${view.start}`;
   if(view.type==='interval')summary+=' · '+view.intervals.map((r:any)=>`${r.id}${t('months')} ${number(r.lower,view.unit)}${locale()?'至':' to '}${number(r.upper,view.unit)} · ${t('median')} ${number(r.median,view.unit)}`).join(' · ');
   else if(view.type==='scatter')summary+=' · '+view.points.map((r:any)=>`${t(r.portfolio)} ${t(r.policy)} ${number(r.y,'percent')}`).join(' · ');
   else summary+=' · '+view.series.map((s:any)=>`${t(s.id)} ${view.categories.map((label:string,i:number)=>`${t(label)} ${number(s.values[i],view.unit)}`).join(' / ')}`).join(' · ');
   root.querySelectorAll<HTMLTableRowElement>('.asset-selected-table tbody tr').forEach(row=>{row.hidden=kind==='endpoints'?(row.dataset.assetRow!==selected.asset||row.dataset.startRow!==selected.start):(row.dataset.productRow!==selected.product||row.dataset.costRow!==selected.cost);});
   const output=root.querySelector<HTMLElement>('[data-asset-chart-summary]')!;let shown=view.type==='interval'?summary:[sample,view.start&&view.sample_months?`${t('start')} ${view.start}`:'',selected.metric?t(selected.metric):'',t(view.unit)].filter(Boolean).join(' · ');
   if(kind==='uncertainty'&&selected.metric==='annual_minus_hold_drawdown')shown+=` ${t('drawdownMeaning')}`;
   if(kind==='spending'&&selected.metric==='shortfall_fraction'&&view.series.filter((s:any)=>s.values.every((v:number)=>v===0)).length>1)shown+=` ${t('overlappingZero')}`;
   output.textContent=shown;
   const canvas=root.querySelector<HTMLElement>('.asset-chart-canvas')!;canvas.setAttribute('aria-label',`${t(kind)}${locale()?'。':'. '}${summary}`);
   root.dataset.chartSelection=JSON.stringify(selected);root.dataset.chartValues=JSON.stringify(view);
   if(!chart)return;
   const theme=readChartTheme();const base=baseChartOptions(theme,matchMedia('(prefers-reduced-motion: reduce)').matches);
   const scale=view.unit==='percent'||view.unit==='pp'?100:1;
   const axisFormatter=(value:number)=>new Intl.NumberFormat(locale()?'zh-CN':'en-US',{maximumFractionDigits:1}).format(value)+(view.unit==='percent'?'%':'');
   const mobile=root.clientWidth<450;
   const option:any={...base,aria:{enabled:true,description:summary},grid:{left:8,right:58,top:50,bottom:42,containLabel:true},legend:{type:'scroll',top:0,textStyle:{color:theme.label}},tooltip:{...base.tooltip,textStyle:{color:'#f3f4f5',fontSize:12},trigger:'axis',confine:true,valueFormatter:(value:any)=>value===null?t('missing'):number(Number(value)/scale,view.unit)},xAxis:{type:'value',name:t(view.unit),nameLocation:'middle',nameGap:26,splitNumber:mobile?3:5,axisLabel:{color:theme.label,formatter:axisFormatter,hideOverlap:true,fontSize:11},splitLine:{lineStyle:{color:theme.grid}}},yAxis:{type:'category',inverse:true,data:view.categories?.map((id:string)=>t(id)),axisLabel:{color:theme.label,width:100,overflow:'truncate',fontSize:11},axisLine:{lineStyle:{color:theme.axis}}}};
   if(view.type==='interval'){
    option.grid.right=20;
    option.legend.show=false;option.tooltip={...option.tooltip,trigger:'item',formatter:(p:any)=>{
     const row=view.intervals[p.seriesIndex%view.intervals.length];
     return `${escape(row.id+t('months'))}<br/>${escape(t('range'))} ${escape(number(row.lower,view.unit))} ${escape(number(row.upper,view.unit))}<br/>${escape(t('median'))} ${escape(number(row.median,view.unit))}`;
    }};
    option.yAxis.data=view.intervals.map((r:any)=>r.id+t('months'));
    option.series=view.intervals.map((r:any,i:number)=>({name:r.id+t('months'),type:'line',symbol:'circle',symbolSize:7,data:[[r.lower*scale,r.id+t('months')],[r.upper*scale,r.id+t('months')]],lineStyle:{width:4,color:colors[0]},itemStyle:{color:colors[0]},markLine:i===0?{silent:true,symbol:'none',label:{show:false},lineStyle:{type:'dashed',color:theme.label},data:[{xAxis:0}]}:undefined}));
    option.series.push({type:'scatter',symbol:'diamond',symbolSize:10,itemStyle:{color:colors[1]},data:view.intervals.map((r:any)=>[r.median*scale,r.id+t('months')]),tooltip:{formatter:(p:any)=>{const row=view.intervals[p.dataIndex];return `${escape(row.id+t('months'))}<br/>${escape(t('median'))} ${escape(number(row.median,view.unit))}`;}}});
   }else if(view.type==='scatter'){
    option.grid.right=20;
    option.xAxis.name=t('risk');option.yAxis={type:'value',name:t('returnAxis'),nameTextStyle:{align:'left'},axisLabel:{color:theme.label,formatter:(value:number)=>`${value}%`},splitLine:{lineStyle:{color:theme.grid}}};
    option.tooltip={...option.tooltip,trigger:'item',formatter:(p:any)=>`${escape(t(p.data.portfolio))}<br/>${escape(t(p.data.policy))}<br/>${escape(t('risk'))} ${escape(number(p.data.value[0]/100,'percent'))}<br/>${escape(t('annualReturn'))} ${escape(number(p.data.value[1]/100,'percent'))}`};
    option.series=Object.keys(portfolioNames).map((id,i)=>({name:t(id),type:'scatter',symbolSize:14,itemStyle:{color:colors[i]},data:view.points.filter((r:any)=>r.portfolio===id).map((r:any)=>({...r,value:[r.x*100,r.y*100],symbol:r.policy==='annual'?'diamond':r.policy==='threshold_5pp'?'triangle':'circle'}))}));
   }else if(view.type==='line'){
    option.xAxis={type:'category',data:view.categories.map((id:string)=>kind==='endpoints'?id.slice(0,4):id),name:kind==='spending'?t('months'):'',nameLocation:'middle',nameGap:26,axisLabel:{color:theme.label}};
    option.yAxis={type:'value',name:t(view.unit),nameTextStyle:{align:'left'},axisLabel:{color:theme.label,formatter:axisFormatter},splitLine:{lineStyle:{color:theme.grid}}};
    if(kind==='endpoints')option.tooltip.formatter=(params:any)=>{const p=params[0],index=p.dataIndex;return `${escape(view.categories[index])}<br/>${escape(t('years'))} ${view.months[index]/12}<br/>${escape(number(p.value/scale,view.unit))}`;};
    option.series=view.series.map((s:any,i:number)=>({name:t(s.id),type:'line',connectNulls:false,symbol:['circle','diamond','triangle'][i],symbolSize:[9,11,8][i],data:s.values.map((v:number|null)=>v===null?null:v*scale),lineStyle:{color:colors[i]},itemStyle:{color:colors[i]}}));
   }else{
    option.series=view.series.map((s:any,i:number)=>({name:t(s.id),type:'bar',barMaxWidth:24,data:s.values.map((v:number|null)=>v===null?null:v*scale),itemStyle:{color:kind==='stress'?'#b86155':colors[i]},label:{show:true,position:'right',color:theme.label,fontSize:11,formatter:(p:any)=>number(p.value/scale,view.unit)}}));
    if(kind==='launch')option.tooltip.formatter=(params:any)=>{const id=view.categories[params[0].dataIndex];return [escape(t(id)),...params.map((p:any)=>`${escape(p.seriesName)} ${escape(number(p.value/scale,view.unit))} · ${view.samples[id][p.seriesIndex===0&&selected.include_pre==='yes'?'pre':'post']} ${escape(t('months'))}`)].join('<br/>');};
   }
   chart.setOption(option,true);root.dataset.chartReady='true';
   const table=document.querySelector<HTMLDetailsElement>(`details[data-asset-table="${kind}"]`);
   if(table&&!table.dataset.chartFolded){table.open=false;table.dataset.chartFolded='true';}
  };
  root.querySelectorAll('select').forEach(s=>s.addEventListener('change',()=>{try{sessionStorage.setItem(`asset-chart-${kind}`,JSON.stringify(state()));}catch{/* Optional storage. */}paint();}));
  if(kind==='spending')for(const id of ['decision-demand','decision-shock'])document.getElementById(id)?.addEventListener('change',paint);
  if(kind==='allocation')document.getElementById('allocation-cost')?.addEventListener('change',paint);
  const themeObserver=new MutationObserver(paint);themeObserver.observe(document.documentElement,{attributes:true,attributeFilter:['lang','data-theme']});
  const observer=new IntersectionObserver(async entries=>{
   if(!entries.some(e=>e.isIntersecting))return;observer.disconnect();
   try{
    const [{echarts},{ScatterChart},{AriaComponent}]=await Promise.all([import('./echarts'),import('echarts/charts'),import('echarts/components')]);
    echarts.use([ScatterChart,AriaComponent]);chart=echarts.init(root.querySelector<HTMLElement>('.asset-chart-canvas')!);paint();
    const resize=new ResizeObserver(()=>chart?.resize());resize.observe(root);
   }catch{root.querySelector<HTMLElement>('[data-asset-chart-summary]')!.textContent=t('fallback');}
  },{rootMargin:'150px'});observer.observe(root);paint();
 });
}
