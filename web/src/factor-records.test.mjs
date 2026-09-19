import test from 'node:test';
import assert from 'node:assert/strict';
import { readFactorRecords } from './content/factor-records.server.ts';

test('same name never collapses different models', async () => {
  const records = await readFactorRecords();
  const sizes = records.filter((record) => record.factorId === 'size');
  assert.equal(new Set(sizes.map((record) => record.key)).size, 3);
  assert.equal(sizes.find((record) => record.model === 'historical').verification, 'unverified');
  assert.equal(sizes.find((record) => record.model === 'inspected').verification, 'source-inspected');
  assert.equal(sizes.find((record) => record.model === 'core-proxy').verification, 'dictionary-defined');
  const quality = records.find((record) => record.model === 'inspected' && record.factorId === 'quality');
  assert.match(quality.calculation, /8.*财务观测/);
  assert.match(quality.calculation, /至少 4/);
  assert.match(quality.calculation, /不保证.*连续季度/);
  assert.match(quality.calculation, /填 0/);
  assert.match(quality.calculation, /列整体缺失/);
});
