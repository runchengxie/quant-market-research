import { lazy, useEffect, useState } from "react";
import { parseCsv, publicDataUrl } from "../../lib/public-data";
import { asNumber, displayValue, formatPercent as pct } from "../../lib/format";
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
export type BarraSummary = { source?: { coverage_start?: string; coverage_end?: string }; size_monotonicity?: { quantiles?: number; tail_spread?: number; monotonicity_score?: number; formation_dates?: number }; legacy_barra_result?: { factor_count?: number } };
export type HistoricalFactor = { factor: string; days: number; years: number; cumulative_ret: number; geometric_annual_ret: number; annual_vol: number; sharpe: number; max_drawdown: number; hit_rate: number };
export type CorrelationMatrix = Record<string, Record<string, number>>;
export type CashflowBasis = "all" | "price_return" | "gross_total_return";
export type DiagnosticView = "daily" | "monthly" | "stage";

const DATA = publicDataUrl("", import.meta.env.BASE_URL);

export function average(values: number[]) { return values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : NaN; }
export function stageForDate(date: string) {
  const year = Number(date.slice(0, 4));
  return year <= 2019 ? "2015–2019" : year <= 2024 ? "2020–2024" : "2025–当前";
}
export function aggregateSizeRows(rows: Row[], period: "month" | "stage") {
  const groups = new Map<string, number[]>();
  rows.forEach((row) => {
    const value = Number(row.forward_return);
    if (!Number.isFinite(value)) return;
    const key = `${period === "month" ? row.formation_date.slice(0, 7) : stageForDate(row.formation_date)}|${row.bucket}`;
    groups.set(key, [...(groups.get(key) ?? []), value]);
  });
  return [...groups.entries()].map(([key, values]) => {
    const [periodLabel, bucket] = key.split("|");
    return { period: periodLabel, bucket, value: average(values) };
  });
}
export function summarizeSizePeriods(rows: Row[], period: "month" | "stage") {
  const grouped = aggregateSizeRows(rows, period);
  const periods = [...new Set(grouped.map((row) => row.period))];
  return periods.map((periodLabel) => {
    const values = grouped.filter((row) => row.period === periodLabel);
    const q1 = values.find((row) => row.bucket === "Q1")?.value ?? NaN;
    const q10 = values.find((row) => row.bucket === "Q10")?.value ?? NaN;
    return { period: periodLabel, q1, q10, spread: q1 - q10, observations: values.length };
  });
}

export function SizeDiagnosticPanel({ rows, dailyCurve }: { rows: Row[]; dailyCurve: Row[] }) {
  const [view, setView] = useState<DiagnosticView>("monthly");
  const monthly = aggregateSizeRows(rows, "month");
  const monthlyCurve = [...new Set(monthly.map((row) => row.bucket))].map((bucket) => ({ bucket, value: String(average(monthly.filter((row) => row.bucket === bucket).map((row) => row.value))) }));
  const stages = summarizeSizePeriods(rows, "stage");
  const chartRows = view === "daily" ? dailyCurve : view === "monthly" ? monthlyCurve : stages.map((row) => ({ bucket: row.period, value: String(row.spread) }));
  const formatter = (value: number) => `${(value * 100).toFixed(2)}%`;
  return <><Panel title="补充研究：市值十分组" tag="当前样本的历史统计"><p className="panel-note">这部分用当前已清洗的 A 股每日数据重新计算，覆盖 {rows[0]?.formation_date ?? "未提供"} 至 {rows.at(-1)?.formation_date ?? "未提供"}。按市值分成十组，观察各组下一交易日的收益，并按月和阶段汇总，检查差异是否稳定。这些结果仅描述历史样本。</p><BarChart rows={dailyCurve} labelKey="bucket" valueKey="value" color="#b64d33" formatter={formatter}/><p className="panel-note">上图展示分组后下一交易日的平均收益。相邻交易日的结果可能相关，分组日期的数量不等于独立样本数。</p><SortableTable rows={rows} columns={[["formation_date", "分组日期"], ["bucket", "市值分组"], ["forward_return", "下一交易日收益"], ["count", "股票数"]]} percentColumns={["forward_return"]}/></Panel><Panel title="稳定性观察：按月与按阶段" tag="观察不同时间尺度"><p className="panel-note">月度结果先计算每月平均收益，再对各月等权平均。阶段图展示最小市值组（Q1）减最大市值组（Q10）的平均收益差。尚未校正时间相关性，也未用区块自助法估计置信区间或检验统计显著性。</p><ControlBar><span className="control-label">观察口径</span><Choice active={view === "daily"} onClick={() => setView("daily")}>按日分组</Choice><Choice active={view === "monthly"} onClick={() => setView("monthly")}>按月汇总</Choice><Choice active={view === "stage"} onClick={() => setView("stage")}>阶段收益差</Choice></ControlBar>{view === "stage" ? <><BarChart rows={chartRows} labelKey="bucket" valueKey="value" color="#1267d6" formatter={formatter}/><SimpleTable rows={stages.map((row) => ({ period: row.period, q1: formatter(row.q1), q10: formatter(row.q10), spread: formatter(row.spread), observations: String(row.observations) }))} columns={[["period", "阶段"], ["q1", "最小市值组平均收益"], ["q10", "最大市值组平均收益"], ["spread", "最小组减最大组"], ["observations", "分组数"]]} /></> : <BarChart rows={chartRows} labelKey="bucket" valueKey="value" color="#1267d6" formatter={formatter}/>}</Panel></>;
}

export function useJson<T>(path: string) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { let active = true; fetch(`${DATA}/${path}`).then((response) => { if (!response.ok) throw new Error(`${path}（${response.status}）`); return response.json() as Promise<T>; }).then((value) => { if (active) setData(value); }).catch((reason: Error) => { if (active) setError(reason.message); }); return () => { active = false; }; }, [path]);
  return { data, error };
}

export function useCsv(path: string) {
  const [data, setData] = useState<Row[] | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { let active = true; fetch(`${DATA}/${path}`).then((response) => { if (!response.ok) throw new Error(`${path}（${response.status}）`); return response.text(); }).then((text) => { if (active) setData(parseCsv(text)); }).catch((reason: Error) => { if (active) setError(reason.message); }); return () => { active = false; }; }, [path]);
  return { data, error };
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
export function StyleSubTabs({ scope, onChange }: { scope: StyleScope; onChange: (value: StyleScope) => void }) { return <div className="sub-tabs" aria-label="市场长期风格研究子主题"><button className={scope === "indices" ? "active" : ""} onClick={() => onChange("indices")}>指数与 ETF</button><button className={scope === "barra" ? "active" : ""} onClick={() => onChange("barra")}>Barra 风格因子研究（18年）</button></div>; }

export function formatTurnover(value: number) {
  if (!Number.isFinite(value)) return "未提供";
  if (value >= 100_000_000) return "¥" + (value / 100_000_000).toFixed(2) + " 亿";
  if (value >= 10_000) return "¥" + (value / 10_000).toFixed(1) + " 万";
  return "¥" + Math.round(value).toLocaleString("zh-CN");
}

export function ThemeHeading({ kicker, title, text, asof }: { kicker: string; title: string; text: string; asof: string }) { return <header className="theme-heading"><div><span className="section-kicker">{kicker}</span><h2>{title}</h2><p>{text}</p></div><span className="asof">{asof}</span></header>; }
export function SimpleTable({ rows, columns, percentColumns = [] }: { rows: Row[]; columns: string[][]; percentColumns?: string[] }) { return <div className="table-scroll"><table><thead><tr>{columns.map(([key, label]) => <th key={key}>{label}</th>)}</tr></thead><tbody>{rows.map((row, index) => <tr key={`${index}-${row[columns[0]?.[0] ?? ""]}`}>{columns.map(([key]) => <td key={key}>{percentColumns.includes(key) ? pct(asNumber(row[key])) : row[key] === "" || row[key] == null ? "未提供" : displayValue(key, row[key])}</td>)}</tr>)}</tbody></table></div>; }
export function SortableTable({ rows, columns, percentColumns = [], searchPlaceholder = "搜索表格内容" }: { rows: Row[]; columns: string[][]; percentColumns?: string[]; searchPlaceholder?: string }) {
  const [query, setQuery] = useState("");
  const [sortKey, setSortKey] = useState(columns[0]?.[0] ?? "");
  const [direction, setDirection] = useState<"asc" | "desc">("desc");
  const visible = rows.filter((row) => Object.values(row).some((value) => value.toLowerCase().includes(query.toLowerCase()))).sort((left, right) => {
    const a = asNumber(left[sortKey]);
    const b = asNumber(right[sortKey]);
    const comparison = Number.isFinite(a) && Number.isFinite(b) ? a - b : String(left[sortKey] ?? "").localeCompare(String(right[sortKey] ?? ""));
    return direction === "desc" ? -comparison : comparison;
  });
  const choose = (key: string) => { if (key === sortKey) setDirection(direction === "desc" ? "asc" : "desc"); else { setSortKey(key); setDirection("desc"); } };
  return <><div className="table-controls"><input aria-label={searchPlaceholder} placeholder={searchPlaceholder} value={query} onChange={(event) => setQuery(event.target.value)}/><span>{visible.length} / {rows.length} 条</span></div><div className="table-scroll"><table><thead><tr>{columns.map(([key, label]) => <th key={key}><button className="table-sort" onClick={() => choose(key)}>{label} {sortKey === key ? (direction === "desc" ? "↓" : "↑") : "↕"}</button></th>)}</tr></thead><tbody>{visible.slice(0, 50).map((row, index) => <tr key={`${index}-${row[columns[0]?.[0] ?? ""]}`}>{columns.map(([key]) => <td key={key}>{percentColumns.includes(key) ? pct(asNumber(row[key])) : row[key] === "" || row[key] == null ? "未提供" : displayValue(key, row[key])}</td>)}</tr>)}</tbody></table></div></>;
}
export function Loading() { return <p className="loading">正在加载研究数据……</p>; }

export type ResearchRouteKey = "cashflow" | "cashflowRecovery" | "microcap" | "microcapRecovery" | "crossMarketLiquidity" | "indices" | "styleFactors" | "liquidity";
