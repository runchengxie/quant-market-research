import test from 'node:test';
import assert from 'node:assert/strict';
import { buildMicrocapReport, buildWindowSvg, readReportSnapshot } from './content/microcap-report.server.ts';

for (const locale of ['en-US', 'zh-CN']) {
  test(`complete ${locale} report preserves published values, boundaries and source appendices`, async () => {
    const { markdown } = await buildMicrocapReport(locale);
    const snapshot = await readReportSnapshot();
    assert.match(markdown, /\n## /);
    for (const row of snapshot.window_sensitivity) {
      assert.ok(markdown.includes(`${row.net_annual_return.toFixed(2)}%`));
      assert.ok(markdown.includes(`${row.net_max_drawdown.toFixed(2)}%`));
    }
    for (const row of snapshot.joint_matrix) assert.ok(markdown.includes(`${row.net_annual_return.toFixed(2)}%`));
    assert.match(markdown, /2026-09-16/);
    assert.match(markdown, /microcap-execution-diagnostic/);
    assert.match(markdown, /https:\/\/runchengxie.github.io\/quant-market-research\/downloads\/microcap-windows/);
    assert.doesNotMatch(markdown, /undefined|\[object Object\]|\/home\/|\/Users\/|\/mnt\//);
    if (locale === 'en-US') assert.doesNotMatch(markdown, /[\u3400-\u9fff]/);
    else {
      assert.match(markdown, /revision_safe=false/);
      assert.match(markdown, /退市现金结算/);
    }
    const svg = await buildWindowSvg(locale);
    assert.match(svg, /<svg/);
    for (const row of snapshot.window_sensitivity) assert.ok(svg.includes(`${row.net_annual_return.toFixed(2)}%`));
  });
}

test('history register preserves research stages and all published table rows with correct units', async () => {
  const { microcapHistory } = await import('./content/microcap-history.ts');
  const { historicalTablesMarkdown } = await import('./content/microcap-history-report.ts');
  assert.equal(microcapHistory.length,34);
  assert.equal(new Set(microcapHistory.map(r=>r.id)).size,34);
  const snapshot=await readReportSnapshot();
  const families=['candidates','anatomy','capacity','rebalance','share_ledger','joint_matrix','window_sensitivity'];
  assert.equal(families.reduce((sum,key)=>sum+snapshot[key].length,0),56);
  for(const locale of ['en-US','zh-CN']) {
    const {markdown}=await buildMicrocapReport(locale);
    for(const record of microcapHistory) assert.ok(markdown.includes(`### ${record.id} · ${record.title[locale==='zh-CN'?1:0]}`));
    const tables=historicalTablesMarkdown(snapshot,locale);
    // Six expanded tables; three window rows are rendered by the report's existing window section.
    const dataRows=tables.split('\n').filter(line=>line.startsWith('| ')&&!line.startsWith('| ---')).length-6;
    assert.equal(dataRows,53);
    for(const row of snapshot.anatomy) assert.ok(tables.includes(`${(row.low_minus_high_return*100).toFixed(2)}%`));
    for(const row of snapshot.candidates) assert.ok(tables.includes(`${row.net_annual_return.toFixed(2)}%`));
    assert.doesNotMatch(tables,/NaN|undefined|artifacts\/runs|configs\/local/);
  }
  const en=(await buildMicrocapReport('en-US')).markdown;
  assert.match(en,/Protocol only/);
  assert.match(en,/One completed month: August 2026/);
  assert.match(en,/stale caveat/);
  assert.match(en,/not 34 independent experiments/);
});
