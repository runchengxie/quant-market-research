import test from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
import { resolveDocLink } from './content/rehype-public-docs.ts';
import { readPublicDocuments } from './content/public-docs-loader.ts';

test('public markdown links keep the Pages base and encoded anchors', () => {
  assert.equal(resolveDocLink('docs/index.md', 'research/factors/microcap.md#先看风险', '/quant-market-research'), '/quant-market-research/docs/research/factors/microcap/#先看风险');
  assert.throws(() => resolveDocLink('docs/index.md', 'superpowers/specs/internal.md', '/'), /public|allowlist/i);
  assert.throws(() => resolveDocLink('docs/index.md', '../../private.md', '/'), /outside|public/i);
});

test('reader only opens the explicit public document allowlist', async () => {
  const repoRoot = resolve(fileURLToPath(new URL('../..', import.meta.url)));
  const docs = await readPublicDocuments(repoRoot);
  assert.equal(docs.length, 7);
  assert.ok(docs.every((doc) => !doc.body.includes('INTERNAL_ONLY_SENTINEL')));
});
