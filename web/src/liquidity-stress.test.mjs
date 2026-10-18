import test from 'node:test';
import assert from 'node:assert/strict';
import {stressBudgets,scaleWindowBudget} from './lib/liquidity-stress.ts';

test('stress budgets preserve the stock-count gate and zero while missing remains unavailable',()=>{
 assert.deepEqual(stressBudgets(100,50,.1,5,10,20),{normal:500,stress:250});
 assert.equal(stressBudgets(100,50,.1,5,21,20),null);
 assert.equal(stressBudgets(100,null,.1,5,10,20),null);
 assert.deepEqual(stressBudgets(100,0,.1,5,10,20),{normal:500,stress:0});
});
test('window budget scaling rejects invalid fractions and preserves real zero',()=>{
 assert.deepEqual(scaleWindowBudget(100,[0,.2,.5]),[0,20,50]);
 for(const row of [[null,.2,.3],[.4,.2,.3],[-.1,.2,.3],[.1,.2,1.1]]) assert.equal(scaleWindowBudget(100,row),null);
 assert.equal(scaleWindowBudget(-1,[.1,.2,.3]),null);
});

test('public stress evidence binds to review and source scope, with conserved cohorts and no identifiers',async()=>{
 const {readFileSync}=await import('node:fs');const {createHash}=await import('node:crypto');
 const raw=readFileSync(new URL('../public/data/liquidity/stress-persistence.json',import.meta.url));
 const data=JSON.parse(raw);const review=JSON.parse(readFileSync(new URL('../public/data/liquidity/stress-review.json',import.meta.url)));
 const base=JSON.parse(readFileSync(new URL('../public/data/liquidity/summary.json',import.meta.url)));
 assert.equal(review.reviewed_summary_sha256,createHash('sha256').update(raw).digest('hex'));
 assert.equal(review.passed,true);assert.equal(review.raw_minute_dates_checked,15);
 assert.equal(data.feature_sha256,base.source_receipts.find(r=>r.source_id==='a_sh_sz_features').sha256);
 assert.equal(data.historical_pit_eligible,false);assert.equal(data.actual_execution_calibrated,false);
 for(const row of data.cohorts){assert.ok(Math.abs(row.retained_fraction+row.migrated_fraction+row.ineligible_fraction+row.missing_fraction-1)<1e-10);assert.ok(row.continuous_fraction<=row.retained_fraction);assert.ok(row.continuous_fraction<=row.usable_continuous_fraction);assert.ok(row.usable_continuous_fraction<=row.retained_fraction+row.migrated_fraction+1e-12);}
 for(const row of data.stress)if(row.retained_budget_fraction!=null)assert.ok(row.retained_budget_fraction>=0&&row.retained_budget_fraction<=1);
 assert.doesNotMatch(raw.toString(),/\/home\/|source_path|\b\d{6}\.(SH|SZ|BJ)\b/);
 const {liquidityStressCopy}=await import('./content/liquidity-stress-copy.ts');
 for(const labels of Object.values(liquidityStressCopy)){assert.equal(labels.length,2);assert.ok(labels.every(s=>s.length>0));}
});
