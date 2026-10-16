// Reviewed bilingual copy is pinned to the exact aggregate content digest.
const translationReviewDigest = '966fa7ea1c959adc487416d70eb5b03dd268cc12f35a5439b230556085734e7e';
const translations = {
  'etf-rotation': {
    title: ['ETF rotation: historical diagnostic', 'ETF 轮动：历史诊断'],
    question: ['Did the retained ETF recipes beat simple holdings across the matched historical window?', '在可匹配的历史区间内，保留的 ETF 配方是否跑赢简单持有？'],
    conclusion: ['No recipe is ready for promotion. At 25 bps all three trail the fixed ETF basket. A small zero-cost raw-price advantage for the ranker does not persist under the adjusted-price convention.', '目前没有配方达到晋级条件。按 25 个基点成本，三种模型都落后于固定 ETF 篮子。排序模型在原始价格、零成本情景下有小幅优势，但在复权价格口径下不再成立。'],
    baseline: ['Initially equal-weight fixed-share basket and single-ETF buy-and-hold, charged the same initial fee on matching dates.', '基准为起始等权、固定份额的 ETF 篮子，以及单只 ETF 持有；在相同日期计入相同的初始费用。'],
    scope: ['Conditional matched-mark tail: 1,183 open-to-open periods, 2021-02-18 to 2025-12-31; fixed basket of three current ETFs, not reconstructed historical membership.', '条件匹配后的尾段：2021-02-18 至 2025-12-31，共 1,183 个开盘到开盘区间；使用三只当前 ETF 组成的固定篮子，没有重建历史成分。'],
    limitations: ['The full window is blocked by a missing opening mark. Backfilled history has no independent historical-availability receipt; this was not an untouched holdout. Adjusted prices are a valuation sensitivity, not a broker cash-flow ledger. Fee levels are scenarios, not brokerage quotes. Execution, corporate actions and capacity remain unaudited.', '完整区间因缺少开盘价标记而无法计算。回填历史没有独立的历史可得性凭证，本次也不是未参与调参的留出集。复权价格只是估值敏感性口径，不是券商现金流账本。费用水平是情景假设，不是券商报价；执行、公司行为和容量仍未审计。'],
    reading: ['The first chart compares cumulative returns under four assumed one-way costs and two price conventions. The second separates the regression recipe’s calendar-year pattern from the fixed basket. Neither chart is a fresh out-of-sample test.', '第一张图按四档单边成本和两种价格口径比较累计收益。第二张图把回归模型与固定篮子的逐年表现并排列出。两张图都不是新的样本外检验。'],
    nextStep: ['The useful next step is a new sample with a dated availability receipt, a frozen comparison and a cost-aware ledger. Until then, treat the regression result as unresolved and keep the other recipes out of promotion.', '下一步应当取得带日期凭证的新样本，预先冻结比较方案，并统一交易成本账本。在此之前，回归模型仍属结论未定，其余配方也不应晋级。'],
  },
  hotsector: {
    title: ['Hotspot overlay: historical diagnostic', '热点叠加筛选：历史诊断'],
    question: ['Did an individual-stock heat overlay improve the same hotspot candidate base?', '在相同热点候选池上，个股热度叠加筛选是否带来改善？'],
    conclusion: ['The overlay improves three of four fixed five-session events at each tested cost. Four events do not establish a reliable edge or validate the complete hotspot strategy.', '在每种测试成本下，四个固定五日事件中有三个因叠加筛选而改善。四个事件不足以证明稳定优势，也不能验证完整热点策略。'],
    baseline: ['Paired candidate arms share the same observed topic and membership base; the comparison changes only the additional individual-stock heat overlay.', '两组使用相同的主题和候选池，只比较是否额外叠加个股热度筛选。'],
    scope: ['Four isolated 2025 signal dates; each event holds for five sessions. Returns use selected opening-price marks and events do not form a continuous portfolio.', '2025 年四个彼此独立的信号日期；每个事件持有五个交易日。收益使用选定的开盘价标记，这些事件不构成连续投资组合。'],
    limitations: ['Historical snapshots do not prove when each input was available to a live researcher. Only four isolated events are available; this is not a significance test, untouched sample, or complete strategy comparison. Raw opening prices omit corporate-action cash flows. Suspensions, price limits, lot sizes and capacity are unaudited.', '历史快照不能证明当时研究者何时能拿到每项输入。这里只有四个独立事件，不是显著性检验、未触碰样本或完整策略比较。原始开盘价未计入公司行为现金流；停牌、涨跌停、交易单位和容量仍未审计。'],
    reading: ['The chart shows the average paired return difference and how many of the four events favored the overlay. These are separate summaries of the same four events, not extra observations. Event-by-event dates and returns are intentionally not published.', '图表展示配对收益差的平均值，以及四个事件中叠加组占优的数量。它们是同一批四个事件的两种汇总，不是新增样本。网页不公开逐个事件的日期和收益。'],
    nextStep: ['A stronger test needs new signal dates, proof that each input was available at the time, and a continuous portfolio comparison against a topic-free candidate base.', '更有力的检验需要新的信号日期、每项输入当时可得的凭证，以及与不带主题筛选的候选池进行连续组合比较。'],
  },
} as const;

export const legacyCopy = {
  shared: {
    stage: ['Historical diagnostic; not investment validation', '历史诊断，尚非投资有效性验证'],
    metrics: ['Aggregate results', '汇总结果'],
    metricNote: ['Returns are percentages. “bps” means basis points. Annual slices are exploratory and were computed after the full-window result was known. Bootstrap ranges are descriptive, not formal significance tests.', '收益以百分比表示；bps 为基点。年度拆分是在完整区间结果已知后计算的探索性结果。自助抽样区间仅作描述，不是正式显著性检验。'],
    noPromotion: ['These diagnostics do not establish profitability or readiness for live trading.', '这些诊断结果不能证明策略盈利，也不代表适合实盘交易。'],
    reading: ['How to read these charts', '图表怎么看'],
    next: ['What would make the next test useful', '下一步要补什么'],
    factors: ['Related factor methods', '相关因子方法'],
    factorBoundary: ['Factor links are conceptual references; their datasets and definitions are not interchangeable with strategy inputs.', '因子链接仅作方法参考，所用数据集和定义不能与策略输入直接替换。'],
    provenance: ['Reviewed source and public-content fingerprints', '已审查的来源与公开内容指纹'],
    return: ['Value', '数值'],
    details: ['Metric definitions', '指标说明'],
  },
} as const;

type Study = { id: string; question: string; conclusion: string; baseline: string; sample_scope: string; limitations: string[] };

export function legacyStudyCopy(study: Study, reviewedContentDigest: string) {
  if (reviewedContentDigest !== translationReviewDigest) throw new Error('Translation content requires review against the changed public evidence');
  if (!(study.id in translations)) throw new Error('Study translation unavailable');
  const t = translations[study.id as keyof typeof translations];
  return { title: t.title, question: t.question, conclusion: t.conclusion, reading: t.reading, nextStep: t.nextStep,
    baseline: [study.baseline, t.baseline], scope: [study.sample_scope, t.scope],
    limitations: [study.limitations.join(' '), t.limitations] } as const;
}

const modelLabels: Record<string, [string, string]> = {
  linear_rank: ['Linear rank', '线性排序'], lightgbm_regression: ['LightGBM regression', 'LightGBM 回归'],
  lightgbm_ranker: ['LightGBM ranker', 'LightGBM 排序'], fixed_share_basket: ['Fixed-share basket', '固定份额篮子'],
  single_etf_510300: ['Single ETF baseline', '单只 ETF 基准'], without_overlay: ['Without overlay', '不叠加热度'], with_overlay: ['With overlay', '叠加热度'],
};
export function metricLabel(name: string, locale: 'en' | 'zh') {
  const parts = name.split('.');
  const model = modelLabels[parts.find(part => part in modelLabels) ?? ''];
  const year = parts.find(part => /^year_\d{4}$/.test(part));
  const date = parts.find(part => /^2025-\d\d-\d\d$/.test(part));
  const cost = parts.find(part => /^cost_\d+_bps$/.test(part))?.replace('cost_', '').replace('_bps', '');
  const valuation = parts.includes('raw') ? (locale === 'en' ? 'Raw price' : '原始价格') : parts.includes('factor_adjusted') ? (locale === 'en' ? 'Adjusted price' : '复权价格') : '';
  const kind = name.includes('maximum_drawdown') ? (locale === 'en' ? 'Max drawdown' : '最大回撤') : name.includes('calendar_return') ? (locale === 'en' ? 'Calendar return' : '年度收益') : name.includes('relative_log_return_ci95') ? (locale === 'en' ? (name.includes('.low.') ? 'Interval lower bound' : 'Interval upper bound') : (name.includes('.low.') ? '区间下界' : '区间上界')) : name.includes('positive_event_count') ? (locale === 'en' ? 'Positive events' : '正向事件数') : name.includes('mean_event_delta') ? (locale === 'en' ? 'Mean event uplift' : '事件平均增量') : name.includes('event_delta') ? (locale === 'en' ? 'Overlay uplift' : '叠加筛选增量') : name.includes('event_return') ? (locale === 'en' ? 'Event return' : '事件收益') : (locale === 'en' ? 'Cumulative return' : '累计收益');
  return [valuation, model?.[locale === 'en' ? 0 : 1], year?.slice(-4), date, cost && (locale === 'en' ? `${cost} bps` : `${cost} 基点`), kind].filter(Boolean).join(' · ');
}

export function metricDefinition(name: string, locale: 'en' | 'zh') {
  if (name.includes('relative_log_return_ci95')) return locale === 'en'
    ? '95% descriptive interval for annualized paired relative log return versus the fixed basket, from 10,000 circular block resamples of 20 periods; not a formal significance test.'
    : '相对固定篮子的年化配对对数收益率之 95% 描述性区间，使用 10,000 次、区块长度 20 期的循环区块重抽样；不是正式显著性检验。';
  if (name.includes('calendar_return')) return locale === 'en'
    ? 'Exploratory compounded calendar-year return grouped by exit year, calculated after the full-period result was known.'
    : '按退出年份汇总的探索性年度复合收益，在完整区间结果已知后计算。';
  if (name.includes('maximum_drawdown')) return locale === 'en'
    ? 'Largest peak-to-trough NAV decline in the stated valuation convention at 25 bps assumed cost.'
    : '在对应价格口径和假设 25 基点成本下，净值从峰值到谷值的最大跌幅。';
  if (name.includes('mean_event_delta')) return locale === 'en'
    ? 'Unweighted mean paired uplift across four isolated five-session events, in percentage points; not a continuous portfolio return.'
    : '四个独立五日事件的配对增量算术平均值，单位为百分点；不代表连续投资组合收益。';
  if (name.includes('positive_event_count')) return locale === 'en'
    ? 'Number of the four isolated events where the overlay return exceeded the no-overlay return.'
    : '四个独立事件中，叠加筛选组收益高于未叠加组的事件数。';
  return locale === 'en'
    ? 'Cumulative net NAV change over 1,183 matched open-to-open periods under the stated price and fee convention.'
    : '在所示价格和费用口径下，1,183 个匹配开盘到开盘区间的净值累计变化。';
}
