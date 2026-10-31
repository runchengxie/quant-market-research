import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { validateAssetRelease } from '../scripts/validate-asset-release.mjs';

test('asset release rejects changed evidence or protocol before building', () => {
  const bytes = Buffer.from('{}');
  const manifest = { schema_version: 1, files: Object.fromEntries(['first', 'followup', 'closure', 'protocol'].map(name => [name, createHash('sha256').update(bytes).digest('hex')])) };
  assert.equal(validateAssetRelease(() => bytes, manifest), true);
  assert.throws(() => validateAssetRelease(path => path === 'protocol' ? Buffer.from('{"admitted":true}') : bytes, manifest), /Unreviewed asset release/);
});
