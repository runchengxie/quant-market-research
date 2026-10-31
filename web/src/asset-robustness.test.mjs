import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { robustnessCopy } from './content/asset-robustness-copy.ts';
const d=JSON.parse(readFileSync(new URL('../public/data/asset_robustness_reviewed.json',import.meta.url)));
test('endpoint cells and signed annual contributions retain their actual scope',()=>{
 for(const r of Object.values(d.sensitivity)){
  assert.equal(r.grid.cells.length,153);
  assert.ok(r.grid.cells.every(c=>c.months>=60));
  assert.equal(r.grid.minimum_cagr,Math.min(...r.grid.cells.map(c=>c.cagr)));
  assert.ok(Math.abs(r.annual.years.reduce((s,r)=>s+r.log_growth,0)-r.annual.total_log_growth)<1e-12);
 }
 assert.equal(d.waiting.small_vs_large.current_underperformance_months,120);
 assert.equal(d.waiting.small_vs_large.episodes.at(-1).censored,true);
});
test('allocation compares fixed policies and explicit cost assumptions',()=>{
 assert.equal(d.allocations.length,19);
 assert.deepEqual([...new Set(d.allocations.map(r=>r.cost_bps_per_traded_notional))],[0,10,50]);
 for(const r of d.allocations){
  assert.equal(r.months,227);
  assert.equal(r.summary.ten_year_completed_windows,108);
  assert.ok(Math.abs(Object.values(r.target_weights).reduce((a,b)=>a+b,0)-1)<1e-12);
  assert.ok(r.summary.net_cagr<=r.summary.gross_cagr+1e-12);
 }
});
test('ETF wealth reconciliation keeps fee and distribution boundaries',()=>{
 for(const r of Object.values(d.etfs)){
  assert.equal(r.months,107);
  assert.equal(r.manager_fees_subtracted_again,false);
  assert.equal(r.full_history_independently_verified,false);
  assert.ok(Math.abs(r.market_relative_wealth_ratio-r.nav_relative_wealth_ratio*r.premium_wealth_ratio*r.distribution_basis_wealth_ratio)<1e-12);
 }
 assert.equal(d.issuer_crosscheck.full_long_window_causal_explanation_verified,false);
 assert.equal(d.constituents['000300.SH'].cohort_retained_count,138);
 assert.equal(d.constituents['000852.SH'].cohort_retained_count,220);
 assert.equal(d.financial_coverage['000300_SH'].initial.fy2025_profit_available,292);
 assert.equal(d.financial_coverage['000852_SH'].initial.fy2025_profit_available,964);
 const text=JSON.stringify(d);
 assert.ok(!text.includes('/home/')&&!text.includes('n_income_attr_p')&&!text.includes('post_holdings'));
 for(const copy of Object.values(robustnessCopy))assert.ok(copy.length===2&&copy.every(Boolean));
});
