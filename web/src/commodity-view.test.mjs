import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {commoditySelection} from './lib/commodity-view.ts';
const evidence=JSON.parse(readFileSync(new URL('../../studies/china_commodity_equity/exploration-summary-20261108.json',import.meta.url)));
test('every commodity selector combination returns its reviewed source case',()=>{
 for(const policy of ['monthly','annual'])for(const weight of ['10','20','30','40'])for(const horizon of ['60','120']){
 assert.equal(commoditySelection(evidence.robustness.cases,{policy,weight,horizon}),evidence.robustness.cases[`${policy}_${weight}_${horizon}`]);
 }
 assert.throws(()=>commoditySelection(evidence.robustness.cases,{policy:'monthly',weight:'99',horizon:'60'}),/unsupported/);
});
