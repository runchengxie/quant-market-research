import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { annualValuations, positiveSegments, buildTopicEvidence } from './lib/valuation-topic.ts';

const row = (date, minimum, extra = {}) => ({ formation_date: date, group: 'non_st', metric: 'pb_parent', sample_basis: 'metric_available', minimum, p01: minimum == null ? null : minimum + .1, p05: minimum == null ? null : minimum + .2, valid_n: minimum == null ? 0 : 100, total_n: 120, nonpositive_denominator_n: 5, missing_or_invalid_n: minimum == null ? 115 : 15, ...extra });

test('annual last snapshot stays separate from sampled extremes and keeps support at the extreme', () => {
  const result = annualValuations([row('20240628', .14, { valid_n: 80 }), row('20241231', .25), row('20261016', .22), row('20241231', .01, { group: 'unknown' })], 'non_st', 'pb_parent');
  assert.deepEqual(result.map(r => r.formation_date), ['20241231', '20261016']);
  assert.equal(result[0].minimum, .25);
  assert.equal(result[0].p01, .35);
  assert.equal(result[0].sampled_minimum, .14);
  assert.deepEqual(result[0].sampled_dates, ['20240628']);
  assert.deepEqual(result[0].sampled_valid_n, [80]);
});

test('annual ties preserve every observed date and unavailable values never become zero', () => {
  const result = annualValuations([row('20240131', .2), row('20240628', .2), row('20241231', null), row('20251231', null)], 'non_st', 'pb_parent');
  assert.deepEqual(result[0].sampled_dates, ['20240131', '20240628']);
  assert.equal(result[0].minimum, null);
  assert.equal(result[1].sampled_minimum, null);
  assert.deepEqual(positiveSegments(result, 'minimum'), []);
  assert.throws(() => annualValuations([row('20241231', .2), row('20241231', .3)], 'non_st', 'pb_parent'), /duplicate/);
});

test('chart segments stop at missing years rather than joining across gaps', () => {
  const rows = [row('20221230', .3), row('20231229', null), row('20241231', .2)];
  assert.deepEqual(positiveSegments(rows, 'minimum').map(s => s.map(p => p.index)), [[0], [2]]);
});

test('annual published numbers retain the audited year-end and partial latest dates', () => {
  const data = JSON.parse(readFileSync(new URL('../public/data/grouped_valuation_draft.json', import.meta.url), 'utf8'));
  const pb = annualValuations(data.distributions, 'non_st', 'pb_parent');
  const deducted = annualValuations(data.distributions, 'non_st', 'pe_deducted_proxy');
  assert.equal(pb.length, 11);
  assert.equal(pb[0].formation_date, '20161230');
  assert.equal(pb.at(-1).formation_date, '20261016');
  assert.equal(pb.find(r => r.year === '2024').minimum, 0.25521141338579195);
  assert.equal(pb.find(r => r.year === '2024').sampled_minimum, 0.14306980529979);
  assert.deepEqual(pb.find(r => r.year === '2024').sampled_dates, ['20240628']);
  assert.equal(deducted.at(-1).valid_n, 3646);
  assert.equal(deducted.at(-1).p05, 11.343526550883519);
});

test('topic evidence uses the published historical version and mutually exclusive gap counts', () => {
  const data = JSON.parse(readFileSync(new URL('../public/data/low_valuation_topic_reviewed.json', import.meta.url), 'utf8'));
  assert.equal(data.legacy.source, 'style-factors/weekly-20260904');
  assert.equal(data.legacy.start, '20080201');
  assert.equal(data.legacy.end, '20260904');
  assert.equal(data.legacy.days, 4518);
  assert.equal(data.legacy.missing_holding_return, 'zero');
  assert.equal(data.early_coverage.available, 10);
  assert.equal(data.early_coverage.quoted, 2558);
  assert.equal(data.ranking.common_n, 1743);
  for (const group of data.gaps) {
    assert.equal(group.group, 'all_market');
    assert.equal(group.reasons.reduce((s, r) => s + r.count, 0), group.unresolved);
  }
  assert.deepEqual(data.gaps.map(g => [g.metric, g.unresolved]), [['pb_parent', 4560], ['pe_deducted_proxy', 2160]]);
  const banned = /"(?:ts_code|securities|denominator|market_value|name|private_path)"|\d{6}\.(?:SZ|SH|BJ)|\/home\//;
  assert.ok(!banned.test(JSON.stringify(data)));
});

test('gap preparation rejects mismatched totals rather than disguising missing results', () => {
  const read = path => JSON.parse(readFileSync(new URL('../public/data/' + path, import.meta.url), 'utf8'));
  const topic = read('low_valuation_topic_reviewed.json');
  const audit = {
    exclusive_reasons: topic.gaps.flatMap(g => [{ metric: g.metric, reason: 'resolved', n: g.resolved }, ...g.reasons.map(r => ({ metric: g.metric, reason: r.reason, n: r.count }))]),
    basket_support: topic.gaps.flatMap(g => g.minimum_missing_by_quintile.map((n, i) => ({ metric: g.metric, quintile: i + 1, attempted_months: 36, minimum_unresolved_members: n, complete_months: 0 }))),
  };
  audit.exclusive_reasons[0].n -= 1;
  assert.throws(() => buildTopicEvidence(read('valuation_panel_reviewed.json'), read('barra/historical_factor_summary.json'), read('barra/barra_source_manifest.json'), audit), /gap totals/);
});
