import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { buildMicrocapReport } from './content/microcap-report.server.ts';

// Zero-collapsed cash, transferred minimum-90 absence or a registered manual
// review would change the evidence and must fail these checks.
for (const locale of ['en-US', 'zh-CN']) {
 test(`chain tables preserve distinct source, inventory and receipt states in ${locale}`, async () => {
  const { primaryTable, traceTable, prospectiveTable } = await import('./content/microcap-chain.ts');
  assert.deepEqual(primaryTable(locale).rows.map(row => row[1]), ['7', '7', '6', '1', '3']);
  assert.deepEqual(traceTable(locale).rows.map(row => row[1]), ['6', '6', '63', '1']);
  const data = JSON.parse(await readFile('public/data/microcap_chain_review.json', 'utf8'));
  const rows = prospectiveTable(locale).rows;
  assert.equal(rows[0][1], data.prospective.actual_review_utc);
  assert.deepEqual(rows.slice(1).map(row => row[1]), ['2', '7', '0', '0']);
 });
 test(`chain ${locale} download shares the catalog and excludes issuer details`, async () => {
  const { chainMarkdown } = await import('./content/microcap-chain.ts');
  const section = chainMarkdown(locale);
  assert.ok((await buildMicrocapReport(locale)).markdown.includes(section));
  assert.doesNotMatch(section, /undefined|NaN|\/home\/|\.worktrees|002729|20211012|cninfo\.com/);
  if (locale === 'en-US') assert.doesNotMatch(section, /[\u3400-\u9fff]/);
 });
}

for (const locale of ['en-US', 'zh-CN']) {
 test(`cash-restart target slice withholds NAV after quantity-contract rejection in ${locale}`, async () => {
  const { targetSliceTable, chainEvidence } = await import('./content/microcap-chain.ts');
  assert.deepEqual(targetSliceTable(locale).rows.slice(0, 7).map(row => row[1]), ['2', '40', '46', '21', '2230', '1', '1']);
  assert.equal(chainEvidence.target_slice.fail_closed, true);
  assert.equal(chainEvidence.target_slice.accepted_nav, false);
  assert.equal(chainEvidence.target_slice.historical_account_recovered, false);
  assert.equal(chainEvidence.target_slice.status, 'blocked_by_sell_quantity_contract');
  assert.equal(targetSliceTable(locale).rows.at(-1)[1], locale === 'zh-CN' ? '暂不接受' : 'Withheld');
 });
}

for (const locale of ['en-US', 'zh-CN']) test(`1.0.7 chain keeps its rejected account and manual receipt as historical evidence in ${locale}`, async () => {
 const { chainCopy, chainMarkdown, chainEvidence } = await import('./content/microcap-chain.ts');
 assert.ok(chainCopy.historicalSnapshot);
 assert.match(chainMarkdown(locale), /1\.0\.7/);
 assert.equal(chainEvidence.reviewed_on, '2026-10-18');
 assert.equal(chainEvidence.target_slice.accepted_nav, false);
 assert.equal(chainEvidence.prospective.new_completed_windows, 0);
});
