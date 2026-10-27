import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve } from 'node:path';
import { publicPages } from './public-registry';
import { englishCopy } from './locale-copy';
import { conclusionCopy } from '../conclusion-copy';
import { lowTurnoverCopy, lowTurnoverEvidence } from './low-turnover-copy';
import { overseasCopy } from './overseas-leadlag-copy';
import { readingCopy, type ReadingSummary, type Copy } from './research-reading';

const read = (path: string) => JSON.parse(readFileSync(resolve('public/data', path), 'utf8'));
const manifest = read('manifest.json');
const iso = (value: string) => /^\d{8}$/.test(value) ? `${value.slice(0,4)}-${value.slice(4,6)}-${value.slice(6)}` : value;
const range = (start?: string, end?: string): Copy => [
  `${start ? iso(start) : 'Not provided'} to ${end ? iso(end) : 'Not provided'}`,
  `${start ? iso(start) : '未提供'} 至 ${end ? iso(end) : '未提供'}`,
];
const definition: Record<string, { snapshot?: string; files: string[]; conclusion: Copy; scope: Copy; limit: Copy; related?: string[]; stage?: ReadingSummary['stage'] }> = {
  'low-turnover': { snapshot:'low_turnover', files:['low_turnover_reader.json'], conclusion:lowTurnoverCopy.lead,
    scope:['60-session turnover; positive-PE common sample; monthly gross low-minus-high spread.', '选股日前 60 日换手率，市盈率为正的共同样本，比较低换手组减高换手组的月均毛收益。'],
    limit:['Revision risk and repeated historical inspection remain. After-cost performance is unverified.', '历史数据仍有修订风险，样本已经反复查看。扣费后的实际收益仍待验证。'], related:['low-turnover-method'] },
  'valuation-groups': { files:['grouped_valuation_draft.json','low_valuation_topic_reviewed.json','valuation_ledger_checkpoint_draft.json','valuation_round2_draft.json'],
    conclusion:['Valuation comparisons depend on accounting definitions and usable stocks. Full-market coverage and achievable trading returns remain unverified.', '估值比较受到财务口径和可用股票范围影响。全市场覆盖与实际交易收益仍待验证。'],
    scope:['Five valuation definitions; distributions and return diagnostics have separate sample periods.', '五种估值口径。估值分布与收益实验分别使用各自的样本期间。'],
    limit:['Financial history and reconstructed ST status retain later-revision risk.', '财务历史和重建 ST 状态可能混入后来的修订。'], related:['pb-roe','valuation-groups-method'] },
  microcap: { snapshot:'microcap', files:['microcap_raw_sell_review.json','microcap_summary.json','microcap_repair_summary.json'], conclusion:[conclusionCopy.byTopic.microcap.en,conclusionCopy.byTopic.microcap.zh],
    scope:['Reference indices and reconstructed portfolios are separate. Dates below refer to the reconstruction snapshot.', '参考指数与自建组合分别展示。这里的日期对应重建快照。'],
    limit:['Missing exit prices and uncalibrated real trading costs limit account-return claims.', '退出价格缺失，实际交易成本尚未校准，账户收益判断仍受限制。'], related:['microcap-report','microcap-method'] },
  cashflow: { snapshot:'cashflow', files:['research/recovery.json','index/cashflow_indices/cashflow_performance.csv','index/cashflow_indices/cashflow_rebalance_frequency.csv','research/replication.json','cashflow-replication/study.json','cashflow-replication/exploration.json','cashflow-replication/navigation.json','cashflow-replication/publication.json','cashflow-replication/migration.json'], stage:'description', conclusion:[conclusionCopy.byTopic.cashflow.en,conclusionCopy.byTopic.cashflow.zh],
    scope:['Reference index history; price and total-return series are shown separately.', '参考指数历史，价格收益与含分红收益分别展示。'], limit:['A complete investable reconstruction remains unverified.', '按规则实际买卖的组合仍缺完整复现与核验。'], related:['cashflow-replication'] },
  indices: { snapshot:'indices', files:['index/linked_indices/ten_year_price_returns.csv','index/linked_indices/paired_index_etf_representatives.csv','index/linked_indices/etf_multi_period_returns.csv','index/index_catalog.csv'], stage:'description', conclusion:[conclusionCopy.byTopic.indices.en,conclusionCopy.byTopic.indices.zh],
    scope:['Index and ETF histories; each series retains its own dates and dividend convention.', '指数与 ETF 历史，各序列保留自己的日期和分红口径。'], limit:['Different periods and conventions prevent a like-for-like return ranking.', '不同期间与收益口径不能直接混排。'] },
  style: { snapshot:'barra', files:['barra/barra_summary.json','barra/historical_factor_summary.json','barra/factor_yearly.csv'], conclusion:[conclusionCopy.byTopic.barra.en,conclusionCopy.byTopic.barra.zh],
    scope:['Archived factor series and yearly comparisons; portfolio return is a separate question.', '历史因子序列与逐年对照，组合实际收益需要另行研究。'], limit:['Historical availability and implementation remain unverified.', '历史可得性与实际交易仍待核验。'], related:['barra-factor-dictionary','barra-source-inventory'] },
  'overseas-leadlag': { files:['overseas_leadlag_reviewed.json'], conclusion:overseasCopy.intro,
    scope:['Forecast error improvement and T+1 ETF cost scenarios are separate outcomes.', '预测误差改善与 T+1 ETF 扣费情景分别展示。'], limit:['Historical delivery times are assumed; daily-bar proxies do not verify fills.', '历史到数时间仍是假设，日线价格代理不能核实真实成交。'], related:['overseas-leadlag-method','overseas-forward'] },
  rotation: { files:['rotation-release-index.json','rotation-evidence-release.json'],
    conclusion:['The published experiments do not establish a stable theme-to-ETF trading advantage.', '已公开的实验尚未证实主题信号转为 ETF 组合后有稳定交易优势。'],
    scope:['Different release cohorts, allocation tests and cost assumptions remain separate.', '不同发布批次、配置实验和成本假设分别展示。'], limit:['Repeated historical inspection and incomplete prospective evidence limit conclusions.', '历史样本已经反复查看，后续观察证据仍不充分。'] },
  liquidity: { snapshot:'liquidity', files:['liquidity/summary.json','liquidity/capacity-data-quality.json','liquidity/followup-audit.json','liquidity/relative-summary.json','liquidity/stability.json','liquidity/scenario-limits.json'], stage:'description', conclusion:[conclusionCopy.byTopic.liquidity.en,conclusionCopy.byTopic.liquidity.zh],
    scope:['Trading-value distributions and cost scenarios; a shared date does not unify market coverage.', '成交额分布与成本情景，共同日期不能消除市场覆盖差异。'], limit:['Real fills, price impact and capacity still need calibration.', '真实成交、价格冲击和容量仍须校准。'], related:['execution-costs','cross-market-liquidity'] },
};

export const readingSummaries: ReadingSummary[] = Object.entries(definition).map(([id,d]) => {
  const page=publicPages.find(p=>p.id===id);
  if(!page) throw Error(`Unregistered research ${id}`);
  const snap=d.snapshot ? manifest.snapshots[d.snapshot] : undefined;
  let coverage: Copy=range(snap?.coverage_start,snap?.coverage_end);
  let date: string|null=snap?.generated_at?.slice(0,10)??null;
  const files=[...d.files];
  if(id==='cashflow') coverage=['Periods differ across index series and experiments; see dates in each chart and table', '各指数与实验的样本期间不同，具体日期见详情图表'];
  if(id==='indices') coverage=['Index and ETF histories have different starts and comparison windows; see each series', '各指数与 ETF 的起点和比较期间不同，具体日期见各序列'];
  if(id==='microcap')date=read(files[0]).reviewed_on;
  if(id==='low-turnover') { coverage=range(lowTurnoverEvidence.formationStart,lowTurnoverEvidence.formationEnd); date=lowTurnoverEvidence.evidenceDate; }
  if(id==='valuation-groups') { const data=read(files[0]); const dates=data.coverage.map((r:{formation_date:string})=>r.formation_date).sort(); coverage=range(dates[0],dates.at(-1)); date=data.generated_at_utc.slice(0,10); }
  if(id==='overseas-leadlag') { const data=read(files[0]); coverage=['Separate forecast and ETF starts; through '+data.sample_end,'预测与 ETF 起点各异，截至 '+data.sample_end];date=data.generated_at_utc.slice(0,10); }
  if(id==='rotation') { const index=read(files[0]);files.push(...index.releases.map((r:{path:string})=>r.path));date=index.releases.find((r:{release_id:string})=>r.release_id===index.current_release_id).published_at.slice(0,10);coverage=['See the period for each experiment; no common performance window','查看各实验期间，尚无统一业绩窗口']; }
  if(id==='liquidity') { const data=read(files[0]);const period=data.periods.find((r:{period:string})=>r.period==='common snapshot');coverage=['Common cross-market snapshot '+period.common_end,'跨市场共同快照 '+period.common_end];date=data.generated_on; }
  const sources=files.map(path=>({path,sha256:createHash('sha256').update(readFileSync(resolve('public/data',path))).digest('hex')}));
  return {id,route:page.route,title:[englishCopy(page).title,page.title],conclusion:d.conclusion,scope:d.scope,limit:d.limit,stage:d.stage??'exploration',coverage,date,sources,related:d.related??[]};
});
export function summaryForRoute(path: string) { return readingSummaries.find(r=>path.endsWith(r.route)); }
export { readingCopy };
