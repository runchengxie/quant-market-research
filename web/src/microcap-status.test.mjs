import test from 'node:test';
import assert from 'node:assert/strict';
import { statusRows, statusMarkdown } from './content/microcap-status.ts';
import { buildMicrocapReport } from './content/microcap-report.server.ts';
for (const locale of ['en-US','zh-CN']) {
 test(`six ${locale} status rows preserve open claims and report parity`,async()=>{
  const rows=statusRows(locale);
  assert.deepEqual(rows.map(row=>row.id),['MC-C01','MC-C02','MC-C03','MC-C04','MC-C05','MC-C06']);
  for(const row of rows){assert.equal(row.cells.length,4);assert.ok(row.href.startsWith('#microcap-'));}
  const section=statusMarkdown(locale);
  assert.ok((await buildMicrocapReport(locale)).markdown.includes(section));
  assert.doesNotMatch(section,/undefined|NaN|\/home\/|artifacts\//);
  if(locale==='en-US'){
   assert.doesNotMatch(section,/[\u3400-\u9fff]/);
   assert.match(section,/remains unrecovered/);
   assert.match(section,/completed months remain zero/);
   assert.match(section,/capacity is not established/);
  }else{
   assert.match(section,/原始运行仍未找回/);
   assert.match(section,/已完成月份仍为零/);
   assert.match(section,/可执行容量尚未确立/);
  }
 });
}
