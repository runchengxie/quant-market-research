import test from 'node:test';
import assert from 'node:assert/strict';
import { buildSearchRecords } from './content/search-records.server.ts';
import { readPublicDocuments } from './content/public-docs-loader.ts';
import { searchRecords } from './lib/search.ts';
import { resolve } from 'node:path';

test('public search retains a bounded Unicode excerpt for every method and respects the size budget', async () => {
  const records = await buildSearchRecords();
  const methods = records.filter(record => record.kind === 'method');
  assert.equal(methods.length, 36);
  for (const record of methods) {
    assert.ok(record.text.length > 0);
    assert.ok(Array.from(record.text).length <= 1200);
    // SearchResults falls back to text; no duplicate English body is necessary.
    assert.equal(record.textEn, undefined);
  }
  assert.ok(records.some(record => record.id === 'valuation-panel'));
  assert.ok(Buffer.byteLength(JSON.stringify(records), 'utf8') <= 250 * 1024);
});


test('method index excerpts preserve complete documents and exclude text after 1200 characters', async () => {
  const documents = await readPublicDocuments(resolve(process.cwd(), '..'));
  const records = await buildSearchRecords();
  for (const document of documents) {
    const record = records.find(row => row.id === document.meta.id);
    assert.equal(record.text, Array.from(document.body).slice(0, 1200).join(''));
  }
  const long = documents.find(row => Array.from(row.body).length > 1200);
  assert.ok(long);
  assert.ok(Array.from(long.body).length > Array.from(records.find(row => row.id === long.meta.id).text).length);
  const excerpt = { ...records.find(row => row.id === long.meta.id), text: 'x'.repeat(250) + ' suspension evidence ' + 'x'.repeat(1500) + ' afterexcerptmarker' };
  excerpt.text = Array.from(excerpt.text).slice(0, 1200).join('');
  assert.deepEqual(searchRecords([excerpt], 'suspension evidence'), [excerpt]);
  assert.deepEqual(searchRecords([excerpt], 'afterexcerptmarker'), []);
});
