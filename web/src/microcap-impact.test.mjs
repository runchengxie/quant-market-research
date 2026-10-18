import test from 'node:test';
import assert from 'node:assert/strict';
import { impactTable, stressTable, accountTable, registerTable, impactMarkdown } from './content/microcap-impact.ts';
import { buildMicrocapReport } from './content/microcap-report.server.ts';

for (const locale of ['en-US','zh-CN']) {
 test(`impact tables retain unknown inventory and correct NAV stress units in ${locale}`,()=>{
  const rows=impactTable(locale).rows;
  assert.equal(rows.length,6);
  assert.deepEqual(rows[2].slice(1),['7','0','81','6']);
  assert.deepEqual(rows[3].slice(1),['6','0','82','6']);
  const stress=stressTable(locale).rows;
  assert.equal(stress.length,2);
  assert.equal(stress[0].at(-1),'0.15–0.26');
  assert.equal(stress[1].at(-1),'0.21–0.26');
  assert.equal(accountTable(locale).rows.length,4);
  assert.equal(registerTable(locale).rows.length,2);
 });
 test(`impact download reuses the reviewed ${locale} section without private data`,async()=>{
  const section=impactMarkdown(locale);
  assert.ok((await buildMicrocapReport(locale)).markdown.includes(section));
  assert.doesNotMatch(section,/undefined|NaN|\/home\/|PRIVATE|002729|20211012/);
  if(locale==='en-US')assert.doesNotMatch(section,/[\u3400-\u9fff]/);
 });
}
