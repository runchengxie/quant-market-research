import test from 'node:test';
import assert from 'node:assert/strict';
import { ResearchBarChart } from './components/ResearchCharts.tsx';

test('English bar charts keep absent values missing and retain actual zero returns', () => {
  const chart = ResearchBarChart({rows: ['', ' ', null, undefined, 'NaN', '0', '-0.2'].map(value => ({value, label: 'sample'})), labelKey: 'label', valueKey: 'value'});
  assert.deepEqual(chart.props.option.series[0].data, [null, null, null, null, null, 0, -.2]);
  assert.equal(chart.props.option.tooltip.valueFormatter(null), 'Not reported');
  assert.equal(chart.props.option.tooltip.valueFormatter(0), '0.0%');
});

test('bar chart describes all dates and values without relying on color or canvas', () => {
  const chart = ResearchBarChart({ rows: [{year: '2025', value: '-0.1'}, {year: '2026', value: ''}], labelKey: 'year', valueKey: 'value' });
  assert.match(chart.props.description, /2025.*-10.0%/);
  assert.match(chart.props.description, /2026.*Not reported/);
  assert.equal(chart.props.option.yAxis.axisLabel.interval, 0);
});

test('Chinese bar charts retain localized missing values and descriptions', () => {
  const previousDocument = globalThis.document;
  globalThis.document = {documentElement: {lang: 'zh-CN'}};
  try {
    const chart = ResearchBarChart({rows: [{year: '2026', value: ''}], labelKey: 'year', valueKey: 'value'});
    assert.equal(chart.props.option.tooltip.valueFormatter(null), '未提供');
    assert.match(chart.props.description, /2026：未提供/);
  } finally {
    if (previousDocument === undefined) delete globalThis.document;
    else globalThis.document = previousDocument;
  }
});
