import test from 'node:test';
import assert from 'node:assert/strict';
import {buildSearchRecords} from './content/search-records.server.ts';
import {readPublicDocuments} from './content/public-docs-loader.ts';
import {resolve} from 'node:path';
test('section search retains every public document within the index budget',async()=>{
 const records=await buildSearchRecords();const docs=await readPublicDocuments(resolve(process.cwd(),'..'));
 for(const doc of docs){
  const sections=records.filter(r=>r.id===doc.meta.id||r.id.startsWith(doc.meta.id+'-section-'));
  assert.ok(sections.length>0,doc.meta.id);
  for(const r of sections){assert.ok(Array.from(r.text).length<=(r.id.endsWith('-section-0')?1200:240));assert.ok(r.href.startsWith(doc.meta.route));}
 }
 assert.ok(records.some(r=>r.id.startsWith('valuation-panel-section-')));
 assert.ok(Buffer.byteLength(JSON.stringify(records),'utf8')<=250*1024);
 assert.equal(new Set(records.map(r=>r.id)).size,records.length);
});
