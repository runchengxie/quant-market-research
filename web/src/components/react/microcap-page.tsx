import { useState } from "react";
import { readableNotes } from "../../research-copy";
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

function HistoricalMicrocapSection() {
  const { data, error } = useJson<HistoricalMicrocapData>(
    "microcap_history_2008_2014.json",
  );
  if (error)
    return (
      <div className="callout compact">
        <span className="section-kicker">2008–2014 历史补充</span>
        <p>历史补充汇总暂时无法加载：{error}</p>
      </div>
    );
  if (!data) return <Loading />;
  const rows = Object.entries(data.series).map(([n, item]) => ({
    n: `N=${n}`,
    max_drawdown: pct(item.max_drawdown),
    longest: `${num(item.longest_completed_underwater_sessions)} 个交易日`,
    p95: `${num(item.completed_duration_quantiles["0.95"])} 个交易日`,
    over_year: pct(item.survival_probability_beyond_sessions["252"]),
    episodes: num(item.completed_episode_count),
  }));
  const latest = data.coverage_by_year.at(-1);
  return (
    <Panel title="2008–2014 年微盘历史补充" tag="独立历史口径">
      <p className="panel-note">
        这段日频重建覆盖 {data.coverage_start} 至 {data.coverage_end}，共{" "}
        {num(data.trading_days)} 个交易日。每年都有价格和市值记录，2014
        年有效价格行 {num(latest?.valid_adj_close ?? 0)}，但历史源的
        ST（特别处理股票）和停牌资格字段不完整，因此单独展示，不与 2015
        年后的清洗口径拼接。
      </p>
      <SimpleTable
        rows={rows}
        columns={[
          ["n", "组合规模"],
          ["max_drawdown", "最大回撤"],
          ["longest", "最长已完成水下期"],
          ["p95", "水下期 95% 分位"],
          ["over_year", "超过一年比例"],
          ["episodes", "已完成区间数"],
        ]}
      />
      <p className="panel-note">
        最长已完成水下期只表示已经回到前高的区间。样本末仍未回本的{" "}
        {num(data.series["400"]?.right_censored_episode_count ?? 0)}{" "}
        个区间单独计为右删失，不能把它当成最终恢复时长。完整逐日净值和事件明细保存在仓库外。
      </p>
    </Panel>
  );
}

export function SmallcapTurnoverSection() {
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
        <span className="section-kicker">小微盘成交额研究</span>
        <p>网页汇总暂时无法加载：{error}</p>
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
  const periodLabel = granularity === "annual" ? "年度" : "月度";
  const diagnosticNote =
    rankCount === 1
      ? "N = 1 是每日市值最小的一只股票，仅作极端诊断。个股切换、停牌、涨跌停和数据异常都会显著影响它，不能代表一组可交易的股票。"
      : "N 较大的口径更适合观察一组小市值股票的整体成交额。";
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
        title="小微盘成交额研究"
        text="按每日总市值选取最小 N 只股票，N 表示股票数量。页面用它观察日成交额的历史变化，并把清洗口径与长历史口径并列展示。"
      />
      <div className="callout compact">
        <span className="section-kicker">覆盖口径</span>
        <p>
          <strong>2015 年起清洗口径</strong>覆盖
          ST、停牌和价格质量规则，数据较完整。<strong>2008 年起历史口径</strong>
          时间更长，但历史源缺少可靠的 ST
          和停牌标记，覆盖不完整。图表的年度值和月度值都表示对应周期内日成交额的中位数，不做累计。
        </p>
      </div>
      <section className="stat-grid">
        <Stat
          label="清洗口径覆盖"
          value={data.clean.coverage_start + " 至 " + data.clean.coverage_end}
          note="主分析口径"
          accent
        />
        <Stat
          label="历史口径覆盖"
          value={
            data.historical.coverage_start +
            " 至 " +
            data.historical.coverage_end
          }
          note="覆盖不完整"
        />
        <Stat
          label={"N = " + rankCount + " · 清洗口径"}
          value={formatTurnover(latestClean?.turnover_median ?? NaN)}
          note={labelOf(latestClean ?? {}) + " " + periodLabel + "日中位数"}
        />
        <Stat
          label={"N = " + rankCount + " · 历史口径"}
          value={formatTurnover(latestHistorical?.turnover_median ?? NaN)}
          note={
            labelOf(latestHistorical ?? {}) + " " + periodLabel + "日中位数"
          }
        />
      </section>
      <Panel
        title="最小 N 只股票的日成交额"
        tag={periodLabel + "汇总 · 可缩放"}
      >
        <ControlBar>
          <span className="control-label">统计粒度</span>
          <Choice
            active={granularity === "annual"}
            onClick={() => setGranularity("annual")}
          >
            年度汇总
          </Choice>
          <Choice
            active={granularity === "monthly"}
            onClick={() => setGranularity("monthly")}
          >
            月度汇总
          </Choice>
          <span className="control-label">股票数量</span>
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
              name: "2015+ 清洗口径",
              values: labels.map((label) => cleanByPeriod.get(label) ?? null),
              color: "#1267d6",
            },
            {
              name: "2008+ 历史口径",
              values: labels.map(
                (label) => historicalByPeriod.get(label) ?? null,
              ),
              color: "#b96800",
            },
          ]}
        />
        <details className="chart-data-details">
          <summary>查看图表数据</summary>
          <SimpleTable rows={chartRows} columns={[["period", periodLabel], ["clean", "2015+ 清洗口径"], ["historical", "2008+ 历史口径"]]} />
        </details>
        <p className="panel-note">
          {diagnosticNote} 单位为人民币成交额。网页只发布{periodLabel}
          汇总，完整日频明细仍保留在仓库外的研究输出目录。
        </p>
      </Panel>
      <Panel
        title="清洗口径与历史口径的重叠审计"
        tag="2015-01-05 至 2026-08-21"
      >
        <p className="panel-note">
          审计比较两套口径在共同日期上的日成交额中位数相对差异。差异来自历史口径的股票资格判定不完整，这张表用于识别可比边界。它不能说明历史口径已经完成清洗。
        </p>
        <SimpleTable
          rows={auditRows}
          columns={[
            ["rank_count", "N"],
            ["common_days", "共同交易日"],
            ["mean_diff", "平均绝对相对差异"],
            ["p90_diff", "P90绝对相对差异"],
            ["within_10", "10%以内比例"],
          ]}
        />
      </Panel>
      <div className="fine-print">
        <span className="section-kicker">研究边界</span>
        <p>{data.caveats.join(" ")}</p>
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
  return (
    <>
      <SectionHeading
        title="这项实验怎么做"
        text="先固定规则，再检查数据能不能支持这套规则。每一步都尽量使用当时已经知道的信息。"
      />
      <div className="research-grid">
        <ResearchCard
          title="第一步：准备数据"
          text="使用 Tushare（行情数据接口）的 A 股日线、估值和复权价格。另取停牌记录与 ST（特别处理股票）记录，用来核对没有报价的日期。行情数据目前覆盖到 2026 年 9 月 17 日。"
        />
        <ResearchCard
          title="第二步：选出股票"
          text="在每个交易日收盘后，按总市值从小到大排序，选出最小的 400 只股票。剔除当日处于 ST、停牌状态，或价格、市值无效的股票。"
        />
        <ResearchCard
          title="第三步：计算收益"
          text="组合在下一交易日收盘时成交，再持有到下一个交易日收盘。400 只股票等权计算组合收益。最后一个有行情的交易日没有下一交易日，因此不计算它的收益。"
        />
        <ResearchCard
          title="第四步：核对缺口"
          text="如果选中的股票在下一交易日没有报价，就查看它之后何时恢复报价，以及这段时间是否有停牌或 ST 记录。查不到直接证据的缺口继续保留，避免把数据问题当成投资结果。"
        />
      </div>
      <Panel title="三种收益口径怎么读" tag="主结果与敏感性">
        <SimpleTable
          rows={[
            {
              name: "严格口径",
              meaning: "所有选中股票都有下一交易日价格才计算这一天的收益",
              use: "主结果",
            },
            {
              name: "部分股票重算",
              meaning: "只用有价格的股票计算，并重新分配权重",
              use: "观察缺失价格对结果的上限影响",
            },
            {
              name: "有证据的停牌按持平",
              meaning: "只对有停牌记录的缺失按零收益处理，其他缺口仍不计算",
              use: "停牌处理的敏感性",
            },
          ]}
          columns={[
            ["name", "口径"],
            ["meaning", "计算方法"],
            ["use", "用途"],
          ]}
        />
        <p className="panel-note">
          网页上的严格口径仍是主结果。其他口径的有效交易日不同，不能直接拼成一条净值，也不能用来证明策略可以交易。
        </p>
      </Panel>
      <Panel title="页面里的几个英文词" tag="首次出现时说明">
        <SimpleTable
          rows={[
            { name: "Tushare", meaning: "提供行情和其他金融数据的接口" },
            { name: "`suspend_d`", meaning: "每日停牌记录，保留项目内部键值" },
            { name: "`stock_st`", meaning: "ST 状态记录，保留项目内部键值" },
            { name: "ST", meaning: "特别处理股票" },
            { name: "PIT", meaning: "点时数据，也就是当时已经可以获得的信息" },
            { name: "NAV", meaning: "净值" },
            { name: "ETF", meaning: "交易型开放式指数基金" },
          ]}
          columns={[
            ["name", "名称"],
            ["meaning", "中文说明"],
          ]}
        />
      </Panel>
    </>
  );
}

export function MicrocapPageContent({ includeMethod = true }: { includeMethod?: boolean }) {
  const { data: summary } = useJson<MicrocapSummary>(
    "index/microcap/summary.json",
  );
  const { data: reconstructed } = useJson<Row>(
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
          title="缺失价格审计"
          tag={`审计区间 ${repair.coverage_start} 至 ${repair.coverage_end}`}
        >
          <p className="panel-note">
            最小市值 400 组合共有 {num(repair.missing_holdings)} 条缺失持仓。
            {num(repair.evidence_counts.suspension)} 条有停牌证据，其中{" "}
            {num(repair.evidence_counts.suspension_and_st)} 条同时有 ST 证据。
            {num(repair.evidence_counts.unclassified)}{" "}
            条没有找到直接证据。当前没有可用的退市日期。
          </p>
          <SimpleTable
            rows={repair.variants.map((item) => ({
              variant: item.name,
              observations: num(item.observations),
              final_nav: num(item.final_nav),
              max_drawdown: pct(item.max_drawdown),
            }))}
            columns={[
              ["variant", "口径"],
              ["observations", "有效交易日"],
              ["final_nav", "期末净值"],
              ["max_drawdown", "最大回撤"],
            ]}
          />
          <p className="panel-note">
            严格口径用于主图。其他口径只用来观察缺失价格的影响，数据覆盖不同，不能直接比较。
            {repair.caveats.join(" ")}
          </p>
        </Panel>
      )}
      <ThemeHeading
        kicker="历史研究档案 · 微盘规则复现"
        title="小微盘的长期收益、回撤与交易限制"
        text="这组结果用固定规则重建小市值股票组合，帮助观察长期收益和风险。规则重建与公开参考指数的成分、调仓和数据来源不同。"
        asof={`重建截至 ${reconstructedNav.at(-1)?.date ?? "未提供"}`}
      />
      <section className="stat-grid">
        <Stat
          label="公开参考净值"
          value={num(asNumber(nav.at(-1)?.nav))}
          note={`截至 ${nav.at(-1)?.date ?? "未提供"}`}
          accent
        />
        <Stat
          label="2025年收益"
          value={pct(asNumber(latestAnnual?.return))}
          note="公开资料参考"
        />
        <Stat
          label="重建最大回撤"
          value={pct(asNumber(reconstructed.max_drawdown))}
          note="2015年以来日频"
        />
        <Stat
          label="最长未回到前高的时间"
          value={`${num(asNumber(reconstructed.longest_underwater_trading_days))} 个交易日`}
          note={`${reconstructed.longest_underwater_start ?? "未提供"} 至 ${reconstructed.longest_underwater_end ?? "未提供"}`}
        />
        <Stat
          label="重建样本"
          value={`${num(asNumber(reconstructed.observations))} 天`}
          note={`${reconstructed.coverage_start ?? "未提供"} 至 ${reconstructed.coverage_end ?? "未提供"}`}
        />
      </section>
      <div className="panel ytd-panel">
        <div className="panel-title">
          <h3>2026 年至今</h3>
          <span className="tag warm">公开资料参考</span>
        </div>
        <p>
          公开资料参考收益截至 {summary.metrics.ytd_2026_as_of ?? "未提供"}
          。规则重建净值截至 {reconstructed.coverage_end ?? "未提供"}
          。两组数据的规则不同，页面分开展示。
        </p>
      </div>
      <SectionHeading
        title="收益路径"
        text="查看公开参考和规则重建的历史净值、回撤与恢复过程。"
      />
      <div className="panel">
        <div className="panel-title">
          <h3>公开资料参考净值</h3>
          <span className="tag">可悬停、缩放</span>
        </div>
        <NavChart rows={nav} name="公开资料参考" color="#1267d6" />
      </div>
      <div className="panel">
        <div className="panel-title">
          <h3>规则重建净值（数据来源：Tushare）</h3>
          <span className="tag warm">2015年以来 · 可悬停、缩放</span>
        </div>
        <p className="panel-note">
          按上海、深圳 A 股总市值选取最小 400
          只，等权持有至下一交易日。图表用于观察规则路径，未扣除交易成本。
        </p>
        <NavChart
          rows={reconstructedNav}
          name="Tushare 规则重建净值"
          color="#b96800"
        />
      </div>
      <div className="panel">
        <div className="panel-title">
          <h3>年度收益</h3>
          <span className="tag warm">悬停查看数值</span>
        </div>
        <AnnualChart rows={annual} />
      </div>
      <div className="research-grid">
        <Panel title="滚动年化收益" tag="持有期限">
          <MetricChart rows={cagr} value="cagr" label="年化收益" />
        </Panel>
        <Panel title="滚动最大回撤" tag="月频与日频参考">
          <MetricChart rows={drawdown} value="max_drawdown" label="最大回撤" />
        </Panel>
      </div>
      <div className="panel">
        <div className="panel-title">
          <h3>最长未回到前高的区间</h3>
          <span className="tag warm">按交易日排序</span>
        </div>
        <p className="panel-note">
          水下期指净值低于此前高点的连续时间。图表展示持续时间最长的 10
          个区间，悬停可以查看区间回撤。
        </p>
        <UnderwaterChart rows={underwater} />
      </div>
      <SectionHeading
        title="研究解读"
        text="了解选股规则、收益来源、历史阶段和实际复制的难点。"
      />
      <div className="research-grid">
        <ResearchCard
          title="两个微盘口径"
          text="8841431.WI 每日调仓，适合观察极小市值与再平衡机制。868008.WI 每月调仓，换手和执行压力相对更低。"
        />
        <ResearchCard
          title="收益来源"
          text="收益可能来自极小市值、等权调仓、短期价格反转，以及承担流动性风险的补偿。各项贡献尚未精确计算。"
        />
        <ResearchCard
          title="历史阶段"
          text="2001 至 2005 年连续下跌。2006 至 2015 年多个极端上涨年份抬高长期年化收益。2017 至 2018 年微盘风格表现不利。"
        />
        <ResearchCard
          title="复制难度"
          text="实际复制还要考虑成交不足、涨跌停、停牌、退市和冲击成本。"
        />
      </div>
      <div className="fine-print">
        <span className="section-kicker">研究边界</span>
        <p>
          {readableNotes(
            reconstructed.caveats ??
              "自制规则与万得官方指数口径不同，交易成本、涨跌停和停牌限制仍需核查。",
          )}
        </p>
      </div>
    </>
  );
}
