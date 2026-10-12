import test from 'node:test';
import assert from 'node:assert/strict';
import {formatEvidenceNumber,formatEvidenceFraction,formatEvidenceNav,selectSurface} from './lib/execution-expansion.ts';
import {expansionCopy} from './content/execution-expansion-copy.ts';
test('missing costs stay missing while published zero remains zero',()=>{
 for(const value of [null,undefined,NaN,Infinity,'0']) {
  assert.equal(formatEvidenceNumber(value),'—');assert.equal(formatEvidenceFraction(value),'—');
 }
 assert.equal(formatEvidenceNumber(0),'0');assert.equal(formatEvidenceFraction(.045),'4.50%');
 assert.equal(formatEvidenceNav(1.30573632),'1.305736');
 assert.equal(formatEvidenceNav(null),'—');
});
test('cost and coverage anchors select the same side and exact yuan amount',()=>{
 const rows=[{side:'buy',reference_notional_cny:10000},{side:'sell',reference_notional_cny:100000},{side:'buy',reference_notional_cny:100000},{side:'buy',reference_notional_cny:1000000}];
 assert.equal(selectSurface(rows,'buy',100000),rows[2]);assert.equal(selectSurface(rows,'buy',1000000),rows[3]);assert.equal(selectSurface(rows,'sell',1000000),undefined);
});
test('published cohort keys and scenarios have both locale labels',()=>{
 for(const key of ['low','middle','high','unavailable','opening','late_morning','early_afternoon','late_afternoon','gross','fee_only','fee_static_10k','fee_static_1m','fee_expanded_100k','fee_expanded_1m']) assert.ok(expansionCopy[key].every(value=>value.length>0));
});

test('interactive surface selection keeps conditional costs, coverage and counts together', async()=>{
 const {surfaceChartRows}=await import('./lib/execution-chart.ts');
 const groups={low:{snapshots:3,cost_surface:[{side:'sell',reference_notional_cny:10000,full_coverage_rate:0,full_order_cost_bp:{count:0,p50:null,p90:null}}]}};
 assert.deepEqual(surfaceChartRows(groups,'sell',10000),[{key:'low',books:3,filled:0,p50:null,p90:null,coverage:0}]);
 assert.equal(surfaceChartRows(groups,'buy',10000)[0].coverage,null);
});
test('strategy comparison selects reviewed capital and only main scenarios',async()=>{
 const {strategyChartRows}=await import('./lib/execution-chart.ts');
 assert.deepEqual(strategyChartRows([{capital_cny:10,scenario:'gross',terminal_nav:1},{capital_cny:10,scenario:'fee_static_10k',terminal_nav:2},{capital_cny:20,scenario:'fee_only',terminal_nav:3}],10).map(r=>r.scenario),['gross']);
});

test('published workflow retains blocked replay and synthetic-only calibration evidence',async()=>{
 const {readFile}=await import('node:fs/promises');
 const workflow=JSON.parse(await readFile(new URL('../public/data/execution-costs/replay.json',import.meta.url),'utf8'));
 assert.equal(workflow.data_quality.full_book_replay,'blocked');
 assert.equal(workflow.data_quality.actual_slippage,'not_measured');
 assert.equal(workflow.calibration_entry.actual_order_calibrated,false);
 assert.equal(workflow.calibration_entry.validation_fixture_kind,'synthetic');
 assert.equal(workflow.simulation.participation.status,'unavailable');
 assert.equal(workflow.simulation.aggregate_results.length,6);
 assert.equal(workflow.simulation.sample_paths,12);
 assert.ok(!JSON.stringify(workflow).match(/\/home\/|\/mnt\/|SecuCode|parent_order_id/));
});
