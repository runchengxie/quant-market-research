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
