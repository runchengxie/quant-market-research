import test from 'node:test';
import assert from 'node:assert/strict';
import { baseChartOptions, chartLabel } from './lib/chart-presentation.ts';

test('missing is not zero and reduced motion is honored', () => {
  assert.equal(chartLabel(null, 'percent'), '未提供');
  assert.equal(chartLabel(0, 'percent'), '0.0%');
  assert.equal(chartLabel(-0.02, 'percent'), '-2.0%');
  const option = baseChartOptions({ axis: '#526174', grid: '#d5dde7', label: '#162233', tooltip: '#ffffff' }, true);
  assert.equal(option.animation, false);
  assert.equal(option.textStyle.fontSize, 12);
});
