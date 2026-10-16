import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { comparisonCopy as copy, comparisonText, type ComparisonLocale } from './microcap-comparison';
export type AggregateRow = Record<string, string | number>;
export interface ExclusionReview {
 schema_version: string; reviewed_on: string;
 input_scope: {start:string;end:string;formation_start:string;formation_end:string;formations:number;return_sessions:number;development_sessions:number;later_sessions:number};
 historical_code_revision: null; historical_fee_bps: null; protocol_default_fee_bps: number;
 buffer_matrix: AggregateRow[]; yearly: AggregateRow[]; era_summary: AggregateRow[]; regime_summary: AggregateRow[]; capacity_matrix: AggregateRow[];
}
// One explicit public asset. Never scan or read private result directories.
export async function readExclusionReview(): Promise<ExclusionReview> {
 return JSON.parse(await readFile(resolve(process.cwd(), 'public/data/microcap_exclusion_review.json'), 'utf8'));
}
const escape = (value: string) => value.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const label = (value: string | number, locale: ComparisonLocale) => {
 const key=String(value) as keyof typeof copy;
 return key in copy ? comparisonText(copy[key],locale) : String(value);
};
const num = (value: string | number | undefined, digits=3) => value === undefined ? '—' : Number(value).toFixed(digits);
export function comparisonTables(data: ExclusionReview, locale: ComparisonLocale) {
 const zh=locale==='zh-CN', t=(en:string,cn:string)=>zh?cn:en;
 const identity=(r:AggregateRow)=>[label(r.candidate ?? r.name,locale), `${num(Number(r.exclusion_percentile)*100,0)}%`,label(r.weighting,locale),label(r.buffer_setting,locale)];
 const base=[t('Candidate','候选'),t('Excluded names','剔除数量'),t('Weight','权重'),t('Buffer','缓冲')];
 return [
  {id:'buffers',title:t('Buffer comparison · 48 rows','缓冲对照 · 48 行'),headers:[...base,t('Gross annual %','毛年化 %'),t('Net annual %','净年化 %'),t('Turnover ×/year','换手 倍/年'),t('Cost drag pp','成本拖累 百分点'),t('Net Sharpe','净夏普'),t('Net drawdown %','净回撤 %')],rows:data.buffer_matrix.map(r=>[...identity(r),...['gross_annual_return','net_annual_return','annualized_turnover','cost_drag','net_sharpe','net_max_drawdown'].map(k=>num(r[k]))])},
  {id:'eras',title:t('Development and inspected later sample · 48 rows','开发与已查看后期样本 · 48 行'),headers:[...base,t('Era','阶段'),t('Sessions','观测日'),t('Net annual %','净年化 %'),t('Cumulative %','累计 %')],rows:data.era_summary.map(r=>[...identity(r),label(r.era,locale),String(r.observations),num(r.net_annual_return),num(r.cumulative_return)])},
  {id:'regimes',title:t('Descriptive registration periods · 72 rows','注册制时期描述对照 · 72 行'),headers:[...base,t('Period','时期'),t('Sessions','观测日'),t('Net period %','期间净收益 %'),t('Net annual %','净年化 %'),t('Sharpe','夏普'),t('Drawdown %','回撤 %'),t('Mean daily turnover','日均换手')],rows:data.regime_summary.map(r=>[...identity(r),label(r.regime,locale),String(r.observations),...['period_return','annual_return','sharpe','max_drawdown','average_turnover'].map(k=>num(r[k]))])},
  {id:'capacity',title:t('Separate cash-ledger capacity simulation · 24 rows','独立现金账本容量模拟 · 24 行'),headers:[...base,t('Capital CNY million','资金 百万元'),t('Net annual %','净年化 %'),t('Sharpe','夏普'),t('Drawdown %','回撤 %'),t('Fill %','成交 %'),t('Cash %','现金 %'),t('Cumulative turnover ×','累计换手 倍')],rows:data.capacity_matrix.map(r=>[...identity(r),num(Number(r.capital)/1e6,0),num(r.net_annual_return),num(r.net_sharpe),num(r.max_drawdown),num(Number(r.fill_ratio)*100),num(Number(r.avg_cash_weight)*100),num(r.cumulative_turnover)])},
 ];
}
export async function comparisonMarkdown(locale: ComparisonLocale, supplied?: ExclusionReview) {
 const data=supplied ?? await readExclusionReview(), t=(key:keyof typeof copy)=>comparisonText(copy[key],locale);
 const table=(headers:string[],rows:string[][])=>[headers,headers.map(()=>'---'),...rows].map(row=>`| ${row.map(v=>v.replaceAll('|','\\|').replaceAll('\n',' ')).join(' | ')} |`).join('\n');
 return [`## ${t('title')}`,t('status'),`[${t('dataDownload')}](https://runchengxie.github.io/quant-market-research/data/microcap_exclusion_review.json)`,...(['finding','weighting','buffers','scope','method','provenance','eras','capacity','units'] as const).map(t),`![${t('chart')}](https://runchengxie.github.io/quant-market-research/downloads/microcap-exclusions.${locale}.svg)`,...comparisonTables(data,locale).map(group=>`<details>\n<summary>${group.title}</summary>\n\n${table(group.headers,group.rows)}\n\n</details>`)].join('\n\n');
}
export const buildExclusionMarkdown = comparisonMarkdown;
export async function buildExclusionSvg(locale: ComparisonLocale, supplied?: ExclusionReview) {
 const data=supplied ?? await readExclusionReview(), t=(key:keyof typeof copy)=>comparisonText(copy[key],locale);
 const rows=data.buffer_matrix, low=Math.floor(Math.min(0,...rows.map(r=>Number(r.net_annual_return)))/5)*5, high=Math.ceil(Math.max(0,...rows.map(r=>Number(r.net_annual_return)))/5)*5;
 const suffix=locale.toLowerCase(), titleId=`microcap-exclusions-title-${suffix}`, descId=`microcap-exclusions-desc-${suffix}`;
 const candidates=['small_cap','low_turnover','composite'] as const, colors=['var(--accent-strong,#1267d6)','var(--ink,#252525)','var(--ink-soft,#514b43)'];
 const facets=(['equal','value'] as const).flatMap(weighting=>(['no_buffer','buffered'] as const).map(buffer=>({weighting,buffer})));
 const description=facets.map(f=>`${t(f.weighting)}, ${t(f.buffer)}: ${candidates.map(c=>`${t(c)} ${[0,.1,.2,.3].map(e=>`${e*100}%: ${num(rows.find(r=>r.candidate===c&&Number(r.exclusion_percentile)===e&&r.weighting===f.weighting&&r.buffer_setting===f.buffer)?.net_annual_return)}%`).join(', ')}`).join('; ')}`).join('. ');
 const panels=facets.map((f,i)=>{
  const ox=52+(i%2)*535, oy=155+Math.floor(i/2)*340, x=(e:number)=>ox+e/.3*290, y=(v:number)=>oy+225-(v-low)/(high-low)*225;
  const ticks=Array.from({length:(high-low)/5+1},(_,n)=>low+n*5);
  return `<g><text x="${ox}" y="${oy-22}" font-size="19" font-weight="600">${escape(t(f.weighting))} · ${escape(t(f.buffer))}</text>${ticks.map(v=>`<line x1="${ox}" x2="${ox+290}" y1="${y(v)}" y2="${y(v)}" stroke="var(--rule,#d1d5db)" ${v===0?'stroke-width="2"':''}/><text x="${ox-9}" y="${y(v)+4}" text-anchor="end" font-size="12">${v}%</text>`).join('')}${[0,.1,.2,.3].map(e=>`<text x="${x(e)}" y="${oy+247}" text-anchor="middle" font-size="13">${e*100}%</text>`).join('')}${candidates.map((c,j)=>{
   const selected=[0,.1,.2,.3].map(e=>rows.find(r=>r.candidate===c&&Number(r.exclusion_percentile)===e&&r.weighting===f.weighting&&r.buffer_setting===f.buffer)!);
   return `<polyline fill="none" stroke="${colors[j]}" stroke-width="2.5" stroke-dasharray="${['none','7 4','2 3'][j]}" points="${selected.map(r=>`${x(Number(r.exclusion_percentile))},${y(Number(r.net_annual_return))}`).join(' ')}"/>${selected.map(r=>`<circle cx="${x(Number(r.exclusion_percentile))}" cy="${y(Number(r.net_annual_return))}" r="4" fill="${colors[j]}"><title>${escape(t(c))}: ${num(Number(r.exclusion_percentile)*100,0)}% → ${num(r.net_annual_return)}%</title></circle>`).join('')}<text x="${ox+312}" y="${oy+48+j*36}" font-size="14" fill="${colors[j]}">${escape(t(c))}</text><text x="${ox+312}" y="${oy+65+j*36}" font-size="12">${num(selected[3].net_annual_return,2)}% @ 30%</text><line x1="${ox+295}" x2="${ox+307}" y1="${y(Number(selected[3].net_annual_return))}" y2="${oy+44+j*36}" stroke="${colors[j]}"/>`;
  }).join('')}</g>`;
 }).join('');
 return `<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="880" viewBox="0 0 1120 880" role="img" aria-labelledby="${titleId} ${descId}"><title id="${titleId}">${escape(t('chart'))}</title><desc id="${descId}">${escape(description)}. ${escape(t('provenance'))}</desc><rect width="1120" height="880" fill="var(--surface,#fff)"/><g font-family="system-ui,sans-serif" fill="var(--ink,#252525)"><text x="28" y="36" font-size="25" font-weight="600">${escape(t('chart'))}</text><text x="28" y="67" font-size="14">${locale==='zh-CN'?'2,778 个共同观测日；月频；四幅图共用线性刻度':'2,778 common sessions; monthly; shared linear scale in all four panels'}</text><text x="28" y="92" font-size="14">${locale==='zh-CN'?'保留的扣费输出；历史费率与代码版本未知；不代表最优参数':'Retained post-cost outputs; historical fees and code unknown; no optimum established'}</text>${panels}<text x="560" y="797" text-anchor="middle" font-size="16">${escape(t('axis'))}</text><text x="28" y="836" font-size="13">${locale==='zh-CN'?'输入：2015-01-01—2026-07-31；2024 年后样本已查看；审阅：2026-10-16':'Input: 2015-01-01–2026-07-31; 2024+ sample inspected; reviewed 2026-10-16'}</text><text x="28" y="859" font-size="13">${locale==='zh-CN'?'当前协议默认 10bp，不能据此确认历史费率。容量结果来自另一引擎。':'Current protocol default 10 bp does not authenticate historical fees. Capacity uses a separate engine.'}</text></g></svg>`;
}
