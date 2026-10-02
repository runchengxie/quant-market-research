import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const read = path => readFileSync(new URL(path, import.meta.url), 'utf8');
test('shared research layout places conclusion before topic content and method', () => {
 const source = read('./components/ResearchPage.astro');
 assert.ok(source.indexOf('class="research-verdict"') > 0);
 assert.ok(source.indexOf('class="research-verdict"') < source.indexOf('<TopicNav'));
 assert.ok(source.indexOf('<div id="topic-content">') < source.indexOf('<details id="research-method"'));
});
test('microcap experiment methods follow the interactive evidence', () => {
 const source = read('./pages/research/microcap/index.astro');
 assert.ok(source.indexOf('<MicrocapPage') < source.indexOf('<MicrocapMethod'));
});
