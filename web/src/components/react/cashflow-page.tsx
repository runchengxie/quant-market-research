import { useState } from "react";
import { displayLabels, displayValue, formatNumber as num } from "../../lib/format";
import RecoverySection from "../RecoverySection";
import ReplicationSection from "../ReplicationSection";
import { Stat, Panel, BarChart, ControlBar, Choice, ThemeHeading, SortableTable, Loading, useCsv } from "./research-shared";
import type { CashflowBasis } from "./research-shared";

export function CashflowPage() {
  return <><ReplicationSection scope="cashflow"/><CashflowPageContent/><RecoverySection scope="cashflow"/></>;
}

export function CashflowPageContent() {
  const { data: rows } = useCsv("index/cashflow_indices/cashflow_performance.csv");
  const { data: frequency } = useCsv("index/cashflow_indices/cashflow_rebalance_frequency.csv");
  const [windowKey, setWindowKey] = useState("rolling_1_year");
  const [basis, setBasis] = useState<CashflowBasis>("all");
  if (!rows || !frequency) return <Loading />;
  const codes = [...new Set(rows.map((row) => row.ts_code))];
  const windows = [...new Set(rows.map((row) => row.window))].sort((left, right) => (Object.keys(displayLabels).indexOf(left) + 100) - (Object.keys(displayLabels).indexOf(right) + 100));
  const matching = rows.filter((row) => row.window === windowKey && (basis === "all" || row.return_basis === basis));
  const comparison = basis === "all" ? matching : codes.map((code) => matching.find((row) => row.ts_code === code) ?? { ts_code: code, name: rows.find((row) => row.ts_code === code)?.name ?? code, window: windowKey, return_basis: basis, return: "", cagr: "" });
  const windowLabel = displayLabels[windowKey] ?? windowKey;
  const basisLabel = basis === "all" ? "全部回报口径" : displayLabels[basis];
  const asOf = [...new Set(rows.map((row) => row.as_of).filter(Boolean))].sort().at(-1);
  return <><ThemeHeading kicker="现金流指数 · 股息与调仓研究" title="比较现金流指数在不同周期下的历史表现。" text="按时间窗口和回报口径筛选，查看调仓频率及历史收益。价格回报只计价格变化，税前全收益计入税前股息再投资。" asof={`数据截至 ${asOf ?? "未提供"}`}/><section className="stat-grid"><Stat label="指数样本" value={num(codes.length)} note="现金流主题指数" accent/><Stat label="调仓频率参考" value={displayValue("rebalance_frequency", frequency[0]?.rebalance_frequency ?? "未提供")} note="首条记录的调仓频率"/><Stat label="可选时间窗口" value={num(windows.length)} note="从近一周到近十年"/></section><Panel title="指数收益对比" tag={`${windowLabel} · ${basisLabel}`}><ControlBar><span className="control-label">时间窗口</span>{windows.map((value) => <Choice key={value} active={windowKey === value} onClick={() => setWindowKey(value)}>{displayValue("window", value)}</Choice>)}<span className="control-label">回报口径</span>{[["all", "全部口径"], ["price_return", "价格回报"], ["gross_total_return", "税前全收益"]].map(([value, label]) => <Choice key={value} active={basis === value} onClick={() => setBasis(value as CashflowBasis)}>{label}</Choice>)}</ControlBar>{comparison.length ? <BarChart rows={comparison} labelKey="name" valueKey="return" color="#1267d6"/> : <p className="panel-note">当前窗口没有对应回报口径的数据。</p>}</Panel><Panel title="当前窗口的表现明细"><SortableTable rows={comparison} columns={[["name", "指数"], ["rebalance_frequency", "调仓"], ["return_basis", "回报口径"], ["window", "窗口"], ["return", "累计回报"], ["cagr", "年化回报"]]} percentColumns={["return", "cagr"]}/></Panel></>;
}
