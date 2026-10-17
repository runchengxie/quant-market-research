import test from 'node:test';
import assert from 'node:assert/strict';
import { nextEvidence as data, nextEvidenceMarkdown, eventTable, readinessTable, caseTable, caseOutcomeTable } from './content/microcap-next-evidence.ts';
import { buildMicrocapReport } from './content/microcap-report.server.ts';

test('reviewed follow-up preserves owner blockers and pending prospective admission',()=>{
 assert.equal(data.raw_share_ready,false);
 assert.equal(data.original_runtime_recovered,false);
 assert.equal(data.events.owner_resolver_recomputed,false);
 assert.deepEqual(data.events.plan_blockers,{'45':83,'90':82});
 assert.equal(Object.values(data.events.priority_counts).reduce((a,b)=>a+b,0),data.events.dated_unique_blockers);
 assert.equal(data.events.retrospective_economic_adjudications+data.events.dated_unresolved,data.events.dated_unique_blockers);
 assert.equal(data.readiness.admitted,false);
 assert.equal(data.readiness.issue_count,7);
 assert.equal(data.initial_readiness.issue_count,8);
 assert.equal(data.calendar.civil_days,61);
 assert.equal(data.calendar.vendor_calendar_mismatches,0);
 assert.equal(data.readiness.new_cohort_completed_windows,0);
});
for(const locale of ['en-US','zh-CN'])test(`latest ${locale} evidence matches downloads and preserves lesson boundaries`,async()=>{
 const section=nextEvidenceMarkdown(locale);
 assert.ok((await buildMicrocapReport(locale)).markdown.includes(section));
 assert.equal(eventTable(locale).rows.length,4);
 assert.equal(readinessTable(locale).rows.length,7);
 assert.equal(caseTable(locale).rows.length,4);
 assert.equal(caseOutcomeTable(locale).rows.length,4);
 for(const value of ['1.2255331','0.3158','0.2650','2025-01-24','2024-07-24','2024-07-02'])assert.ok(section.includes(value));
 assert.doesNotMatch(section,/undefined|NaN|\/home\/|artifacts\//);
 if(locale==='en-US'){
  assert.doesNotMatch(section,/[\u3400-\u9fff]/);
  assert.match(section,/no multi-day unlisted phase is observed/);
  assert.match(section,/do not establish observed intraday payment/);
  assert.match(section,/cannot be filled with zero/);
  assert.match(section,/original 120-session runtime remains unrecovered/);
  assert.match(section,/sellable shares remain unknown/);
  assert.match(section,/earlier receipt is preserved/);
  assert.match(section,/scheduled dates, not observed future sessions/);
 }else{
  assert.match(section,/原解析器未重算/);
  assert.match(section,/不能补零/);
  assert.match(section,/实际价差、盘口深度和成交记录/);
 }
});
