import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {selectCostRows, costValue} from './lib/overseas-cost-chart.ts';
const {costs} = JSON.parse(fs.readFileSync(new URL('../public/data/overseas_leadlag_reviewed.json',import.meta.url),'utf8'));
test('cost selection preserves reviewed ETF, lag, samples and exact values',()=>{
 for(const target of ['510300','512480']) for(const lag of [0,1]) {
  const selected=selectCostRows(costs,target,lag);
  assert.equal(selected.length,20);
  assert.ok(selected.every(r=>r.target===target && r.lag_sessions===lag && r.scenario==='flat_bps'));
  for(const row of selected) assert.ok(costs.includes(row));
 }
 assert.equal(selectCostRows(costs,'unknown',0).length,0);
});
test('missing cost outcomes remain gaps rather than zero',()=>{
 for(const value of [undefined,null,NaN,Infinity]) assert.equal(costValue(value),null);
 assert.equal(costValue(0),0);
 assert.equal(costValue(-1.25),-1.25);
});
