import { useState } from "react";
import { readableNotes } from "../../research-copy";
import { asNumber, displayLabels, displayValue, formatNumber as num, formatPercent as pct } from "../../lib/format";
import { parseCsv } from "../../lib/public-data";
import RecoverySection from "../RecoverySection";
import ReplicationSection from "../ReplicationSection";
import { LiquidityPage } from "./liquidity-page";
import { NavChart, AnnualChart, MetricChart, UnderwaterChart } from "../MicrocapCharts";
import { ResearchBarChart, ResearchLineChart } from "../ResearchCharts";
import { Stat, Panel, SectionHeading, ResearchCard, LineChart, ControlBar, Choice, MicrocapSubTabs, ThemeHeading, SimpleTable, Loading, useJson, useCsv, formatTurnover } from "./research-shared";
import type { Row, Series, MicrocapSummary, MicrocapScope, StyleScope, TurnoverPeriod, TurnoverSnapshot, TurnoverAudit, SmallcapTurnoverData, LiquidityBucket, LiquidityPeriodMarket, LiquidityPeriod, LiquiditySummary, BarraSummary, HistoricalFactor, CorrelationMatrix, CashflowBasis, DiagnosticView } from "./research-shared";

export function SmallcapTurnoverSection() {
  const { data, error } = useJson<SmallcapTurnoverData>("smallcap_turnover.json");
  const [rankCount, setRankCount] = useState(400);
  const [granularity, setGranularity] = useState<"annual" | "monthly">("annual");
  if (error) return <div className="callout compact"><span className="section-kicker">小微盘成交额研究</span><p>网页汇总暂时无法加载：{error}</p></div>;
  if (!data) return <Loading />;
  const cleanRows = data.clean[granularity].filter((row) => row.rank_count === rankCount);
  const historicalRows = data.historical[granularity].filter((row) => row.rank_count === rankCount);
  const labelOf = (row: TurnoverPeriod | Record<string, never>) => granularity === "annual" ? String(row.year ?? "") : row.month ?? "";
  const labels = [...new Set([...cleanRows, ...historicalRows].map(labelOf))].sort();
  const byPeriod = (rows: TurnoverPeriod[]) => new Map(rows.map((row) => [labelOf(row), row.turnover_median]));
  const cleanByPeriod = byPeriod(cleanRows);
  const historicalByPeriod = byPeriod(historicalRows);
  const latestClean = cleanRows.at(-1);
  const latestHistorical = historicalRows.at(-1);
  const periodLabel = granularity === "annual" ? "年度" : "月度";
  const diagnosticNote = rankCount === 1 ? "N=1 是每日市值最小的一只股票，仅作极端诊断；个股切换、停牌、涨跌停和数据异常都会显著影响它，不代表可交易组合。" : "N 较大的口径更适合观察一组小市值股票的整体成交额。";
  const auditRows: Row[] = data.overlap_audit.map((row) => ({
    rank_count: String(row.rank_count),
    common_days: num(row.common_days),
    mean_diff: pct(row.mean_abs_relative_diff_turnover_median),
    p90_diff: pct(row.p90_abs_relative_diff_turnover_median),
    within_10: pct(row.within_10pct_ratio),
  }));
  return <><SectionHeading title="小微盘成交额研究" text="按每日总市值选取最小 N 只股票，观察日成交额的历史变化，并把清洗口径与长历史口径并列展示。"/><div className="callout compact"><span className="section-kicker">覆盖口径</span><p><strong>2015 年起清洗口径</strong>覆盖 ST、停牌和价格质量规则，标记为 verified；<strong>2008 年起历史口径</strong>时间更长，但历史源缺少可靠的 ST/停牌标记，标记为 incomplete。图表的年度值和月度值都是“日成交额中位数”的对应周期中位数，不是累计成交额。</p></div><section className="stat-grid"><Stat label="清洗口径覆盖" value={data.clean.coverage_start + " 至 " + data.clean.coverage_end} note="主分析口径" accent/><Stat label="历史口径覆盖" value={data.historical.coverage_start + " 至 " + data.historical.coverage_end} note="质量待补强"/><Stat label={"N=" + rankCount + " · 清洗口径"} value={formatTurnover(latestClean?.turnover_median ?? NaN)} note={labelOf(latestClean ?? {}) + " " + periodLabel + "日中位数"}/><Stat label={"N=" + rankCount + " · 历史口径"} value={formatTurnover(latestHistorical?.turnover_median ?? NaN)} note={labelOf(latestHistorical ?? {}) + " " + periodLabel + "日中位数"}/></section><Panel title="最小 N 只股票的日成交额" tag={periodLabel + "汇总 · 可缩放"}><ControlBar><span className="control-label">统计粒度</span><Choice active={granularity === "annual"} onClick={() => setGranularity("annual")}>年度汇总</Choice><Choice active={granularity === "monthly"} onClick={() => setGranularity("monthly")}>月度汇总</Choice><span className="control-label">股票数量</span>{data.clean.rank_counts.map((value) => <Choice key={value} active={rankCount === value} onClick={() => setRankCount(value)}>N={value}</Choice>)}</ControlBar><LineChart labels={labels} series={[{ name: "2015+ 清洗口径", values: labels.map((label) => cleanByPeriod.get(label) ?? null), color: "#1267d6" }, { name: "2008+ 历史口径", values: labels.map((label) => historicalByPeriod.get(label) ?? null), color: "#b96800" }]}/><p className="panel-note">{diagnosticNote} 单位为人民币成交额；网页只发布{periodLabel}汇总，完整日频明细仍保留在仓库外的研究输出目录。</p></Panel><Panel title="清洗口径与历史口径的重叠审计" tag="2015-01-05 至 2026-08-21"><p className="panel-note">审计比较两套口径在共同日期上的日成交额中位数相对差异。差异来自历史口径的股票资格判定不完整，因此这张表用于识别可比边界，不代表历史口径已经完成清洗。</p><SimpleTable rows={auditRows} columns={[["rank_count", "N"], ["common_days", "共同交易日"], ["mean_diff", "平均绝对相对差异"], ["p90_diff", "P90绝对相对差异"], ["within_10", "10%以内比例"]]}/></Panel><div className="fine-print"><span className="section-kicker">研究边界</span><p>{data.caveats.join(" ")}</p></div></>;
}

export function MicrocapPage({ scope, onScopeChange }: { scope: MicrocapScope; onScopeChange: (value: MicrocapScope) => void }) {
  return <><MicrocapSubTabs scope={scope} onChange={onScopeChange}/>{scope === "cross-market" ? <LiquidityPage embedded/> : <><ReplicationSection scope="microcap"/><RecoverySection scope="microcap"/><MicrocapPageContent/></>}</>;
}

export function MicrocapPageContent() {
  const { data: summary } = useJson<MicrocapSummary>("index/microcap/summary.json");
  const { data: reconstructed } = useJson<Row>("index/microcap/reconstructed_summary.json");
  const { data: nav } = useCsv("index/microcap/nav.csv");
  const { data: reconstructedNav } = useCsv("index/microcap/reconstructed_daily_nav.csv");
  const { data: annual } = useCsv("index/microcap/annual_returns.csv");
  const { data: cagr } = useCsv("index/microcap/rolling_cagr.csv");
  const { data: drawdown } = useCsv("index/microcap/rolling_drawdown.csv");
  const { data: underwater } = useCsv("index/microcap/reconstructed_underwater_periods.csv");
  if (!summary || !reconstructed || !nav || !reconstructedNav || !annual || !cagr || !drawdown || !underwater) return <Loading />;
  const latestAnnual = annual.find((row) => row.year === "2025");
  return <><SmallcapTurnoverSection/><ThemeHeading kicker="历史研究档案 · 微盘规则复现" title="小微盘的长期收益、回撤与交易限制" text="旧版重建净值在部分持仓缺少报价时，重新分配了其余持仓的权重，计算存在问题，尚未完成重算。以下仅作历史档案，收益准确性和实际可交易性均未验证。" asof={`重建截至 ${reconstructedNav.at(-1)?.date ?? "未提供"}`}/><section className="stat-grid"><Stat label="公开参考净值" value={num(asNumber(nav.at(-1)?.nav))} note={`截至 ${nav.at(-1)?.date ?? "未提供"}`} accent/><Stat label="2025年收益" value={pct(asNumber(latestAnnual?.return))} note="公开资料参考"/><Stat label="重建最大回撤" value={pct(asNumber(reconstructed.max_drawdown))} note="2015年以来日频"/><Stat label="最长未回到前高的时间" value={`${num(asNumber(reconstructed.longest_underwater_trading_days))} 个交易日`} note={`${reconstructed.longest_underwater_start ?? "未提供"} 至 ${reconstructed.longest_underwater_end ?? "未提供"}`}/><Stat label="重建样本" value={`${num(asNumber(reconstructed.observations))} 天`} note={`${reconstructed.coverage_start ?? "未提供"} 至 ${reconstructed.coverage_end ?? "未提供"}`}/></section><div className="panel ytd-panel"><div className="panel-title"><h3>2026 年至今</h3><span className="tag warm">公开资料参考</span></div><p>截至 {summary.metrics.ytd_2026_as_of ?? "未提供"}，公开资料参考收益为 {pct(asNumber(summary.metrics.ytd_2026_reference))}。规则重建净值更新到 {reconstructed.coverage_end ?? "未提供"}，公开参考与规则重建采用不同口径，应分别阅读。</p></div><SectionHeading title="收益路径" text="查看公开参考和规则重建的历史净值、回撤与恢复过程。"/><div className="panel"><div className="panel-title"><h3>公开资料参考净值</h3><span className="tag">可悬停、缩放</span></div><NavChart rows={nav} name="公开资料参考" color="#1267d6"/></div><div className="panel"><div className="panel-title"><h3>规则重建净值（数据来源：Tushare）</h3><span className="tag warm">2015年以来 · 可悬停、缩放</span></div><p className="panel-note">按上海、深圳 A 股总市值选取最小 400 只，等权持有至下一交易日。这里用于观察规则路径，暂未扣除交易成本。</p><NavChart rows={reconstructedNav} name="Tushare 规则重建净值" color="#b96800"/></div><div className="panel"><div className="panel-title"><h3>年度收益</h3><span className="tag warm">悬停查看数值</span></div><AnnualChart rows={annual}/></div><div className="research-grid"><Panel title="滚动年化收益" tag="持有期限"><MetricChart rows={cagr} value="cagr" label="年化收益"/></Panel><Panel title="滚动最大回撤" tag="月频与日频参考"><MetricChart rows={drawdown} value="max_drawdown" label="最大回撤"/></Panel></div><div className="panel"><div className="panel-title"><h3>最长未回到前高的区间</h3><span className="tag warm">按交易日排序</span></div><p className="panel-note">未回到前高的时间，指净值连续低于此前最高点的交易日数。图表展示持续时间最长的 10 个区间，悬停可以查看区间回撤。</p><UnderwaterChart rows={underwater}/></div><SectionHeading title="研究解读" text="了解选股规则、可能的收益来源、历史阶段和实际复制的难点。"/><div className="research-grid"><ResearchCard title="两个微盘口径" text="8841431.WI 每日调仓，适合观察极小市值与再平衡机制。868008.WI 每月调仓，换手和执行压力相对更低。"/><ResearchCard title="收益来源" text="收益可能来自极小市值、等权调仓、短期价格反转，以及承担流动性风险的补偿。各项贡献尚未精确计算。"/><ResearchCard title="历史阶段" text="2001 至 2005 年连续下跌。2006 至 2015 年多个极端上涨年份抬高长期年化收益。2017 至 2018 年微盘风格表现不利。"/><ResearchCard title="复制难度" text="实际复制的收益和可行性需要单独验证。成交不足、涨跌停、停牌、退市和冲击成本都可能造成差异。"/></div><div className="fine-print"><span className="section-kicker">研究边界</span><p>{readableNotes(reconstructed.caveats ?? "自制规则与万得官方指数口径不同，交易成本、涨跌停和停牌限制仍需核查。")}</p></div></>;
}
