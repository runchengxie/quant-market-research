import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { publicPages } from './content/public-registry.ts';

test('one rotation topic owns both retired routes without duplicate directory entries', () => {
  const pages = publicPages.filter(entry => entry.id === 'rotation');
  assert.equal(pages.length, 1);
  assert.equal(pages[0].route, '/research/style-theme-rotation/');
  assert.deepEqual(pages[0].aliases, ['/research/etf-rotation/', '/research/hotsector/']);
  assert.equal(publicPages.filter(entry => ['etf-rotation', 'hotsector'].includes(entry.id)).length, 0);
});

import { createHash } from 'node:crypto';
import { validateLegacyStudyEvidence } from './content/legacy-strategy-evidence.server.ts';
import { legacyStudyCopy } from './content/legacy-strategy-copy.ts';
import { etfAnnualRows, etfSensitivityRows, hotspotSensitivityRows } from './content/legacy-strategy-chart-data.ts';

test('rendered evidence claims follow the reviewed asset and stale translations fail closed', () => {
  const asset = validateLegacyStudyEvidence();
  const study = { ...asset.studies[0], conclusion: 'A newly reviewed conclusion',
    limitations: ['One material limitation', 'A second limitation'] };
  const copy = legacyStudyCopy(study, asset.reviewed_content_digest);
  assert.match(copy.conclusion[0], /25 bps/);
  assert.equal(copy.baseline[0], study.baseline);
  assert.equal(typeof copy.baseline[1], 'string');
  assert.equal(typeof copy.scope[1], 'string');
  assert.equal(typeof copy.limitations[1], 'string');
  assert.doesNotMatch(copy.baseline[1], /Initially|equal-weight/);
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

test('interactive ETF chart data uses only reviewed aggregate values and both price conventions', () => {
  const asset = validateLegacyStudyEvidence();
  const rows = etfSensitivityRows(asset.studies.find(study => study.id === 'etf-rotation'));
  assert.equal(rows.length, 4);
  assert.deepEqual(rows.map(row => row.costBps), [0, 10, 25, 50]);
  assert.deepEqual(Object.keys(rows[0].raw), ['linear_rank', 'lightgbm_regression', 'lightgbm_ranker', 'fixed_share_basket', 'single_etf_baseline']);
  assert.deepEqual(Object.keys(rows[0].adjusted), Object.keys(rows[0].raw));
  assert.equal(Number(rows.find(row => row.costBps === 25).adjusted.lightgbm_regression.toFixed(2)), -8.14);
  assert.equal(Number(rows.find(row => row.costBps === 25).adjusted.fixed_share_basket.toFixed(2)), 1.52);
  assert.deepEqual(etfAnnualRows(asset.studies[0]).map(row => row.year), [2021, 2022, 2023, 2024, 2025]);
  assert.equal(Number(etfAnnualRows(asset.studies[0]).find(row => row.year === 2025).regression.toFixed(2)), 33.81);
});

test('hotspot chart stays aggregate-only and keeps mean uplift separate from event count', () => {
  const asset = validateLegacyStudyEvidence();
  const rows = hotspotSensitivityRows(asset.studies.find(study => study.id === 'hotsector'));
  assert.deepEqual(rows.map(row => [row.costBps, Number(row.meanUpliftPp.toFixed(3)), row.positiveEvents, row.eventCount]), [
    [0, 0.239, 3, 4], [25, 0.239, 3, 4], [50, 0.238, 3, 4],
  ]);
  assert.doesNotMatch(JSON.stringify(rows), /2025-\d\d-\d\d/);
});

test('Barra page presents a labeled current conclusion before the interactive workbench', async () => {
  const page = await readFile(new URL('./pages/research/style-factors-18y/index.astro', import.meta.url), 'utf8');
  assert.match(page, /showConclusion/);
  assert.match(page, /BarraNarrative/);
  assert.match(page, /长期风格研究|style-factor/);
  assert.match(page, /showConclusion/);
  const implementation = await readFile(new URL('./components/ResearchPage.astro', import.meta.url), 'utf8');
  assert.match(implementation, /id="current-conclusion"/);
});

import { selectWeeklyRows } from './content/rotation-research.ts';
test('weekly chart groups keep incompatible portfolio comparisons separate and preserve absent metrics', () => {
  const risk = selectWeeklyRows('risk');
  assert.equal(risk.length, 9);
  assert.deepEqual(risk.find(row => row.id === 'hrp-75'), {
    id: 'hrp-75', group: 'risk', label: ['HRP allocation · 75% risk cap', '层次风险平价 · 风险上限 75%'],
    cagr: 6.70, sharpe: 1.026, drawdown: -8.56, fallback: 64.22, executions: null,
  });
  const holdover = selectWeeklyRows('holdover');
  assert.deepEqual(holdover.map(row => row.executions), [649, 595, 551]);
  assert.ok(holdover.every(row => row.fallback === null));
  assert.equal(selectWeeklyRows('pool').length, 8);
  assert.equal(selectWeeklyRows('score').length, 4);
  assert.ok(selectWeeklyRows('pool').every(row => row.group === 'pool'));
});
