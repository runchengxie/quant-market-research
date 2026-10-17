import review from '../../public/data/microcap_followup_review.json';
import type { LocalText } from './microcap-hub';

export type FollowupLocale = 'en-US' | 'zh-CN';
export const followupReview = review;
export const followupCopy = {
  title: ['What the follow-up resolved · 2026-10-17', '后续核查解决了什么 · 2026-10-17'],
  conclusion: ['Shared-stock rescoring explains why support-policy target differences persist. Cash and share accounting reconciles in a synthetic fixture, but this does not validate real share execution. The original 120-session runtime is still missing.', '共同股票的截面评分变化解释了为什么观测门槛不同会持续产生持仓差异。合成样例中的现金与份额核算已对齐，但这不能验证真实股数执行。原始 120 日窗口运行仍未找回。'],
  scope: ['The execution comparison holds the reconstructed minimum-90-observation target path fixed: 2015-03-02–2026-07-31, 2,778 sessions, CNY 100 million initial capital and an assumed 10 bp cost per traded notional. These are new current-input diagnostics, not recovered historical performance. The share/cash scenarios are separate from the earlier 4.22% continuous-weight replay and do not replace that accounting basis.', '执行对照固定使用重建的最低 90 个观测目标路径：2015-03-02—2026-07-31，2,778 个交易日，初始资金 1 亿元，假设按成交金额收取 10bp 成本。这些是当前输入下的新诊断，不是找回的历史业绩。份额／现金情景与此前 4.22% 的连续权重重放属于不同核算口径，不能替换该结果。'],
  accounting: ['On the controlled synthetic fixture, the largest daily-return difference between held-weight and share/cash accounting is 1.28 × 10⁻¹⁵. This closes that fixture’s accounting identity check; it does not establish historical input identity or explain every difference between the historical return engines.', '在受控合成样例中，持有权重与份额／现金核算的最大单日收益差为 1.28 × 10⁻¹⁵。这通过了该样例的核算一致性检查，但不能证明历史输入相同，也不能解释不同历史收益引擎之间的所有差异。'],
  executionTitle: ['Eight fixed-target execution scenarios', '固定目标路径的八种执行情景'],
  executionFinding: ['The ideal one-day share/cash replay returns 5.18% annually; the scenario combining a prior-20-session budget with a realized-amount guard returns 5.41%. Scenario returns are not a ranking of deployable strategies. Adding constraints can raise a realized historical return by changing timing, cash and holdings; it does not create a causal performance premium.', '理想单日份额／现金重放的净年化为 5.18%；前 20 日预算叠加当日成交额保护的情景为 5.41%。这些收益不是可部署策略排名。约束改变成交时点、现金与持仓后，历史收益也可能上升，不能据此解释为因果溢价。'],
  synthetic: ['All share scenarios use adjusted synthetic shares priced from total-return-adjusted closes, without a validated corporate-action share ledger. A 100-unit lot here is an adjusted synthetic unit, not a verified exchange lot of raw shares. Cash dividends, share changes and real trading-unit reconciliation remain unresolved. These results do not establish investability or certified capacity.', '所有份额情景都按总回报调整收盘价计价，使用复权合成份额，尚无经过验证的公司行动股数账本。这里的 100 单位整手是复权合成单位，不等于已核实的交易所原始股数整手。现金分红、股数变动与真实交易单位仍待对齐。这些结果不能证明可投资性或认证容量。'],
  executionRules: ['Retry scenarios allow up to three buy days and five sell days. The same-day cap uses 5% of realized traded amount, so it is an ex-post feasibility bound, not information available when placing an order. The prior-20-session budget uses the strictly lagged mean and requires all 20 observations; unknown liquidity stays unknown. Its realized guard also applies the 5% same-day cap. T+1 adds no return difference in this particular fixed monthly path, not proof that it is generally irrelevant.', '重试情景最多允许买入 3 日、卖出 5 日。当日上限使用实际成交额的 5%，因此是事后可行性边界，不是下单时已知的信息。前 20 日预算使用严格滞后均值，要求 20 个观测齐全；未知流动性不补成已知。叠加的当日保护同样限制为实际成交额的 5%。T+1 在这条固定月频路径上没有新增收益差异，不能说明它普遍无关。'],
  suspension: ['The new realized-cap + lot scenario returns 5.5891%, versus 5.6545% in the earlier scenario. The new ladder uses the engine’s native full-day suspension gate. Twelve fills previously flagged on suspension-related dates are a policy-comparison diagnostic, not proof that those trades were illegal. The suspension interpretation changes the scenario and must stay explicit.', '新运行的当日上限＋整手情景净年化为 5.5891%，此前情景为 5.6545%。新执行对照采用引擎原生的全日停牌拦截。此前在停牌相关日期标记出的 12 笔成交属于规则对照诊断，不能据此证明交易违法。停牌解释改变了情景，比较时必须保留这一差别。'],
  metricMeaning: ['Annual return and drawdown are percentages; fill and average cash are displayed as percentages of the reported ratios. Fill ratio is the engine’s requested-order diagnostic, not the fraction of target stocks held. The final column counts fills exceeding 5% of realized daily traded amount; it is not a failure count for other rules. The 2026-07-31 formation has no next-session execution within this sample. “Not reported” is preserved for the ideal arm. Market impact and real trading costs are not calibrated.', '年化收益与回撤以百分比表示；成交比例和平均现金将原报告比率转为百分比。成交比例是引擎的订单请求诊断，不代表目标股票的持有比例。末列统计超过当日实际成交额 5% 的成交笔数，不代表其他规则的失败次数。2026-07-31 形成的目标在本样本内没有下一交易日可供执行。理想情景未报告的字段保持缺失。市场冲击与真实交易成本尚未校准。'],
  chartTitle: ['Net annual return by execution scenario', '各执行情景的净年化收益'],
  chartDescription: ['Eight modeled net annual returns on the same target path. Bars start at zero; the complete metrics and limitations are in the adjacent table.', '同一目标路径的八种模拟净年化收益，柱长从零起算；完整指标与限制见相邻表格。'],
  chartUnit: ['Net annual return (%) · modeled, not a strategy ranking', '净年化收益（%）· 模拟结果，不代表策略排名'],
  supportTitle: ['Why 45- and 90-observation targets keep differing', '45 与 90 个观测门槛为什么持续产生不同持仓'],
  supportFinding: ['Across 138 formations from 2015-02-27 to 2026-07-31, full-policy targets differ on 132 dates with or without the retention buffer. Restricting both arms to common valid names, while preserving their original scores, still gives 130 differing dates; both versions differ on 122 of 127 formations from 2016 onward. Buffer memory alone cannot explain the persistence.', '在 2015-02-27—2026-07-31 的 138 个形成日中，完整门槛规则无论是否使用缓冲，均有 132 日目标不同。将两组限制为共同有效股票、保留各自原评分后，仍有 130 日不同；两种缓冲设置在 2016 年起的 127 日中均有 122 日不同。仅靠缓冲记忆无法解释这种持续性。'],
  supportMechanism: ['The 514,750 common valid stock-month rows have exactly equal raw 120-session turnover means. Original cross-sectional scores differ because clipping and industry demeaning use a changed valid scoring cross-section. Recomputing both scores on the identical eligible raw-support90 set produces exact score equality. Scoring precedes the original eligibility filter, so this controlled recomputation deliberately changes the scoring universe.', '514,750 个共同有效股票月的原始 120 日换手均值完全相同。原截面评分仍不同，因为缩尾与行业去均值所用的有效评分截面改变了。把两组都放在同一组满足 90 个观测的合格股票上重新评分，结果完全相同。原流程先评分、后筛选资格，因此这项受控重算刻意改变了评分股票池。'],
  supportBoundary: ['Coverage and buffer effects overlap with rescoring. Removing nonshared names under the existing 45-observation scores changes 28 formations without a buffer and 35 with it (19 and 25 since 2016). These counts are not additive causal shares. Buffer 40 means ordinary top-40 selection; buffer 60 retains prior holdings within rank 60. Empty startup formations stay in the denominator. No new performance or parameter optimization is implied.', '覆盖变化与缓冲效应会和评分变化重叠。保留 45 个观测版本原评分、移除非共同股票后，无缓冲时有 28 日变化，有缓冲时有 35 日变化（2016 年起分别为 19 与 25 日）。这些数量不能相加解释为因果占比。缓冲 40 等于普通前 40 名选择；缓冲 60 则保留仍在前 60 名的旧持仓。启动期空仓形成日保留在分母内。这不构成新的业绩结论或参数优化。'],
  coverageTitle: ['Corporate actions and historical evidence remain incomplete', '公司行动覆盖与历史运行证据仍不完整'],
  coverageFinding: ['Missing full-window query evidence means no retained evidence of a completed symbol-history request covering the entire audit window; partial-window requests do not qualify. It does not verify the absence of corporate actions. The minimum-45 targets include 125 names and 985 stock-months without this evidence; minimum-90 includes 114 names and 921 stock-months. Each arm also has one positive share-change row without a listing date. Until these gaps and the share ledger reconcile, raw-share readiness remains false.', '“缺少全窗口查询证据”指没有保留证据能证明该股票的历史查询请求已完成且覆盖整个审计窗口；仅覆盖部分窗口的请求不计入。这不代表确认没有公司行动。最低 45 个观测目标中，有 125 只股票、985 个股票月缺少这项证据；最低 90 个观测目标中，有 114 只、921 个股票月。每组还各有一行正向股数变化记录缺少上市日期。在这些缺口与股数账本对齐前，真实股数执行仍未就绪。'],
  history: ['A bounded history trace inspected 20 records, not 20 experiments. Reachable source history explicitly passes 75% support (90 observations for a 120-session window), but no retained standalone invocation, target path or daily series authenticates the original published 7.60% annual return. A helper’s default of 45 does not establish what that missing invocation used. The historical result remains source-reported.', '有范围的历史追查检查了 20 条记录，不是 20 次实验。可达源码历史明确传入 75% 观测门槛（120 日窗口对应 90 个观测），但尚无保留的独立调用、目标路径或逐日序列能认证原公开 7.60% 年化收益。辅助函数默认 45 个观测，不能证明缺失调用采用了该默认值。历史结果仍属于来源报告。'],
  next: ['Stronger conclusions require a reconciled raw-price/raw-share corporate-action ledger, complete action coverage, calibrated costs and impact, and an original runtime receipt binding code, inputs, targets and daily outputs. Preserve the failed recovery and the current-vintage diagnostics as separate evidence.', '更强结论需要原始价格／原始股数公司行动账本对齐、公司行动覆盖完整、成本与冲击校准，以及绑定代码、输入、目标和逐日输出的原始运行收据。未成功的历史找回与当前版本诊断应分别保留。'],
  provenance: ['Reviewed public projection and source fingerprints', '已审查的公开投影与来源指纹'],
  provenanceText: ['This section uses the explicit public aggregate projection reviewed on 2026-10-17. Hashes identify the reviewed evidence artifacts; they do not make the missing historical runtime available. No holdings, symbols, private runtime locators or provider rows are published.', '本节使用于 2026-10-17 审查的明确公开汇总投影。哈希用于识别已审查证据制品，不能补回缺失的历史运行。未公开持仓、证券代码、私有运行位置或供应商原始行。'],
  svgLink: ['Download execution chart', '下载执行对照图'],
  dataLink: ['Download the reviewed aggregate JSON', '下载已审查的汇总 JSON'],
} satisfies Record<string, LocalText>;

export const executionLabels: Record<string, LocalText> = {
  ideal_one_day: ['Ideal one-day share/cash', '理想单日份额／现金'],
  retry_tradable_unlimited: ['Tradable retries, unlimited capacity', '可交易日重试，不设容量上限'],
  same_day_capacity: ['5% realized-amount cap', '当日实际成交额 5% 上限'],
  same_day_capacity_lots: ['Realized cap + 100-unit lots', '当日上限＋100 单位整手'],
  same_day_capacity_lots_t1: ['Realized cap + lots + T+1', '当日上限＋整手＋T+1'],
  same_day_capacity_lots_t1_limits: ['Realized cap + lots + T+1 + limits', '当日上限＋整手＋T+1＋涨跌停'],
  prior20_budget: ['Prior-20 budget + lots + T+1 + limits', '前 20 日预算＋整手＋T+1＋涨跌停'],
  prior20_budget_realized_guard: ['Prior-20 budget + realized guard + lots + T+1 + limits', '前 20 日预算＋当日保护＋整手＋T+1＋涨跌停'],
};
const supportLabels: Record<keyof typeof review.support, LocalText> = {
  support_no_buffer: ['Full 45 vs 90; buffer 40', '完整 45 对 90；缓冲 40'],
  support_buffer: ['Full 45 vs 90; buffer 60', '完整 45 对 90；缓冲 60'],
  shared_scores_no_buffer: ['Common names, existing scores; buffer 40', '共同股票、原评分；缓冲 40'],
  shared_scores_buffer: ['Common names, existing scores; buffer 60', '共同股票、原评分；缓冲 60'],
  coverage_s45_b40: ['Full vs common names, existing 45 scores; buffer 40', '完整对共同股票、45 原评分；缓冲 40'],
  coverage_s45_b60: ['Full vs common names, existing 45 scores; buffer 60', '完整对共同股票、45 原评分；缓冲 60'],
};
export const sourceLabels: Record<string, LocalText> = {
  execution_metrics: ['Execution metrics', '执行指标'], execution_receipt: ['Execution receipt', '执行收据'],
  support_summary: ['Support summary', '门槛对照汇总'], support_receipt: ['Support receipt', '门槛对照收据'],
  action_coverage: ['Action coverage', '公司行动覆盖'], accounting_review: ['Accounting review', '核算复核'],
  historical_trace: ['Historical trace', '历史追查'],
};
export const followupText = (value: LocalText, locale: FollowupLocale) => value[locale === 'zh-CN' ? 1 : 0];
const choose = (en: string, zh: string, locale: FollowupLocale) => locale === 'zh-CN' ? zh : en;
const number = (value: number, locale: FollowupLocale, digits = 2) => new Intl.NumberFormat(locale, { minimumFractionDigits: digits, maximumFractionDigits: digits }).format(value);
export function executionTable(locale: FollowupLocale) {
  const missing = choose('Not reported', '未报告', locale);
  return {
    headers: choose('Scenario|Net annual %|Max drawdown %|Sharpe|Fill %|Avg cash %|Fills above 5% realized amount', '情景|净年化 %|最大回撤 %|夏普|成交 %|平均现金 %|超过当日成交额 5% 的笔数', locale).split('|'),
    rows: review.execution.map(row => [followupText(executionLabels[row.id], locale), number(row.net_annual_return, locale), number(row.net_max_drawdown, locale), number(row.net_sharpe, locale, 3), row.fill_ratio === null ? missing : number(row.fill_ratio * 100, locale), row.avg_cash_weight === null ? missing : number(row.avg_cash_weight * 100, locale), row.fills_over_5pct_realized_amount === null ? missing : number(row.fills_over_5pct_realized_amount, locale, 0)]),
  };
}
export function supportTable(locale: FollowupLocale) {
  return {
    headers: choose('Intervention|Different / 138 formations|Different / 127 since 2016', '干预对照|不同／138 个形成日|2016 年起不同／127 日', locale).split('|'),
    rows: (Object.keys(supportLabels) as Array<keyof typeof review.support>).map(key => [followupText(supportLabels[key], locale), String(review.support[key].different), String(review.support[key].different_2016plus)]),
  };
}
export function coverageTable(locale: FollowupLocale) {
  return {
    headers: choose('Minimum observations|Selected names|Stock-months|Names with full-window query evidence|Names without full-window query evidence|Stock-months without full-window query evidence|Positive share rows missing listing date', '最低观测数|入选股票数|股票月|有全窗口查询证据的股票|缺全窗口查询证据的股票|缺全窗口查询证据的股票月|缺上市日期的正向股数变化行', locale).split('|'),
    rows: (['45', '90'] as const).map(key => { const row = review.action_coverage[key]; return [key, ...[row.names, row.stock_months, row.queried_names, row.unqueried_names, row.unqueried_stock_months, row.positive_share_rows_missing_listing_date].map(n => number(n, locale, 0))]; }),
  };
}
const markdownTable = (data: {headers: string[]; rows: string[][]}) => [data.headers, data.headers.map(() => '---'), ...data.rows].map(row => `| ${row.map(cell => cell.replaceAll('|', '\\|')).join(' | ')} |`).join('\n');
export function followupMarkdown(locale: FollowupLocale) {
  const t = (key: keyof typeof followupCopy) => followupText(followupCopy[key], locale);
  return [
    `## ${t('title')}`, t('conclusion'), t('scope'), t('accounting'),
    `### ${t('executionTitle')}`, t('executionFinding'), t('synthetic'), t('executionRules'), t('suspension'), `![${t('chartTitle')}](https://runchengxie.github.io/quant-market-research/downloads/microcap-execution-followup.${locale}.svg)`, markdownTable(executionTable(locale)), t('metricMeaning'),
    `### ${t('supportTitle')}`, t('supportFinding'), t('supportMechanism'), markdownTable(supportTable(locale)), t('supportBoundary'),
    `### ${t('coverageTitle')}`, t('coverageFinding'), markdownTable(coverageTable(locale)), t('history'), t('next'),
    `### ${t('provenance')}`, t('provenanceText'),
    `[${t('dataLink')}](https://runchengxie.github.io/quant-market-research/data/microcap_followup_review.json)`,
    ...Object.entries(review.source_hashes).map(([key, hash]) => `- ${followupText(sourceLabels[key], locale)}: \`${hash}\``),
  ].join('\n\n');
}

export function buildFollowupSvg(locale: FollowupLocale) {
  const t = (key: keyof typeof followupCopy) => followupText(followupCopy[key], locale);
  const escape = (value: string) => value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('"', '&quot;');
  const rows = review.execution;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="620" viewBox="0 0 1100 620" role="img" aria-labelledby="title desc"><title id="title">${escape(t('chartTitle'))}</title><desc id="desc">${escape(t('chartDescription'))} ${rows.map(row => `${escape(followupText(executionLabels[row.id], locale))}: ${number(row.net_annual_return, locale)}%`).join('; ')}</desc><rect width="1100" height="620" fill="var(--surface,#fff)"/><g font-family="sans-serif" fill="var(--ink,#252525)"><text x="24" y="36" font-size="22">${escape(t('chartTitle'))}</text>${[0,2,4,6].map(value => `<line x1="${590+value/6*400}" x2="${590+value/6*400}" y1="55" y2="516" stroke="var(--rule,#d5d8df)"/><text x="${590+value/6*400}" y="542" text-anchor="middle" font-size="15">${value}%</text>`).join('')}${rows.map((row,i) => `<text x="24" y="${92+i*56}" font-size="15">${escape(followupText(executionLabels[row.id], locale))}</text><rect x="590" y="${72+i*56}" width="${row.net_annual_return/6*400}" height="27" fill="var(--accent-strong,#1267d6)"/><text x="${600+row.net_annual_return/6*400}" y="${92+i*56}" font-size="16">${number(row.net_annual_return, locale)}%</text>`).join('')}<text x="24" y="577" font-size="15">${escape(t('chartUnit'))}</text><text x="24" y="605" font-size="14">${locale === 'zh-CN' ? '2015-03-02—2026-07-31；复权合成份额；不证明真实股数可执行或容量。' : '2015-03-02–2026-07-31; adjusted synthetic shares; no raw-share investability or capacity claim.'}</text></g></svg>`;
}
