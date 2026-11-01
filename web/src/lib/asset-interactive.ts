/** Exact chart selections over already reviewed public summaries. No statistical recomputation. */
type RecordData=Record<string,any>;
export type AssetChartData={returns:RecordData;robustness:RecordData;decision:RecordData};
export type ChartState=Record<string,string>;
export function assetChartView(kind:string,data:AssetChartData,state:ChartState={}):RecordData{
 const {returns:r,robustness:b,decision:d}=data;
 if(kind==='returns')return {type:'bar',unit:'percent',categories:r.equities.map((x:any)=>x.id),series:['price','total'].map(id=>({id,values:r.equities.map((x:any)=>x[id+'_cagr'])})),sample_months:252};
 if(kind==='holding')return {type:'bar',unit:'percent',categories:r.equities.map((x:any)=>x.id),series:[{id:state.metric==='real'?'real':'nominal',values:r.equities.map((x:any)=>x.horizons.find((h:any)=>h.months===120)[state.metric==='real'?'real_loss_fraction':'nominal_loss_fraction'])}],sample_windows:r.equities[0].horizons.find((h:any)=>h.months===120).completed_windows};
 if(kind==='endpoints'){
  const cells=b.sensitivity[state.asset??'all_share'].grid.cells;
  const start=state.start??cells[0].start;
  const rows=cells.filter((x:any)=>x.start===start).sort((a:any,b:any)=>a.end.localeCompare(b.end));
  return {type:'line',unit:'percent',categories:rows.map((x:any)=>x.end),months:rows.map((x:any)=>x.months),series:[{id:'annualReturn',values:rows.map((x:any)=>x.cagr)}],start};
 }
 if(kind==='allocation')return {type:'scatter',unit:'percent',points:b.allocations.filter((x:any)=>x.id==='equity_only'||x.cost_bps_per_traded_notional===Number(state.cost??0)).map((x:any)=>({portfolio:x.id,policy:x.policy,cost:x.cost_bps_per_traded_notional,x:-x.summary.net_max_drawdown,y:x.summary.net_cagr})),sample_months:227};
 if(kind==='waiting'){
  const keys=Object.keys(b.waiting);return {type:'bar',unit:'months',categories:keys,series:[{id:'ongoing',values:keys.map(key=>b.waiting[key].current_underperformance_months)},{id:'completed',values:keys.map(key=>b.waiting[key].longest_completed_underperformance_months)}]};
 }
 if(kind==='uncertainty'){
  const metric=state.metric??'small_large_relative_cagr';
  return {type:'interval',unit:metric==='small_large_relative_cagr'?'percent':'pp',intervals:d.uncertainty.map((x:any)=>({id:String(x.block_months),lower:x[metric].lower,median:x[metric].median,upper:x[metric].upper})),draws:d.uncertainty[0].draws};
 }
 if(kind==='spending'){
  const demand=Number(state.demand??4),shock=state.shock&&state.shock!=='none'?Number(state.shock):null;
  const metric=state.metric??'shortfall_fraction';
  const rows=d.spending.filter((x:any)=>x.annual_real_demand_per_initial_100===demand&&x.shock_month===shock);
  const portfolios=[...new Set(rows.map((x:any)=>x.portfolio))] as string[];
  return {type:'line',unit:metric.includes('fraction')?'percent':'capital',categories:['0','12','24'],series:portfolios.map(id=>({id,values:[0,12,24].map(buffer=>rows.find((x:any)=>x.portfolio===id&&x.cash_buffer_months===buffer).summary[metric])})),sample_windows:rows[0].summary.completed_windows};
 }
 if(kind==='stress'){
  const row=d.stress.find((x:any)=>x.id===(state.mask??'equity_down_5pct'));
  return {type:'bar',unit:'percent',categories:['equity_bond','equity_gold','bond_gold'],series:[{id:'jointLoss',values:['equity_bond','equity_gold','bond_gold'].map(id=>row.joint_negative_fraction[id])}],sample_months:row.months};
 }
 if(kind==='launch')return {type:'bar',unit:'percent',categories:Object.keys(d.launches),series:(state.include_pre==='yes'?['pre_launch','post_launch']:['post_launch']).map(id=>({id,values:Object.values(d.launches).map((x:any)=>x[id].cagr)})),samples:Object.fromEntries(Object.entries(d.launches).map(([id,x]:any)=>[id,{pre:x.pre_launch.months,post:x.post_launch.months}]))};
 if(kind==='etf'){
  const x=d.products[state.product??'510300.SH'];
  return {type:'bar',unit:'percent',categories:['reference','nav','market','afterCost'],series:[{id:'annualReturn',values:[x.gap.index_total_cagr,x.gap.nav_cagr,x.gap.market_total_proxy_cagr,x.round_trip_sensitivities.find((c:any)=>c.cost_bps_per_side===Number(state.cost??50)).market_proxy_cagr_after_entry_exit]}],start:x.first_observed_month_end,sample_months:x.gap.months};
 }
 throw new Error('Unknown asset chart');
}

export function assetChartJSON(data:unknown):string{
 return JSON.stringify(data).replaceAll('<',String.fromCharCode(92)+'u003c');
}
