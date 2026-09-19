import { useState } from "react";
import {
  asNumber,
  formatNumber as num,
  formatPercent as pct,
} from "../../lib/format";
import {
  Stat,
  Panel,
  SectionHeading,
  ResearchCard,
  BarChart,
  ControlBar,
  Choice,
  StyleSubTabs,
  ThemeHeading,
  SimpleTable,
  SortableTable,
  Loading,
  useJson,
  useCsv,
  SizeDiagnosticPanel,
} from "./research-shared";
import type {
  Row,
  StyleScope,
  BarraSummary,
  HistoricalFactor,
  CorrelationMatrix,
} from "./research-shared";

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
        kicker="指数长期回报 · ETF 可投资性"
        title="指数长期回报与可投资的基金产品"
        text="查看指数目录、十年价格回报，以及跟踪指数的代表性交易型开放式指数基金（ETF）。价格回报不含分红，基金回报还受费用和跟踪误差影响。"
        asof="已发布的历史数据"
      />
      <section className="stat-grid">
        <Stat
          label="指数目录"
          value={num(catalog.length)}
          note="已收录公开目录"
          accent
        />
        <Stat
          label="当前类别指数"
          value={num(filteredReturns.length)}
          note={category === "全部" ? "全部类别" : category}
        />
        <Stat
          label="代表性基金"
          value={num(etfs.length)}
          note="与指数对应的基金产品"
        />
        <Stat
          label="符合成交额筛选的基金"
          value={num(liquid)}
          note="近60日成交额筛选"
        />
      </section>
      <Panel title="十年价格回报最高的指数" tag="按类别筛选 · 前12名">
        <ControlBar>
          <span className="control-label">指数类别</span>
          {categories.map((value) => (
            <Choice
              key={value}
              active={category === value}
              onClick={() => setCategory(value)}
            >
              {value}
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
          这里的指数排行榜仍使用十年价格回报，类别筛选用于定位研究对象。下方 ETF
          表提供统一的 1 年、3 年、5 年和 10 年区间比较。
        </p>
      </Panel>
      <Panel title="指数与代表性基金的表现" tag="可搜索、可排序">
        <SortableTable
          rows={etfs}
          columns={[
            ["ts_code", "ETF"],
            ["matched_index_name", "跟踪指数"],
            ["etf_cagr", "基金年化回报"],
            ["index_cagr", "指数年化回报"],
            ["etf_max_drawdown", "基金最大回撤"],
            ["median_amount_60d", "近60日成交额中位数"],
          ]}
          percentColumns={["etf_cagr", "index_cagr", "etf_max_drawdown"]}
        />
      </Panel>
      <Panel title="代表性 ETF 的多区间表现" tag="前复权价格 · 2015 年以来">
        <ControlBar>
          <span className="control-label">区间</span>
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
            ["name", "名称"],
            ["matched_index_name", "跟踪指数"],
            ["start", "起始日"],
            ["end", "结束日"],
            ["total_return", "累计收益"],
            ["cagr", "年化收益"],
            ["annualized_volatility", "年化波动率"],
            ["max_drawdown", "最大回撤"],
            ["current_drawdown", "期末回撤"],
            ["median_amount", "成交额中位数"],
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
          区间从共同数据结束日倒推，按各 ETF
          的实际上市和可用交易日计算。收益使用前复权收盘价，不含费用和税费。波动率按日收益年化，期末回撤表示区间结束日相对区间内最高点的回撤。它是历史比较，不构成未来收益预测。
        </p>
      </Panel>
    </>
  );
}

const FACTOR_NAMES: Record<string, string> = {
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
  liquidity: "低换手（当前快照）",
  liquidity_flow: "大单资金流",
  lowvol: "总波动率（21日）",
  momentum: "短期动量（21日）",
  ps_value: "市销率价值",
  quality: "复合质量",
  size: "市值",
  value: "价值",
};
const FACTOR_DEFINITIONS: Row[] = [
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

const FACTOR_DETAILS: Record<string, FactorDetail> = {
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

export function BarraPage({ includeNarrative = true }: { includeNarrative?: boolean }) {
  const { data: summary, error: summaryError } = useJson<BarraSummary>(
    "barra/barra_summary.json",
  );
  const { data: quantiles, error: quantilesError } = useCsv(
    "barra/barra_size_quantiles.csv",
  );
  const { data: factors } = useJson<HistoricalFactor[]>(
    "barra/historical_factor_summary.json",
  );
  const { data: yearly } = useCsv("barra/factor_yearly.csv");
  const { data: correlations } = useJson<CorrelationMatrix>(
    "barra/factor_correlation.json",
  );
  const { data: qualityComponents } = useCsv(
    "barra/quality_component_summary.csv",
  );
  const [selectedFactor, setSelectedFactor] = useState("size");
  if (
    !summary ||
    !quantiles ||
    !factors ||
    !yearly ||
    !correlations ||
    !qualityComponents
  )
    return (
      <>
        <ThemeHeading
          kicker="18 年 A 股风格因子研究"
          title="18 年 A 股风格因子动态：收益、稳定性与市场阶段"
          text="研究快照正在加载；研究问题是这些风格因子在不同 A 股市场阶段是否持续存在。"
          asof="历史快照加载中"
        />
        <div className="callout status-panel">
          <span className="section-kicker">研究状态</span>
          <h3>历史研究快照正在加载</h3>
          <p>
            {summaryError || quantilesError
              ? "网页数据不完整，请先生成并发布 Barra 历史派生文件。"
              : "正在加载历史因子总览、逐年收益和相关性数据。"}
          </p>
        </div>
      </>
    );
  const quantileRows = quantiles.map((row) => ({
    bucket: row.bucket_label || row.bucket,
    forward_return: row.mean_forward_return,
    count: row.count,
    formation_date: row.formation_date,
  }));
  const quantileCurve = Object.values(
    quantileRows.reduce<Record<string, Row>>((result, row) => {
      const current = result[row.bucket] ?? {
        bucket: row.bucket,
        forward_return: "0",
        count: "0",
      };
      current.forward_return = String(
        Number(current.forward_return) + Number(row.forward_return || 0),
      );
      current.count = String(Number(current.count) + 1);
      result[row.bucket] = current;
      return result;
    }, {}),
  ).map((row) => ({
    bucket: row.bucket,
    value: String(Number(row.forward_return) / Math.max(Number(row.count), 1)),
  }));
  const factorRows = factors.map((factor) => ({
    factor: FACTOR_NAMES[factor.factor] ?? factor.factor,
    coverage: `${factor.years} 年 · ${factor.days} 日`,
    annual: String(factor.geometric_annual_ret / 100),
    vol: String(factor.annual_vol / 100),
    sharpe: String(factor.sharpe),
    drawdown: String(factor.max_drawdown / 100),
    hit: String(factor.hit_rate / 100),
  }));
  const selectedYearly = yearly
    .filter((row) => row.factor === selectedFactor)
    .map((row) => ({
      year: row.year,
      value: String(asNumber(row.annual_ret) / 100),
    }));
  const related = Object.entries(correlations[selectedFactor] ?? {})
    .filter(([factor]) => factor !== selectedFactor)
    .sort(([, left], [, right]) => Math.abs(right) - Math.abs(left))
    .slice(0, 8)
    .map(([factor, value]) => ({
      factor: FACTOR_NAMES[factor] ?? factor,
      correlation: String(value),
    }));
  const selectedFactorSummary = factors.find(
    (factor) => factor.factor === selectedFactor,
  );
  const selectedFactorDefinition = FACTOR_DEFINITIONS.find(
    (definition) => definition.factor === selectedFactor,
  );
  const selectedFactorDetail = FACTOR_DETAILS[selectedFactor];
  return (
    <>
      {includeNarrative && <>
      <ThemeHeading
        kicker="历史研究档案 · Barra 风格因子"
        title="A 股风格因子的长期历史表现"
        text="查看因子定义、长期表现、逐年收益、相关性和样本范围，最后补充独立计算的市值十分组研究。"
        asof="历史样本 2008-01-02 至 2026-09-04"
      />
      <div className="callout research-status">
        <span className="section-kicker">研究性质</span>
        <h3>历史多空合成收益</h3>
        <p>
          每天用高分组收益减去低分组收益，再复合计算年化和逐年收益。所得数值仅代表合成序列，不能作为实际账户盈亏。本页研究分组收益差。Barra
          风格分析还可用于解释风险来源，预测能力需要另行检验。
        </p>
      </div>
      <SectionHeading
        title="研究问题与方法"
        text="了解分组方式、行业处理和样本范围，再阅读历史结果。"
      />
      <div className="research-grid">
        <ResearchCard
          title="研究对象"
          text="研究 19 个 A 股风格因子。每个月末按当时构造的因子得分将股票分为五组，最高和最低的各 20% 分别等权建仓，固定份额持有至下个月末。每天用高分组收益减去低分组收益。财务数据是否在当时已可获取，尚未完整验证。"
        />
        <ResearchCard
          title="行业处理"
          text="按各历史日期对应的申万一级行业，先从因子值中减去本行业平均值，再进行全市场标准化。行业信息缺失的股票单列一组。这种处理后，多空两组的行业权重仍可能不同。"
        />
        <ResearchCard
          title="样本口径"
          text="大部分基础因子覆盖约 18.6 年。机构持仓、筹码和公募持仓类因子覆盖约 11 年或更短，资金流因子约 0.6 年。"
        />
      </div>
      <div className="callout">
        <span className="section-kicker">评分是否有效，交易能否实现</span>
        <p>
          判断因子评分是否有用，要看高分股票之后是否表现更好，以及收益是否随分组得分提高而上升。目前尚未提供得分与未来收益的相关性结果，还需要样本外验证和统计检验。下方将股票按市值分成十组，独立观察后续收益，与历史五分组研究采用不同分组，不能用于复核后者的多空收益。
        </p>
        <p>
          实际交易还需逐期确认能否借到股票、借券费用和保证金要求，并计入交易成本与成交限制。这些条件尚未验证。
        </p>
        <details>
          <summary>方法与术语</summary>
          <p>
            <code>IC</code> 衡量同一天各股票的因子得分与未来收益的相关性。
            <code>rankIC</code>{" "}
            比较两者的排名相关性。本页尚未提供这两项结果。样本外验证是用构造因子时未使用的数据检查结果。
          </p>
          <p>
            市值因子（<code>size</code>
            ）按大市值组减小市值组计算。下方十分组图中的 Q1 减 Q10
            则是最小市值组减最大市值组，两处方向不同。
          </p>
        </details>
      </div>
      </>}
      <Panel title="逐年合成收益与阶段表现" tag="按每日收益差复合计算">
        <ControlBar>
          <span className="control-label">因子</span>
          {factors.map((factor) => (
            <Choice
              key={factor.factor}
              active={selectedFactor === factor.factor}
              onClick={() => setSelectedFactor(factor.factor)}
            >
              {FACTOR_NAMES[factor.factor] ?? factor.factor}
            </Choice>
          ))}
        </ControlBar>
        <BarChart
          rows={selectedYearly}
          labelKey="year"
          valueKey="value"
          color="#1267d6"
        />
        <p className="panel-note">
          {FACTOR_NAMES[selectedFactor] ?? selectedFactor}：覆盖{" "}
          {selectedFactorSummary?.years ?? "未提供"} 年，合成收益的几何年化{" "}
          {pct((selectedFactorSummary?.geometric_annual_ret ?? 0) / 100)}
          ，数值沿用历史研究结果。年度收益仅按该年已有数据计算，数据不足一年的按实际区间展示。
        </p>
      </Panel>
      <Panel title="因子定义、特征与计算方法" tag="随上方因子联动">
        <div className="factor-detail-grid">
          <div>
            <span className="section-kicker">{selectedFactorDetail?.family ?? "历史因子"} · {selectedFactor}</span>
            <h4>{selectedFactorDefinition?.name ?? selectedFactor}</h4>
            <dl className="factor-detail-list">
              <div><dt>多空方向</dt><dd>{selectedFactorDefinition?.direction ?? "历史方向未提供"}</dd></div>
              <div><dt>包含什么特征</dt><dd>{selectedFactorDetail?.feature ?? "历史原始特征未完整保留"}</dd></div>
              <div><dt>怎么计算</dt><dd>{selectedFactorDetail?.calculation ?? "历史计算口径未完整保留"}</dd></div>
              <div><dt>当前核心字典对应关系</dt><dd>{selectedFactorDetail?.current ?? "当前核心字典没有完全对应的可重算定义。"}</dd></div>
            </dl>
          </div>
          <div className="factor-detail-note">
            <span className="section-kicker">可验证程度</span>
            <p>{selectedFactorDetail?.verification ?? "历史 provenance 不完整。"}</p>
            <p>上方收益来自历史分组与合成序列。名称相同不代表历史快照和当前核心 descriptor 是同一版本。缺少原始字段或计算脚本时，不用常见行业公式替代历史事实。</p>
          </div>
        </div>
        {selectedFactor === "quality" && <>
          <h4>Quality 子因子诊断</h4>
          <p className="panel-note">当前 Quality 由盈利能力、低杠杆、盈利质量、盈利稳定性四项等权复合。下表把四项拆开看，基于当前可用 PIT 财务资产，主要覆盖 2020 年以后、前 800 只股票，用于诊断复合因子的内部来源，不替代 18 年历史结果。</p>
          <SortableTable
            rows={qualityComponents.filter((row) => row.factor.startsWith("quality_")).map((row) => ({
              ...row,
              factor: ({
                quality_profitability: "盈利能力 · ROE",
                quality_leverage: "低杠杆 · Debt / Assets",
                quality_earnings_quality: "盈利质量 · OCF / Net Profit",
                quality_earnings_variability: "盈利稳定性 · 8 季度净利润同比波动",
              } as Record<string, string>)[row.factor] ?? row.factor,
            }))}
            columns={[["factor", "子因子与主要特征"], ["days", "交易日"], ["years", "样本年数"], ["geometric_annual_ret", "几何年化"], ["annual_vol", "年化波动率"], ["sharpe", "夏普比率"], ["max_drawdown", "最大回撤"], ["hit_rate", "正收益比例"]]}
            percentColumns={["geometric_annual_ret", "annual_vol", "max_drawdown", "hit_rate"]}
          />
          <div className="quality-method-grid">
            <div><strong>盈利能力</strong><span>ROE，截面缩尾后标准化。ROA 只作敏感性版本。</span></div>
            <div><strong>低杠杆</strong><span>Debt / Assets，缩尾与标准化后反向计分。</span></div>
            <div><strong>盈利质量</strong><span>OCF / Net Profit，缩尾后标准化，仍需继续核验 PIT 可见时间。</span></div>
            <div><strong>盈利稳定性</strong><span>连续 8 季度净利润同比波动率取负值，波动越小得分越高。</span></div>
          </div>
        </>}
      </Panel>
      <Panel title="19 个因子表现总览" tag="历史合成序列（账户收益未验证）">
        <SortableTable
          rows={factorRows}
          columns={[
            ["factor", "因子"],
            ["coverage", "样本范围"],
            ["annual", "合成收益的几何年化"],
            ["vol", "年化波动率"],
            ["sharpe", "夏普比率"],
            ["drawdown", "最大回撤"],
            ["hit", "日收益为正的比例"],
          ]}
          percentColumns={["annual", "vol", "drawdown", "hit"]}
        />
      </Panel>
      <Panel title="因子相关性" tag="历史多空日收益差的相关性">
        <SimpleTable
          rows={related}
          columns={[
            ["factor", "因子"],
            ["correlation", "相关系数"],
          ]}
        />
      </Panel>
      <SizeDiagnosticPanel rows={quantileRows} dailyCurve={quantileCurve} />
      {includeNarrative && <div className="fine-print">
        <span className="section-kicker">研究限制</span>
        <p>
          历史研究使用每日行情、估值和事后重建的财务数据。财务数据未完整保留当时可见的版本（
          <code>PIT</code>
          ），即使按公告日对齐，仍可能混入后续修订。各因子的样本区间不同，比较时需注意样本长度。每日收益可能存在时间相关性，夏普比率、年化收益、回撤和正收益比例均描述合成序列。尚未检验统计显著性、用自助法估计不确定性，或校正同时检验多个因子带来的偏差。历史计算将持仓期缺失收益记为零，退市时的最终价值尚未完整处理。手续费、可交易规模、涨跌停、停牌和成交限制也需另行核查。
        </p>
      </div>}
    </>
  );
}
