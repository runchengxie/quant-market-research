import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const fixture=JSON.parse(await readFile(new URL('../tests/fixtures/rotation-operations.json',import.meta.url),'utf8'));
const sha=s=>createHash('sha256').update(s).digest('hex');

test('new operations contract admits its separately reviewed synthetic aggregate',async()=>{
 const {validateRotationOperations}=await import('./content/rotation-operations.server.ts');
 assert.equal(validateRotationOperations(fixture.asset,fixture.review).schema_version,'research.rotation_operations.v1');
});

test('operations rejects private fields, unsupported protocols, incomplete metrics and stale review',async()=>{
 const {validateRotationOperations}=await import('./content/rotation-operations.server.ts');
 for(const mutate of [
  e=>e.asset.health.positions={secret:1},
  e=>e.asset.comparisons.rows[0].status='unavailable',
  e=>e.asset.comparisons.risk.lookback=61,
  e=>e.asset.health.cutoff_local='14:00',
  e=>e.asset.comparisons.rows[0].comparator_period.end='2024-01-04',
  e=>e.asset.comparisons.rows.push(structuredClone(e.asset.comparisons.rows[0])),
  e=>e.review.asset_sha256='0'.repeat(64),
  e=>e.asset.schema_version='research.rotation_operations.v99',
 ]) {const e=structuredClone(fixture);mutate(e);assert.throws(()=>validateRotationOperations(e.asset,e.review));}
});

test('changed protocols and source trust never produce numeric version deltas',async()=>{
 const {compareRotationReleases}=await import('./content/rotation-release-comparison.ts');
 const left=structuredClone(fixture.asset),right=structuredClone(left);
 right.comparisons.protocol_sha256='c'.repeat(64);
 let result=compareRotationReleases(left,right);
 assert.equal(result.rows[0].cagr_delta,null);assert.equal(result.rows[0].drawdown_delta,null);
 right.comparisons.protocol_sha256=left.comparisons.protocol_sha256;
 right.audit.audit_sha256='f'.repeat(64);
 result=compareRotationReleases(left,right);assert.equal(result.rows[0].cagr_delta,null);
 assert.equal(result.rows[0].drawdown_delta,null);
});

test('operations import keeps retained bytes and an interrupted index readable',async(t)=>{
 const {mkdtemp,writeFile,readFile,rm}=await import('node:fs/promises');
 const {tmpdir}=await import('node:os');const {join}=await import('node:path');
 const {importRotationRelease}=await import('../scripts/import-rotation-release.mjs');
 const {canonical}=await import('./content/rotation-evidence.ts');
 const root=await mkdtemp(join(tmpdir(),'rotation-operations-import-'));t.after(()=>rm(root,{recursive:true,force:true}));
 const output=join(root,'public');
 const old=new URL('../tests/fixtures/rotation-extension.json',import.meta.url);
 await importRotationRelease({envelopePath:old,outputDirectory:output});
 const oldIndex=JSON.parse(await readFile(join(output,'rotation-release-index.json'),'utf8'));
 const oldEntry=oldIndex.releases[0],before=await readFile(join(output,oldEntry.path));
 await importRotationRelease({envelopePath:new URL('../tests/fixtures/rotation-operations.json',import.meta.url),outputDirectory:output});
 assert.deepEqual(await readFile(join(output,oldEntry.path)),before);
 const first=await readFile(join(output,'rotation-release-index.json'));
 const changed=structuredClone(fixture);changed.asset.release_id='operations-second';
 const source={...changed.asset};delete source.schema_version;delete source.reviewed_source_digest;
 changed.asset.reviewed_source_digest=sha(canonical(source));changed.review.source_sha256=changed.asset.reviewed_source_digest;
 changed.review.content_sha256=sha(canonical(changed.asset));changed.review.asset_sha256=sha(canonical(changed.asset)+'\n');
 const candidate=join(root,'candidate.json');await writeFile(candidate,canonical(changed)+'\n');
 await assert.rejects(importRotationRelease({envelopePath:candidate,outputDirectory:output,beforeRename(){throw Error('interrupted');}}),/interrupted/);
 assert.deepEqual(await readFile(join(output,'rotation-release-index.json')),first);
 await importRotationRelease({envelopePath:candidate,outputDirectory:output});
 assert.equal(JSON.parse(await readFile(join(output,'rotation-release-index.json'),'utf8')).current_release_id,'operations-second');
});

test('unknown release schemas fail explicit dispatch before publication',async(t)=>{
 const {mkdtemp,writeFile,access,rm}=await import('node:fs/promises');const {tmpdir}=await import('node:os');const {join}=await import('node:path');
 const {importRotationRelease}=await import('../scripts/import-rotation-release.mjs');
 const root=await mkdtemp(join(tmpdir(),'rotation-unknown-'));t.after(()=>rm(root,{recursive:true,force:true}));
 const changed=structuredClone(fixture);changed.asset.schema_version='research.rotation_future.v99';
 const candidate=join(root,'unknown.json');await writeFile(candidate,JSON.stringify(changed));
 await assert.rejects(importRotationRelease({envelopePath:candidate,outputDirectory:join(root,'public')}),/schema/i);
 await assert.rejects(access(join(root,'public')));
});

test('empty audit dimensions remain explicitly unknown',async()=>{
 const {validateOperationsShape}=await import('./content/rotation-operations.ts');
 const asset=structuredClone(fixture.asset);
 const dimension={rule:'minimum_history',state:'unknown',records:0,reason:'missing_evidence',admitted:0,unknown:0,rejected:0};
 asset.audit.dimensions=[dimension];assert.ok(validateOperationsShape(asset));
 dimension.state='admitted';assert.throws(()=>validateOperationsShape(asset),/dimension/);
});

test('named comparison windows cannot relabel shortened periods',async()=>{
 const {validateOperationsShape}=await import('./content/rotation-operations.ts');
 for(const window of ['last_252','last_756','rolling_252_2024-01-03','rolling_756_2024-01-03','year_2024','rolling_252_2024-02-30','unknown_window']){
  const asset=structuredClone(fixture.asset),row=asset.comparisons.rows[0];row.window_id=window;row.id=row.id.replace(/common$/,window);
  assert.throws(()=>validateOperationsShape(asset),/window/);
 }
});

test('complete named windows retain their declared count and endpoint',async()=>{
 const {validateOperationsShape}=await import('./content/rotation-operations.ts');
 for(const [window,sessions] of [['last_252',252],['last_756',756],['rolling_252_2024-12-31',252],['rolling_756_2024-12-31',756],['year_2024',250]]){
  const asset=structuredClone(fixture.asset),row=asset.comparisons.rows[0];row.window_id=window;row.id=row.id.replace(/common$/,String(window));
  for(const key of ['period','reference_period','comparator_period'])row[key]={start:sessions===756?'2021-01-04':'2024-01-02',end:'2024-12-31',sessions};
  assert.ok(validateOperationsShape(asset));
  if(String(window).startsWith('rolling_')||String(window).startsWith('year_')){
   for(const key of ['period','reference_period','comparator_period'])row[key].end='2024-11-29';
   assert.throws(()=>validateOperationsShape(asset),/window/);
  }
 }
});
