import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const fixture=JSON.parse(await readFile(new URL('../tests/fixtures/rotation-foundation.json',import.meta.url),'utf8'));

test('foundation separate schema admits only reviewed aggregates',async()=>{
 const {validateRotationFoundation}=await import('./content/rotation-foundation.server.ts');
 assert.equal(validateRotationFoundation(fixture.asset,fixture.review).schema_version,'research.rotation_foundation.v1');
});
test('foundation rejects private nested keys, private text, nonfinite and unavailable-to-zero',async()=>{
 const {validateRotationFoundation}=await import('./content/rotation-foundation.server.ts');
 for(const mutate of [a=>a.causes.positions={},a=>a.comparisons[0].reasons=['/home/private/model'],a=>a.causes.cells=NaN,a=>a.comparisons[0].metrics={},a=>a.comparisons[0].status='available']){
 const e=structuredClone(fixture);mutate(e.asset);assert.throws(()=>validateRotationFoundation(e.asset,e.review));
 }
 const changed=structuredClone(fixture);changed.review.content_sha256='0'.repeat(64);assert.throws(()=>validateRotationFoundation(changed.asset,changed.review));
});
test('foundation selectors preserve coverage and unavailable formatting',async()=>{
 const {foundationComparison,foundationPercent}=await import('./content/rotation-foundation.ts');
 assert.equal(foundationComparison(fixture.asset,'primary','combined','passive').metrics,null);
 assert.equal(foundationComparison(fixture.asset,'unknown','combined','passive'),undefined);
 assert.equal(foundationPercent(null,'en-US'),'Unavailable');
 assert.equal(foundationPercent(null,'zh-CN'),'不可用');
 assert.equal(foundationPercent(0,'en-US'),'0.00%');
});

test('foundation dispatch and immutable importer preserve retained releases',async(t)=>{
 const {validateReviewedRotationEnvelope}=await import('./content/rotation-operations.server.ts');
 assert.equal(validateReviewedRotationEnvelope(fixture).schema_version,'research.rotation_foundation.v1');
 const {importRotationRelease}=await import('../scripts/import-rotation-release.mjs');
 const {mkdtemp,writeFile,rm}=await import('node:fs/promises');const {tmpdir}=await import('node:os');const {join}=await import('node:path');
 const root=await mkdtemp(join(tmpdir(),'rotation-foundation-'));t.after(()=>rm(root,{recursive:true,force:true}));
 const old=JSON.parse(await readFile(new URL('../tests/fixtures/rotation-operations.json',import.meta.url),'utf8'));
 const oldPath=join(root,'old.json'),candidate=join(root,'candidate.json'),out=join(root,'out');
 await writeFile(oldPath,JSON.stringify(old)+'\n');await writeFile(candidate,JSON.stringify(fixture)+'\n');
 await importRotationRelease({envelopePath:oldPath,outputDirectory:out});const before=await readFile(join(out,`rotation/releases/${old.asset.release_id}.json`));
 await importRotationRelease({envelopePath:candidate,outputDirectory:out});
 assert.deepEqual(await readFile(join(out,`rotation/releases/${old.asset.release_id}.json`)),before);
 assert.equal(JSON.parse(await readFile(join(out,'rotation-release-index.json'),'utf8')).current_release_id,fixture.asset.release_id);
});

test('foundation public matrix cannot shorten calendars or omit registered rows',async()=>{
 const {validateFoundationShape}=await import('./content/rotation-foundation.ts');
 const shortened=structuredClone(fixture.asset);shortened.comparisons[0].period={start:'2023-09-25',end:'2023-09-26'};shortened.comparisons[0].expected_sessions=2;
 assert.throws(()=>validateFoundationShape(shortened),/calendar/i);
 const missing=structuredClone(fixture.asset);missing.comparisons=missing.comparisons.slice(0,1);assert.throws(()=>validateFoundationShape(missing),/matrix/i);
});
test('foundation cannot advertise theme returns without admitted attention evidence',async()=>{
 const {validateFoundationShape}=await import('./content/rotation-foundation.ts');
 const a=structuredClone(fixture.asset),r=a.comparisons.find(r=>r.left==='theme-overlay');
 const metric=Object.fromEntries(['total_return','cagr','max_drawdown','volatility','total_cost','turnover','mean_risky_exposure'].map(k=>[k,0]));
 Object.assign(r,{status:'available',weekly_pairs:1,reasons:[],metrics:{left:metric,right:metric},uncertainty:{estimate:0,interval:[0,0],weekly_pairs:1,expected_block_weeks:13,replicates:10000,seed:20261018,sensitivity:[{expected_block_weeks:8,interval:[0,0]},{expected_block_weeks:26,interval:[0,0]}]}});
 assert.throws(()=>validateFoundationShape(a),/theme/i);
});
