import {test} from 'node:test';
import assert from 'node:assert/strict';
import {chineseProse, proseFindings, tidyChinesePunctuation} from './lib/prose-audit.ts';

test('prose extraction preserves lookup keys, code and identifiers',()=>{
 const source=`const copy={'不是A，而是B':['English','不是大盘重要，而是买入时点重要。']}; const id='cashflow';`;
 const spans=chineseProse(source,'copy.ts');
 assert.equal(spans.length,1);
 assert.equal(spans[0].text,'不是大盘重要，而是买入时点重要。');
 assert(proseFindings(spans[0].text).some(x=>x.rule==='rhetorical_reversal'));
 const md='正文用中文(说明)；句子。\n\n'+['```python','print("不是A，而是B")','```'].join('\n');
 assert.equal(chineseProse(md,'a.md').length,1);
 assert.equal(tidyChinesePunctuation('正文(说明)；按 `f(x)` 计算。'),'正文（说明）。按 `f(x)` 计算。');
});

test('templates expose prose without changing interpolation or quoted evidence',()=>{
 const source='const value=`共有 ${n} 个月；范围已核对。`;';
 const spans=chineseProse(source,'copy.ts');
 assert(spans.some(x=>x.text.includes('个月')));
 const patched=spans.reduceRight((s,x)=>s.slice(0,x.start)+tidyChinesePunctuation(x.text)+s.slice(x.end),source);
 assert(patched.includes('${n}'));
 assert(patched.includes('个月。范围'));
 assert(chineseProse('> 原文“不是A，而是B”。','source.md').length===0);
});

test('Astro scripts and formula syntax stay executable during punctuation edits',()=>{
 const source='---\nconst text="说明(中文)；下一句。";\n---\n<p title="中文(说明)">图表</p><script>const fn=()=>{button.setAttribute("aria-label", "收起主导航");};</script>';
 const spans=chineseProse(source,'page.astro');
 assert(!spans.some(x=>x.text.includes('setAttribute')));
 const patched=spans.reduceRight((s,x)=>s.slice(0,x.start)+tidyChinesePunctuation(x.text)+s.slice(x.end),source);
 assert(patched.includes('setAttribute("aria-label", "收起主导航")'));
 assert.equal(tidyChinesePunctuation('图表 fill="var(--surface,#fff)"，单位(元)。'),'图表 fill="var(--surface,#fff)"，单位（元）。');
});

test('Chinese explanation labels and sentences avoid colon scaffolding',()=>{
 assert.equal(tidyChinesePunctuation('样本：35个月'),'样本 35个月');
 assert.equal(tidyChinesePunctuation('回顾性验证：组合使用已经核对的历史数据。'),'组合使用已经核对的历史数据。');
 assert(!tidyChinesePunctuation('数据按月末计算：部分月份共用行情。').includes('：'));
});
