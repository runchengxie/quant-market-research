import test from 'node:test';
import assert from 'node:assert/strict';
import { buildSearchRecords } from './content/search-records.server.ts';

test('public search retains every method body once and respects the size budget', async () => {
  const records = await buildSearchRecords();
  const methods = records.filter(record => record.kind === 'method');
  assert.equal(methods.length, 30);
  for (const record of methods) {
    assert.ok(record.text.length > 0);
    // SearchResults falls back to text; no duplicate English body is necessary.
    assert.equal(record.textEn, undefined);
  }
  assert.ok(records.some(record => record.id === 'valuation-panel'));
  assert.ok(Buffer.byteLength(JSON.stringify(records), 'utf8') <= 250 * 1024);
});
