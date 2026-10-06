import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { publicDocs, publicPages, validateRegistry } from './content/public-registry.ts';

test('the reviewed English and Chinese documents are admissible', () => {
  assert.equal(publicDocs.length, 18);
  assert.equal(publicDocs.filter((d) => d.route === '/docs/').length, 1);
  assert.ok(publicDocs.every((d) => !/superpowers|runbooks/.test(d.source)));
  assert.doesNotThrow(() => validateRegistry(publicPages, publicDocs));
  assert.throws(() => validateRegistry([...publicPages, publicPages[0]], publicDocs), /duplicate/i);
  assert.throws(() => validateRegistry(publicPages, [{ ...publicDocs[0], source: '../private.md' }]), /source|allowlist/i);
  assert.throws(() => validateRegistry([{ ...publicPages[0], related: [], snapshotKeys: ['private.file'] }], []), /snapshotKey/i);
  assert.throws(() => validateRegistry(publicPages, [{ ...publicDocs[0], slug: '/escape' }]), /slug/i);
});

test('every published English document has a reciprocal Chinese Astro route', async () => {
  const root = resolve(fileURLToPath(new URL('../..', import.meta.url)));
  const documents = await Promise.all(publicDocs.map(async (meta) => ({
    meta,
    body: await readFile(resolve(root, meta.source), 'utf8'),
  })));
  const byId = new Map(documents.map((doc) => [doc.meta.id, doc]));
  const english = documents.filter(({ meta }) => !meta.id.endsWith('-zh-CN'));
  const chinese = documents.filter(({ meta }) => meta.id.endsWith('-zh-CN'));

  assert.equal(english.length, chinese.length);
  for (const { meta, body } of english) {
    const translated = byId.get(`${meta.id}-zh-CN`);
    assert.ok(translated, `missing Chinese companion for ${meta.source}`);
    assert.ok(meta.route.startsWith('/docs/'));
    assert.ok(translated.meta.route.startsWith('/docs/'));
    assert.ok(body.includes(translated.meta.source.split('/').at(-1)), `${meta.source} must link to Chinese`);
    assert.ok(translated.body.includes(meta.source.split('/').at(-1)), `${translated.meta.source} must link to English`);
  }
});
