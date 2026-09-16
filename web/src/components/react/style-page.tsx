import { useState } from "react";
import { asNumber, formatNumber as num, formatPercent as pct } from "../../lib/format";
import { withBase } from "../../lib/routes";
import { Stat, Panel, SectionHeading, ResearchCard, BarChart, ControlBar, Choice, StyleSubTabs, ThemeHeading, SimpleTable, SortableTable, Loading, useJson, useCsv, SizeDiagnosticPanel } from "./research-shared";
import type { Row, StyleScope, BarraSummary, HistoricalFactor, CorrelationMatrix } from "./research-shared";

export function StyleFactorStudyIntro() {
  const docsHref = withBase("/docs/research/factors/barra-factor-dictionary/", import.meta.env?.BASE_URL ?? "/");
  return <section className="featured-study study-intro" aria-label="18-year style factor study framing"><div><span className="section-kicker">Featured Quant Research · Barra-style 风格归因</span><h2>18 年 A 股风格因子动态：收益、稳定性与市场阶段</h2><p>这些风格因子在不同 A 股市场阶段是否持续存在？本页用历史分组收益、年度阶段、相关性和市值诊断来观察这个问题。当前定义和口径见 <a href={docsHref}>Barra 风格因子字典</a>。IC、样本外验证和统计显著性仍待补充。</p></div></section>;
}
export function StylePage({ scope, onScopeChange }: { scope: StyleScope; onScopeChange: (value: StyleScope) => void }) {
  return <><StyleSubTabs scope={scope} onChange={onScopeChange}/>{scope === "barra" ? <><StyleFactorStudyIntro/><BarraPage/></> : <IndicesPage/>}</>;
}

export function IndicesPage() {
  const { data: returns } = useCsv("index/linked_indices/ten_year_price_returns.csv");
  const { data: etfs } = useCsv("index/linked_indices/paired_index_etf_representatives.csv");
  const { data: catalog } = useCsv("index/index_catalog.csv");
  const { data: multi } = useCsv("index/linked_indices/etf_multi_period_returns.csv");
  const [category, setCategory] = useState("全部");
  const [period, setPeriod] = useState("10Y");
  if (!returns || !etfs || !catalog || !multi) return <Loading />;
  const categories = ["全部", ...new Set(catalog.map((row) => row.category).filter(Boolean))];
  const catalogByCode = new Map(catalog.map((row) => [row.ts_code, row.category]));
  const filteredReturns = category === "全部" ? returns : returns.filter((row) => catalogByCode.get(row.ts_code) === category);
  const top = [...filteredReturns].sort((a, b) => asNumber(b.cagr) - asNumber(a.cagr)).slice(0, 12);
  const liquid = etfs.filter((row) => row.liquid_10m === "True").length;
  return <><ThemeHeading kicker="指数长期回报 · ETF 可投资性" title="指数长期回报与可投资的基金产品" text="查看指数目录、十年价格回报，以及跟踪指数的代表性交易型开放式指数基金（ETF）。价格回报不含分红，基金回报还受费用和跟踪误差影响。" asof="已发布的历史数据"/><section className="stat-grid"><Stat label="指数目录" value={num(catalog.length)} note="已收录公开目录" accent/><Stat label="当前类别指数" value={num(filteredReturns.length)} note={category === "全部" ? "全部类别" : category}/><Stat label="代表性基金" value={num(etfs.length)} note="与指数对应的基金产品"/><Stat label="符合成交额筛选的基金" value={num(liquid)} note="近60日成交额筛选"/></section><Panel title="十年价格回报最高的指数" tag="按类别筛选 · 前12名"><ControlBar><span className="control-label">指数类别</span>{categories.map((value) => <Choice key={value} active={category === value} onClick={() => setCategory(value)}>{value}</Choice>)}</ControlBar><BarChart rows={top} labelKey="indx_name" valueKey="cagr" color="#1267d6"/><p className="panel-note">当前公开快照提供十年价格回报，未提供统一的多区间日频收益，因此这里先用类别筛选帮助定位研究对象。</p></Panel><Panel title="指数与代表性基金的表现" tag="可搜索、可排序"><SortableTable rows={etfs} columns={[["ts_code", "ETF"], ["matched_index_name", "跟踪指数"], ["etf_cagr", "基金年化回报"], ["index_cagr", "指数年化回报"], ["etf_max_drawdown", "基金最大回撤"], ["median_amount_60d", "近60日成交额中位数"]]} percentColumns={["etf_cagr", "index_cagr", "etf_max_drawdown"]}/></Panel><Panel title="代表性 ETF 的多区间表现" tag="前复权价格 · 2015 年以来"><ControlBar><span className="control-label">区间</span>{["1Y", "3Y", "5Y", "10Y"].map((value) => <Choice key={value} active={period === value} onClick={() => setPeriod(value)}>{value}</Choice>)}</ControlBar><SortableTable rows={multi.filter((row) => row.period === period)} columns={[["ts_code", "ETF"], ["name", "名称"], ["matched_index_name", "跟踪指数"], ["start", "起始日"], ["end", "结束日"], ["total_return", "累计收益"], ["cagr", "年化收益"], ["annualized_volatility", "年化波动率"], ["max_drawdown", "最大回撤"], ["current_drawdown", "期末回撤"], ["median_amount", "成交额中位数"]]} percentColumns={["total_return", "cagr", "annualized_volatility", "max_drawdown", "current_drawdown"]}/><p className="panel-note">区间从共同数据结束日倒推，按各 ETF 的实际上市和可用交易日计算。收益使用前复权收盘价，不含费用和税费。波动率按日收益年化，期末回撤表示区间结束日相对区间内最高点的回撤。它是历史比较，不构成未来收益预测。</p></Panel></>;
}

const FACTOR_NAMES: Record<string, string> = { beta: "低贝塔", chip_concentration: "筹码集中度", dividend_yield: "股息率", earnings_yield: "盈利收益率", fund_breadth: "公募重仓广度", fund_breadth_change: "公募重仓广度变化", fund_ownership: "公募重仓比例", fund_ownership_change: "公募重仓比例变化", growth: "成长", institution_holding: "机构持仓", leverage: "低杠杆", liquidity: "低换手（当前快照）", liquidity_flow: "大单资金流", lowvol: "总波动率（21日）", momentum: "短期动量（21日）", ps_value: "市销率价值", quality: "复合质量", size: "市值", value: "价值" };
const FACTOR_DEFINITIONS: Row[] = [
  { factor: "size", name: "市值", direction: "大市值减小市值", method: "总市值取自然对数，每月分组" },
  { factor: "value", name: "价值", direction: "低市净率减高市净率", method: "市净率倒数，每月分组" },
  { factor: "momentum", name: "短期动量（21日）", direction: "强势减弱势", method: "排除形成日的21日收益，每月分组" },
  { factor: "quality", name: "复合质量", direction: "高质量减低质量", method: "盈利能力、低杠杆、盈利稳定性和现金流质量等权合成" },
  { factor: "earnings_yield", name: "盈利收益率", direction: "低市盈率减高市盈率", method: "滚动市盈率倒数" },
  { factor: "lowvol", name: "总波动率（21日）", direction: "低波动减高波动", method: "最近21个收益观察值的总收益波动率" },
  { factor: "growth", name: "成长", direction: "高增长减低增长", method: "净利润同比和营业收入同比，按公告日对齐" },
  { factor: "leverage", name: "低杠杆", direction: "低杠杆减高杠杆", method: "资产负债率，按公告日对齐" },
  { factor: "beta", name: "低贝塔", direction: "低贝塔减高贝塔", method: "252日滚动市场贝塔，至少126日" },
  { factor: "liquidity", name: "低换手（当前快照）", direction: "低换手减高换手", method: "形成日单日换手率，长期低换手研究另有20日和60日口径" },
  { factor: "liquidity_flow", name: "大单资金流", direction: "大单净买入较高减较低", method: "大单净买入占比" },
  { factor: "chip_concentration", name: "筹码集中度", direction: "集中度较高减较低", method: "前十大流通股东持股占比" },
  { factor: "institution_holding", name: "机构持仓", direction: "机构持仓较高减较低", method: "前十大机构流通持股占比" },
  { factor: "fund_breadth", name: "公募前十大重仓广度", direction: "重仓基金较多减较少", method: "按月末可见的持仓记录，统计将该股票列入前十大重仓的基金数量" },
  { factor: "fund_breadth_change", name: "公募重仓广度变化", direction: "重仓覆盖增加减减少", method: "前十大重仓基金数量相对上期变化" },
  { factor: "fund_ownership", name: "公募重仓比例", direction: "重仓比例较高减较低", method: "前十大重仓流通股持仓比例合计" },
  { factor: "fund_ownership_change", name: "公募重仓比例变化", direction: "重仓比例增加减减少", method: "前十大重仓流通股持仓比例相对上期变化" },
  { factor: "dividend_yield", name: "股息率", direction: "高股息率减低股息率", method: "过去12个月股息率" },
  { factor: "ps_value", name: "市销率价值", direction: "低市销率减高市销率", method: "滚动市销率倒数" },
];

export function BarraPage() {
  const { data: summary, error: summaryError } = useJson<BarraSummary>("barra/barra_summary.json");
  const { data: quantiles, error: quantilesError } = useCsv("barra/barra_size_quantiles.csv");
  const { data: factors } = useJson<HistoricalFactor[]>("barra/historical_factor_summary.json");
  const { data: yearly } = useCsv("barra/factor_yearly.csv");
  const { data: correlations } = useJson<CorrelationMatrix>("barra/factor_correlation.json");
  const [selectedFactor, setSelectedFactor] = useState("size");
  if (!summary || !quantiles || !factors || !yearly || !correlations) return <><ThemeHeading kicker="18 年 A 股风格因子研究" title="18 年 A 股风格因子动态：收益、稳定性与市场阶段" text="研究快照正在加载；研究问题是这些风格因子在不同 A 股市场阶段是否持续存在。" asof="历史快照加载中"/><div className="callout status-panel"><span className="section-kicker">研究状态</span><h3>历史研究快照正在加载</h3><p>{summaryError || quantilesError ? "网页数据不完整，请先生成并发布 Barra 历史派生文件。" : "正在加载历史因子总览、逐年收益和相关性数据。"}</p></div></>;
  const quantileRows = quantiles.map((row) => ({ bucket: row.bucket_label || row.bucket, forward_return: row.mean_forward_return, count: row.count, formation_date: row.formation_date }));
  const quantileCurve = Object.values(quantileRows.reduce<Record<string, Row>>((result, row) => { const current = result[row.bucket] ?? { bucket: row.bucket, forward_return: "0", count: "0" }; current.forward_return = String(Number(current.forward_return) + Number(row.forward_return || 0)); current.count = String(Number(current.count) + 1); result[row.bucket] = current; return result; }, {})).map((row) => ({ bucket: row.bucket, value: String(Number(row.forward_return) / Math.max(Number(row.count), 1)) }));
  const factorRows = factors.map((factor) => ({ factor: FACTOR_NAMES[factor.factor] ?? factor.factor, coverage: `${factor.years} 年 · ${factor.days} 日`, annual: String(factor.geometric_annual_ret / 100), vol: String(factor.annual_vol / 100), sharpe: String(factor.sharpe), drawdown: String(factor.max_drawdown / 100), hit: String(factor.hit_rate / 100) }));
  const selectedYearly = yearly.filter((row) => row.factor === selectedFactor).map((row) => ({ year: row.year, value: String(asNumber(row.annual_ret) / 100) }));
  const related = Object.entries(correlations[selectedFactor] ?? {}).filter(([factor]) => factor !== selectedFactor).sort(([, left], [, right]) => Math.abs(right) - Math.abs(left)).slice(0, 8).map(([factor, value]) => ({ factor: FACTOR_NAMES[factor] ?? factor, correlation: String(value) }));
  const selectedFactorSummary = factors.find((factor) => factor.factor === selectedFactor);
  return <><ThemeHeading kicker="历史研究档案 · Barra 风格因子" title="A 股风格因子的长期历史表现" text="查看因子定义、长期表现、逐年收益、相关性和样本范围，最后补充独立计算的市值十分组研究。" asof="历史样本 2008-01-02 至 2026-09-04"/><div className="callout research-status"><span className="section-kicker">研究性质</span><h3>历史多空合成收益</h3><p>每天用高分组收益减去低分组收益，再复合计算年化和逐年收益。所得数值仅代表合成序列，不能作为实际账户盈亏。本页研究分组收益差。Barra 风格分析还可用于解释风险来源，预测能力需要另行检验。</p></div><SectionHeading title="研究问题与方法" text="了解分组方式、行业处理和样本范围，再阅读历史结果。"/><div className="research-grid"><ResearchCard title="研究对象" text="研究 19 个 A 股风格因子。每个月末按当时构造的因子得分将股票分为五组，最高和最低的各 20% 分别等权建仓，固定份额持有至下个月末。每天用高分组收益减去低分组收益。财务数据是否在当时已可获取，尚未完整验证。"/><ResearchCard title="行业处理" text="按各历史日期对应的申万一级行业，先从因子值中减去本行业平均值，再进行全市场标准化。行业信息缺失的股票单列一组。这种处理后，多空两组的行业权重仍可能不同。"/><ResearchCard title="样本口径" text="大部分基础因子覆盖约 18.6 年。机构持仓、筹码和公募持仓类因子覆盖约 11 年或更短，资金流因子约 0.6 年。"/></div><div className="callout"><span className="section-kicker">评分是否有效，交易能否实现</span><p>判断因子评分是否有用，要看高分股票之后是否表现更好，以及收益是否随分组得分提高而上升。目前尚未提供得分与未来收益的相关性结果，还需要样本外验证和统计检验。下方将股票按市值分成十组，独立观察后续收益，与历史五分组研究采用不同分组，不能用于复核后者的多空收益。</p><p>实际交易还需逐期确认能否借到股票、借券费用和保证金要求，并计入交易成本与成交限制。这些条件尚未验证。</p><details><summary>方法与术语</summary><p><code>IC</code> 衡量同一天各股票的因子得分与未来收益的相关性。<code>rankIC</code> 比较两者的排名相关性。本页尚未提供这两项结果。样本外验证是用构造因子时未使用的数据检查结果。</p><p>市值因子（<code>size</code>）按大市值组减小市值组计算。下方十分组图中的 Q1 减 Q10 则是最小市值组减最大市值组，两处方向不同。</p></details></div><Panel title="因子定义与方向" tag="历史研究方法"><SimpleTable rows={FACTOR_DEFINITIONS} columns={[["name", "因子"], ["direction", "高分组减低分组"], ["method", "构造方法"]]} /></Panel><Panel title="19 个因子表现总览" tag="历史合成序列（账户收益未验证）"><SortableTable rows={factorRows} columns={[["factor", "因子"], ["coverage", "样本范围"], ["annual", "合成收益的几何年化"], ["vol", "年化波动率"], ["sharpe", "夏普比率"], ["drawdown", "最大回撤"], ["hit", "日收益为正的比例"]]} percentColumns={["annual", "vol", "drawdown", "hit"]}/></Panel><Panel title="逐年合成收益与阶段表现" tag="按每日收益差复合计算"><ControlBar><span className="control-label">因子</span>{factors.map((factor) => <Choice key={factor.factor} active={selectedFactor === factor.factor} onClick={() => setSelectedFactor(factor.factor)}>{FACTOR_NAMES[factor.factor] ?? factor.factor}</Choice>)}</ControlBar><BarChart rows={selectedYearly} labelKey="year" valueKey="value" color="#1267d6"/><p className="panel-note">{FACTOR_NAMES[selectedFactor] ?? selectedFactor}：覆盖 {selectedFactorSummary?.years ?? "未提供"} 年，合成收益的几何年化 {pct((selectedFactorSummary?.geometric_annual_ret ?? 0) / 100)}，数值沿用历史研究结果。年度收益仅按该年已有数据计算，数据不足一年的按实际区间展示。</p></Panel><Panel title="因子相关性" tag="历史多空日收益差的相关性"><SimpleTable rows={related} columns={[["factor", "因子"], ["correlation", "相关系数"]]} /></Panel><SizeDiagnosticPanel rows={quantileRows} dailyCurve={quantileCurve}/><div className="fine-print"><span className="section-kicker">研究限制</span><p>历史研究使用每日行情、估值和事后重建的财务数据。财务数据未完整保留当时可见的版本（<code>PIT</code>），即使按公告日对齐，仍可能混入后续修订。各因子的样本区间不同，比较时需注意样本长度。每日收益可能存在时间相关性，夏普比率、年化收益、回撤和正收益比例均描述合成序列。尚未检验统计显著性、用自助法估计不确定性，或校正同时检验多个因子带来的偏差。历史计算将持仓期缺失收益记为零，退市时的最终价值尚未完整处理。手续费、可交易规模、涨跌停、停牌和成交限制也需另行核查。</p></div></>;
}
