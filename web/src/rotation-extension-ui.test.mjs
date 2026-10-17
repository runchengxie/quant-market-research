import test from 'node:test';import assert from 'node:assert/strict';import {readFile} from 'node:fs/promises';
import React from 'react';import {renderToStaticMarkup} from 'react-dom/server';
const {asset}=JSON.parse(await readFile(new URL('../tests/fixtures/rotation-extension.json',import.meta.url),'utf8'));
test('empty forward evidence shows waiting and never a zero-performance chart',async()=>{
 const {default:Forward}=await import('./components/RotationForwardEvidence.tsx');
 const html=renderToStaticMarkup(React.createElement(Forward,{evidence:asset}));
 assert.match(html,/Waiting for fresh inputs/);assert.doesNotMatch(html,/0\.00%/);
 assert.match(html,/515910/);assert.match(html,/512890/);
});
test('theme result rendering follows evidence state',async()=>{
 const {default:Theme}=await import('./components/RotationThemeEvidence.tsx');
 const blocked=renderToStaticMarkup(React.createElement(Theme,{theme:asset.theme}));
 assert.match(blocked,/still missing/);assert.doesNotMatch(blocked,/5\.00%/);
 const metrics={total_return:.05,cagr:.05,max_drawdown:-.1,sharpe_zero_rf:1};
 const diagnostic=renderToStaticMarkup(React.createElement(Theme,{theme:{status:'diagnostic',reasons:[],registration_id:'fixture',metrics:{baseline:metrics,overlay:metrics,difference:{cagr_pp:0,total_return_pp:0}}}}));
 assert.match(diagnostic,/5\.00%/);assert.doesNotMatch(diagnostic,/still missing/);
});
