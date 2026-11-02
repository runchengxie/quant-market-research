import test from 'node:test';import assert from 'node:assert/strict';
import {readingSummaries} from './content/research-reading.server.ts';
import {libraryGroups} from './content/research-library.ts';
test('every directory topic has a complete source-backed reading summary',()=>{
 for(const id of libraryGroups.flatMap(g=>g.topics)){const r=readingSummaries.find(r=>r.id===id);assert.ok(r,id);assert.ok(r.sources.length,id);assert.ok(r.coverage[1]);}
});
