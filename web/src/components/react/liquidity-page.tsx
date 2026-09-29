import { useState } from "react";
import { readableNotes } from "../../research-copy";
import { formatNumber as num } from "../../lib/format";
import {
  Stat,
  Panel,
  BarChart,
  ControlBar,
  Choice,
  ThemeHeading,
  SimpleTable,
  Loading,
  useJson,
  englishLocale,
} from "./research-shared";
import type { LiquiditySummary } from "./research-shared";

const t = (zh: string, en: string) => englishLocale() ? en : zh;

export function LiquidityPage({ embedded = false }: { embedded?: boolean }) {
  return (
    <>
      <LiquidityPeriodPanel embedded={embedded} />
      <LiquidityPageLegacy />
    </>
  );
}

export function LiquidityPeriodPanel({ embedded }: { embedded: boolean }) {
  const { data: summary } = useJson<LiquiditySummary>("liquidity/summary.json");
  const [period, setPeriod] = useState("latest");
  if (!summary) return <Loading />;
  const options = [
    "latest",
    ...(summary.periods ?? []).map((item) => item.period),
  ];
  const selected =
    period === "latest"
      ? null
      : summary.periods?.find((item) => item.period === period);
  const markets = selected?.markets ?? summary.markets;
  const available = markets.filter((item) => item.status !== "incomplete");
  const periodStatus = selected?.status ?? "mixed";
  const latestDates = markets
    .filter((item) => item.as_of)
    .map((item) => `${item.market} ${item.as_of}`)
    .join("，");
  const statusLabel =
    periodStatus === "verified"
      ? t("口径已核验", "Methodology verified")
      : periodStatus === "mixed"
        ? t("日期不一致", "Dates differ")
        : periodStatus === "pending"
          ? t("待生成", "Pending generation")
          : t("覆盖不完整", "Incomplete coverage");
  return (
    <section className={`period-panel ${embedded ? "embedded" : ""}`}>
      <div className="period-heading">
        <div>
          <span className="section-kicker">{t("跨市场小微盘流动性", "Cross-market micro-cap liquidity")}</span>
          <h3>{t("按各市场最近可用数据比较小市值股票的流动性", "Compare small-cap liquidity using each market's latest available data")}</h3>
          <p>
            {t("各市场按最近可用数据划分市值区间，使用截至前一交易日的 20 日平均成交额。数据更新不同步，各市场日期分别列出。", "Each market uses its latest available size buckets and 20-day average turnover known by the prior trading day. Refresh dates are not synchronized and are shown separately.")}
          </p>
        </div>
        <span className={`status-badge ${periodStatus}`}>{statusLabel}</span>
      </div>
      <ControlBar>
        <span className="control-label">{t("时间区间", "Period")}</span>
        {options.map((value) => {
          const item =
            value === "latest"
              ? null
              : summary.periods?.find(
                  (candidate) => candidate.period === value,
                );
          const itemStatus = item?.status;
          return (
            <Choice
              key={value}
              active={period === value}
              onClick={() => setPeriod(value)}
            >
              {value === "latest" ? t("最近可用数据", "Latest available") : value}
              {itemStatus === "incomplete"
                ? t(" · 覆盖不完整", " · incomplete coverage")
                : itemStatus === "pending"
                  ? t(" · 待生成", " · pending")
                  : ""}
            </Choice>
          );
        })}
      </ControlBar>
      <div className="period-meta">
        {selected
          ? `${selected.common_start ?? "未提供"} 至 ${selected.common_end ?? "未提供"} · ${available.length}/${markets.length} 个市场可比`
          : `${t("各市场最近可用数据", "Latest available data by market")} · ${latestDates || t("日期待补充", "dates pending")}`}
      </div>
      {selected && selected.status === "incomplete" && (
        <div className="callout compact">
          <span className="section-kicker">{t("覆盖提醒", "Coverage notice")}</span>
          <p>
            {t("该区间各市场的数据覆盖不同，下表展示已有数据，缺失市场保留为空。", "Market coverage differs in this period. The table shows available data and leaves missing markets empty.")}
          </p>
        </div>
      )}
      {selected && selected.status === "pending" && (
        <div className="callout compact">
          <span className="section-kicker">{t("生成状态", "Generation status")}</span>
          <p>
            {t("该区间的数据预计可以计算，网页尚未发布分组汇总。生成后会补充共同覆盖日期和市场明细。", "This period is expected to be computable, but its grouped summary is not published yet. The release will add common coverage dates and market details.")}
          </p>
        </div>
      )}
      <div className="period-table">
        {available.length ? (
          <SimpleTable
            rows={available.flatMap((market) =>
              market.buckets.map((bucket) => ({
                market: `${market.market} (${t("截至", "as of")} ${selected ? (market.coverage_end ?? t("日期待补", "date pending")) : (market.as_of ?? t("日期待补", "date pending"))})`,
                bucket: bucket.label,
                median_usd: `$${num(bucket.median_usd)}`,
                mean_usd: `$${num(bucket.mean_usd)}`,
                observations: num(bucket.observations),
              })),
            )}
            columns={[
              ["market", t("市场", "Market")],
              ["bucket", t("市值区间", "Size bucket")],
              ["median_usd", t("成交额中位数", "Median turnover")],
              ["mean_usd", t("成交额均值", "Mean turnover")],
              ["observations", t("观测数量", "Observations")],
            ]}
          />
        ) : (
          <p className="panel-note">{t("当前时间段还没有可展示的分组汇总。", "No grouped summary is available for this period.")}</p>
        )}
      </div>
    </section>
  );
}

export function LiquidityPageLegacy() {
  const { data: summary } = useJson<LiquiditySummary>("liquidity/summary.json");
  const [market, setMarket] = useState("all");
  const [metric, setMetric] = useState<"median_usd" | "mean_usd" | "p90_usd">(
    "median_usd",
  );
  const [logScale, setLogScale] = useState(true);
  if (!summary) return <Loading />;
  const markets = summary.markets.filter(
    (item) => market === "all" || item.market === market,
  );
  const comparison = markets.map((item) => ({
    market: item.market,
    value: String(item.buckets[0]?.[metric] ?? item.sub_100m_median_usd),
  }));
  const bucketRows = markets.flatMap((item) =>
    item.buckets.map((bucket) => ({
      market: item.market,
      bucket: bucket.label,
      count: String(bucket.count),
      median_usd: String(bucket.median_usd),
      mean_usd: String(bucket.mean_usd),
      p90_usd: bucket.p90_usd == null ? "未提供" : String(bucket.p90_usd),
    })),
  );
  const metricLabel =
    metric === "median_usd"
      ? t("成交额中位数", "Median turnover")
      : metric === "mean_usd"
        ? t("成交额均值", "Mean turnover")
        : t("第90百分位", "90th percentile");
  return (
    <>
      <ThemeHeading
        kicker={t("小微盘历史研究 · 跨市场流动性", "Micro-cap history · cross-market liquidity")}
        title={t("比较各市场小市值股票的成交规模", "Compare small-cap turnover across markets")}
        text={t("比较各市场小市值股票的流动性，并列出数据覆盖情况。页面仅展示汇总结果，原始行情不公开。", "Compare small-cap liquidity across markets and disclose data coverage. This page shows summaries only; raw quotes are not public.")}
        asof={`${summary.method.roll_days}日平均 · ${summary.method.currency}`}
      />
      <ControlBar>
        <span className="control-label">{t("市场", "Market")}</span>
        <Choice active={market === "all"} onClick={() => setMarket("all")}>
          {t("全部", "All")}
        </Choice>
        {summary.markets.map((item) => (
          <Choice
            key={item.market}
            active={market === item.market}
            onClick={() => setMarket(item.market)}
          >
            {item.market}
          </Choice>
        ))}
        <span className="control-label">{t("指标", "Metric")}</span>
        <Choice
          active={metric === "median_usd"}
          onClick={() => setMetric("median_usd")}
        >
          {t("中位数", "Median")}
        </Choice>
        <Choice
          active={metric === "mean_usd"}
          onClick={() => setMetric("mean_usd")}
        >
          {t("均值", "Mean")}
        </Choice>
        <Choice
          active={metric === "p90_usd"}
          onClick={() => setMetric("p90_usd")}
        >
          {t("第90百分位", "90th percentile")}
        </Choice>
        <Choice active={logScale} onClick={() => setLogScale(!logScale)}>
          {logScale ? t("对数坐标", "Log scale") : t("线性坐标", "Linear scale")}
        </Choice>
      </ControlBar>
      <section className="stat-grid">
        {markets.map((item, index) => (
          <Stat
            key={item.market}
            label={`${item.market} (${t("市值低于1亿美元", "market cap below $100m")})`}
            value={`$${num(item.sub_100m_median_usd)}`}
            note={`${num(item.sub_100m_count)} ${t("只股票", "stocks")}`}
            accent={index === markets.length - 1}
          />
        ))}
      </section>
      <Panel
        title={t("小市值股票的成交额比较", "Small-cap turnover comparison")}
        tag={`${metricLabel} · ${logScale ? t("对数", "log") : t("线性", "linear")}`}
      >
        <BarChart
          rows={comparison}
          labelKey="market"
          valueKey="value"
          color="#1267d6"
          formatter={(value) => `$${num(value)}`}
          logScale={logScale}
        />
      </Panel>
      <Panel title={t("各市场市值分组明细", "Market size-bucket details")} tag={t("美元成交额", "USD turnover")}>
        <SimpleTable
          rows={bucketRows}
          columns={[
            ["market", t("市场", "Market")],
            ["bucket", t("市值区间", "Size bucket")],
            ["count", t("数量", "Count")],
            ["median_usd", t("成交额中位数", "Median turnover")],
            ["mean_usd", t("成交额均值", "Mean turnover")],
            ["p90_usd", t("第90百分位", "90th percentile")],
          ]}
        />
      </Panel>
      <div className="fine-print">
        <span className="section-kicker">{t("数据与研究边界", "Data and research boundary")}</span>
        <p>{readableNotes(summary.caveats)}</p>
      </div>
      <div className="research-grid">
        <article className="research-card">
          <span className="section-kicker">{t("定义", "Definition")}</span>
          <h3>{t("可交易规模还受哪些因素影响", "What else affects tradable size")}</h3>
          <p>
            {t("成交额反映市场交易规模。判断实际能买卖多少，还需查看此前的日均成交额、日成交额中位数、订单占市场成交的比例，以及交易对价格的影响。", "Turnover reflects market activity. Estimating what can actually be traded also requires prior daily turnover, median turnover, order share of market volume, and price impact.")}
          </p>
        </article>
        <article className="research-card">
          <span className="section-kicker">{t("时间", "Timing")}</span>
          <h3>{t("使用前一交易日已知的数据", "Use information known by the prior trading day")}</h3>
          <p>
            {t("流动性指标使用前一交易日及更早的数据，确保判断依据在交易前已知。", "Liquidity metrics use data from the prior trading day or earlier so the evidence is known before trading.")}
          </p>
        </article>
        <article className="research-card">
          <span className="section-kicker">{t("数据边界", "Data boundary")}</span>
          <h3>{t("日股数据待更新", "Japan data pending refresh")}</h3>
          <p>
            {t("日股数据已接入，仍需按相同统计口径更新本地数据，才能补充分组结果。", "Japan data is connected, but the local snapshot still needs to be refreshed under the same methodology before grouped results can be added.")}
          </p>
        </article>
      </div>
    </>
  );
}
