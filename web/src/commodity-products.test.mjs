import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {selectProductCases} from './lib/commodity-products';
const source=JSON.parse(readFileSync(new URL('../../studies/china_commodity_equity/forward-summary-20261108.json',import.meta.url)));
test('all product cost cash and return-basis controls select reviewed cases',()=>{
 for(const fee of ['0','10','50'])for(const cash of ['0','0.5'])for(const basis of ['market','nav']){
 const rows=selectProductCases(source.products.products,{fee,cash,basis});assert.equal(rows.length,9);
 for(const row of rows){const original=source.products.products[row.product].cases.find(x=>x.strategy===row.strategy&&x.fee_bps_per_side===Number(fee)&&x.cash_shibor_fraction===Number(cash)&&x.basis===basis);assert.equal(row.cagr,original.cagr);}
 }
 assert.throws(()=>selectProductCases(source.products.products,{fee:'5',cash:'0',basis:'market'}),/unsupported/);
});
