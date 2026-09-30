const sourceNoteTranslations: Record<string, string> = {
  "2015 年起清洗口径覆盖 ST、停牌和价格质量规则，适合做当前主分析。": "The cleaned basis from 2015 applies special-treatment, suspension, and price-quality rules and is suitable for the primary analysis.",
  "2008 年起历史口径覆盖更长，但历史源缺少可靠的 ST/停牌标记，标记为 incomplete，不应与清洗口径直接视为同一序列。": "The historical basis begins in 2008 but lacks reliable special-treatment and suspension flags. It is marked incomplete and should not be treated as the same series as the cleaned basis.",
  "N=1 只有每日市值最小的一只股票，受个股异常、停牌、涨跌停和资格切换影响很大，仅作为极端诊断，不代表可交易组合。": "N=1 contains only the smallest stock by market value each day. It is highly sensitive to single-stock events, suspensions, price limits, and eligibility changes; it is an extreme-case diagnostic, not a tradable portfolio.",
  "网页发布年度和月度汇总及审计摘要；完整日频明细保留在仓库外的研究输出目录。": "The site publishes annual and monthly summaries plus an audit summary. Full daily details remain in the research output directory outside the repository.",
  "1999 年至 2021 年 3 月以前的历史主要属于回溯数据。": "Most observations before March 2021 were backfilled.",
  "月频最大回撤会低估日内和日间回撤。": "Monthly maximum drawdown understates intramonth and interday drawdowns.",
  "公开资料参考口径不是 Tushare 直接返回的 Wind 原始序列。": "The public-reference series is not the raw Wind series returned directly by Tushare.",
  "这是基于本地 Tushare 日线数据的规则重建，不是 Wind 8841431.WI 官方指数。": "This is a rule-based reconstruction from local Tushare daily data, not the official Wind 8841431.WI index.",
  "使用复权收盘价计算，当前版本未模拟涨跌停无法成交、手续费、印花税、冲击成本和资金容量。": "Returns use adjusted closing prices. This version does not simulate unfilled trades at price limits, commissions, stamp duty, market impact, or capital capacity.",
  "调仓信号使用当日总市值，收益从下一交易日收盘价计算，保留了一天的持有滞后。": "Rebalancing signals use same-day total market value; returns begin at the next trading-day close, retaining a one-day holding lag.",
  "strict 是唯一主口径；其余均为敏感性，不用于替换网页主曲线。": "Strict is the sole primary basis. Other variants are sensitivities and do not replace the main site series.",
  "carry_evidence_only 只对有明确 suspend_d 证据的缺失按 0 收益处理。": "carry_evidence_only assigns a zero return only to missing prices with explicit suspend_d evidence.",
  "退市没有可验证的日期和清算价格，因此不做隐含填值。": "Verified delisting dates and liquidation prices are unavailable, so missing values are not imputed.",
  "历史区间缺少与2015年以后完全一致的ST和停牌字段。": "The historical period does not have special-treatment and suspension fields fully consistent with those available after 2015.",
  "这是规则重建的描述性序列，不代表Wind官方指数或可成交策略净值。": "This descriptive series is a rule-based reconstruction, not the official Wind index or an executable strategy NAV.",
  "最长水下期只统计已完成区间，当前右删失区间单独计数。": "The longest underwater period uses completed episodes only; currently right-censored episodes are counted separately.",
  "每个 N 的汇总来自 return_unknown_flat 情景。该情景把已分类的缺价按前值持平处理。": "Each N summary uses the return_unknown_flat scenario, which carries forward the prior value for classified missing prices.",
  "最长已完成水下期只包含已经回到前高的区间。样本末仍低于前高的区间计为右删失，不能据此断言最终恢复时间。": "The longest completed underwater period includes only episodes that recovered to a prior high. Episodes still below the prior high at the sample end are right-censored and do not establish their eventual recovery time.",
  "2008–2014 各年都有价格和市值记录，但历史源的 ST 与停牌资格字段不完整，年度 eligible_rows 只用于覆盖审计。": "Price and market-value records exist for every year from 2008 through 2014, but the source has incomplete special-treatment and suspension eligibility fields. Annual eligible_rows are for coverage audits only.",
};

export const sourceNoteTranslationsForAudit = sourceNoteTranslations;

export function sourceNotes(notes: string[], locale = typeof document === "undefined" || document.documentElement.lang !== "zh-CN" ? "en-US" : "zh-CN") {
  return locale === "zh-CN"
    ? notes.join(" ")
    : notes.map((note) => sourceNoteTranslations[note] ?? "An untranslated research note is available in the Chinese source.").join(" ");
}
