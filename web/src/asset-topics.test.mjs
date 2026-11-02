import test from 'node:test';
import assert from 'node:assert/strict';
import {assetTopics,assetLegacyTarget} from './content/asset-topics.ts';
import {publicPages} from './content/public-registry.ts';
import {libraryGroups} from './content/research-library.ts';
test('ten reviewed charts belong to complete, independently discoverable asset topics',()=>{
 assert.deepEqual(assetTopics.map(x=>x.id),['returns','allocation','implementation']);
 const kinds=assetTopics.flatMap(x=>x.charts);assert.equal(kinds.length,10);assert.equal(new Set(kinds).size,10);
 for(const topic of assetTopics){assert.ok(publicPages.some(p=>p.id===`asset-${topic.id}`&&p.route===topic.route));assert.ok(libraryGroups.some(g=>g.topics.includes(`asset-${topic.id}`)));}
 assert.deepEqual(assetTopics.find(x=>x.id==='allocation').charts,['allocation','spending','stress']);
});
test('old cashflow asset anchors retain the owning page, query and selected anchor',()=>{
 assert.equal(assetLegacyTarget('#cashflow-long-run','?lang=zh-CN'),'/research/asset-returns/?lang=zh-CN#cashflow-long-run');
 assert.equal(assetLegacyTarget('#cashflow-robustness','?lang=en-US'),'/research/asset-implementation/?lang=en-US#cashflow-robustness');
 assert.equal(assetLegacyTarget('#asset-chart-spending-title','?lang=zh-CN'),'/research/asset-allocation/?lang=zh-CN#asset-chart-spending-title');
 assert.equal(assetLegacyTarget('#allocation-rules','?lang=zh-CN'),'/research/asset-allocation/?lang=zh-CN#allocation-rules');
 assert.equal(assetLegacyTarget('#cashflow-recovery','?lang=zh-CN'),null);
});
