import test from 'node:test';import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const {asset}=JSON.parse(await readFile(new URL('../tests/fixtures/rotation-extension.json',import.meta.url),'utf8'));
const row={id:'fixed-base-cost5-delay1-common',experiment_id:'fixed-base',group_id:'risk',allocator:'fixed_slots',cost_bps:5,delay_sessions:1,window_id:'common',status:'available',reasons:[],period:{start:'2024-01-01',end:'2024-12-31',sessions:252},metrics:{total_return:.1,cagr:.1,max_drawdown:-.1,sharpe_zero_rf:1,volatility:.1,cost_drag:.01,avg_bond_weight:.5,attribution:{risk:.1,bond:0,costs:0,residual:0,total_return:.1}},turnover:1,pending_terminal:0};
test('matching protocols admit deltas; incompatible periods or vintages suppress them',async()=>{
 const {compareRotationReleases}=await import('./content/rotation-release-comparison.ts');
 const left=structuredClone(asset),right=structuredClone(asset);left.robustness.rows=[structuredClone(row)];right.robustness.rows=[structuredClone(row)];
 right.robustness.rows[0].metrics.cagr=.12;
 let result=compareRotationReleases(left,right);assert.ok(Math.abs(result.rows[0].cagr_delta-.02)<1e-12);
 right.robustness.rows[0].period.start='2024-01-02';result=compareRotationReleases(left,right);
 assert.equal(result.rows[0].status,'incompatible');assert.equal(result.rows[0].cagr_delta,null);
 right.robustness.rows[0].period.start='2024-01-01';right.sources.hashes.core='f'.repeat(64);
 assert.equal(compareRotationReleases(left,right).rows[0].cagr_delta,null);
});
test('old schemas and missing cases stay explicit',async()=>{
 const {compareRotationReleases}=await import('./content/rotation-release-comparison.ts');
 assert.equal(compareRotationReleases({schema_version:'research.rotation_evidence.v1'},asset).status,'incompatible');
 const right=structuredClone(asset);right.robustness.rows=[row];
 assert.equal(compareRotationReleases(asset,right).rows[0].status,'added');
});

test('old-schema comparison still explains the actual newly reviewed changes',async()=>{
 const {compareRotationReleases}=await import('./content/rotation-release-comparison.ts');
 const result=compareRotationReleases({schema_version:'research.rotation_evidence.v1'},asset);
 assert.ok(result.changes.includes('recovered_two_symbols'));
});

test('source trust, mapping and complete row definitions suppress deltas',async()=>{
 const {compareRotationReleases}=await import('./content/rotation-release-comparison.ts');
 for(const mutate of [a=>a.sources.availability='verified',a=>a.robustness.historical_availability='verified',a=>a.sources.hashes.mapping='f'.repeat(64),a=>a.robustness.rows[0].experiment_id='pool-core',a=>a.robustness.rows[0].window_id='last_252',a=>a.robustness.rows[0].group_id='pool']){
 const l=structuredClone(asset);l.robustness.rows=[structuredClone(row)];const r=structuredClone(l);mutate(r);
 const result=compareRotationReleases(l,r);assert.equal(result.rows[0].cagr_delta,null);assert.ok(!result.changes.includes('same_definitions'));
 }
});

test('changed forward registration remains visible when historical metrics are unchanged',async()=>{
 const {compareRotationReleases}=await import('./content/rotation-release-comparison.ts');
 const right=structuredClone(asset);right.forward.registration_id='new-registration';right.changes.push({kind:'forward',code:'forward_controls_hardened'});
 const result=compareRotationReleases(asset,right);assert.ok(result.changes.includes('forward_evidence_changed'));assert.ok(result.changes.includes('forward_controls_hardened'));
});
