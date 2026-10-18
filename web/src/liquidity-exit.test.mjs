import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {liquidityExitCopy} from './content/liquidity-exit-copy.ts';
const get=name=>JSON.parse(readFileSync(new URL(`../public/data/liquidity/${name}`,import.meta.url)));

test('published fixed-name budgets preserve reviewed bytes, source and original denominators',()=>{
 const raw=readFileSync(new URL('../public/data/liquidity/exit-exploration.json',import.meta.url));
 const data=JSON.parse(raw);const review=get('exit-review.json');const base=get('summary.json');
 assert.equal(review.passed,true);assert.equal(review.reviewed_summary_sha256,createHash('sha256').update(raw).digest('hex'));
 assert.equal(data.feature_sha256,base.source_receipts.find(r=>r.source_id==='a_sh_sz_features').sha256);
 assert.equal(data.actual_execution_calibrated,false);assert.equal(data.historical_pit_eligible,false);
 for(const r of data.rows){assert.equal(r.covered+r.not_covered+r.unresolved,r.stocks);if(r.covered<r.stocks)assert.equal(r.all_names_day_max,null);}
 assert.doesNotMatch(raw.toString(),/\/home\/|\b\d{6}\.(?:SH|SZ|BJ)\b/);
 const sample=data.rows.find(r=>r.year===2025&&r.bucket===2&&r.mode==='guarded'&&r.position_usd===1000000&&r.participation===.03&&r.horizon===5);
 assert.equal(sample.stocks,32161);assert.equal(sample.covered,24256);assert.equal(sample.not_covered,7905);
});

test('minute boundary evidence and identical-byte revision baseline retain their limits',()=>{
 const m=get('minute-clock-probe.json');const r=get('revision-baseline.json');
 assert.equal(m.native_interval_semantics_verified,false);
 assert.equal(m.accepted_stock_days,m.quality.reduce((n,r)=>n+r.accepted,0));
 assert.equal(m.dates,m.quality.length);assert.ok(m.dates>15);
 assert.equal(r.comparison_kind,'same_bytes_baseline_only');assert.equal(r.longitudinal_vendor_stability_verified,false);
 assert.equal(r.sha256.baseline,r.sha256.candidate);
 for(const pair of Object.values(liquidityExitCopy)){assert.equal(pair.length,2);assert.ok(pair.every(v=>v.length>0));}
});
