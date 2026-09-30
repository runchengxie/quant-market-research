import { useState } from "react";
import { sourceNotes } from "../../microcap-copy";
import {
  asNumber,
  formatNumber as num,
  formatPercent as pct,
} from "../../lib/format";
import RecoverySection from "../RecoverySection";
import ReplicationSection from "../ReplicationSection";
import { LiquidityPage } from "./liquidity-page";
import {
  NavChart,
  AnnualChart,
  MetricChart,
  UnderwaterChart,
} from "../MicrocapCharts";
import {
  Stat,
  Panel,
  SectionHeading,
  ResearchCard,
  LineChart,
  ControlBar,
  Choice,
  MicrocapSubTabs,
  ThemeHeading,
  SimpleTable,
  Loading,
  useJson,
  useCsv,
  formatTurnover,
  englishLocale,
} from "./research-shared";
import type {
  Row,
  MicrocapSummary,
  MicrocapScope,
  TurnoverPeriod,
  SmallcapTurnoverData,
} from "./research-shared";

type HistoricalMicrocapData = {
  coverage_start: string;
  coverage_end: string;
  trading_days: number;
  quality_status: string;
  series: Record<
    string,
    {
      max_drawdown: number;
      longest_completed_underwater_sessions: number;
      longest_observed_underwater_sessions: number;
      completed_duration_quantiles: Record<string, number>;
      survival_probability_beyond_sessions: Record<string, number>;
      episode_count: number;
      completed_episode_count: number;
      right_censored_episode_count: number;
    }
  >;
  coverage_by_year: Array<{
    calendar_year: number;
    rows: number;
    valid_adj_close: number;
    eligible_rows: number;
    suspended_rows: number;
  }>;
  audit_notes: string[];
  caveats: string[];
};
type MicrocapRepairSummary = {
  coverage_start: string;
  coverage_end: string;
  missing_holdings: number;
  evidence_counts: {
    suspension: number;
    suspension_and_st: number;
    unclassified: number;
    delist: number;
  };
  variants: Array<{
    name: string;
    observations: number;
    final_nav: number;
    max_drawdown: number;
  }>;
  caveats: string[];
};
type ReconstructedMicrocapSummary = Row & {caveats?: string[]};

function HistoricalMicrocapSection() {
  const t = (zh: string, en: string) => englishLocale() ? en : zh;
  const { data, error } = useJson<HistoricalMicrocapData>(
    "microcap_history_2008_2014.json",
  );
  if (error)
    return (
      <div className="callout compact">
        <span className="section-kicker">{t("2008–2014 历史补充", "2008–2014 historical supplement")}</span>
        <p>{t("历史补充汇总暂时无法加载：", "Historical supplement failed to load: ")}{error}</p>
      </div>
    );
  if (!data) return <Loading />;
  const rows = Object.entries(data.series).map(([n, item]) => ({
    n: `N=${n}`,
    max_drawdown: pct(item.max_drawdown),
    longest: `${num(item.longest_completed_underwater_sessions)} ${t("个交易日", "trading days")}`,
    p95: `${num(item.completed_duration_quantiles["0.95"])} ${t("个交易日", "trading days")}`,
    over_year: pct(item.survival_probability_beyond_sessions["252"]),
    episodes: num(item.completed_episode_count),
  }));
  const latest = data.coverage_by_year.at(-1);
  return (
    <Panel title={t("2008–2014 年微盘历史补充", "2008–2014 microcap history")} tag={t("独立历史口径", "Independent historical basis")}>
      <p className="panel-note">
        {t("这段日频重建覆盖", "This daily reconstruction covers")} {data.coverage_start} {t("至", "to")} {data.coverage_end}，{t("共", "with")} {num(data.trading_days)} {t("个交易日。每年都有价格和市值记录，2014 年有效价格行", "trading days. Price and market-value records are available for every year; valid 2014 price rows: ")} {num(latest?.valid_adj_close ?? 0)}. {t("但历史源的 ST（特别处理股票）和停牌资格字段不完整，因此单独展示，不与 2015 年后的清洗口径拼接。", "Eligibility fields for special-treatment stocks and suspensions are incomplete in the historical source. This period is shown separately and is not joined to the cleaned basis from 2015 onward.")}
      </p>
      <SimpleTable
        rows={rows}
        columns={[
          ["n", t("组合规模", "Basket size")],
          ["max_drawdown", t("最大回撤", "Max drawdown")],
          ["longest", t("最长已完成水下期", "Longest completed underwater period")],
          ["p95", t("水下期 95% 分位", "95th percentile underwater duration")],
          ["over_year", t("超过一年比例", "Share exceeding one year")],
          ["episodes", t("已完成区间数", "Completed episodes")],
        ]}
      />
      <p className="panel-note">
        {t("最长已完成水下期只表示已经回到前高的区间。样本末仍未回本的", "The longest completed underwater period covers episodes that recovered to a prior high. Episodes still below the high at the sample end (")}{" "}
        {num(data.series["400"]?.right_censored_episode_count ?? 0)}{" "}
        {t("个区间单独计为右删失，不能把它当成最终恢复时长。完整逐日净值和事件明细保存在仓库外。", ") are counted separately as right-censored; this is not their eventual recovery duration. Full daily NAV and event details are kept outside the repository.")}
      </p>
    </Panel>
  );
}

export function SmallcapTurnoverSection() {
  const t = (zh: string, en: string) => englishLocale() ? en : zh;
  const { data, error } = useJson<SmallcapTurnoverData>(
    "smallcap_turnover.json",
  );
  const [rankCount, setRankCount] = useState(400);
  const [granularity, setGranularity] = useState<"annual" | "monthly">(
    "annual",
  );
  if (error)
    return (
      <div className="callout compact">
        <span className="section-kicker">{t("小微盘成交额研究", "Small-cap turnover research")}</span>
        <p>{t("网页汇总暂时无法加载：", "Web summary failed to load: ")}{error}</p>
      </div>
    );
  if (!data) return <Loading />;
  const cleanRows = data.clean[granularity].filter(
    (row) => row.rank_count === rankCount,
  );
  const historicalRows = data.historical[granularity].filter(
    (row) => row.rank_count === rankCount,
  );
  const labelOf = (row: TurnoverPeriod | Record<string, never>) =>
    granularity === "annual" ? String(row.year ?? "") : (row.month ?? "");
  const labels = [
    ...new Set([...cleanRows, ...historicalRows].map(labelOf)),
  ].sort();
  const byPeriod = (rows: TurnoverPeriod[]) =>
    new Map(rows.map((row) => [labelOf(row), row.turnover_median]));
  const cleanByPeriod = byPeriod(cleanRows);
  const historicalByPeriod = byPeriod(historicalRows);
  const chartRows: Row[] = labels.map((label) => ({
    period: label,
    clean: cleanByPeriod.has(label) ? formatTurnover(cleanByPeriod.get(label)!) : "N/A",
    historical: historicalByPeriod.has(label) ? formatTurnover(historicalByPeriod.get(label)!) : "N/A",
  }));
  const latestClean = cleanRows.at(-1);
  const latestHistorical = historicalRows.at(-1);
  const periodLabel = granularity === "annual" ? t("年度", "annual") : t("月度", "monthly");
  const diagnosticNote =
    rankCount === 1
      ? t("N = 1 是每日市值最小的一只股票，仅作极端诊断。个股切换、停牌、涨跌停和数据异常都会显著影响它，不能代表一组可交易的股票。", "N=1 tracks only the smallest stock by market value each day and serves as an extreme-case diagnostic. Constituent changes, suspensions, price limits, and data anomalies can dominate the result; it does not represent a tradable basket.")
      : t("N 较大的口径更适合观察一组小市值股票的整体成交额。", "Larger N values are more representative of aggregate turnover across a basket of small-cap stocks.");
  const auditRows: Row[] = data.overlap_audit.map((row) => ({
    rank_count: String(row.rank_count),
    common_days: num(row.common_days),
    mean_diff: pct(row.mean_abs_relative_diff_turnover_median),
    p90_diff: pct(row.p90_abs_relative_diff_turnover_median),
    within_10: pct(row.within_10pct_ratio),
  }));
  return (
    <>
      <SectionHeading
        title={t("小微盘成交额研究", "Small-cap turnover research")}
        text={t("按每日总市值选取最小 N 只股票，N 表示股票数量。页面用它观察日成交额的历史变化，并把清洗口径与长历史口径并列展示。", "Select the N smallest stocks by daily total market value. The page compares turnover history under the cleaned and long-history definitions.")}
      />
      <div className="callout compact">
        <span className="section-kicker">{t("覆盖口径", "Coverage definitions")}</span>
        <p>
          <strong>{t("2015 年起清洗口径", "Cleaned basis from 2015")}</strong> {t("覆盖 ST、停牌和价格质量规则，数据较完整。", "applies special-treatment, suspension, and price-quality rules and has more complete coverage.")} <strong>{t("2008 年起历史口径", "Historical basis from 2008")}</strong> {t("时间更长，但历史源缺少可靠的 ST 和停牌标记，覆盖不完整。图表的年度值和月度值都表示对应周期内日成交额的中位数，不做累计。", "extends further back but has incomplete coverage because the historical source lacks reliable special-treatment and suspension flags. Annual and monthly chart values are medians of daily turnover within each period, not cumulative totals.")}
        </p>
      </div>
      <section className="stat-grid">
        <Stat
          label={t("清洗口径覆盖", "Cleaned coverage")}
          value={data.clean.coverage_start + (englishLocale() ? " to " : " 至 ") + data.clean.coverage_end}
          note={t("主分析口径", "Primary analysis basis")}
          accent
        />
        <Stat
          label={t("历史口径覆盖", "Historical coverage")}
          value={
            data.historical.coverage_start +
            (englishLocale() ? " to " : " 至 ") +
            data.historical.coverage_end
          }
          note={t("覆盖不完整", "Incomplete coverage")}
        />
        <Stat
          label={"N = " + rankCount + " · " + t("清洗口径", "cleaned basis")}
          value={formatTurnover(latestClean?.turnover_median ?? NaN)}
          note={labelOf(latestClean ?? {}) + " " + periodLabel + t("日中位数", " daily median")}
        />
        <Stat
          label={"N = " + rankCount + " · " + t("历史口径", "historical basis")}
          value={formatTurnover(latestHistorical?.turnover_median ?? NaN)}
          note={
            labelOf(latestHistorical ?? {}) + " " + periodLabel + t("日中位数", " daily median")
          }
        />
      </section>
      <Panel
        title={t("最小 N 只股票的日成交额", "Daily turnover of the N smallest stocks")}
        tag={periodLabel + t("汇总 · 可缩放", " summary · zoomable")}
      >
        <ControlBar>
          <span className="control-label">{t("统计粒度", "Granularity")}</span>
          <Choice
            active={granularity === "annual"}
            onClick={() => setGranularity("annual")}
          >
            {t("年度汇总", "Annual")}
          </Choice>
          <Choice
            active={granularity === "monthly"}
            onClick={() => setGranularity("monthly")}
          >
            {t("月度汇总", "Monthly")}
          </Choice>
          <span className="control-label">{t("股票数量", "Stock count")}</span>
          {data.clean.rank_counts.map((value) => (
            <Choice
              key={value}
              active={rankCount === value}
              onClick={() => setRankCount(value)}
            >
              N = {value}
            </Choice>
          ))}
        </ControlBar>
        <LineChart
          labels={labels}
          series={[
            {
              name: t("2015+ 清洗口径", "2015+ cleaned basis"),
              values: labels.map((label) => cleanByPeriod.get(label) ?? null),
              color: "#1267d6",
            },
            {
              name: t("2008+ 历史口径", "2008+ historical basis"),
              values: labels.map(
                (label) => historicalByPeriod.get(label) ?? null,
              ),
              color: "#b96800",
            },
          ]}
        />
        <details className="chart-data-details">
          <summary>{t("查看图表数据", "View chart data")}</summary>
          <SimpleTable rows={chartRows} columns={[["period", periodLabel], ["clean", t("2015+ 清洗口径", "2015+ cleaned basis")], ["historical", t("2008+ 历史口径", "2008+ historical basis")]]} />
        </details>
        <p className="panel-note">
          {diagnosticNote} {t("单位为人民币成交额。网页只发布", "Turnover is in CNY. The site publishes only the ")}{periodLabel}{t("汇总，完整日频明细仍保留在仓库外的研究输出目录。", " summary; full daily detail remains in the research output directory outside the repository.")}
        </p>
      </Panel>
      <Panel
        title={t("清洗口径与历史口径的重叠审计", "Overlap audit: cleaned vs historical")}
        tag={"2015-01-05 " + t("至", "to") + " 2026-08-21"}
      >
        <p className="panel-note">
          {t("审计比较两套口径在共同日期上的日成交额中位数相对差异。差异来自历史口径的股票资格判定不完整，这张表用于识别可比边界。它不能说明历史口径已经完成清洗。", "This audit compares relative differences in median daily turnover on shared dates. Differences reflect incomplete stock-eligibility records in the historical basis. The table defines the comparison boundary; it does not show that the historical basis has been cleaned.")}
        </p>
        <SimpleTable
          rows={auditRows}
          columns={[
            ["rank_count", "N"],
            ["common_days", t("共同交易日", "Shared trading days")],
            ["mean_diff", t("平均绝对相对差异", "Mean absolute relative difference")],
            ["p90_diff", t("P90绝对相对差异", "P90 absolute relative difference")],
            ["within_10", t("10%以内比例", "Share within 10%")],
          ]}
        />
      </Panel>
      <div className="fine-print">
        <span className="section-kicker">{t("研究边界", "Research boundary")}</span>
        <p>{sourceNotes(data.caveats)}</p>
      </div>
    </>
  );
}

export function MicrocapPage({
  initialScope = "a-share",
}: {
  initialScope?: MicrocapScope;
}) {
  const [scope, setScope] = useState<MicrocapScope>(initialScope);
  return (
    <>
      <MicrocapSubTabs scope={scope} onChange={setScope} />
      {scope === "cross-market" ? (
        <LiquidityPage embedded />
      ) : (
        <>
          <ReplicationSection scope="microcap" />
          <RecoverySection scope="microcap" />
          <MicrocapPageContent includeMethod={false} />
        </>
      )}
    </>
  );
}

function MicrocapMethodSection() {
  const t = (zh: string, en: string) => englishLocale() ? en : zh;
  return (
    <>
      <SectionHeading
        title={t("这项实验怎么做", "How this experiment works")}
        text={t("先固定规则，再检查数据能不能支持这套规则。每一步都尽量使用当时已经知道的信息。", "Fix the rules first, then test whether the data supports them. Each step uses only information available at the time.")}
      />
      <div className="research-grid">
        <ResearchCard
          title={t("第一步：准备数据", "Step 1: Prepare the data")}
          text={t("使用 Tushare（行情数据接口）的 A 股日线、估值和复权价格。另取停牌记录与 ST（特别处理股票）记录，用来核对没有报价的日期。行情数据目前覆盖到 2026 年 9 月 17 日。", "Use Tushare A-share daily prices, valuation data, and adjusted prices. Suspension and special-treatment records are also used to investigate dates without quotes. Market data currently runs through 2026-09-17.")}
        />
        <ResearchCard
          title={t("第二步：选出股票", "Step 2: Select stocks")}
          text={t("在每个交易日收盘后，按总市值从小到大排序，选出最小的 400 只股票。剔除当日处于 ST、停牌状态，或价格、市值无效的股票。", "After each market close, rank stocks by total market value and select the 400 smallest. Exclude stocks marked special-treatment or suspended that day, as well as invalid prices or market values.")}
        />
        <ResearchCard
          title={t("第三步：计算收益", "Step 3: Calculate returns")}
          text={t("组合在下一交易日收盘时成交，再持有到下一个交易日收盘。400 只股票等权计算组合收益。最后一个有行情的交易日没有下一交易日，因此不计算它的收益。", "The portfolio trades at the next trading-day close and is held until the following close. Returns are equal-weighted across 400 stocks. No return is calculated for the final observed trading day because there is no next session.")}
        />
        <ResearchCard
          title={t("第四步：核对缺口", "Step 4: Audit missing prices")}
          text={t("如果选中的股票在下一交易日没有报价，就查看它之后何时恢复报价，以及这段时间是否有停牌或 ST 记录。查不到直接证据的缺口继续保留，避免把数据问题当成投资结果。", "When a selected stock has no quote on the next trading day, check when quotes resume and whether suspension or special-treatment records exist in the gap. Leave gaps without direct evidence unresolved rather than treating data problems as investment outcomes.")}
        />
      </div>
      <Panel title={t("三种收益口径怎么读", "How to read the three return treatments")} tag={t("主结果与敏感性", "Primary result and sensitivities")}>
        <SimpleTable
          rows={[
            {
              name: t("严格口径", "Strict"),
              meaning: t("所有选中股票都有下一交易日价格才计算这一天的收益", "Calculate a day's return only when every selected stock has a next-session price."),
              use: t("主结果", "Primary result"),
            },
            {
              name: t("部分股票重算", "Reweight available prices"),
              meaning: t("只用有价格的股票计算，并重新分配权重", "Calculate using only stocks with prices and redistribute their weights."),
              use: t("观察缺失价格对结果的上限影响", "Sensitivity to missing prices"),
            },
            {
              name: t("有证据的停牌按持平", "Flat return for evidenced suspensions"),
              meaning: t("只对有停牌记录的缺失按零收益处理，其他缺口仍不计算", "Assign zero return only to missing prices with suspension evidence; leave other gaps uncalculated."),
              use: t("停牌处理的敏感性", "Suspension-treatment sensitivity"),
            },
          ]}
          columns={[
            ["name", t("口径", "Treatment")],
            ["meaning", t("计算方法", "Calculation")],
            ["use", t("用途", "Purpose")],
          ]}
        />
        <p className="panel-note">
          {t("网页上的严格口径仍是主结果。其他口径的有效交易日不同，不能直接拼成一条净值，也不能用来证明策略可以交易。", "The strict treatment remains the primary result. Other treatments use different sets of valid trading days, so their series must not be stitched together or treated as evidence of tradability.")}
        </p>
      </Panel>
      <Panel title={t("页面里的几个英文词", "Terms used on this page")} tag={t("首次出现时说明", "Defined at first mention")}>
        <SimpleTable
          rows={[
            { name: "Tushare", meaning: t("提供行情和其他金融数据的接口", "An interface providing market and other financial data.") },
            { name: "`suspend_d`", meaning: t("每日停牌记录，保留项目内部键值", "Daily suspension records; the internal field name is retained.") },
            { name: "`stock_st`", meaning: t("ST 状态记录，保留项目内部键值", "Special-treatment status records; the internal field name is retained.") },
            { name: "ST", meaning: t("特别处理股票", "Special-treatment status for a listed stock.") },
            { name: "PIT", meaning: t("点时数据，也就是当时已经可以获得的信息", "Point-in-time: information that was available at the time.") },
            { name: "NAV", meaning: t("净值", "Net asset value.") },
            { name: "ETF", meaning: t("交易型开放式指数基金", "Exchange-traded fund.") },
          ]}
          columns={[
            ["name", t("名称", "Term")],
            ["meaning", t("中文说明", "Definition")],
          ]}
        />
      </Panel>
    </>
  );
}

export function MicrocapPageContent({ includeMethod = true }: { includeMethod?: boolean }) {
  const t = (zh: string, en: string) => englishLocale() ? en : zh;
  const { data: summary } = useJson<MicrocapSummary>(
    "index/microcap/summary.json",
  );
  const { data: reconstructed } = useJson<ReconstructedMicrocapSummary>(
    "index/microcap/reconstructed_summary.json",
  );
  const { data: nav } = useCsv("index/microcap/nav.csv");
  const { data: reconstructedNav } = useCsv(
    "index/microcap/reconstructed_daily_nav.csv",
  );
  const { data: annual } = useCsv("index/microcap/annual_returns.csv");
  const { data: cagr } = useCsv("index/microcap/rolling_cagr.csv");
  const { data: drawdown } = useCsv("index/microcap/rolling_drawdown.csv");
  const { data: underwater } = useCsv(
    "index/microcap/reconstructed_underwater_periods.csv",
  );
  const { data: repair } = useJson<MicrocapRepairSummary>(
    "microcap_repair_summary.json",
  );
  if (
    !summary ||
    !reconstructed ||
    !nav ||
    !reconstructedNav ||
    !annual ||
    !cagr ||
    !drawdown ||
    !underwater
  )
    return <Loading />;
  const latestAnnual = annual.find((row) => row.year === "2025");
  return (
    <>
      <SmallcapTurnoverSection />
      <HistoricalMicrocapSection />
      {includeMethod && <MicrocapMethodSection />}
      {repair && (
        <Panel
          title={t("缺失价格审计", "Missing-price audit")}
          tag={`${t("审计区间", "Audit window")} ${repair.coverage_start} ${t("至", "to")} ${repair.coverage_end}`}
        >
          <p className="panel-note">
            {t("最小市值 400 组合共有", "The smallest-400 basket has")} {num(repair.missing_holdings)} {t("条缺失持仓。", "missing holding-price records.")} {num(repair.evidence_counts.suspension)} {t("条有停牌证据，其中", "records have suspension evidence, including")} {num(repair.evidence_counts.suspension_and_st)} {t("条同时有 ST 证据。", "with special-treatment evidence as well.")} {num(repair.evidence_counts.unclassified)} {t("条没有找到直接证据。当前没有可用的退市日期。", "records have no direct evidence. No usable delisting dates are currently available.")}
          </p>
          <SimpleTable
            rows={repair.variants.map((item) => ({
              variant: t(item.name, ({strict: "Strict", partial: "Reweight available prices", carry_all_missing: "Carry all missing prices", carry_evidence_only: "Carry evidenced suspensions"} as Record<string, string>)[item.name] ?? item.name),
              observations: num(item.observations),
              final_nav: num(item.final_nav),
              max_drawdown: pct(item.max_drawdown),
            }))}
            columns={[
              ["variant", t("口径", "Treatment")],
              ["observations", t("有效交易日", "Valid trading days")],
              ["final_nav", t("期末净值", "Ending NAV")],
              ["max_drawdown", t("最大回撤", "Max drawdown")],
            ]}
          />
          <p className="panel-note">
            {t("严格口径用于主图。其他口径只用来观察缺失价格的影响，数据覆盖不同，不能直接比较。", "The strict treatment is used in the main chart. Other treatments only show the sensitivity to missing prices; coverage differs, so their results are not directly comparable.")} {sourceNotes(repair.caveats)}
          </p>
        </Panel>
      )}
      <ThemeHeading
        kicker={t("历史研究档案 · 微盘规则复现", "Historical research archive · microcap rule reconstruction")}
        title={t("小微盘的长期收益、回撤与交易限制", "Long-term returns, drawdowns, and trading constraints for microcaps")}
        text={t("这组结果用固定规则重建小市值股票组合，帮助观察长期收益和风险。规则重建与公开参考指数的成分、调仓和数据来源不同。", "These results reconstruct a small-cap portfolio with fixed rules to study long-term returns and risk. The reconstruction differs from the public reference index in constituents, rebalancing, and data source.")}
        asof={`${t("重建截至", "Reconstruction through")} ${reconstructedNav.at(-1)?.date ?? t("未提供", "not available")}`}
      />
      <section className="stat-grid">
        <Stat
          label={t("公开参考净值", "Public reference NAV")}
          value={num(asNumber(nav.at(-1)?.nav))}
          note={`${t("截至", "Through")} ${nav.at(-1)?.date ?? t("未提供", "not available")}`}
          accent
        />
        <Stat
          label={t("2025年收益", "2025 return")}
          value={pct(asNumber(latestAnnual?.return))}
          note={t("公开资料参考", "Public reference")}
        />
        <Stat
          label={t("重建最大回撤", "Reconstructed max drawdown")}
          value={pct(asNumber(reconstructed.max_drawdown))}
          note={t("2015年以来日频", "Daily, since 2015")}
        />
        <Stat
          label={t("最长未回到前高的时间", "Longest time below a prior high")}
          value={`${num(asNumber(reconstructed.longest_underwater_trading_days))} ${t("个交易日", "trading days")}`}
          note={`${reconstructed.longest_underwater_start ?? t("未提供", "not reported")} ${t("至", "to")} ${reconstructed.longest_underwater_end ?? t("未提供", "not reported")}`}
        />
        <Stat
          label={t("重建样本", "Reconstructed sample")}
          value={`${num(asNumber(reconstructed.observations))} ${t("天", "days")}`}
          note={`${reconstructed.coverage_start ?? t("未提供", "not reported")} ${t("至", "to")} ${reconstructed.coverage_end ?? t("未提供", "not reported")}`}
        />
      </section>
      <div className="panel ytd-panel">
        <div className="panel-title">
          <h3>{t("2026 年至今", "2026 year to date")}</h3>
          <span className="tag warm">{t("公开资料参考", "Public reference")}</span>
        </div>
        <p>
          {t("公开资料参考收益截至", "Public-reference returns run through")} {summary.metrics.ytd_2026_as_of ?? t("未提供", "not reported")}. {t("规则重建净值截至", "The reconstructed NAV runs through")} {reconstructed.coverage_end ?? t("未提供", "not reported")}. {t("两组数据的规则不同，页面分开展示。", "The two series use different rules and are shown separately.")}
        </p>
      </div>
      <SectionHeading
        title={t("收益路径", "Return paths")}
        text={t("查看公开参考和规则重建的历史净值、回撤与恢复过程。", "Review historical NAV, drawdowns, and recovery paths for the public reference and reconstruction.")}
      />
      <div className="panel">
        <div className="panel-title">
          <h3>{t("公开资料参考净值", "Public reference NAV")}</h3>
          <span className="tag">{t("可悬停、缩放", "Hover and zoom")}</span>
        </div>
        <NavChart rows={nav} name={t("公开资料参考", "Public reference")} color="#1267d6" />
      </div>
      <div className="panel">
        <div className="panel-title">
          <h3>{t("规则重建净值（数据来源：Tushare）", "Rule-reconstructed NAV (source: Tushare)")}</h3>
          <span className="tag warm">{t("2015年以来 · 可悬停、缩放", "Since 2015 · hover and zoom")}</span>
        </div>
        <p className="panel-note">
          {t("按上海、深圳 A 股总市值选取最小 400 只，等权持有至下一交易日。图表用于观察规则路径，未扣除交易成本。", "Select the 400 smallest Shanghai and Shenzhen A-share stocks by total market value, weight them equally, and hold through the next trading day. The chart shows the rule-based path before transaction costs.")}
        </p>
        <NavChart
          rows={reconstructedNav}
          name={t("Tushare 规则重建净值", "Tushare rule-reconstructed NAV")}
          color="#b96800"
        />
      </div>
      <div className="panel">
        <div className="panel-title">
          <h3>{t("年度收益", "Annual returns")}</h3>
          <span className="tag warm">{t("悬停查看数值", "Hover for values")}</span>
        </div>
        <AnnualChart rows={annual} />
      </div>
      <div className="research-grid">
        <Panel title={t("滚动年化收益", "Rolling annualized returns")} tag={t("持有期限", "Holding period")}>
          <MetricChart rows={cagr} value="cagr" label={t("年化收益", "Annualized return")} />
        </Panel>
        <Panel title={t("滚动最大回撤", "Rolling maximum drawdown")} tag={t("月频与日频参考", "Monthly and daily reference")}>
          <MetricChart rows={drawdown} value="max_drawdown" label={t("最大回撤", "Max drawdown")} />
        </Panel>
      </div>
      <div className="panel">
        <div className="panel-title">
          <h3>{t("最长未回到前高的区间", "Longest periods below a prior high")}</h3>
          <span className="tag warm">{t("按交易日排序", "Ranked by trading days")}</span>
        </div>
        <p className="panel-note">
          {t("水下期指净值低于此前高点的连续时间。图表展示持续时间最长的 10 个区间，悬停可以查看区间回撤。", "An underwater period is the time the NAV stays below a prior high. The chart shows the 10 longest episodes; hover to inspect each episode’s drawdown.")}
        </p>
        <UnderwaterChart rows={underwater} />
      </div>
      <SectionHeading
        title={t("研究解读", "Research interpretation")}
        text={t("了解选股规则、收益来源、历史阶段和实际复制的难点。", "Understand the selection rules, return drivers, historical phases, and replication challenges.")}
      />
      <div className="research-grid">
        <ResearchCard
          title={t("两个微盘口径", "Two micro-cap definitions")}
          text={t("8841431.WI 每日调仓，适合观察极小市值与再平衡机制。868008.WI 每月调仓，换手和执行压力相对更低。", "8841431.WI rebalances daily and is useful for studying the smallest-cap segment and rebalancing effects. 868008.WI rebalances monthly, with relatively lower turnover and execution pressure.")}
        />
        <ResearchCard
          title={t("收益来源", "Potential return drivers")}
          text={t("收益可能来自极小市值、等权调仓、短期价格反转，以及承担流动性风险的补偿。各项贡献尚未精确计算。", "Returns may reflect very small market capitalization, equal-weight rebalancing, short-term price reversal, and compensation for liquidity risk. Their individual contributions have not been estimated precisely.")}
        />
        <ResearchCard
          title={t("历史阶段", "Historical periods")}
          text={t("2001 至 2005 年连续下跌。2006 至 2015 年多个极端上涨年份抬高长期年化收益。2017 至 2018 年微盘风格表现不利。", "Returns declined through 2001–2005. Several extreme up years from 2006–2015 raised long-run annualized returns. Micro-cap stocks underperformed in 2017–2018.")}
        />
        <ResearchCard
          title={t("复制难度", "Implementation constraints")}
          text={t("实际复制还要考虑成交不足、涨跌停、停牌、退市和冲击成本。", "Practical implementation must account for insufficient liquidity, price limits, suspensions, delistings, and market impact.")}
        />
      </div>
      <div className="fine-print">
        <span className="section-kicker">{t("研究边界", "Research boundary")}</span>
        <p>
          {sourceNotes(reconstructed.caveats ?? ["这是基于本地 Tushare 日线数据的规则重建，不是 Wind 8841431.WI 官方指数。", "使用复权收盘价计算，当前版本未模拟涨跌停无法成交、手续费、印花税、冲击成本和资金容量。", "调仓信号使用当日总市值，收益从下一交易日收盘价计算，保留了一天的持有滞后。"])}
        </p>
      </div>
    </>
  );
}
