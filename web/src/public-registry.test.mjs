import test from 'node:test';
import assert from 'node:assert/strict';
import { publicDocs, publicPages, validateRegistry } from './content/public-registry.ts';

test('only eight reviewed documents are admissible', () => {
  assert.equal(publicDocs.length, 8);
  assert.equal(publicDocs.filter((d) => d.route === '/docs/').length, 1);
  assert.ok(publicDocs.every((d) => !/superpowers|runbooks/.test(d.source)));
  assert.doesNotThrow(() => validateRegistry(publicPages, publicDocs));
  assert.throws(() => validateRegistry([...publicPages, publicPages[0]], publicDocs), /duplicate/i);
  assert.throws(() => validateRegistry(publicPages, [{ ...publicDocs[0], source: '../private.md' }]), /source|allowlist/i);
  assert.throws(() => validateRegistry([{ ...publicPages[0], related: [], snapshotKeys: ['private.file'] }], []), /snapshotKey/i);
  assert.throws(() => validateRegistry(publicPages, [{ ...publicDocs[0], slug: '/escape' }]), /slug/i);
});
