import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { publicPages } from './content/public-registry.ts';

test('ETF and hotspot studies are discoverable without performance claims', async () => {
  for (const id of ['etf-rotation', 'hotsector']) {
    const page = publicPages.find((entry) => entry.id === id);
    assert.ok(page, `missing study ${id}`);
    assert.equal(page.route, `/research/${id}/`);
    const source = await readFile(new URL(`./pages/research/${id}/index.astro`, import.meta.url), 'utf8');
    assert.match(source, /LegacyStrategyStudy/);
  }
});

import { createHash } from 'node:crypto';
import { validateLegacyStudyEvidence } from './content/legacy-strategy-evidence.server.ts';

test('source and content review reject stale or edited evidence', async () => {
  const raw = await readFile(new URL('../public/data/legacy-strategy-evidence.json', import.meta.url));
  const value = JSON.parse(raw);
  const review = JSON.parse(await readFile(new URL('../public/data/legacy-strategy-review.json', import.meta.url), 'utf8'));
  assert.equal(createHash('sha256').update(raw).digest('hex'), review.asset_sha256);
  assert.doesNotThrow(() => validateLegacyStudyEvidence(value, review));
  assert.throws(() => validateLegacyStudyEvidence(value, { ...review, source_sha256: '0'.repeat(64) }), /review/i);
  value.studies[0].conclusion = 'An unsupported edited claim';
  assert.throws(() => validateLegacyStudyEvidence(value, review), /content/i);
});

test('build admission rejects unknown public envelope fields', () => {
  const asset = validateLegacyStudyEvidence();
  assert.throws(() => validateLegacyStudyEvidence({ ...asset, private_locator: 'unreviewed' }), /field|asset/i);
});
