import { useEffect, useState } from "react";
import {
  asNumber,
  formatNumber as num,
  formatPercent as pct,
} from "../../lib/format";
import {
  Stat,
  Panel,
  BarChart,
  ControlBar,
  Choice,
  StyleSubTabs,
  ThemeHeading,
  SortableTable,
  Loading,
  useJson,
  useCsv,
  SizeDiagnosticPanel,
  englishLocale,
} from "./research-shared";
import { dailySizeCurve, comparableSizeRows, finiteNumber } from "../../lib/size-diagnostics";
import { currentFactorImplementations, commonFactorProcessing, implementationSource } from "../../lib/factor-implementations";
import { FACTOR_NAMES, FACTOR_DEFINITIONS, FACTOR_DETAILS } from "../../content/factors";
import type {
  Row,
  StyleScope,
  BarraSummary,
  HistoricalFactor,
  CorrelationMatrix,
} from "./research-shared";

function text(zh: string, en: string) {
  return englishLocale() ? en : zh;
}

export function StylePage({ scope }: { scope: StyleScope }) {
  return (
    <>
      <StyleSubTabs scope={scope} />
      {scope === "barra" ? (
        <>
          <BarraPage includeNarrative={false} />
        </>
      ) : (
        <IndicesPage />
      )}
    </>
  );
}

export function IndicesPage() {
  const english = englishLocale();
  const ui = (zh: string, en: string) => english ? en : zh;
  const { data: returns } = useCsv(
    "index/linked_indices/ten_year_price_returns.csv",
  );
  const { data: etfs } = useCsv(
    "index/linked_indices/paired_index_etf_representatives.csv",
  );
  const { data: catalog } = useCsv("index/index_catalog.csv");
  const { data: multi } = useCsv(
    "index/linked_indices/etf_multi_period_returns.csv",
  );
  const [category, setCategory] = useState("全部");
  const [period, setPeriod] = useState("10Y");
  if (!returns || !etfs || !catalog || !multi) return <Loading />;
  const categories = [
    "全部",
    ...new Set(catalog.map((row) => row.category).filter(Boolean)),
  ];
  const catalogByCode = new Map(
    catalog.map((row) => [row.ts_code, row.category]),
  );
  const filteredReturns =
    category === "全部"
      ? returns
      : returns.filter((row) => catalogByCode.get(row.ts_code) === category);
  const top = [...filteredReturns]
    .sort((a, b) => asNumber(b.cagr) - asNumber(a.cagr))
    .slice(0, 12);
  const liquid = etfs.filter((row) => row.liquid_10m === "True").length;
  return (
    <>
      <ThemeHeading
        kicker={ui("指数长期回报 · ETF 可投资性", "Long-run index returns · ETF investability")}
        title={ui("指数长期回报与可投资的基金产品", "Long-run index returns and investable ETFs")}
        text={ui("查看指数目录、十年价格回报，以及跟踪指数的代表性交易型开放式指数基金（ETF）。价格回报不含分红，基金回报还受费用和跟踪误差影响。", "Review the index catalog, ten-year price returns, and representative exchange-traded funds (ETFs). Price returns exclude dividends; fund returns also reflect fees and tracking error.")}
        asof={ui("已发布的历史数据", "Published historical data")}
      />
      <section className="stat-grid">
        <Stat
          label={ui("指数目录", "Index catalog")}
          value={num(catalog.length)}
          note={ui("已收录公开目录", "Public entries")}
          accent
        />
        <Stat
          label={ui("当前类别指数", "Indexes in selected category")}
          value={num(filteredReturns.length)}
          note={category === "全部" ? ui("全部类别", "All categories") : category}
        />
        <Stat
          label={ui("代表性基金", "Representative funds")}
          value={num(etfs.length)}
          note={ui("与指数对应的基金产品", "Funds matched to indexes")}
        />
        <Stat
          label={ui("符合成交额筛选的基金", "Funds passing liquidity filter")}
          value={num(liquid)}
          note={ui("近60日成交额筛选", "60-day median turnover")}
        />
      </section>
      <Panel title={ui("十年价格回报最高的指数", "Top ten-year price returns")} tag={ui("按类别筛选 · 前12名", "Category filter · top 12")}>
        <ControlBar>
          <span className="control-label">{ui("指数类别", "Index category")}</span>
          {categories.map((value) => (
            <Choice
              key={value}
              active={category === value}
              onClick={() => setCategory(value)}
            >
              {value === "全部" ? ui("全部", "All") : value}
            </Choice>
          ))}
        </ControlBar>
        <BarChart
          rows={top}
          labelKey="indx_name"
          valueKey="cagr"
          color="#1267d6"
        />
        <p className="panel-note">
          {ui("这里的指数排行榜仍使用十年价格回报，类别筛选用于定位研究对象。下方 ETF 表提供统一的 1 年、3 年、5 年和 10 年区间比较。", "This ranking uses ten-year price returns; the category filter narrows the research universe. The ETF table below provides consistent 1-, 3-, 5-, and 10-year comparisons.")}
        </p>
      </Panel>
      <Panel title={ui("指数与代表性基金的表现", "Index and representative ETF performance")} tag={ui("可搜索、可排序", "Searchable · sortable")}>
        <SortableTable
          rows={etfs}
          columns={[
            ["ts_code", "ETF"],
            ["matched_index_name", ui("跟踪指数", "Tracked index")],
            ["etf_cagr", ui("基金年化回报", "ETF annualized return")],
            ["index_cagr", ui("指数年化回报", "Index annualized return")],
            ["etf_max_drawdown", ui("基金最大回撤", "ETF max drawdown")],
            ["median_amount_60d", ui("近60日成交额中位数", "60-day median turnover")],
          ]}
          percentColumns={["etf_cagr", "index_cagr", "etf_max_drawdown"]}
        />
      </Panel>
      <Panel title={ui("代表性 ETF 的多区间表现", "Representative ETF performance across horizons")} tag={ui("前复权价格 · 2015 年以来", "Adjusted prices · since 2015")}>
        <ControlBar>
          <span className="control-label">{ui("区间", "Horizon")}</span>
          {["1Y", "3Y", "5Y", "10Y"].map((value) => (
            <Choice
              key={value}
              active={period === value}
              onClick={() => setPeriod(value)}
            >
              {value}
            </Choice>
          ))}
        </ControlBar>
        <SortableTable
          rows={multi.filter((row) => row.period === period)}
          columns={[
            ["ts_code", "ETF"],
            ["name", ui("名称", "Name")],
            ["matched_index_name", ui("跟踪指数", "Tracked index")],
            ["start", ui("起始日", "Start")],
            ["end", ui("结束日", "End")],
            ["total_return", ui("累计收益", "Total return")],
            ["cagr", ui("年化收益", "Annualized return")],
            ["annualized_volatility", ui("年化波动率", "Annualized volatility")],
            ["max_drawdown", ui("最大回撤", "Max drawdown")],
            ["current_drawdown", ui("期末回撤", "Current drawdown")],
            ["median_amount", ui("成交额中位数", "Median turnover")],
          ]}
          percentColumns={[
            "total_return",
            "cagr",
            "annualized_volatility",
            "max_drawdown",
            "current_drawdown",
          ]}
        />
        <p className="panel-note">
          {ui("区间从共同数据结束日倒推，按各 ETF 的实际上市和可用交易日计算。收益使用前复权收盘价，不含费用和税费。波动率按日收益年化，期末回撤表示区间结束日相对区间内最高点的回撤。它是历史比较，不构成未来收益预测。", "Each horizon is measured backward from the shared data end date using each ETF's actual listing and available trading days. Returns use adjusted closes and exclude fees and taxes. Volatility is annualized from daily returns; current drawdown is measured from the in-period high. This is historical comparison, not a forecast.")}
        </p>
      </Panel>
    </>
  );
}

const LEGACY_FACTOR_NAMES: Record<string, string> = {
  beta: "低贝塔",
  chip_concentration: "筹码集中度",
  dividend_yield: "股息率",
  earnings_yield: "盈利收益率",
  fund_breadth: "公募重仓广度",
  fund_breadth_change: "公募重仓广度变化",
  fund_ownership: "公募重仓比例",
  fund_ownership_change: "公募重仓比例变化",
  growth: "成长",
  institution_holding: "机构持仓",
  leverage: "低杠杆",
  liquidity: "流动性（历史）",
  liquidity_flow: "交易流（历史）",
  lowvol: "低波动（历史）",
  momentum: "动量（历史）",
  ps_value: "市销率价值",
  quality: "复合质量",
  size: "市值",
  value: "价值",
};
const LEGACY_FACTOR_DEFINITIONS: Row[] = [
  {
    factor: "size",
    name: "市值",
    direction: "大市值减小市值",
    method: "总市值取自然对数，每月分组",
  },
  {
    factor: "value",
    name: "价值",
    direction: "低市净率减高市净率",
    method: "市净率倒数，每月分组",
  },
  {
    factor: "momentum",
    name: "短期动量（21日）",
    direction: "强势减弱势",
    method: "排除形成日的21日收益，每月分组",
  },
  {
    factor: "quality",
    name: "复合质量",
    direction: "高质量减低质量",
    method: "盈利能力、低杠杆、盈利稳定性和现金流质量等权合成",
  },
  {
    factor: "earnings_yield",
    name: "盈利收益率",
    direction: "低市盈率减高市盈率",
    method: "滚动市盈率倒数",
  },
  {
    factor: "lowvol",
    name: "总波动率（21日）",
    direction: "低波动减高波动",
    method: "最近21个收益观察值的总收益波动率",
  },
  {
    factor: "growth",
    name: "成长",
    direction: "高增长减低增长",
    method: "净利润同比和营业收入同比，按公告日对齐",
  },
  {
    factor: "leverage",
    name: "低杠杆",
    direction: "低杠杆减高杠杆",
    method: "资产负债率，按公告日对齐",
  },
  {
    factor: "beta",
    name: "低贝塔",
    direction: "低贝塔减高贝塔",
    method: "252日滚动市场贝塔，至少126日",
  },
  {
    factor: "liquidity",
    name: "低换手（当前快照）",
    direction: "低换手减高换手",
    method: "形成日单日换手率，长期低换手研究另有20日和60日口径",
  },
  {
    factor: "liquidity_flow",
    name: "大单资金流",
    direction: "大单净买入较高减较低",
    method: "大单净买入占比",
  },
  {
    factor: "chip_concentration",
    name: "筹码集中度",
    direction: "集中度较高减较低",
    method: "前十大流通股东持股占比",
  },
  {
    factor: "institution_holding",
    name: "机构持仓",
    direction: "机构持仓较高减较低",
    method: "前十大机构流通持股占比",
  },
  {
    factor: "fund_breadth",
    name: "公募前十大重仓广度",
    direction: "重仓基金较多减较少",
    method: "按月末可见的持仓记录，统计将该股票列入前十大重仓的基金数量",
  },
  {
    factor: "fund_breadth_change",
    name: "公募重仓广度变化",
    direction: "重仓覆盖增加减减少",
    method: "前十大重仓基金数量相对上期变化",
  },
  {
    factor: "fund_ownership",
    name: "公募重仓比例",
    direction: "重仓比例较高减较低",
    method: "前十大重仓流通股持仓比例合计",
  },
  {
    factor: "fund_ownership_change",
    name: "公募重仓比例变化",
    direction: "重仓比例增加减减少",
    method: "前十大重仓流通股持仓比例相对上期变化",
  },
  {
    factor: "dividend_yield",
    name: "股息率",
    direction: "高股息率减低股息率",
    method: "过去12个月股息率",
  },
  {
    factor: "ps_value",
    name: "市销率价值",
    direction: "低市销率减高市销率",
    method: "滚动市销率倒数",
  },
];

type FactorDetail = {
  family: string;
  feature: string;
  calculation: string;
  current: string;
  verification: string;
};

const LEGACY_FACTOR_DETAILS: Record<string, FactorDetail> = {
  size: {
    family: "规模",
    feature: "历史命名对应股票市值规模。当前核心 descriptor 使用 daily_basic.total_mv。",
    calculation: "历史收益序列的原始 descriptor 没有随来源包提交。当前可重算版本对总市值取自然对数形成 log_market_cap，再做截面处理。",
    current: "log_market_cap。当前核心字典以小市值为高分方向，因此与历史页面的大市值减小市值收益方向相反。",
    verification: "当前代理定义可验证；历史收益序列的原始公式未完整保留。",
  },
  value: {
    family: "价值",
    feature: "历史 value 是价值风格合成快照，具体由哪些估值指标组成没有完整留档。",
    calculation: "历史原始 descriptor 和权重未确认。当前核心字典把价值拆成 book_to_price（1 / PB）与 earnings_yield（1 / PE_TTM，仅正 PE）两个独立因子。",
    current: "当前研究分别保留账面市值比与盈利收益率，不再把历史 value 当成一个可直接重算的单指标。",
    verification: "历史组成未确认；当前两个价值 descriptor 可验证。",
  },
  momentum: {
    family: "动量",
    feature: "历史命名表示价格动量风格，但形成窗口与是否跳过近期收益没有完整保留。",
    calculation: "历史公式未确认。当前核心代理 short_term_momentum_21d 使用形成日前 21 个交易日收益，并排除形成日价格。",
    current: "short_term_momentum_21d，更接近短期价格行为代理，不能直接视为历史 momentum 的同版本实现。",
    verification: "当前 21 日代理可验证；历史窗口与处理未确认。",
  },
  quality: {
    family: "质量",
    feature: "历史质量因子为复合风格。当前核心版本由盈利能力、低杠杆、盈利质量、盈利稳定性四个子因子组成。",
    calculation: "历史复合权重未完整保留。当前版本先分别缩尾、统一方向并标准化四个子因子，再对当期可用项等权平均。",
    current: "profitability + leverage + earnings_quality + earnings_variability。ROA 只用于敏感性检查，不进入主复合因子。",
    verification: "当前四子因子版本可验证；18 年历史收益尚未用该版本重跑。",
  },
  earnings_yield: {
    family: "价值",
    feature: "历史命名表示盈利收益率风格，通常与市盈率倒数相关。",
    calculation: "历史字段与缺失规则未确认。当前核心版本只对正 PE_TTM 计算 1 / PE_TTM，亏损公司不生成该分数。",
    current: "earnings_yield = 1 / PE_TTM（PE_TTM > 0）。",
    verification: "当前公式可验证；不能自动认定与历史版本完全一致。",
  },
  lowvol: {
    family: "波动率",
    feature: "历史命名表示低历史波动股票相对高波动股票的风格收益。",
    calculation: "历史窗口、基准调整和中性化方式未确认。当前核心代理 total_volatility_21d 使用最近 21 个收益观察值的标准差。",
    current: "total_volatility_21d，当前仅为总收益波动率，尚未剥离市场和行业波动。",
    verification: "当前 21 日代理可验证；历史窗口未确认。",
  },
  growth: {
    family: "成长",
    feature: "历史命名表示公司成长风格，可能来自盈利、收入或资产扩张类指标。",
    calculation: "来源包没有保留历史组成字段、权重与公式，因此不把净利润同比、营收同比等常见做法写成既定事实。",
    current: "当前核心 descriptor 字典没有与历史 growth 一一对应的可重算定义。",
    verification: "仅历史收益序列可验证；原始特征与公式未确认。",
  },
  leverage: {
    family: "质量",
    feature: "历史命名表示杠杆水平风格。",
    calculation: "历史具体财务字段未确认。当前核心版本使用 fundamental.debt_to_assets，经缩尾、标准化后统一为低杠杆高分方向。",
    current: "debt_to_assets 的反向标准化得分，同时也是当前 Quality 的四个子因子之一。",
    verification: "当前定义可验证；历史字段与处理未确认。",
  },
  beta: {
    family: "市场敏感度",
    feature: "历史命名表示股票收益对市场收益的敏感度。",
    calculation: "历史基准指数、估计窗口、最少观测数及是否使用加权回归均未随来源包保留。",
    current: "当前核心 descriptor 字典没有与这条历史 beta 收益序列一一对应的重算定义。",
    verification: "仅历史收益序列可验证；不能把 252 日窗口写成已证实历史公式。",
  },
  liquidity: {
    family: "流动性",
    feature: "历史 liquidity 可能反映换手、交易摩擦或价格冲击，但原始组成未保留。",
    calculation: "当前核心字典拆成 turnover_1d、turnover_20d、turnover_60d 与 amihud_20d，分别描述交易活跃度和单位成交额价格冲击。",
    current: "换手率使用形成日值或滞后均值；Amihud 为 abs(return) / amount 的 20 日滞后均值。",
    verification: "当前四个流动性 descriptor 可验证；历史 liquidity 的具体合成方式未确认。",
  },
  liquidity_flow: {
    family: "流动性 / 交易流",
    feature: "历史命名指向流动性资金流或交易流变化。",
    calculation: "原始字段、是否使用大单净买入、归一化方式与形成窗口均未随来源包保留。",
    current: "当前核心 descriptor 字典没有与该历史因子一一对应的重算定义。",
    verification: "只有约 0.6 年历史收益摘要；原始公式未确认。",
  },
  chip_concentration: {
    family: "持仓 / 筹码",
    feature: "历史命名表示股东或筹码集中程度。",
    calculation: "具体持股来源、是否仅统计前十大流通股东、集中度公式及披露滞后均未完整留档。",
    current: "当前核心 descriptor 字典没有对应的可重算定义。",
    verification: "历史收益摘要可验证；底层持仓公式未确认。",
  },
  institution_holding: {
    family: "持仓",
    feature: "历史命名表示机构投资者持仓水平。",
    calculation: "机构范围、持股字段、汇总方法和披露可见日未完整保留。",
    current: "当前核心 descriptor 字典没有对应的可重算定义。",
    verification: "历史收益摘要可验证；机构口径和 PIT 处理未确认。",
  },
  fund_breadth: {
    family: "基金持仓",
    feature: "历史命名表示持有某股票的基金覆盖广度。",
    calculation: "基金集合、是否限定前十大重仓、覆盖计数规则与披露可见日未完整保留。",
    current: "当前核心 descriptor 字典没有对应的可重算定义。",
    verification: "历史收益摘要可验证；覆盖定义未确认。",
  },
  fund_breadth_change: {
    family: "基金持仓",
    feature: "历史命名表示基金持仓覆盖面的变化。",
    calculation: "基金集合、广度定义、变化窗口与披露可见日未完整保留。",
    current: "当前核心 descriptor 字典没有对应的可重算定义。",
    verification: "历史收益摘要可验证；变化公式未确认。",
  },
  fund_ownership: {
    family: "基金持仓",
    feature: "历史命名表示公募基金对股票的持股水平。",
    calculation: "基金集合、持股比例分母、是否限定前十大重仓以及披露可见日未完整保留。",
    current: "当前核心 descriptor 字典没有对应的可重算定义。",
    verification: "历史收益摘要可验证；持股比例公式未确认。",
  },
  fund_ownership_change: {
    family: "基金持仓",
    feature: "历史命名表示公募基金持股水平的变化。",
    calculation: "基金集合、持股比例分母、变化窗口与披露可见日未完整保留。",
    current: "当前核心 descriptor 字典没有对应的可重算定义。",
    verification: "历史收益摘要可验证；变化公式未确认。",
  },
  dividend_yield: {
    family: "价值 / 收益",
    feature: "历史命名表示股息收益率暴露。",
    calculation: "股息字段、滚动窗口、复权和形成日处理未随来源包保留，因此不把过去 12 个月写成已验证历史公式。",
    current: "当前核心 descriptor 字典没有对应的可重算定义。",
    verification: "历史收益摘要可验证；底层股息口径未确认。",
  },
  ps_value: {
    family: "价值",
    feature: "名称表明该历史风格与 Price-to-Sales 估值相关。",
    calculation: "历史销售字段、是否取 1 / PS、负值与缺失处理未完整保留。",
    current: "当前核心 descriptor 字典没有对应的可重算定义。",
    verification: "历史收益摘要可验证；具体公式未确认。",
  },
};

// Kept beside the migration boundary for one release so old imports can be audited safely.
void LEGACY_FACTOR_NAMES;
void LEGACY_FACTOR_DEFINITIONS;
void LEGACY_FACTOR_DETAILS;

function DataNotice({ label, error, retry, empty = false }: { label: string; error?: string; retry?: () => void; empty?: boolean }) {
  return <div className="data-notice" role={error ? "alert" : "status"}>
    <strong>{label}{text("：", ": ")}{error ? text("加载失败", "Loading failed") : empty ? text("暂无可用数据", "No data available") : text("正在加载", "Loading")}</strong>
    <p>{error ? text("其余研究内容仍可使用。请重试，或稍后再查看此数据。", "The remaining research remains available. Retry this dataset or check again later.") : empty ? text("未提供不等于零；不据此生成收益或结论。", "Unavailable does not mean zero; no return or conclusion is inferred.") : text("正在读取公开派生快照。", "Reading the public derived snapshot.")}</p>
    {error && retry && <button type="button" className="button-link" onClick={retry}>{text("重试", "Retry")}{label}</button>}
  </div>;
}

function QualityDiagnostic() {
  const { data: qualityComponents, error, retry } = useCsv("barra/quality_component_summary.csv");
  const names: Record<string, string> = {
    quality_profitability: "盈利能力 · ROE",
    quality_leverage: "低杠杆 · Debt / Assets",
    quality_earnings_quality: "盈利质量 · OCF / Net Profit",
    quality_earnings_variability: "盈利稳定性 · 财务同比波动",
  };
  return <section className="quality-diagnostic" role="region" aria-label={text("Quality 子因子数据", "Quality sub-factor data")}>
    <h4>{text("Quality 子因子诊断", "Quality sub-factor diagnostic")}</h4>
    <p className="panel-note">独立短样本诊断，按原说明主要覆盖 2020 年以后、前 800 只股票；原始生成记录尚未定位。它与 18 年历史复合因子的样本和版本不同，不能视为对历史收益的贡献分解。</p>
    {!qualityComponents || !qualityComponents.length ? <DataNotice label={text("Quality 子因子", "Quality sub-factors")} error={error} retry={retry} empty={!!qualityComponents} /> :
      <SortableTable rows={qualityComponents.filter(row => row.factor.startsWith("quality_")).map(row => ({
        ...row,
        ...Object.fromEntries(["geometric_annual_ret", "annual_vol", "max_drawdown", "hit_rate"].map(key => [key, Number.isFinite(finiteNumber(row[key])) ? String(finiteNumber(row[key]) / 100) : ""])),
        sharpe: num(row.sharpe),
        years: num(row.years),
        factor: names[row.factor] ?? row.factor,
      }))}
        columns={[["factor", text("子因子与主要特征", "Sub-factor and features")], ["days", text("交易日", "Trading days")], ["years", text("样本年数", "Sample years")], ["geometric_annual_ret", text("几何年化", "Geometric annualized")], ["annual_vol", text("年化波动率", "Annualized volatility")], ["sharpe", text("夏普比率", "Sharpe ratio")], ["max_drawdown", text("最大回撤", "Max drawdown")], ["hit_rate", text("正收益比例", "Positive-return ratio")]]}
        percentColumns={["geometric_annual_ret", "annual_vol", "max_drawdown", "hit_rate"]} />}
    <div className="quality-method-grid">
      <div><strong>01 · 盈利能力</strong><span>ROE，截面缩尾后标准化。ROA 只作敏感性版本。</span></div>
      <div><strong>02 · 低杠杆</strong><span>Debt / Assets，缩尾与标准化后反向计分。</span></div>
      <div><strong>03 · 盈利质量</strong><span>OCF / Net Profit，缩尾后标准化，仍需核验 PIT 可见时间。</span></div>
      <div><strong>04 · 盈利稳定性</strong><span>现行实现对 8 个财务观测（至少 4 个）的净利润同比波动取负值，不保证为连续 8 季度。</span></div>
    </div>
  </section>;
}

function SizeSnapshot() {
  const { data, error, retry } = useCsv("barra/barra_size_quantiles.csv");
  const metadata = useJson<BarraSummary & { revision?: { input_vintage?: string; as_of?: string } }>("barra/barra_summary.json");
  if (!data || !data.length) return <DataNotice label={text("市值诊断", "Size diagnostic")} error={error} retry={retry} empty={!!data} />;
  const rows = data.map(row => ({ ...row, bucket: row.bucket_label || row.bucket, forward_return: row.mean_forward_return }));
  return <>
    <p className="panel-note">独立十分组诊断，不用于复核上方历史五分组收益。修订结果先固定形成日成员，再报告后续缺失报价；完整样本筛选仍可能带来条件选择偏差，不代表可交易或无偏收益。</p>
    {metadata.data?.revision ? <p className="size-revision-note">修订快照 · 输入版本 {metadata.data.revision.input_vintage} · 数据截至 {metadata.data.revision.as_of}。这不是原始输入版本的精确复现。缺失后续报价 {num(metadata.data.size_monotonicity?.missing_return_count)} 条，未填零，也未猜测退市终值。</p> : <DataNotice label={text("诊断版本说明", "Diagnostic version note")} error={metadata.error} retry={metadata.retry} empty={!!metadata.data} />}
    <SizeDiagnosticPanel rows={rows} dailyCurve={dailySizeCurve(comparableSizeRows(rows))} />
  </>;
}

function CorrelationPanel({ selectedFactor, onSelect }: { selectedFactor: string; onSelect: (id: string) => void }) {
  const { data, error, retry } = useJson<CorrelationMatrix>("barra/factor_correlation.json");
  const correlations = data?.[selectedFactor];
  const related = correlations && typeof correlations === "object" ? Object.entries(correlations)
    .filter(([id, value]) => id !== selectedFactor && Object.hasOwn(FACTOR_NAMES, id) && typeof value === "number" && Number.isFinite(value) && Math.abs(value) <= 1)
    .sort(([, a], [, b]) => Math.abs(b) - Math.abs(a)).slice(0, 8) : [];
  return <section role="region" aria-label={text("因子相关性", "Factor correlations")} id="barra-correlations">
    <Panel title={text("因子相关性", "Factor correlations")} tag={text("日收益差 · 非因果关系", "Daily return spread · non-causal")}>
      <p className="panel-note">与{FACTOR_NAMES[selectedFactor]}相关程度最高的 8 个因子。正相关表示同向变化，负相关表示反向变化；点击名称切换观察对象。配对样本区间未完整提供，不应直接据此构建组合。</p>
      {!related.length ? <DataNotice label="相关性" error={error} retry={retry} empty={!!data} /> :
        <div className="correlation-list">
          <div className="correlation-scale"><span>{text("−1 · 负相关", "−1 · negative")}</span><span>0</span><span>{text("正相关 · +1", "positive · +1")}</span></div>
          {related.map(([id, value]) => <button type="button" key={id} onClick={() => onSelect(id)} className="correlation-row" aria-label={text(`查看${FACTOR_NAMES[id]}，相关系数 ${value.toFixed(2)}`, `View ${FACTOR_NAMES[id]}, correlation ${value.toFixed(2)}`)}>
            <span className="correlation-name">{FACTOR_NAMES[id]}</span>
            <span className="correlation-track" aria-hidden="true"><i className={value < 0 ? "negative" : "positive"} style={{ width: `${Math.abs(value) * 50}%`, left: value < 0 ? `${50 + value * 50}%` : "50%" }} /></span>
            <strong>{value > 0 ? "+" : ""}{value.toFixed(2)}</strong>
          </button>)}
        </div>}
    </Panel>
  </section>;
}

export function BarraPage({ includeNarrative = true }: { includeNarrative?: boolean }) {
  const factorsResource = useJson<HistoricalFactor[]>("barra/historical_factor_summary.json");
  const yearlyResource = useCsv("barra/factor_yearly.csv");
  const [selectedFactor, setSelectedFactor] = useState("size");
  const [query, setQuery] = useState("");
  const [family, setFamily] = useState("全部");
  const familyLabel = (value: string) => text(value, ({ "全部": "All", "规模": "Size", "价值": "Value", "质量": "Quality", "成长": "Growth", "动量": "Momentum", "波动率": "Volatility", "市场敏感度": "Market sensitivity", "流动性": "Liquidity", "持仓与筹码": "Holdings & positioning" } as Record<string, string>)[value] ?? value);
  const [showSizeDiagnostic, setShowSizeDiagnostic] = useState(false);
  useEffect(() => {
    const restore = () => {
      const value = new URL(window.location.href).searchParams.get("factor");
      setSelectedFactor(value && Object.hasOwn(FACTOR_NAMES, value) ? value : "size");
    };
    restore();
    window.addEventListener("popstate", restore);
    return () => window.removeEventListener("popstate", restore);
  }, []);
  const selectFactor = (id: string) => {
    setSelectedFactor(id);
    const url = new URL(window.location.href);
    url.searchParams.set("factor", id);
    window.history.replaceState(null, "", url);
  };
  const factors = Array.isArray(factorsResource.data) ? factorsResource.data.filter(row => row && Object.hasOwn(FACTOR_NAMES, row.factor)) : [];
  const selectedFactorSummary = factors.find(row => row.factor === selectedFactor);
  const selectedFactorDefinition = FACTOR_DEFINITIONS.find(row => row.factor === selectedFactor);
  const selectedFactorDetail = FACTOR_DETAILS[selectedFactor];
  const groupedFamily = (id: string) => {
    const value = FACTOR_DETAILS[id]?.family ?? "其他";
    return /持仓|筹码/.test(value) ? "持仓与筹码" : value.split(" / ")[0];
  };
  const familyOrder = ["规模", "价值", "质量", "成长", "动量", "波动率", "市场敏感度", "流动性", "持仓与筹码"];
  const shown = factors.filter(row => (family === "全部" || groupedFamily(row.factor) === family) &&
    `${row.factor} ${FACTOR_NAMES[row.factor]} ${groupedFamily(row.factor)}`.toLowerCase().includes(query.trim().toLowerCase()));
  const selectedYearly = (yearlyResource.data ?? []).filter(row => row.factor === selectedFactor)
    .sort((a, b) => Number(a.year) - Number(b.year))
    .map(row => ({ year: row.year, value: Number.isFinite(finiteNumber(row.annual_ret)) ? String(finiteNumber(row.annual_ret) / 100) : "" }));
  const percentage = (value: number | undefined) => pct(value == null || !Number.isFinite(value) ? NaN : value / 100);
  const factorRows = factors.map(row => ({
    factor: FACTOR_NAMES[row.factor], coverage: `${num(row.years)} 年 · ${num(row.days)} 日`,
    annual: row.geometric_annual_ret == null ? "" : String(row.geometric_annual_ret / 100),
    vol: row.annual_vol == null ? "" : String(row.annual_vol / 100),
    sharpe: Number.isFinite(finiteNumber(row.sharpe)) ? String(Number(finiteNumber(row.sharpe).toFixed(2))) : "",
    drawdown: row.max_drawdown == null ? "" : String(row.max_drawdown / 100),
    hit: row.hit_rate == null ? "" : String(row.hit_rate / 100),
  }));
  return <div className="barra-explorer">
    {includeNarrative && <ThemeHeading kicker={text("历史研究档案 · Barra 风格因子", "Historical research archive · Barra-style factors")} title={text("A 股风格因子的长期历史表现", "Long-run A-share style-factor performance")} text={text("历史多空合成收益，不代表实际账户盈亏。", "Historical long-short composite returns do not represent account P&L.")} asof={text("各因子样本区间不同", "Sample windows differ by factor")} />}
    <nav className="section-nav" aria-label={text("本页目录", "On this page")}>
      <a href="#barra-annual">{text("因子探索", "Factor explorer")}</a><a href="#barra-factor-detail">{text("定义与计算", "Definition & calculation")}</a><a href="#barra-overview">{text("全部表现", "All performance")}</a><a href="#barra-correlations">{text("相关性", "Correlations")}</a>
    </nav>
    <section className="factor-diagnostic-workspace" aria-label={text("当前因子诊断工作区", "Selected-factor diagnostic workspace")}>
      <div className="workspace-context">
        <span className="section-kicker">{text("当前因子诊断", "Selected-factor diagnostic")}</span>
        <strong>{FACTOR_NAMES[selectedFactor]}</strong>
        <span>{text("切换因子后，历史收益、阶段指标、定义和计算方法同步更新", "Historical returns, period metrics, definitions, and calculations update with the selected factor.")}</span>
      </div>
      <section id="barra-annual" aria-label={text("年度因子探索", "Annual factor exploration")}>
      <Panel title={text("逐年合成收益与阶段表现", "Annual composite returns and period performance")} tag={text("历史序列 · 公式待核验", "Historical series · formula pending audit")}>
        <div className="explorer-layout">
          <aside className="factor-navigator" aria-label={text("因子选择", "Factor selection")}>
            <div className="factor-filter">
            <label>{text("搜索因子", "Search factors")}<input type="search" aria-label={text("搜索因子", "Search factors")} placeholder={text("中文名称或英文代码", "Chinese name or English code")} value={query} onChange={event => setQuery(event.target.value)} /></label>
              <label>{text("因子家族", "Factor family")}<select aria-label={text("因子家族", "Factor family")} value={family} onChange={event => setFamily(event.target.value)}><option value="全部">{familyLabel("全部")}</option>{familyOrder.map(value => <option key={value} value={value}>{familyLabel(value)}</option>)}</select></label>
              <span className="filter-count">{shown.length} / {factors.length} {text("个因子", "factors")}</span>
            </div>
            {!factors.length ? <DataNotice label="因子目录" error={factorsResource.error} retry={factorsResource.retry} empty={!!factorsResource.data} /> :
              !shown.length ? <div className="filter-empty" role="status"><p>{text("没有匹配的因子", "No matching factors")}</p><button type="button" className="button-link" onClick={() => { setQuery(""); setFamily("全部"); }}>{text("清除筛选", "Clear filters")}</button></div> :
              <div className="factor-groups">{familyOrder.map(group => {
                const groupFactors = shown.filter(row => groupedFamily(row.factor) === group);
                return groupFactors.length > 0 && <div className="factor-group" key={group}><span className="factor-group-label">{familyLabel(group)}</span><div>{groupFactors.map(row => <button key={row.factor} type="button" className={`choice ${selectedFactor === row.factor ? "active" : ""}`} aria-pressed={selectedFactor === row.factor} aria-controls="barra-factor-detail" data-factor={row.factor} onClick={() => selectFactor(row.factor)}>{FACTOR_NAMES[row.factor]}</button>)}</div></div>;
              })}</div>}
          </aside>
          <div className="factor-chart">
            <div className="selected-heading"><div><span className="section-kicker">{selectedFactorDetail?.family} · {selectedFactor}</span><h3>{FACTOR_NAMES[selectedFactor]}</h3></div><span className="chart-unit">{text("年度合成收益 · %", "Annual composite return · %")}</span></div>
            <section className="factor-stats" role="region" aria-label={text("所选因子关键指标", "Selected-factor key metrics")}>
              <Stat label={text("几何年化", "Geometric annualized")} value={percentage(selectedFactorSummary?.geometric_annual_ret)} note={text("历史合成序列", "Historical composite series")} />
              <Stat label={text("最大回撤", "Max drawdown")} value={percentage(selectedFactorSummary?.max_drawdown)} note={text("同一历史序列", "Same historical series")} />
              <Stat label={text("样本年数", "Sample years")} value={num(selectedFactorSummary?.years)} note={`${num(selectedFactorSummary?.days)} ${text("个交易日", "trading days")}`} />
            </section>
            {!selectedYearly.length ? <DataNotice label={text("年度收益", "Annual returns")} error={yearlyResource.error} retry={yearlyResource.retry} empty={!!yearlyResource.data} /> :
              <><BarChart rows={selectedYearly} labelKey="year" valueKey="value" color="#2563a6" />
                <details className="chart-data"><summary>{text("查看年度数值", "View annual values")}</summary><SortableTable rows={selectedYearly} columns={[["year", text("年份", "Year")], ["value", text("年度合成收益", "Annual composite return")]]} percentColumns={["value"]} /></details></>}
            <p className="panel-note">按每日多空收益差复合计算；不足一年的按已有区间展示。切换因子时样本可能不同，不宜直接排名判断优劣。</p>
          </div>
        </div>
      </Panel>
      </section>
      <div id="barra-factor-detail" role="region" aria-label="所选因子详情" aria-live="polite">
      <Panel title={text("因子定义、特征与计算方法", "Factor definition, features, and calculation")} tag={text("随所选因子联动", "Linked to selected factor")}>
        <div className="factor-detail-grid">
          <div>
            <span className="section-kicker">{selectedFactorDetail?.family} · {selectedFactor}</span>
            <h4>{FACTOR_NAMES[selectedFactor]}</h4>
            <dl className="factor-detail-list">
              <div><dt>{text("是什么 · 包含什么特征", "What it is · included features")}</dt><dd>{selectedFactorDetail?.feature}</dd></div>
              <div><dt>{text("历史页面记录的多空方向", "Historical long-short direction")}</dt><dd>{selectedFactorDefinition?.direction ?? text("未提供", "not available")}。此处沿用旧页面标签，原始得分方向待源代码核验。</dd></div>
              <div><dt>{text("怎么计算 · 已核查的现行实现", "How it is calculated · reviewed implementation")}</dt><dd>{currentFactorImplementations[selectedFactor]}</dd></div>
              <div><dt>{text("共同处理流程", "Common processing")}</dt><dd>{commonFactorProcessing}</dd></div>
              <div><dt>{text("当前核心字典对应关系", "Current core-dictionary mapping")}</dt><dd>{selectedFactorDetail?.current}</dd></div>
            </dl>
          </div>
          <aside className="factor-detail-note">
            <span className="section-kicker">{text("验证状态 · 请与收益一起阅读", "Verification status · read with returns")}</span>
            <p>现行代码已核查：{implementationSource.project} · <code>{implementationSource.revision.slice(0, 7)}</code>（{implementationSource.inspected}）。</p>
            <p>历史收益文件与原运行包一致，但历史生成提交尚未定位；包内一份元数据的校验值不一致。因此现行公式不能直接视为上方历史收益的原公式。</p>
            <p>历史收益、历史原始公式、当前核心代理是三件不同的事。PIT、持仓缺失收益及可交易性仍需独立验证。</p>
          </aside>
        </div>
        {selectedFactor === "quality" && <QualityDiagnostic />}
      </Panel>
      </div>
    </section>
    <section id="barra-overview">
      <Panel title={text("19 个因子表现总览", "Overview of 19 factor results")} tag={text("可搜索 · 可排序", "Searchable · sortable")}>
        <p className="panel-note">完整数值供查阅。短样本与长样本并列，不代表同期间比较；收益不是已验证的可交易回报。</p>
        {!factorRows.length ? <DataNotice label={text("因子总览", "Factor overview")} error={factorsResource.error} retry={factorsResource.retry} empty={!!factorsResource.data} /> :
          <SortableTable rows={factorRows} columns={[["factor", text("因子", "Factor")], ["coverage", text("样本范围", "Coverage")], ["annual", text("几何年化", "Geometric annualized")], ["vol", text("年化波动率", "Annualized volatility")], ["sharpe", text("夏普比率", "Sharpe ratio")], ["drawdown", text("最大回撤", "Max drawdown")], ["hit", text("日收益为正比例", "Positive daily-return ratio")]]} percentColumns={["annual", "vol", "drawdown", "hit"]} />}
      </Panel>
    </section>
    <CorrelationPanel selectedFactor={selectedFactor} onSelect={id => { selectFactor(id); setFamily("全部"); setQuery(""); document.getElementById("barra-annual")?.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" }); }} />
    <details className="panel size-diagnostic" onToggle={event => setShowSizeDiagnostic(event.currentTarget.open)}>
      <summary>{text("补充研究：市值十分组与稳定性诊断", "Supplement: size deciles and stability diagnostics")}</summary>
      {showSizeDiagnostic && <SizeSnapshot />}
    </details>
  </div>;
}
