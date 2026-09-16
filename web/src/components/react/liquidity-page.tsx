import { useState } from "react";
import { readableNotes } from "../../research-copy";
import { formatNumber as num } from "../../lib/format";
import { Stat, Panel, BarChart, ControlBar, Choice, ThemeHeading, SimpleTable, Loading, useJson } from "./research-shared";
import type { LiquiditySummary } from "./research-shared";

export function LiquidityPage({ embedded = false }: { embedded?: boolean }) { return <><LiquidityPeriodPanel embedded={embedded}/><LiquidityPageLegacy/></>; }

export function LiquidityPeriodPanel({ embedded }: { embedded: boolean }) {
  const { data: summary } = useJson<LiquiditySummary>("liquidity/summary.json");
  const [period, setPeriod] = useState("latest");
  if (!summary) return <Loading />;
  const options = ["latest", ...(summary.periods ?? []).map((item) => item.period)];
  const selected = period === "latest" ? null : summary.periods?.find((item) => item.period === period);
  const markets = selected?.markets ?? summary.markets;
  const available = markets.filter((item) => item.status !== "incomplete");
  const periodStatus = selected?.status ?? "mixed";
  const latestDates = markets.filter((item) => item.as_of).map((item) => `${item.market} ${item.as_of}`).join("，");
  const statusLabel = periodStatus === "verified" ? "口径已核验" : periodStatus === "mixed" ? "日期不一致" : periodStatus === "pending" ? "待生成" : "覆盖不完整";
  return <section className={`period-panel ${embedded ? "embedded" : ""}`}><div className="period-heading"><div><span className="section-kicker">跨市场小微盘流动性</span><h3>按各市场最近可用数据比较小市值股票的流动性</h3><p>各市场按最近可用数据划分市值区间，使用截至前一交易日的 20 日平均成交额。数据更新不同步，各市场日期分别列出。</p></div><span className={`status-badge ${periodStatus}`}>{statusLabel}</span></div><ControlBar><span className="control-label">时间区间</span>{options.map((value) => { const item = value === "latest" ? null : summary.periods?.find((candidate) => candidate.period === value); const itemStatus = item?.status; return <Choice key={value} active={period === value} onClick={() => setPeriod(value)}>{value === "latest" ? "最近可用数据" : value}{itemStatus === "incomplete" ? " · 覆盖不完整" : itemStatus === "pending" ? " · 待生成" : ""}</Choice>; })}</ControlBar><div className="period-meta">{selected ? `${selected.common_start ?? "未提供"} 至 ${selected.common_end ?? "未提供"} · ${available.length}/${markets.length} 个市场可比` : `各市场最近可用数据 · ${latestDates || "日期待补充"}`}</div>{selected && selected.status === "incomplete" && <div className="callout compact"><span className="section-kicker">覆盖提醒</span><p>该区间各市场的数据覆盖不同，下表展示已有数据，缺失市场保留为空。</p></div>}{selected && selected.status === "pending" && <div className="callout compact"><span className="section-kicker">生成状态</span><p>该区间的数据预计可以计算，网页尚未发布分组汇总。生成后会补充共同覆盖日期和市场明细。</p></div>}<div className="period-table">{available.length ? <SimpleTable rows={available.flatMap((market) => market.buckets.map((bucket) => ({ market: `${market.market}（截至 ${selected ? market.coverage_end ?? "日期待补" : market.as_of ?? "日期待补"}）`, bucket: bucket.label, median_usd: `$${num(bucket.median_usd)}`, mean_usd: `$${num(bucket.mean_usd)}`, observations: num(bucket.observations) })))} columns={[["market", "市场"], ["bucket", "市值区间"], ["median_usd", "成交额中位数"], ["mean_usd", "成交额均值"], ["observations", "观测数量"]]} /> : <p className="panel-note">当前时间段还没有可展示的分组汇总。</p>}</div></section>;
}

export function LiquidityPageLegacy() {
  const { data: summary } = useJson<LiquiditySummary>("liquidity/summary.json");
  const [market, setMarket] = useState("all");
  const [metric, setMetric] = useState<"median_usd" | "mean_usd" | "p90_usd">("median_usd");
  const [logScale, setLogScale] = useState(true);
  if (!summary) return <Loading />;
  const markets = summary.markets.filter((item) => market === "all" || item.market === market);
  const comparison = markets.map((item) => ({ market: item.market, value: String(item.buckets[0]?.[metric] ?? item.sub_100m_median_usd) }));
  const bucketRows = markets.flatMap((item) => item.buckets.map((bucket) => ({ market: item.market, bucket: bucket.label, count: String(bucket.count), median_usd: String(bucket.median_usd), mean_usd: String(bucket.mean_usd), p90_usd: bucket.p90_usd == null ? "未提供" : String(bucket.p90_usd) })));
  const metricLabel = metric === "median_usd" ? "成交额中位数" : metric === "mean_usd" ? "成交额均值" : "第90百分位";
  return <><ThemeHeading kicker="小微盘历史研究 · 跨市场流动性" title="比较各市场小市值股票的成交规模" text="比较各市场小市值股票的流动性，并列出数据覆盖情况。页面仅展示汇总结果，原始行情不公开。" asof={`${summary.method.roll_days}日平均 · ${summary.method.currency}`}/><ControlBar><span className="control-label">市场</span><Choice active={market === "all"} onClick={() => setMarket("all")}>全部</Choice>{summary.markets.map((item) => <Choice key={item.market} active={market === item.market} onClick={() => setMarket(item.market)}>{item.market}</Choice>)}<span className="control-label">指标</span><Choice active={metric === "median_usd"} onClick={() => setMetric("median_usd")}>中位数</Choice><Choice active={metric === "mean_usd"} onClick={() => setMetric("mean_usd")}>均值</Choice><Choice active={metric === "p90_usd"} onClick={() => setMetric("p90_usd")}>第90百分位</Choice><Choice active={logScale} onClick={() => setLogScale(!logScale)}>{logScale ? "对数坐标" : "线性坐标"}</Choice></ControlBar><section className="stat-grid">{markets.map((item, index) => <Stat key={item.market} label={`${item.market}（市值低于1亿美元）`} value={`$${num(item.sub_100m_median_usd)}`} note={`${num(item.sub_100m_count)} 只股票`} accent={index === markets.length - 1}/>)}</section><Panel title="小市值股票的成交额比较" tag={`${metricLabel} · ${logScale ? "对数" : "线性"}`}><BarChart rows={comparison} labelKey="market" valueKey="value" color="#1267d6" formatter={(value) => `$${num(value)}`} logScale={logScale}/></Panel><Panel title="各市场市值分组明细" tag="美元成交额"><SimpleTable rows={bucketRows} columns={[["market", "市场"], ["bucket", "市值区间"], ["count", "数量"], ["median_usd", "成交额中位数"], ["mean_usd", "成交额均值"], ["p90_usd", "第90百分位"]]} /></Panel><div className="fine-print"><span className="section-kicker">数据与研究边界</span><p>{readableNotes(summary.caveats)}</p></div><div className="research-grid"><article className="research-card"><span className="section-kicker">定义</span><h3>可交易规模还受哪些因素影响</h3><p>成交额反映市场交易规模。判断实际能买卖多少，还需查看此前的日均成交额、日成交额中位数、订单占市场成交的比例，以及交易对价格的影响。</p></article><article className="research-card"><span className="section-kicker">时间</span><h3>使用前一交易日已知的数据</h3><p>流动性指标使用前一交易日及更早的数据，确保判断依据在交易前已知。</p></article><article className="research-card"><span className="section-kicker">数据边界</span><h3>日股数据待更新</h3><p>日股数据已接入，仍需按相同统计口径更新本地数据，才能补充分组结果。</p></article></div></>;
}
