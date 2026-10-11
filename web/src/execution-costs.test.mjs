import test from 'node:test';
import assert from 'node:assert/strict';
import { annualCost, costScenarios } from './lib/execution-costs.ts';
import { publicPages } from './content/public-registry.ts';
test('turnover definitions produce the stated fee and slippage sensitivities', () => {
 assert.ok(Math.abs(annualCost(.6,.6,0)-.105)<1e-12);
 assert.ok(Math.abs(annualCost(.3,.3,0)-.0525)<1e-12);
 assert.ok(Math.abs(annualCost(.6,.6,1)-annualCost(.6,.6,0)-.03)<1e-12);
 assert.deepEqual(costScenarios.map(r=>Number((r.oneWay*100).toFixed(1))),[10.5,13.5,19.5,25.5,40.5]);
 assert.equal(annualCost(0,0,10),0);
 assert.throws(()=>annualCost(.6,.6,NaN),RangeError);
});
test('topic is discoverable without claiming an empirical snapshot', () => {
 const topic=publicPages.find(p=>p.id==='execution-costs');
 assert.equal(topic.route,'/research/execution-costs/');
 assert.deepEqual(topic.snapshotKeys,[]);
 assert.ok(publicPages.find(p=>p.id==='research').related.includes(topic.id));
});
