import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {assetChartView} from './lib/asset-interactive.ts';
const load=name=>JSON.parse(readFileSync(new URL(`../public/data/${name}`,import.meta.url)));
const data={returns:load('asset_returns_reviewed.json'),robustness:load('asset_robustness_reviewed.json'),decision:load('asset_decision_reviewed.json')};

test('uncertainty charts preserve reviewed asymmetric bounds and zero crossings',()=>{
 const view=assetChartView('uncertainty',data,{metric:'small_large_relative_cagr'});
 assert.equal(view.type,'interval');
 assert.equal(view.intervals[1].lower,data.decision.uncertainty[1].small_large_relative_cagr.lower);
 assert.equal(view.intervals[1].upper,data.decision.uncertainty[1].small_large_relative_cagr.upper);
 assert(view.intervals.every(r=>r.lower<0&&r.upper>0));
});
test('spending graph and table use identical fixed demands and no invented paths',()=>{
 const view=assetChartView('spending',data,{demand:'4',shock:'12',metric:'shortfall_fraction'});
 assert.equal(view.unit,'percent');assert.deepEqual(view.categories,['0','12','24']);
 assert.equal(view.series[0].values[0],6/108);assert.equal(view.series[0].values[2],4/108);
 assert.equal(view.sample_windows,108);assert(!('paths' in view));
});
test('endpoint and ETF charts retain actual windows and per-side costs',()=>{
 const view=assetChartView('endpoints',data,{asset:'all_share',start:'2004-12-31'});
 assert(view.months.every(n=>n>=60));
 const etf=assetChartView('etf',data,{product:'512100.SH',cost:'50'});
 const source=data.decision.products['512100.SH'];
 assert.equal(etf.series[0].values[3],source.round_trip_sensitivities.find(x=>x.cost_bps_per_side===50).market_proxy_cagr_after_entry_exit);
 assert.equal(etf.start,'2016-11-30');
});
test('stress and allocation preserve mask denominators and exact scenario cost',()=>{
 const stress=assetChartView('stress',data,{mask:'equity_down_5pct'});
 assert.equal(stress.sample_months,42);assert.equal(stress.series[0].values[1],20/42);
 const allocation=assetChartView('allocation',data,{cost:'50'});
 assert.equal(allocation.points.length,7);
 assert(allocation.points.every(x=>x.portfolio==='equity_only'||x.cost===50));
});

test('embedded chart JSON round-trips text while escaping script boundaries',async()=>{
 const {assetChartJSON}=await import('./lib/asset-interactive.ts');
 const value={label:'</script><p>原始说明</p>'};const encoded=assetChartJSON(value);
 assert(!encoded.includes('<'));assert.deepEqual(JSON.parse(encoded),value);
});
