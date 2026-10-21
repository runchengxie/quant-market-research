export const valuationCopy = {
  title: ['Low-valuation research', '低估值研究'],
  introduction: ['How cheap have A-share stocks been, why do definitions disagree, and what do valuation factors establish? Explore historical distributions, annual comparisons and the limits of return evidence.', 'A 股历史上能有多便宜，不同口径为什么选出不同股票，估值因子又能说明什么？这里把年度比较、分组分布和收益证据放在一起读。'],
  warning: ['Unpublished retrospective exploration. Financial and reconstructed ST histories both have revision_safe=false. The original financial-template coverage gap remains. These are conditional samples, not a certified complete market or executable portfolio.', '未发布的历史探索草稿。财务历史和重建 ST 历史均为 revision_safe=false。原面板金融模板覆盖缺口仍在。结果属于条件样本，尚未认证全市场完整性或组合可执行性。'],
  date: ['Formation date', '形成日期'], group: ['Stock group', '股票分组'], metric: ['Valuation definition', '估值口径'], basis: ['Sample basis', '样本口径'],
  all_market: ['All quoted names (including unknown)', '全部有报价证券（含未知）'], non_st: ['Non-ST', '非 ST'], st: ['ST', 'ST'], star_st: ['*ST', '*ST'], unknown: ['Unknown status', '未知状态'],
  metric_available: ['Available for this metric', '该指标可用样本'], common_five: ['All five positive, matching report period', '五口径均为正且报告期一致'],
  pe_ttm: ['Parent-profit PE TTM', '归母利润 PE TTM'], pe_deducted_proxy: ['Deducted-profit PE TTM proxy', '扣非 PE TTM proxy'], pb_parent: ['Parent-equity PB', '归母权益 PB'], pb_ex_goodwill_proxy: ['PB excluding goodwill proxy', '扣商誉 PB proxy'], pb_ex_intangibles_proxy: ['PB excluding goodwill and intangibles proxy', '扣商誉及无形资产 PB proxy'],
  distribution: ['Valuation distribution', '估值分布'], supported: ['Valid positive / candidate records', '有效正值／候选记录'], equal_mean: ['Equal-weight arithmetic mean', '等权算术均值'], totals: ['Total market value / total denominator', '总市值／总分母'], median: ['Median', '中位数'], minimum: ['Minimum valid positive value', '最小有效正值'], range: ['P01 / P25 / P75 / P99', 'P01／P25／P75／P99'],
  aggregation: ['The two aggregates use the identical valid sample. Ratio of totals is neither an arithmetic nor a market-cap-weighted mean. Zero/negative denominators are unavailable, and missing assets are not zero.', '两种聚合使用完全相同的有效样本。“总市值／总分母”不等于算术均值或市值加权均值。零、负分母不可用，缺失资产不填零。'],
  minimum_note: ['A minimum is an extreme accounting ratio, not a trading recommendation. Its security, denominator, market value, ties and warning flags are retained in the private audit. Only aggregates appear here.', '最小值是极端会计比率，不构成选股建议。对应证券、分母、市值、并列值及风险标记保留在私有核查表中；此处仅展示聚合结果。'],
  proxy_note: ['Adjusted PB subtracts consolidated goodwill and intangibles from parent equity. Parent/minority allocation, preferred equity and multi-class market value are not certified; proxy labels remain.', '调整 PB 从归母权益扣除集团合并商誉和无形资产。归母与少数股东分配、优先股及多股类市值尚未认证，继续保留 proxy 标签。'],
  trend: ['Historical median on a logarithmic vertical scale', '历史中位数，纵轴为对数刻度'],
  coverage: ['Unknown state is separate, never inferred normal from a missing ST row. All-quoted statistics include unknown names; return diagnostics additionally require a listing interval.', '未知状态单列，不能因 ST 正样本缺行就认定正常股。全部报价统计包含未知证券；收益诊断另须有上市区间。'],
  factor: ['Conditional factor diagnostics · 2023–2025', '条件样本因子诊断 · 2023–2025'],
  factor_basis: ['Factor diagnostics always use the available sample for this metric (metric_available), independently of the distribution sample selector above.', '因子诊断固定使用该指标可用样本（metric_available），不随上方分布样本口径选项切换。'],
  factor_note: ['Lower multiples receive higher scores. Rank IC compares that score with next-session close to next-formation-next-session close adjusted-price returns, conditional on resolved endpoints. Groups are selected before future availability; any missing member invalidates its entire quintile return.', '估值越低，因子分数越高。Rank IC 对照下一交易日收盘至下期形成日后交易日收盘的复权价格收益，条件是端点可核实。先分组再核对未来资料，任一成员缺失即该五分组收益不可用。'],
  execution: ['Endpoint suspension/limit flags and delisting are checked. Intramonth fills, dividend/action cash accounting, impact and borrowing are not established. The 0/10/30 bp additive traded-notional scenarios are cost sensitivity only. Missing previous marks make turnover/net unavailable; no cash reset or zero return is invented.', '检查端点停牌、涨跌停及退市。尚无持有期内成交、分红送转现金账本、冲击或融券证明。0／10／30 基点的交易名义额扣费仅为成本敏感性。上期持仓无法计价时换手和净值不可用，不重置为现金或编造零收益。'],
  ic: ['Mean Rank IC / observed months', '平均 Rank IC／有效月份'], tails: ['Cheap minus expensive / paired months', '低估值减高估值／配对月份'], q: ['Quintile (1 = cheapest)', '五分组（1 为最便宜）'], gross: ['Mean monthly gross / complete months', '月均毛收益／完整月份'], turnover: ['Mean traded notional / months', '平均交易名义额／月份'], cost0: ['0 bp scenario / months', '0 基点情景／月份'], cost10: ['10 bp scenario / months', '10 基点情景／月份'], cost30: ['30 bp scenario / months', '30 基点情景／月份'],
  support: ['Every value shows its own support. Gross and cost estimates can cover different months; there is no full-history CAGR across gaps. Cheap-minus-expensive is a descriptive spread without a borrow claim.', '每个数值附带自己的样本数。毛收益与成本情景可能覆盖不同月份，不跨缺口计算整段年化。低减高只是描述性收益差，没有融券可得性结论。'],
  not_available: ['unavailable', '不计算／不可用'], unknown_factor: ['Factor diagnostics are unavailable for unknown status as a separate trading universe.', '未知状态不能单独充当交易股票池，因子诊断不计算。'],
  method: ['Methods, provenance and reproduction', '方法、来源与复现'], download: ['Download draft aggregates', '下载草稿聚合结果'], draft: ['Draft · not deployed', '草稿 · 未部署'],
  formula: ['Formula', '公式'],
} as const;

export type ValuationCopyKey = keyof typeof valuationCopy;

export const valuationFormulas: Record<string, string> = {
  pe_ttm: 'M / TTM(n_income_attr_p)', pe_deducted_proxy: 'M / TTM(profit_dedt) [proxy]',
  pb_parent: 'M / total_hldr_eqy_exc_min_int', pb_ex_goodwill_proxy: 'M / (parent equity − goodwill) [proxy]',
  pb_ex_intangibles_proxy: 'M / (parent equity − goodwill − intan_assets) [proxy]',
};
