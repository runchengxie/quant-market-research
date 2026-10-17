import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,mkdtemp,writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
const fixture=JSON.parse(await readFile(new URL('../tests/fixtures/rotation-extension.json',import.meta.url),'utf8'));

test('strict reviewed extension admits producer fixture and rejects nested private fields',async()=>{
 const {validateRotationExtension}=await import('./content/rotation-extension.server.ts');
 assert.equal(validateRotationExtension(fixture.asset,fixture.review).release_id,'rotation-forward-test');
 assert.throws(()=>validateRotationExtension({...fixture.asset,private_positions:[]},fixture.review));
 const copy=structuredClone(fixture);copy.asset.changes[0].code='/home/owner/private';
 assert.throws(()=>validateRotationExtension(copy.asset,copy.review));
 assert.throws(()=>validateRotationExtension(fixture.asset,{...fixture.review,asset_sha256:'f'.repeat(64)}));
});

test('immutable registry preserves previous index on import failure and conflicting identity',async()=>{
 const {importRotationRelease}=await import('../scripts/import-rotation-release.mjs');
 const root=await mkdtemp(join(tmpdir(),'rotation-release-'));
 const input=join(root,'input.json');await writeFile(input,JSON.stringify(fixture));
 const out=join(root,'data');
 await importRotationRelease({envelopePath:input,outputDirectory:out});
 const previous=await readFile(join(out,'rotation-release-index.json'),'utf8');
 await importRotationRelease({envelopePath:input,outputDirectory:out});
 assert.equal(await readFile(join(out,'rotation-release-index.json'),'utf8'),previous);
 const broken=structuredClone(fixture);broken.asset.forward.captured_weeks=3;
 await writeFile(input,JSON.stringify(broken));
 await assert.rejects(importRotationRelease({envelopePath:input,outputDirectory:out}));
 assert.equal(await readFile(join(out,'rotation-release-index.json'),'utf8'),previous);
});

test('index rejects traversal and failed publication keeps the last valid version',async()=>{
 const {validateReleaseIndex}=await import('./content/rotation-extension.ts');
 const {importRotationRelease}=await import('../scripts/import-rotation-release.mjs');
 const {canonical}=await import('./content/rotation-evidence.ts');
 const {createHash}=await import('node:crypto');const sha=s=>createHash('sha256').update(s).digest('hex');
 const root=await mkdtemp(join(tmpdir(),'rotation-index-'));const input=join(root,'input.json'),out=join(root,'data');
 await writeFile(input,JSON.stringify(fixture));await importRotationRelease({envelopePath:input,outputDirectory:out});
 const original=await readFile(join(out,'rotation-release-index.json'),'utf8');
 const next=structuredClone(fixture);next.asset.release_id='second-release';
 next.review.content_sha256=sha(canonical(next.asset));next.review.asset_sha256=sha(canonical(next.asset)+'\n');
 await writeFile(input,JSON.stringify(next));
 await assert.rejects(importRotationRelease({envelopePath:input,outputDirectory:out,beforeRename:()=>{throw Error('interrupted');}}));
 assert.equal(await readFile(join(out,'rotation-release-index.json'),'utf8'),original);
 const index=JSON.parse(original);index.releases[0].path='../private.json';
 assert.throws(()=>validateReleaseIndex(index));
 const changed=structuredClone(fixture);changed.asset.forward.captured_weeks=1;
 changed.review.content_sha256=sha(canonical(changed.asset));changed.review.asset_sha256=sha(canonical(changed.asset)+'\n');
 await writeFile(input,JSON.stringify(changed));
 await assert.rejects(importRotationRelease({envelopePath:input,outputDirectory:out}),/identity conflict/);
});

test('index shape rejects missing current identity and duplicate IDs',async()=>{
 const {validateReleaseIndex}=await import('./content/rotation-extension.ts');
 assert.throws(()=>validateReleaseIndex({schema_version:'research.rotation_release_index.v1',current_release_id:'missing',releases:[]}));
});

test('unavailable benchmark cannot contain performance',async()=>{
 const {validateExtensionShape}=await import('./content/rotation-extension.ts');
 const copy=structuredClone(fixture.asset);
 copy.robustness.benchmarks=[{group_id:'risk',allocator:'fixed_slots',benchmark_id:'bond_buy_hold',window_id:'common',cost_bps:5,status:'unavailable',reasons:['missing_history'],period:{start:'2024-01-01',end:'2024-12-31',sessions:252},metrics:{total_return:.1,cagr:.1,max_drawdown:-.1,sharpe_zero_rf:1}}];
 assert.throws(()=>validateExtensionShape(copy),/benchmark/i);
});

test('coverage cannot publish unobserved performance and index metadata binds envelope',async()=>{
 const {validateExtensionShape,validateIndexedBinding}=await import('./content/rotation-extension.ts');
 const a=structuredClone(fixture.asset);a.forward.coverage=[{experiment_id:'fixed-base',captured_weeks:0,settled_weeks:0,metrics:{total_return:0,cagr:0,max_drawdown:0,sharpe_zero_rf:0}}];
 assert.throws(()=>validateExtensionShape(a));
 const entry={release_id:fixture.asset.release_id,schema_version:fixture.asset.schema_version,content_sha256:fixture.review.content_sha256,reviewer:fixture.review.reviewer,published_at:fixture.review.reviewed_at};
 validateIndexedBinding(entry,fixture);
 for(const field of ['release_id','schema_version','reviewer','published_at'])assert.throws(()=>validateIndexedBinding({...entry,[field]:'wrong'},fixture));
});

test('retained registry metadata corruption blocks import without replacing index',async()=>{
 const {importRotationRelease}=await import('../scripts/import-rotation-release.mjs');
 const root=await mkdtemp(join(tmpdir(),'rotation-binding-')),input=join(root,'input.json'),out=join(root,'data');
 await writeFile(input,JSON.stringify(fixture));await importRotationRelease({envelopePath:input,outputDirectory:out});
 const path=join(out,'rotation-release-index.json'),index=JSON.parse(await readFile(path,'utf8'));
 index.releases[0].reviewer='incorrect-reviewer';const corrupted=JSON.stringify(index);await writeFile(path,corrupted);
 await assert.rejects(importRotationRelease({envelopePath:input,outputDirectory:out}),/binding/);
 assert.equal(await readFile(path,'utf8'),corrupted);
});

test('unavailable strategy cannot retain metrics, period or turnover independently',async()=>{
 const {validateExtensionShape}=await import('./content/rotation-extension.ts');
 const row={id:'case',experiment_id:'fixed-base',group_id:'risk',allocator:'fixed_slots',cost_bps:5,delay_sessions:1,window_id:'common',status:'unavailable',reasons:['insufficient_complete_sessions'],period:null,metrics:null,turnover:null,pending_terminal:0};
 for(const [field,value] of [['metrics',{total_return:0,cagr:0,max_drawdown:0,sharpe_zero_rf:0,volatility:0,cost_drag:0,avg_bond_weight:0,attribution:{risk:0,bond:0,costs:0,residual:0,total_return:0}}],['period',{start:'2024-01-01',end:'2024-12-31',sessions:252}],['turnover',0]]){
 const a=structuredClone(fixture.asset);a.robustness.rows=[{...row,[field]:value}];assert.throws(()=>validateExtensionShape(a),/robustness/);
 }
});
