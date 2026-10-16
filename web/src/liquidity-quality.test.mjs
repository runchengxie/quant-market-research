import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { auditLiquidityMarket, liquidityComparison, marketsForPeriod, mechanicalOrderBudget } from './lib/liquidity-quality.ts';
const source = JSON.parse(readFileSync(new URL('../public/data/liquidity/summary.json', import.meta.url)));
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
