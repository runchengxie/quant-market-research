import { useState } from "react";
import {
  displayLabels,
  displayValue,
  formatNumber as num,
} from "../../lib/format";
import RecoverySection from "../RecoverySection";
import ReplicationSection from "../ReplicationSection";
import {
  Stat,
  Panel,
  BarChart,
  ControlBar,
  Choice,
  ThemeHeading,
  SortableTable,
  Loading,
  englishLocale,
  useCsv,
} from "./research-shared";
import type { CashflowBasis } from "./research-shared";

export function CashflowPage() {
  return (
    <>
      <ReplicationSection scope="cashflow" />
      <CashflowPageContent />
      <RecoverySection scope="cashflow" />
    </>
  );
}

export function CashflowPageContent() {
  const english = englishLocale();
  const t = (zh: string, en: string) => english ? en : zh;
  const { data: rows } = useCsv(
    "index/cashflow_indices/cashflow_performance.csv",
  );
  const { data: frequency } = useCsv(
    "index/cashflow_indices/cashflow_rebalance_frequency.csv",
  );
  const [windowKey, setWindowKey] = useState("rolling_1_year");
  const [basis, setBasis] = useState<CashflowBasis>("all");
  if (!rows || !frequency) return <Loading />;
  const codes = [...new Set(rows.map((row) => row.ts_code))];
  const windows = [...new Set(rows.map((row) => row.window))].sort(
    (left, right) =>
      Object.keys(displayLabels).indexOf(left) +
      100 -
      (Object.keys(displayLabels).indexOf(right) + 100),
  );
  const matching = rows.filter(
    (row) =>
      row.window === windowKey &&
      (basis === "all" || row.return_basis === basis),
  );
  const comparison =
    basis === "all"
      ? matching
      : codes.map(
          (code) =>
            matching.find((row) => row.ts_code === code) ?? {
              ts_code: code,
              name: rows.find((row) => row.ts_code === code)?.name ?? code,
              window: windowKey,
              return_basis: basis,
              return: "",
              cagr: "",
            },
        );
  const windowLabel = displayLabels[windowKey] ?? windowKey;
  const basisLabel = basis === "all" ? t("全部回报口径", "all return bases") : displayLabels[basis];
  const asOf = [...new Set(rows.map((row) => row.as_of).filter(Boolean))]
    .sort()
    .at(-1);
  return (
    <>
      <ThemeHeading
        kicker={t("现金流指数 · 股息与调仓研究", "Cash-flow indices · dividends and rebalancing")}
        title={t("比较现金流指数在不同周期下的历史表现。", "Compare cash-flow indices across historical windows.")}
        text={t("按时间窗口和回报口径筛选，查看调仓频率及历史收益。价格回报只计价格变化，税前全收益计入税前股息再投资。", "Filter by window and return basis to inspect rebalancing frequency and historical returns. Price return excludes dividends; gross total return reinvests pre-tax dividends.")}
        asof={`${t("数据截至", "Data through")} ${asOf ?? t("未提供", "not available")}`}
      />
      <section className="stat-grid">
        <Stat
          label={t("指数样本", "Index samples")}
          value={num(codes.length)}
          note={t("现金流主题指数", "Cash-flow themed indices")}
          accent
        />
        <Stat
          label={t("调仓频率参考", "Rebalancing reference")}
          value={displayValue(
            "rebalance_frequency",
            frequency[0]?.rebalance_frequency ?? "未提供",
          )}
          note={t("首条记录的调仓频率", "Frequency from the first record")}
        />
        <Stat
          label={t("可选时间窗口", "Available windows")}
          value={num(windows.length)}
          note={t("从近一周到近十年", "One week to ten years")}
        />
      </section>
      <Panel title={t("指数收益对比", "Index return comparison")} tag={`${windowLabel} · ${basisLabel}`}>
        <ControlBar>
          <span className="control-label">{t("时间窗口", "Time window")}</span>
          {windows.map((value) => (
            <Choice
              key={value}
              active={windowKey === value}
              onClick={() => setWindowKey(value)}
            >
              {displayValue("window", value)}
            </Choice>
          ))}
          <span className="control-label">{t("回报口径", "Return basis")}</span>
          {[
            ["all", t("全部口径", "All bases")],
            ["price_return", t("价格回报", "Price return")],
            ["gross_total_return", t("税前全收益", "Gross total return")],
          ].map(([value, label]) => (
            <Choice
              key={value}
              active={basis === value}
              onClick={() => setBasis(value as CashflowBasis)}
            >
              {label}
            </Choice>
          ))}
        </ControlBar>
        {comparison.length ? (
          <BarChart
            rows={comparison}
            labelKey="name"
            valueKey="return"
            color="#1267d6"
          />
        ) : (
          <p className="panel-note">{t("当前窗口没有对应回报口径的数据。", "No return-basis data is available for the current window.")}</p>
        )}
      </Panel>
      <Panel title={t("当前窗口的表现明细", "Current-window detail")}>
        <SortableTable
          rows={comparison}
          columns={[
            ["name", t("指数", "Index")],
            ["rebalance_frequency", t("调仓", "Rebalancing")],
            ["return_basis", t("回报口径", "Return basis")],
            ["window", t("窗口", "Window")],
            ["return", t("累计回报", "Cumulative return")],
            ["cagr", t("年化回报", "Annualized return")],
          ]}
          percentColumns={["return", "cagr"]}
        />
      </Panel>
    </>
  );
}
