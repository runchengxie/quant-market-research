import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { assetReturnCopy } from './content/asset-return-copy.ts';
const data=JSON.parse(readFileSync(new URL('../public/data/asset_returns_reviewed.json',import.meta.url)));
test('published monthly results reconcile and retain their different scopes',()=>{
 assert.equal(data.frequency,'monthly');
 assert.equal(data.equities.length,3);
 for(const row of data.equities){
  assert.equal(row.months,252);
  assert.ok(Math.abs((1+row.price_cagr)*(1+row.distribution_component_cagr)-(1+row.total_cagr))<1e-12);
  const h=row.horizons.find(h=>h.months===120);
  assert.equal(h.completed_windows,133);
  assert.equal(h.incomplete_windows,120);
  assert.ok(h.real_loss_fraction>=h.nominal_loss_fraction);
 }
 assert.equal(data.diversification.months,227);
 assert.equal(data.diversification.down_market.gold.months,101);
 assert.ok(data.small_vs_large.cost_sensitivities.every(r=>r.calibrated_execution_cost===false));
 assert.ok(data.small_vs_large.cost_sensitivities.at(-1).relative_cagr<0);
 for(const value of Object.values(assetReturnCopy))assert.ok(value.length===2&&value.every(v=>v.length>0));
 const text=JSON.stringify(data);
 assert.ok(!text.includes('/home/')&&!text.includes('cash_per_unit')&&!text.includes('recovery_entries'));
});
