import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {readingSummaries,summaryForRoute} from './content/research-reading.server.ts';
import {publicPages} from './content/public-registry.ts';
import {methodSections} from './content/search-sections.server.ts';
import {searchRecords} from './lib/search.ts';

test('each main topic has resolvable evidence files, versions and subordinate links',()=>{
 assert.equal(readingSummaries.length,9);
 for(const r of readingSummaries){
  assert.equal(summaryForRoute('/quant-market-research'+r.route)?.id,r.id);
  assert.ok(r.limit.every(Boolean));assert.ok(r.coverage.every(Boolean));
  for(const id of r.related)assert.ok(publicPages.some(p=>p.id===id),id);
  for(const source of r.sources)assert.equal(source.sha256,createHash('sha256').update(readFileSync('public/data/'+source.path)).digest('hex'));
 }
 assert.equal(summaryForRoute('/research/microcap/report/'),undefined);
 const low=JSON.parse(readFileSync('public/data/low_turnover_reader.json','utf8'));
 assert.ok(readingSummaries.find(r=>r.id==='low-turnover').coverage[0].includes(low.formationEnd));
});
test('search indexes late sections, duplicate heading slugs and legacy anchors',async()=>{
 const meta={id:'test',title:'Test',route:'/docs/test/',source:'docs/test.md',aliases:[]};
 const records=await methodSections(meta,'# Start\n'+('intro '.repeat(350))+'\n## Late evidence\nUnresolved terminal prices.\n## Late evidence\nAnother observation.');
 const found=searchRecords(records,'terminal');assert.equal(found.length,1);assert.equal(found[0].href,'/docs/test/#late-evidence');
 assert.equal(records.at(-1).href,'/docs/test/#late-evidence-1');
 const legacy=await methodSections({...meta,source:'docs/research/factors/low-turnover.md'},'# Title\nText\n## Snapshot\nEvidence');
 assert.equal(legacy[1].href,'/docs/test/#2026-09-16');
});
test('common research records are searchable in both languages',()=>{
 const r={id:'research',title:'低换手',titleEn:'Low turnover',text:'历史比较',textEn:'Historical comparison',kind:'research',href:'/',aliases:[]};
 assert.equal(searchRecords([r],'historical').length,1);assert.equal(searchRecords([r],'低换手').length,1);
});
test('heterogeneous index histories do not imply one missing or common sample window',()=>{
 for (const id of ['cashflow','indices']) {
  const summary=readingSummaries.find(row=>row.id===id);
  assert.ok(summary.coverage[0].includes('differ'));
  assert.ok(summary.coverage[1].includes('不同'));
  assert.ok(summary.coverage.every(text=>!text.includes('Not provided')&&!text.includes('未提供')));
 }
});
