import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { publicPages } from './content/public-registry.ts';

test('ETF and hotspot studies are discoverable with diagnostic evidence labels', async () => {
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
import { legacyStudyCopy } from './content/legacy-strategy-copy.ts';

test('rendered evidence claims follow the reviewed asset and stale translations fail closed', () => {
  const asset = validateLegacyStudyEvidence();
  const study = { ...asset.studies[0], conclusion: 'A newly reviewed conclusion',
    limitations: ['One material limitation', 'A second limitation'] };
  const copy = legacyStudyCopy(study, asset.reviewed_content_digest);
  assert.match(copy.conclusion[0], /25 bps/);
  assert.equal(copy.baseline[0], study.baseline);
  assert.equal(copy.scope[0], study.sample_scope);
  assert.equal(copy.limitations[0], 'One material limitation A second limitation');
  assert.throws(() => legacyStudyCopy(study, '0'.repeat(64)), /translation.*review/i);
  assert.equal(asset.studies[0].metrics.length, 66);
  assert.equal(asset.studies[1].metrics.length, 6);
  assert.equal(asset.studies[1].metrics[0].unit, 'percentage_points');
  assert.ok(asset.studies[1].metrics.every(metric => !/2025-\d\d-\d\d/.test(metric.name)));
  for (const cost of [0, 10, 25, 50]) {
    for (const valuation of ['raw', 'factor_adjusted']) {
      assert.ok(asset.studies[0].metrics.some(metric => metric.name === `etf.cumulative_return.${valuation}.lightgbm_regression.cost_${cost}_bps`));
    }
  }
  assert.doesNotMatch(JSON.stringify(asset.studies), /510300|\/home\/|\/tmp\//);
});

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

test('public metrics reject edited or malformed public payloads', () => {
  const asset = validateLegacyStudyEvidence();
  const metric = asset.studies[0].metrics[0];
  for (const unsafe of [
    { ...metric, name: 'etf.cumulative_return.000001' },
    { ...metric, definition: 'Local source at /home/private/data.csv' },
    { ...metric, value: Number.NaN },
    { ...metric, extra: 'unreviewed' },
  ]) {
    const studies = structuredClone(asset.studies);
    studies[0].metrics[0] = unsafe;
    const changed = { ...asset, studies };
    assert.throws(() => validateLegacyStudyEvidence(changed), /digest|metric|review/i);
  }
});
