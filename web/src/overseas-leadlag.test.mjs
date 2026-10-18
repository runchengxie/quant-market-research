import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { publicPages, publicDocs } from './content/public-registry.ts';

const data = JSON.parse(readFileSync(new URL('../public/data/overseas_leadlag_reviewed.json', import.meta.url)));
test('overseas publication preserves timing uncertainty and purged annual folds', () => {
  assert.equal(data.timing.historical_pit_certified, false);
  assert.equal(data.timing.historical_retrieval_verified_rows, 0);
  assert.equal(data.timing.future_assumed_inputs, 0);
  assert.equal(data.comparisons.length, 36);
  assert.equal(data.costs.length, 224);
  for (const f of data.folds) {
    assert.ok(Date.parse(f.last_training_label_utc) < Date.parse(f.test_first_decision_utc));
    assert.ok(f.train_n >= 252);
  }
  assert.ok(data.etf_input_quality['512480'].verified_suspension_dates.includes('2021-03-26'));
  assert.equal(data.etf_input_quality.jpy.crossed_quotes_excluded, 1);
});

test('source bars and private predictions are excluded while routes are discoverable', () => {
  assert.ok(publicPages.some(p => p.route === '/research/overseas-leadlag/'));
  assert.equal(publicDocs.filter(p => p.id.startsWith('overseas-leadlag-method')).length, 2);
  const text = JSON.stringify(data);
  assert.doesNotMatch(text, /\/home\/|\/Users\/|\/mnt\/|TUSHARE_TOKEN|private_predictions|bid_close|raw_open/);
  for (const row of data.comparisons) {
    assert.ok(row.n > 0);
    assert.ok(row.mse_gain_ci95[0] <= row.mse_gain_ci95[1]);
    assert.ok(row.augmented_hit >= 0 && row.augmented_hit <= 1);
  }
});
