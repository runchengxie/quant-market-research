import test from 'node:test';
import assert from 'node:assert/strict';
import { normalizeQuery, searchRecords } from './lib/search.ts';
const items = [{ id: 'quality', title: '复合质量', kind: 'factor', href: '/quant-market-research/research/style-factors-18y/?factor=quality#barra-factor-detail', text: 'ROE 及盈利稳定性；现行源码，不代表历史公式', aliases: ['quality', '质量'] }];
test('Chinese and English search are normalized and never invent results', () => {
  assert.deepEqual(searchRecords(items, '盈利稳定'), items);
  assert.deepEqual(searchRecords(items, '  QUALITY  '), items);
  assert.deepEqual(searchRecords(items, '不存在的指标'), []);
  assert.deepEqual(searchRecords(items, '   '), []);
  assert.deepEqual(searchRecords(items, '<script>alert(1)</script>'), []);
  assert.equal(normalizeQuery('ＡＢＣ'), 'abc');
});
