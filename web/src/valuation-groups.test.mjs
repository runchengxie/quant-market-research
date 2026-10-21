import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';

function study() {
  const path = new URL('../public/data/grouped_valuation_draft.json', import.meta.url);
  assert.ok(existsSync(path), 'grouped valuation aggregate has not been prepared');
  return JSON.parse(readFileSync(path, 'utf8'));
}

test('draft retains the baseline, separates unknown states and carries revision warnings', () => {
  const data = study();
  assert.equal(data.original_baseline_reproduced, true);
  assert.equal(data.panel_records, 556948);
  assert.equal(data.formation_count, 130);
  assert.equal(data.financial_revision_safe, false);
  assert.equal(data.st_revision_safe, false);
  assert.equal(data.executable_returns_certified, false);
  assert.deepEqual(data.groups, ['all_market', 'non_st', 'st', 'star_st', 'unknown']);
  for (const row of data.coverage) {
    assert.equal(row.non_st_n + row.st_n + row.star_st_n + row.unknown_n, row.quoted_n);
  }
});

test('public projection contains complete aggregate keys but no private security or denominator rows', () => {
  const data = study();
  const banned = new Set(['ts_code', 'name', 'denominator', 'market_value', 'minimum_records', 'tail_records', '_source_retrieved_at']);
  const visit = (value) => {
    if (Array.isArray(value)) return value.forEach(visit);
    if (value && typeof value === 'object') for (const [key, next] of Object.entries(value)) {
      assert.ok(!banned.has(key), `private field ${key} in public projection`);
      visit(next);
    }
  };
  visit(data);
  assert.ok(!JSON.stringify(data).includes('/home/'));
  assert.equal(data.distributions.length, 130 * 5 * 5 * 2);
  for (const row of data.distributions) {
    assert.ok(row.valid_n <= row.total_n);
    if (row.valid_n) {
      assert.ok(row.minimum > 0 && row.ratio_of_totals > 0 && row.equal_weight_mean > 0);
      assert.ok(row.minimum <= row.p01 && row.p01 <= row.median && row.median <= row.maximum);
    } else assert.equal(row.minimum, null);
  }
});

test('factor costs use identical observed months and increase monotonically with the stated rate', () => {
  const data = study();
  assert.equal(data.factor_summaries.length, 20);
  for (const factor of data.factor_summaries) {
    assert.ok(factor.ic_months <= factor.attempted_months);
    if (factor.mean_rank_ic != null) assert.ok(Math.abs(factor.mean_rank_ic) <= 1);
    for (const q of factor.quintiles) {
      const [zero, ten, thirty] = ['0', '10', '30'].map(k => q.cost_sensitivity[k]);
      assert.equal(zero.months, ten.months);
      assert.equal(ten.months, thirty.months);
      if (zero.months) {
        assert.ok(zero.mean_monthly_return >= ten.mean_monthly_return);
        assert.ok(ten.mean_monthly_return >= thirty.mean_monthly_return);
      }
    }
  }
});
