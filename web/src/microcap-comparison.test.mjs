import test from 'node:test';
import assert from 'node:assert/strict';
import { readExclusionReview, comparisonTables, comparisonMarkdown, buildExclusionSvg } from './content/microcap-comparison.server.ts';
const data=await readExclusionReview(), candidates=['small_cap','low_turnover','composite'];
const near=(a,b)=>assert.ok(Math.abs(a-b)<1e-9,`${a} differs from ${b}`);
test('reviewed grid is complete with provenance gaps preserved',()=>{
 assert.equal(data.historical_code_revision,null);assert.equal(data.historical_fee_bps,null);assert.equal(data.input_scope.return_sessions,2778);
 const keys=new Set(data.buffer_matrix.map(r=>[r.candidate,r.exclusion_percentile,r.weighting,r.buffer_setting].join('|')));assert.equal(keys.size,48);assert.equal(data.buffer_matrix.length,48);
 for(const c of candidates)for(const e of [0,.1,.2,.3])for(const w of ['equal','value'])for(const b of ['no_buffer','buffered'])assert.ok(keys.has([c,e,w,b].join('|')));
 assert.deepEqual([data.era_summary.length,data.regime_summary.length,data.capacity_matrix.length],[48,72,24]);
 assert.ok(data.capacity_matrix.every(r=>['small_cap','composite'].includes(r.candidate)&&[0,.3].includes(r.exclusion_percentile)&&r.buffer_setting==='buffered'));
});
test('era CAGRs compound matching yearly returns with actual session support',()=>{
 for(const e of data.era_summary){
  const rows=data.yearly.filter(r=>r.name===e.candidate&&r.exclusion_percentile===e.exclusion_percentile&&r.weighting===e.weighting&&r.buffer_setting===e.buffer_setting&&(e.era==='development'?r.year<=2023:r.year>=2024));
  assert.equal(rows.length,e.era==='development'?9:3);
  const n=rows.reduce((s,r)=>s+r.observations,0),g=rows.reduce((s,r)=>s*(1+r.period_return/100),1);
  assert.equal(n,e.observations);assert.equal(n,e.era==='development'?2154:624);near((g-1)*100,e.cumulative_return);near((g**(252/n)-1)*100,e.net_annual_return);
 }
});
test('buffer comparison retains failures and supports exactly eight net improvements',()=>{
 let improvements=0;
 for(const r of data.buffer_matrix.filter(r=>r.buffer_setting==='buffered')){
  const b=data.buffer_matrix.find(b=>b.candidate===r.candidate&&b.exclusion_percentile===r.exclusion_percentile&&b.weighting===r.weighting&&b.buffer_setting==='no_buffer');
  assert.ok(r.annualized_turnover<b.annualized_turnover);near(r.gross_annual_return-r.net_annual_return,r.cost_drag);if(r.net_annual_return>b.net_annual_return)improvements++;
 }assert.equal(improvements,8);
});
test('localized table and Markdown projections retain every reviewed row',async()=>{
 for(const locale of ['en-US','zh-CN']){
  const groups=comparisonTables(data,locale);assert.deepEqual(groups.map(g=>g.rows.length),[48,48,72,24]);
  for(const g of groups)for(const r of g.rows){assert.equal(r.length,g.headers.length);assert.ok(r.every(v=>!String(v).match(/NaN|undefined/)));}
  const md=await comparisonMarkdown(locale,data);assert.ok(md.includes(`microcap-exclusions.${locale}.svg`));assert.equal((md.match(/<details>/g)||[]).length,4);
 }
});
test('all SVG points encode actual values on shared zero-inclusive linear axes',async()=>{
 for(const locale of ['en-US','zh-CN']){
  const svg=await buildExclusionSvg(locale,data);assert.equal((svg.match(/<circle /g)||[]).length,48);assert.equal((svg.match(/<polyline /g)||[]).length,12);assert.ok(svg.includes(`id="microcap-exclusions-title-${locale.toLowerCase()}"`));
  const points=[...svg.matchAll(/<circle cx="([^"]+)" cy="([^"]+)"[^>]*><title>[^<]*→ ([^<]+)%<\/title>/g)];assert.equal(points.length,48);
  const lo=Math.floor(Math.min(0,...data.buffer_matrix.map(r=>r.net_annual_return))/5)*5,hi=Math.ceil(Math.max(0,...data.buffer_matrix.map(r=>r.net_annual_return))/5)*5;
  for(let i=0;i<48;i++){
   const facet=Math.floor(i/12),cut=[0,.1,.2,.3][i%4],candidate=candidates[Math.floor(i%12/4)];
   const r=data.buffer_matrix.find(r=>r.candidate===candidate&&r.exclusion_percentile===cut&&r.weighting===(facet<2?'equal':'value')&&r.buffer_setting===(facet%2?'buffered':'no_buffer'));
   near(Number(points[i][1]),52+(facet%2)*535+cut/.3*290);near(Number(points[i][2]),155+Math.floor(facet/2)*340+225-(r.net_annual_return-lo)/(hi-lo)*225);assert.equal(points[i][3],r.net_annual_return.toFixed(3));
  }
  assert.equal((svg.match(/>0%<\/text>/g)||[]).length,8);assert.doesNotMatch(svg,/\/home\/|\/mnt\/|NaN|undefined/);
 }
});
