import test from 'node:test';import assert from 'node:assert/strict';import{readFileSync}from'node:fs';
import{assetTopicContents}from'./content/asset-topics.ts';
import{validateAssetPublication,assetEvidenceVersion}from'./content/asset-publication.server.ts';
import{readingSummaries}from'./content/research-reading.server.ts';
test('non-chart research and records have directory entries on their owning topics',()=>{
 const ids=topic=>assetTopicContents[topic].map(x=>x.id);
 for(const id of['asset-diversification','asset-smallcap-costs','asset-return-gaps','asset-return-records'])assert.ok(ids('returns').includes(id),id);
 for(const id of['asset-cost-basis','asset-stress-recovery','asset-method-records'])assert.ok(ids('allocation').includes(id),id);
 for(const id of['asset-etf-reconciliation','asset-constituent-coverage','asset-evidence-checks','asset-conclusion-register','asset-method-records'])assert.ok(ids('implementation').includes(id),id);
 for(const entries of Object.values(assetTopicContents))assert.equal(entries.length,new Set(entries.map(x=>x.id)).size);
});
test('asset evidence version is source-bound and separate from acquisition/sample dates',()=>{
 const record=JSON.parse(readFileSync('../studies/asset_returns/publication-record.json','utf8'));const manifest=readFileSync('../studies/asset_returns/release-manifest.json');
 assert.equal(validateAssetPublication(record,manifest).version_date,'2026-11-01');assert.equal(assetEvidenceVersion.revision,'dc85d825d4e3eadd587020ffced36e038c0df27f');
 for(const id of['returns','allocation','implementation']){const r=readingSummaries.find(x=>x.id===`asset-${id}`);assert.equal(r.date,'2026-11-01');assert.equal(r.evidenceVersion.date,r.date);assert.match(r.evidenceVersion.manifestUrl,/dc85d825/);}
 assert.throws(()=>validateAssetPublication({...record,version_date:'2026-10-31'},manifest),/date/i);
 assert.throws(()=>validateAssetPublication(record,Buffer.from('{}')),/manifest/i);
 const crossing={...record,published_at:'2026-10-31T16:30:00Z'};assert.equal(validateAssetPublication(crossing,manifest).version_date,'2026-11-01');
});
