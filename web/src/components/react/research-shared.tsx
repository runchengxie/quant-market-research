import { lazy, useCallback, useEffect, useMemo, useRef, useState, useSyncExternalStore } from "react";
import { publicDataUrl } from "../../lib/public-data";
import { withBase } from "../../lib/routes";
import { displayValue, formatNumber, formatPercent as pct } from "../../lib/format";
import { createResource, parseCsvResource, parseJsonResource } from "../../lib/research-resource";
import { compareSizeBuckets, finiteNumber, sizeDateRange, sizeMonthlyCurve, summarizeSizePeriods } from "../../lib/size-diagnostics";
export { average, aggregateSizeRows, stageForDate, summarizeSizePeriods } from "../../lib/size-diagnostics";
const ResearchBarChart = lazy(() => import("../ResearchCharts").then((module) => ({ default: module.ResearchBarChart })));
const ResearchLineChart = lazy(() => import("../ResearchCharts").then((module) => ({ default: module.ResearchLineChart })));

export type Row = Record<string, string>;
export type Series = { name: string; values: Array<number | null>; color: string };
export type MicrocapSummary = { metrics: { ytd_2026_as_of?: string; ytd_2026_reference?: string }; caveats?: string[] };
export type MicrocapScope = "a-share" | "cross-market";
export type StyleScope = "indices" | "barra";
export type TurnoverPeriod = { year?: number; month?: string; rank_count: number; turnover_median: number; trading_days: number; median_coverage_ratio: number; min_selected_count: number };
export type TurnoverSnapshot = { coverage_start: string; coverage_end: string; quality_status: "verified" | "incomplete"; rank_counts: number[]; annual: TurnoverPeriod[]; monthly: TurnoverPeriod[] };
export type TurnoverAudit = { rank_count: number; common_days: number; common_start: string; common_end: string; mean_abs_relative_diff_turnover_median: number; p90_abs_relative_diff_turnover_median: number; within_5pct_ratio: number; within_10pct_ratio: number; within_25pct_ratio: number; quality_note: string };
export type SmallcapTurnoverData = { schema_version: string; method: string; clean: TurnoverSnapshot; historical: TurnoverSnapshot; overlap_audit: TurnoverAudit[]; caveats: string[] };
export type LiquidityBucket = { label: string; count?: number; median_usd: number; mean_usd: number; p90_usd?: number; observations?: number };
export type LiquidityPeriodMarket = { market: string; status: string; as_of?: string; coverage_start?: string; coverage_end?: string; sub_100m_count?: number; sub_100m_median_usd?: number; buckets: LiquidityBucket[] };
export type LiquidityPeriod = { period: string; status: string; common_start?: string | null; common_end?: string | null; markets: LiquidityPeriodMarket[] };
export type LiquiditySummary = { method: { roll_days: number; metric: string; currency: string; source_project: string }; markets: LiquidityPeriodMarket[]; periods?: LiquidityPeriod[]; caveats: string[] };
export type BarraSummary = { source?: { coverage_start?: string; coverage_end?: string }; size_monotonicity?: { status?: "available" | "unavailable"; quantiles?: number; requested_quantiles?: number; tail_spread?: number | null; monotonicity_score?: number | null; formation_dates?: number; observed_return_count?: number; missing_return_count?: number; return_coverage?: number | null }; legacy_barra_result?: { factor_count?: number } };
export type HistoricalFactor = { factor: string; days: number; years: number; cumulative_ret: number; geometric_annual_ret: number; annual_vol: number; sharpe: number; max_drawdown: number; hit_rate: number };
export type CorrelationMatrix = Record<string, Record<string, number>>;
export type CashflowBasis = "all" | "price_return" | "gross_total_return";
export type DiagnosticView = "daily" | "monthly" | "stage";

const DATA = publicDataUrl("", import.meta.env.BASE_URL);

export function SizeDiagnosticPanel({ rows, dailyCurve }: { rows: Row[]; dailyCurve: Row[] }) {
  const [view, setView] = useState<DiagnosticView>("monthly");
  const monthlyCurve = sizeMonthlyCurve(rows);
  const stages = summarizeSizePeriods(rows, "stage");
  const daily = [...dailyCurve].sort((a, b) => compareSizeBuckets(a.bucket, b.bucket));
  const chartRows = view === "daily" ? daily : view === "monthly" ? monthlyCurve : stages.map(row => ({ bucket: row.period, value: Number.isFinite(row.spread) ? String(row.spread) : "" }));
  const dates = sizeDateRange(rows);
  const formatter = (value: number) => Number.isFinite(value) ? `${(value * 100).toFixed(2)}%` : "未提供";
  const coverageColumns = [["formation_count", "形成时股票数"], ["count", "形成时股票数（count）"], ["observed_return_count", "已观测收益数"], ["missing_return_count", "缺失收益数"], ["return_coverage", "收益覆盖率"], ["observed_count", "已观测股票数"], ["missing_count", "缺失股票数"], ["coverage_ratio", "观测覆盖率"]].filter(([key]) => rows.some(row => key in row));
  return <>
    <Panel title="补充研究：市值十分组" tag="当前样本的历史统计">
      <p className="panel-note">当前快照的分组日期覆盖 {dates.start ?? "未提供"} 至 {dates.end ?? "未提供"}。按市值分成十组，观察各组下一交易日的收益，并按月和阶段汇总。这些结果仅描述历史样本；旧快照未提供完整覆盖字段时，覆盖质量仍待核实。</p>
      <BarChart rows={daily} labelKey="bucket" valueKey="value" color="#b64d33" formatter={formatter}/>
      <p className="panel-note">上图展示快照中的下一交易日平均收益。相邻交易日的结果可能相关，分组日期的数量不等于独立样本数。</p>
      <SortableTable rows={rows} columns={[["formation_date", "分组日期"], ["bucket", "市值分组"], ["forward_return", "下一交易日收益"], ...coverageColumns]} percentColumns={["forward_return", "return_coverage", "coverage_ratio"]}/>
    </Panel>
    <Panel title="稳定性观察：按月与按阶段" tag="观察不同时间尺度">
      <p className="panel-note">月度结果先计算每月平均收益，再对各月等权平均。阶段（2015–2019、2020–2024、2025–当前）收益差仅使用 Q1 与 Q10 同时有有效收益的共同分组日期，剔除已知覆盖不完整的记录。尚未校正时间相关性，也未用区块自助法估计置信区间或检验统计显著性。</p>
      <ControlBar><span className="control-label">观察口径</span><Choice active={view === "daily"} onClick={() => setView("daily")}>按日分组</Choice><Choice active={view === "monthly"} onClick={() => setView("monthly")}>按月汇总</Choice><Choice active={view === "stage"} onClick={() => setView("stage")}>阶段收益差</Choice></ControlBar>
      <BarChart rows={chartRows} labelKey="bucket" valueKey="value" color="#1267d6" formatter={formatter}/>
      {view === "stage" && <SimpleTable rows={stages.map(row => ({ period: row.period, q1: formatter(row.q1), q10: formatter(row.q10), spread: formatter(row.spread), pairedDates: String(row.pairedDates) }))} columns={[["period", "阶段"], ["q1", "共同日期最小组平均收益"], ["q10", "共同日期最大组平均收益"], ["spread", "最小组减最大组"], ["pairedDates", "共同分组日期数"]]}/>}
    </Panel>
  </>;
}

function useResource<T>(path: string | null, parse: (text: string) => T) {
  const resource = useMemo(() => createResource(path === null ? null : `${DATA}/${path}`, parse), [path, parse]);
  const current = useRef(resource);
  // Update only after commit, so a discarded render cannot redirect retries.
  useEffect(() => { current.current = resource; resource.load(); return resource.cancel; }, [resource]);
  const retry = useCallback(() => current.current.load(), []);
  const snapshot = useSyncExternalStore(resource.subscribe, resource.getSnapshot, resource.getServerSnapshot);
  return { ...snapshot, retry };
}

export function useJson<T>(path: string | null) { return useResource<T>(path, parseJsonResource<T>); }
export function useCsv(path: string | null) { return useResource<Row[]>(path, parseCsvResource); }

export function ResourceState({ error = "", loading = false, empty = false, retry, label = "研究数据" }: { error?: string; loading?: boolean; empty?: boolean; retry?: () => void; label?: string }) {
  if (error) return <div role="alert"><p>{label}加载失败：{error}</p>{retry && <button type="button" aria-label={`重试加载${label}`} onClick={retry}>重试</button>}</div>;
  if (loading) return <p className="loading" role="status">正在加载{label}……</p>;
  if (empty) return <p role="status">暂无{label}可展示。</p>;
  return null;
}

export function Stat({ label, value, note, accent = false }: { label: string; value: string; note: string; accent?: boolean }) { return <article className={`stat ${accent ? "accent" : ""}`}><span>{label}</span><strong>{value}</strong><small>{note}</small></article>; }
export function Panel({ title, tag, children }: { title: string; tag?: string; children: React.ReactNode }) { return <section className="panel"><div className="panel-title"><h3>{title}</h3>{tag && <span className="tag warm">{tag}</span>}</div>{children}</section>; }
export function SectionHeading({ title, text }: { title: string; text: string }) { return <div className="section-heading"><h3>{title}</h3><p>{text}</p></div>; }
export function ResearchCard({ title, text }: { title: string; text: string }) { return <article className="research-card"><span className="section-kicker">阅读提示</span><h3>{title}</h3><p>{text}</p></article>; }

export function BarChart({ rows, labelKey, valueKey, color = "#c84b2f", formatter = pct, logScale = false }: { rows: Row[]; labelKey: string; valueKey: string; color?: string; formatter?: (value: number) => string; logScale?: boolean }) { return <ResearchBarChart rows={rows} labelKey={labelKey} valueKey={valueKey} color={color} formatter={formatter} logScale={logScale}/>; }
export function LineChart({ series, labels }: { series: Series[]; labels: string[] }) { return <ResearchLineChart series={series} labels={labels}/>; }

export function ControlBar({ children }: { children: React.ReactNode }) { return <div className="control-bar">{children}</div>; }
export function Choice({ active, children, onClick }: { active: boolean; children: React.ReactNode; onClick: () => void }) { return <button className={`choice ${active ? "active" : ""}`} onClick={onClick}>{children}</button>; }
export function MicrocapSubTabs({ scope, onChange }: { scope: MicrocapScope; onChange: (value: MicrocapScope) => void }) { return <div className="sub-tabs" aria-label="小微盘研究子主题"><button className={scope === "a-share" ? "active" : ""} onClick={() => onChange("a-share")}>A股小微盘</button><button className={scope === "cross-market" ? "active" : ""} onClick={() => onChange("cross-market")}>跨市场小微盘流动性</button></div>; }
export function StyleSubTabs({ scope }: { scope: StyleScope }) { const base = import.meta.env.BASE_URL ?? "/"; return <div className="sub-tabs" aria-label="市场长期风格研究子主题"><a className={scope === "indices" ? "active" : ""} href={withBase("/research/indices/", base)}>指数与 ETF</a><a className={scope === "barra" ? "active" : ""} href={withBase("/research/style-factors-18y/", base)}>Barra 风格因子研究（18年）</a></div>; }

export function formatTurnover(value: number) {
  if (!Number.isFinite(value)) return "未提供";
  if (value >= 100_000_000) return "¥" + (value / 100_000_000).toFixed(2) + " 亿";
  if (value >= 10_000) return "¥" + (value / 10_000).toFixed(1) + " 万";
  return "¥" + Math.round(value).toLocaleString("zh-CN");
}

export function ThemeHeading({ kicker, title, text, asof }: { kicker: string; title: string; text: string; asof: string }) { return <header className="theme-heading"><div><span className="section-kicker">{kicker}</span><h2>{title}</h2><p>{text}</p></div><span className="asof">{asof}</span></header>; }
function tableValue(key: string, value: string | undefined, percent: boolean) {
  if (value == null || !String(value).trim()) return "未提供";
  if (percent) return pct(finiteNumber(value));
  if (/(?:^|_)(?:count|observations|days|years)$/.test(key)) return formatNumber(finiteNumber(value));
  return displayValue(key, value);
}
export function SimpleTable({ rows, columns, percentColumns = [] }: { rows: Row[]; columns: string[][]; percentColumns?: string[] }) { return <div className="table-scroll"><table><thead><tr>{columns.map(([key, label]) => <th key={key} scope="col">{label}</th>)}</tr></thead><tbody>{rows.map((row, index) => <tr key={`${index}-${row[columns[0]?.[0] ?? ""]}`}>{columns.map(([key]) => <td key={key}>{tableValue(key, row[key], percentColumns.includes(key))}</td>)}</tr>)}</tbody></table></div>; }
export function SortableTable({ rows, columns, percentColumns = [], searchPlaceholder = "搜索表格内容" }: { rows: Row[]; columns: string[][]; percentColumns?: string[]; searchPlaceholder?: string }) {
  const [query, setQuery] = useState("");
  const [sortKey, setSortKey] = useState(columns[0]?.[0] ?? "");
  const [direction, setDirection] = useState<"asc" | "desc">("desc");
  const visible = rows.filter((row) => Object.values(row).some((value) => String(value ?? "").toLowerCase().includes(query.toLowerCase()))).sort((left, right) => {
    const a = finiteNumber(left[sortKey]);
    const b = finiteNumber(right[sortKey]);
    const comparison = Number.isFinite(a) && Number.isFinite(b) ? a - b : String(left[sortKey] ?? "").localeCompare(String(right[sortKey] ?? ""), "zh-CN", { numeric: true });
    return direction === "desc" ? -comparison : comparison;
  });
  const choose = (key: string) => { if (key === sortKey) setDirection(direction === "desc" ? "asc" : "desc"); else { setSortKey(key); setDirection("desc"); } };
  return <><div className="table-controls"><input aria-label={searchPlaceholder} placeholder={searchPlaceholder} value={query} onChange={(event) => setQuery(event.target.value)}/><span>{visible.length} / {rows.length} 条</span></div><div className="table-scroll"><table><thead><tr>{columns.map(([key, label]) => <th key={key} scope="col" aria-sort={sortKey === key ? (direction === "desc" ? "descending" : "ascending") : "none"}><button type="button" className="table-sort" onClick={() => choose(key)}>{label} {sortKey === key ? (direction === "desc" ? "↓" : "↑") : "↕"}</button></th>)}</tr></thead><tbody>{visible.map((row, index) => <tr key={`${index}-${row[columns[0]?.[0] ?? ""]}`}>{columns.map(([key]) => <td key={key}>{tableValue(key, row[key], percentColumns.includes(key))}</td>)}</tr>)}</tbody></table></div></>;
}
export function Loading() { return <p className="loading">正在加载研究数据……</p>; }
