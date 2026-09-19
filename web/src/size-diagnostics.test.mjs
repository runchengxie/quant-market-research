import test from 'node:test';
import assert from 'node:assert/strict';
import { buildSync } from 'esbuild';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

// Load the actual shared module with Astro's base URL supplied, without a browser.
const output = buildSync({
  stdin: { contents: `export * from './components/react/research-shared'; export {createElement, Suspense} from 'react'; export {renderToStaticMarkup, renderToString} from 'react-dom/server';`, resolveDir: fileURLToPath(new URL('.', import.meta.url)) },
  bundle: true, packages: 'external', platform: 'node', format: 'cjs', write: false,
  define: { 'import.meta.env': '{"BASE_URL":"/"}' },
});
const loaded = { exports: {} };
new Function('require', 'module', 'exports', output.outputFiles[0].text)(createRequire(import.meta.url), loaded, loaded.exports);
const shared = loaded.exports;
const { aggregateSizeRows, summarizeSizePeriods, average, createElement: h, renderToStaticMarkup: render } = shared;
const row = (date, bucket, value, extra = {}) => ({ formation_date: date, bucket, forward_return: value, ...extra });

test('lazy chart wrappers preserve surrounding content while their module is loading', () => {
  for (const [Component, props] of [
    [shared.BarChart, {rows:[{bucket:'Q1',value:'0'}],labelKey:'bucket',valueKey:'value'}],
    [shared.LineChart, {series:[{name:'sample',values:[0],color:'#123456'}],labels:['2025-01-01']}],
  ]) {
    let html;
    assert.doesNotThrow(() => { html=render(h('section',null,h('h2',null,'Research remains visible'),h(Component,props))); });
    assert.match(html, /Research remains visible/);
    assert.match(html, /role="status"/);
    assert.match(html, /图表/);
  }
});

test('blank/nonfinite returns never contribute artificial zero observations', () => {
  const result = aggregateSizeRows([row('2025-01-01', 'Q1', ''), row('2025-01-02', 'Q1', ' '), row('2025-01-03', 'Q1', '0.2'), row('2025-01-04', 'Q2', 'Infinity')], 'month');
  assert.deepEqual(result, [{period: '2025-01', bucket: 'Q1', value: .2}]);
  assert.ok(Number.isNaN(average([])));
  assert.equal(aggregateSizeRows([row('2025-01-01', 'Q1', '0')], 'month')[0].value, 0);
});

test('periods and buckets sort chronologically and numerically without mutating rows', () => {
  const rows = [row('2025-02-01','Q10','.1'), row('2025-01-03','Q10','.2'), row('2025-01-02','Q2','.3'), row('2025-01-01','Q1','.4')];
  const saved = structuredClone(rows);
  assert.deepEqual(aggregateSizeRows(rows, 'month').map(r => [r.period,r.bucket]), [['2025-01','Q1'], ['2025-01','Q2'], ['2025-01','Q10'], ['2025-02','Q10']]);
  assert.deepEqual(rows, saved);
});

test('tail means and spreads use only common formation dates', () => {
  const rows = [row('2025-01-01','Q1','.9'), row('2025-01-01','Q10',''), row('2025-01-02','Q1','.3'), row('2025-01-02','Q10','.1'), row('2025-01-03','Q1',''), row('2025-01-03','Q10','-.7')];
  const [summary] = summarizeSizePeriods(rows, 'month');
  assert.equal(summary.q1, .3);
  assert.equal(summary.q10, .1);
  assert.ok(Math.abs(summary.spread - .2) < 1e-12);
  assert.equal(summary.pairedDates, 1);
});

test('known incomplete coverage is excluded, while legacy rows remain usable without a verified claim', () => {
  const bad = [
    {formation_count:'10',observed_count:'9',missing_count:'1',coverage_ratio:'.9'},
    {count:'10',observed_count:'9'}, {missing_count:'1'}, {coverage_ratio:'.8'},
    {formation_count:'10',observed_count:''}, {formation_count:'0',observed_count:'0'},
  ];
  for (const extra of bad) {
    const rows = [row('2025-01-01','Q1','.9',extra), row('2025-01-01','Q10','.1'), row('2025-01-02','Q1','.3'), row('2025-01-02','Q10','.1')];
    assert.equal(aggregateSizeRows(rows,'month').find(r => r.bucket === 'Q1').value, .3);
    assert.equal(summarizeSizePeriods(rows,'stage')[0].pairedDates, 1);
  }
});

test('unpaired periods stay visible with missing spreads, never fake zero', () => {
  const [summary] = summarizeSizePeriods([row('2025-01-01','Q1','.2'),row('2025-01-02','Q10','.1')], 'month');
  assert.ok(Number.isNaN(summary.spread));
  assert.ok(Number.isNaN(summary.q1));
  assert.equal(summary.pairedDates, 0);
});

test('formation contract rejects partial and inconsistent return coverage without falling back to observed-only means', async () => {
  const {dailySizeCurve}=await import('./lib/size-diagnostics.ts');
  const complete={count:'10',observed_return_count:'10',missing_return_count:'0',return_coverage:'1',requested_quantiles:'10'};
  const incomplete=[
    {count:'10',observed_return_count:'9'}, {missing_return_count:'1'}, {return_coverage:'.9'},
    {count:'10',observed_return_count:'11'}, {observed_return_count:''}, {return_coverage:''},
    {missing_return_count:'-1'}, {return_coverage:'1.1'},
  ];
  for(const coverage of incomplete) {
    const rows=[row('2025-01-01','Q1','.9',coverage),row('2025-01-01','Q10','.1',complete),row('2025-01-02','Q1','.3',complete),row('2025-01-02','Q10','.1',complete)];
    assert.equal(dailySizeCurve(rows)[0].value,'0.3');
    assert.equal(summarizeSizePeriods(rows,'month')[0].pairedDates,1);
  }
  const nullRows=[row('2025-01-01','Q1',null,{...complete,observed_only_mean_forward_return:'.8'})];
  assert.deepEqual(dailySizeCurve(nullRows),[{bucket:'Q1',value:''}]);
  assert.equal(aggregateSizeRows(nullRows,'month').length,0);
});

test('monthly curve remains equal weighted across months with unequal daily counts', () => {
  const rows = [row('2025-01-01','Q1','0'),row('2025-01-02','Q1','0'),row('2025-02-01','Q1','.6')];
  const monthly = aggregateSizeRows(rows,'month');
  assert.equal(average(monthly.map(r => r.value)), .3);
});

test('daily curve excludes missing and incomplete values, preserves zero and orders buckets numerically', async () => {
  const helpers = await import('./lib/size-diagnostics.ts').catch(() => ({}));
  assert.equal(typeof helpers.dailySizeCurve, 'function');
  const rows = [row('2025-01-01','Q10','.4'),row('2025-01-01','Q2',''),row('2025-01-02','Q2','0'),row('2025-01-01','Q1','.2'),row('2025-01-02','Q1','.4'),row('2025-01-03','Q1','.9',{count:'10',observed_count:'9'}),row('2025-01-01','Q3','')];
  const curve=helpers.dailySizeCurve(rows);
  assert.deepEqual(curve.map(r=>r.bucket), ['Q1','Q2','Q3','Q10']);
  assert.ok(Math.abs(Number(curve[0].value)-.3)<1e-12);
  assert.deepEqual(curve.slice(1),[{bucket:'Q2',value:'0'},{bucket:'Q3',value:''},{bucket:'Q10',value:'0.4'}]);
});

test('date range is sorted and does not use input row order; period boundaries are explicit', async () => {
  const helpers = await import('./lib/size-diagnostics.ts').catch(() => ({}));
  assert.equal(typeof helpers.sizeDateRange,'function');
  assert.deepEqual(helpers.sizeDateRange([row('2025-03-01','Q1','0'),row('2025-01-01','Q1','0'),row('2025-02-01','Q1','0')]),{start:'2025-01-01',end:'2025-03-01'});
  assert.deepEqual(helpers.sizeDateRange([]),{start:null,end:null});
  assert.deepEqual(['2019-12-31','2020-01-01','2024-12-31','2025-01-01'].map(helpers.stageForDate), ['2015–2019','2020–2024','2020–2024','2025–当前']);
});

test('table missing percentages remain missing and real zero is displayed', () => {
  for (const Component of [shared.SimpleTable, shared.SortableTable]) {
    const html = render(h(Component,{rows:[{value:' '},{value:''},{value:'0'}],columns:[['value','Return']],percentColumns:['value']}));
    assert.equal((html.match(/未提供/g) ?? []).length, 2);
    assert.equal((html.match(/0\.0%/g) ?? []).length, 1);
  }
});

test('sortable tables expose sort direction, a bounded page, its range and navigation', () => {
  const html = render(h(shared.SortableTable,{rows:Array.from({length:55},(_,i)=>({value:String(i)})),columns:[['value','Value'],['other','Other']]}));
  assert.match(html, /aria-sort="descending"/);
  assert.match(html, /aria-sort="none"/);
  assert.equal((html.match(/<tr/g) ?? []).length, 51);
  assert.match(html.replace(/<[^>]*>/g,''), /1–50 \/ 55/);
  assert.match(html, /aria-label="下一页"/);
  assert.match(html, /aria-label="上一页"[^>]*disabled/);
  assert.match(html, /aria-label="最后一页"/);
});

test('large tables render only 50 data rows and report all 28380 records', () => {
  const html=render(h(shared.SortableTable,{rows:Array.from({length:28380},(_,i)=>({value:String(i)})),columns:[['value','Value']]}));
  assert.equal((html.match(/<tr/g) ?? []).length,51);
  assert.match(html.replace(/<[^>]*>/g,''), /1–50 \/ 28380/);
});

test('empty tables report a zero range without enabled navigation', () => {
  const html=render(h(shared.SortableTable,{rows:[],columns:[['value','Value']]}));
  assert.match(html.replace(/<[^>]*>/g,''), /0–0 \/ 0/);
  assert.doesNotMatch(html, /aria-label="下一页"(?![^>]*disabled)/);
});

test('resource state distinguishes error, loading, empty and ready with labeled retry', () => {
  assert.equal(typeof shared.ResourceState, 'function');
  const error = render(h(shared.ResourceState,{error:'HTTP 503',loading:false,retry:()=>{},label:'Size data'}));
  assert.match(error, /role="alert"/);
  assert.match(error, /HTTP 503/);
  assert.match(error, /<button[^>]*aria-label="[^"]*Size data/);
  assert.match(render(h(shared.ResourceState,{loading:true})), /role="status"/);
  assert.match(render(h(shared.ResourceState,{empty:true})), /暂无/);
  assert.equal(render(h(shared.ResourceState,{})), '');
});
