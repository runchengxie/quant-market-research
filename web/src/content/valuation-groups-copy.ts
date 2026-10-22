export const valuationCopy = {
  title: ['Low-valuation research', '低估值研究'],
  introduction: ["How cheap have A-share stocks been, and does buying cheaper stocks pay? Read the findings first, then compare the evidence and trading assumptions.", "A 股历史上能有多便宜，买便宜股票是否更赚钱？先看目前的发现，再查看数据和交易假设。"],
  warning: ["This research is public, but the results remain exploratory. Historical financial data and reconstructed ST status may contain later revisions. Financial-company report coverage is incomplete. Results describe only the stocks with usable data and do not establish complete market coverage or achievable trading returns.", "研究页面已经公开，结果仍处于探索阶段。历史财务数据和事后重建的 ST 状态可能混入后来的修订，金融类公司的财报数据也有缺漏。结果只描述现有数据能覆盖的股票，尚不能代表全市场，也不能据此判断实际交易能赚多少。"],
  date: ["Sample date", "采样日期"], group: ['Stock group', '股票分组'], metric: ['Valuation definition', '估值口径'], basis: ['Sample basis', '样本口径'],
  all_market: ['All quoted names (including unknown)', '全部有报价证券（含未知）'], non_st: ['Non-ST', '非 ST'], st: ['ST', 'ST'], star_st: ['*ST', '*ST'], unknown: ['Unknown status', '未知状态'],
  metric_available: ['Available for this metric', '该指标可用样本'], common_five: ['All five positive, matching report period', '五口径均为正且报告期一致'],
  pe_ttm: ['Parent-profit PE TTM', '归母利润 PE TTM'], pe_deducted_proxy: ["Deducted-profit PE TTM estimate", "扣非市盈率（近一年，近似计算）"], pb_parent: ['Parent-equity PB', '归母权益 PB'], pb_ex_goodwill_proxy: ["PB excluding goodwill estimate", "扣商誉市净率（近似计算）"], pb_ex_intangibles_proxy: ["PB excluding goodwill and intangibles estimate", "扣商誉及无形资产市净率（近似计算）"],
  distribution: ['Valuation distribution', '估值分布'], supported: ['Valid positive / candidate records', '有效正值／候选记录'], equal_mean: ['Equal-weight arithmetic mean', '等权算术均值'], totals: ['Total market value / total denominator', '总市值／总分母'], median: ['Median', '中位数'], minimum: ['Minimum valid positive value', '最小有效正值'], range: ['P01 / P25 / P75 / P99', 'P01／P25／P75／P99'],
  aggregation: ['The two aggregates use the identical valid sample. Ratio of totals is neither an arithmetic nor a market-cap-weighted mean. Zero/negative denominators are unavailable, and missing assets are not zero.', '两种聚合使用完全相同的有效样本。“总市值／总分母”不等于算术均值或市值加权均值。零、负分母不可用，缺失资产不填零。'],
  minimum_note: ['A minimum is an extreme accounting ratio, not a trading recommendation. Its security, denominator, market value, ties and warning flags are retained in the private audit. Only aggregates appear here.', '最小值是极端会计比率，不构成选股建议。对应证券、分母、市值、并列值及风险标记保留在私有核查表中；此处仅展示聚合结果。'],
  proxy_note: ["Adjusted PB subtracts consolidated goodwill and intangibles from parent equity. Ownership scopes, preferred equity and multi-class market value have not been fully reconciled, so these remain estimates (proxy).", "调整后的市净率从归母净资产中扣除合并报表的商誉或无形资产。两者的股东归属范围尚未完全对齐，优先股和多股类市值也未核实，因此仍属于近似计算，公式保留 proxy 标记。"],
  trend: ['Historical median on a logarithmic vertical scale', '历史中位数，纵轴为对数刻度'],
  coverage: ['Unknown state is separate, never inferred normal from a missing ST row. All-quoted statistics include unknown names; return diagnostics additionally require a listing interval.', '未知状态单列，不能因 ST 正样本缺行就认定正常股。全部报价统计包含未知证券；收益诊断另须有上市区间。'],
  factor: ["Did cheaper stocks perform better in the usable sample? · 2023–2025", "在可核实的样本里，便宜股票后来表现怎样 · 2023–2025"],
  factor_basis: ['Factor diagnostics always use the available sample for this metric (metric_available), independently of the distribution sample selector above.', '因子诊断固定使用该指标可用样本（metric_available），不随上方分布样本口径选项切换。'],
  factor_note: ["Lower multiples receive higher scores. Rank IC compares cheapness ranks with subsequent return ranks. Adjusted-price returns run from the next trading-day close to the close after the next sample date. Only verifiable endpoints enter this comparison, which can select the sample. Groups are formed first; a missing member makes the whole quintile return unavailable.", "估值越低，分数越高。Rank IC 比较便宜程度与后续收益的排名关系。收益从采样后的下一交易日收盘，算到下期采样后的下一交易日收盘，使用复权价格。只有起止数据可核实的股票参与比较，因此可能产生样本偏差。股票先分组，任一成员的数据缺失，整组收益就保留为空。"],
  execution: ['Endpoint suspension/limit flags and delisting are checked. Intramonth fills, dividend/action cash accounting, impact and borrowing are not established. The 0/10/30 bp additive traded-notional scenarios are cost sensitivity only. Missing previous marks make turnover/net unavailable; no cash reset or zero return is invented.', '检查端点停牌、涨跌停及退市。尚无持有期内成交、分红送转现金账本、冲击或融券证明。0／10／30 基点的交易名义额扣费仅为成本敏感性。上期持仓无法计价时换手和净值不可用，不重置为现金或编造零收益。'],
  ic: ["Mean Rank IC / observed months", "便宜程度与后续收益的排名相关／有效月数"], tails: ["Cheap minus expensive / paired months", "便宜组减贵组的月均收益／可比较月数"], q: ['Quintile (1 = cheapest)', '五分组（1 为最便宜）'], gross: ['Mean monthly gross / complete months', '月均毛收益／完整月份'], turnover: ['Mean traded notional / months', '平均交易名义额／月份'], cost0: ['0 bp scenario / months', '0 基点情景／月份'], cost10: ['10 bp scenario / months', '10 基点情景／月份'], cost30: ['30 bp scenario / months', '30 基点情景／月份'],
  support: ['Every value shows its own support. Gross and cost estimates can cover different months; there is no full-history CAGR across gaps. Cheap-minus-expensive is a descriptive spread without a borrow claim.', '每个数值附带自己的样本数。毛收益与成本情景可能覆盖不同月份，不跨缺口计算整段年化。低减高只是描述性收益差，没有融券可得性结论。'],
  not_available: ['unavailable', '不计算／不可用'], unknown_factor: ['Factor diagnostics are unavailable for unknown status as a separate trading universe.', '未知状态不能单独充当交易股票池，因子诊断不计算。'],
  method: ['Methods, provenance and reproduction', '方法、来源与复现'], download: ['Download draft aggregates', '下载草稿聚合结果'], draft: ["Exploratory research · trading not validated", "探索性研究 · 尚未验证实际交易"],
  formula: ['Formula', '公式'],
} as const;

export type ValuationCopyKey = keyof typeof valuationCopy;

export const valuationFormulas: Record<string, string> = {
  pe_ttm: 'M / TTM(n_income_attr_p)', pe_deducted_proxy: 'M / TTM(profit_dedt) [proxy]',
  pb_parent: 'M / total_hldr_eqy_exc_min_int', pb_ex_goodwill_proxy: 'M / (parent equity − goodwill) [proxy]',
  pb_ex_intangibles_proxy: 'M / (parent equity − goodwill − intan_assets) [proxy]',
};
