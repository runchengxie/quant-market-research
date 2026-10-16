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
