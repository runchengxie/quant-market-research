import test from 'node:test';import assert from 'node:assert/strict';import {readFile} from 'node:fs/promises';
const {asset}=JSON.parse(await readFile(new URL('../tests/fixtures/rotation-operations.json',import.meta.url),'utf8'));
test('matched controls restore exact permitted dates and preserve unrelated URL state',async()=>{
 const {matchedSelection,matchedRow,selectionParams}=await import('./content/rotation-operations-display.ts');
 const selected=matchedSelection(new URLSearchParams('opsBaseline=pool-core&opsWindow=last_252&opsCase=delay-two'),['common','last_252']);
 assert.equal(selected.baseline,'pool-core');assert.equal(selected.window,'last_252');assert.equal(selected.case,'delay-two');
 assert.equal(matchedRow(asset.comparisons.rows,selected),undefined);
 const query=selectionParams(new URLSearchParams('lang=zh-CN&rotationDate=2026-08-21'),selected);
 assert.equal(query.get('lang'),'zh-CN');assert.equal(query.get('rotationDate'),'2026-08-21');assert.equal(query.get('opsWindow'),'last_252');
 const reset=matchedSelection(new URLSearchParams('opsWindow=2099&opsCase=unknown'),['common']);
 assert.equal(reset.window,'common');assert.equal(reset.case,'primary');
});
test('both locales are complete and CSV retains unavailable state without invented performance',async()=>{
 const {operationsCopy,operationCodes}=await import('./content/rotation-operations-copy.ts');
 for(const catalog of [operationsCopy,operationCodes])for(const pair of Object.values(catalog)){assert.equal(pair.length,2);assert.ok(pair.every(v=>typeof v==='string'&&v.length));}
 const {matchedCsv}=await import('./content/rotation-operations-display.ts');
 const row=structuredClone(asset.comparisons.rows[0]);row.status='unavailable';row.metrics=null;row.differences=null;row.period=null;
 const csv=matchedCsv(row);assert.match(csv,/unavailable/);assert.doesNotMatch(csv,/positions|source_path|NaN|undefined/);
});
