import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { auditLiquidityMarket, liquidityComparison, marketsForPeriod, mechanicalOrderBudget } from './lib/liquidity-quality.ts';
const source = JSON.parse(readFileSync(new URL('../public/data/liquidity/inherited-summary.json', import.meta.url)));
test('count conflicts quarantine the published A-share snapshot without guessing a correction', () => {
 assert.deepEqual(auditLiquidityMarket(source.markets[2]).map(x => x.code), ['total_count_mismatch','sub100m_count_mismatch']);
 assert.deepEqual(auditLiquidityMarket(source.markets[0]), []);
 assert.deepEqual(liquidityComparison(source.markets, 0, 'median_usd').map(x=>x.market), ['US','HK']);
});
test('missing P90 remains null and bucket selections use the same group across markets', () => {
 const rows=liquidityComparison(source.markets,1,'p90_usd');
 assert.equal(rows[0].value,1983502); assert.equal(rows[1].value,null);
 assert.equal(liquidityComparison(source.markets,1,'median_usd')[1].value,13004);
});
test('pending and unknown periods never show latest data', () => {
 assert.deepEqual(marketsForPeriod(source,'2025'),[]);
 assert.deepEqual(marketsForPeriod(source,'missing'),[]);
 assert.equal(marketsForPeriod(source,'latest').length,3);
});
test('arithmetic budget validates bounds and preserves missing input', () => {
 assert.equal(mechanicalOrderBudget(100000,0.05,5),25000);
 assert.equal(mechanicalOrderBudget(null,0.05,5),null);
 for(const args of [[100,0,1],[100,1.1,1],[100,.1,0],[100,.1,1.5],[-1,.1,1],[NaN,.1,1]]) assert.throws(()=>mechanicalOrderBudget(...args),RangeError);
});
test('arithmetic overflow is rejected instead of displaying infinite capacity',()=>{
 assert.throws(()=>mechanicalOrderBudget(1e308,1,10),RangeError);
});

test('pooled stock counts may overlap buckets but security-day totals must reconcile',()=>{
 const item={market:'JP',aggregation:'security_day',unique_stocks:1,eligible_observations:4,below_100m_observations:2,buckets:[{label:'< $10m',count:1,observations:2},{label:'$10m-$100m',count:0,observations:0},{label:'$100m-$1bn',count:1,observations:2}]};
 assert.deepEqual(auditLiquidityMarket(item),[]);
 assert.equal(auditLiquidityMarket({...item,eligible_observations:5})[0].code,'observation_count_mismatch');
});

test('rolling median is selected explicitly rather than relabeled ADV20',()=>{
 const market={market:'US',buckets:[{label:'< $10m',count:1,median_usd:100,median20_median_usd:80}]};
 assert.equal(liquidityComparison([market],0,'median_usd','median20')[0].value,80);
 assert.equal(liquidityComparison([market],0,'p90_usd','median20')[0].value,null);
});
