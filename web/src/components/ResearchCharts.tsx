import { useEffect, useRef } from "react";
import { echarts, type EChartsOption } from "./echarts";
import { readChartTheme } from "../theme";

type ChartRow = Record<string, string>;
type Series = { name: string; values: Array<number | null>; color: string };

function Chart({ option, description = "研究数据图表，数值可在相邻表格中查阅" }: { option: EChartsOption; description?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current) return;
    const chart = echarts.init(ref.current);
    const paint = () => {
      chart.setOption(option, true);
      const theme = readChartTheme();
      const axis = { axisLabel: { color: theme.axis }, axisLine: { lineStyle: { color: theme.axis } }, splitLine: { lineStyle: { color: theme.grid } } };
      chart.setOption({ xAxis: axis, yAxis: axis, textStyle: { color: theme.label }, series: (Array.isArray(option.series) ? option.series : []).map(() => ({ label: { color: theme.label } })) });
    };
    paint();
    const resize = () => chart.resize();
    window.addEventListener("resize", resize);
    const observer = new ResizeObserver(resize);
    observer.observe(ref.current);
    const themeObserver = new MutationObserver(paint);
    themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    return () => {
      window.removeEventListener("resize", resize);
      observer.disconnect();
      themeObserver.disconnect();
      chart.dispose();
    };
  }, [option]);
  return <div ref={ref} className="research-chart" role="img" aria-label={description} />;
}

const grid = { left: 72, right: 72, top: 24, bottom: 48 };

export function ResearchBarChart({ rows, labelKey, valueKey, color = "#1267d6", formatter = (value: number) => `${(value * 100).toFixed(1)}%`, logScale = false }: { rows: ChartRow[]; labelKey: string; valueKey: string; color?: string; formatter?: (value: number) => string; logScale?: boolean }) {
  const theme = readChartTheme();
  const axis = { axisLine: { lineStyle: { color: theme.axis } }, axisLabel: { color: theme.axis } };
  const values = rows.map((row) => { const raw = row[valueKey]; if (raw == null || raw.trim() === '') return null; const value = Number(raw); return Number.isFinite(value) ? value : null; });
  const finiteValues = values.filter((value): value is number => value != null);
  const canUseLog = logScale && finiteValues.length > 0 && finiteValues.every((value) => value > 0);
  const formatValue = (value: unknown) => value == null || value === "" || !Number.isFinite(Number(value)) ? "未提供" : formatter(Number(value));
  return <Chart description={rows.map((row, index) => `${row[labelKey]}：${formatValue(values[index])}`).join("；")} option={{ animationDuration: 220, grid: { ...grid, left: 48, right: 54, containLabel: true }, tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, valueFormatter: formatValue }, xAxis: { ...axis, type: canUseLog ? "log" : "value", axisLabel: { ...axis.axisLabel, hideOverlap: true, formatter: (value: number) => canUseLog ? String(value) : formatter(value) }, splitLine: { lineStyle: { color: theme.grid } } }, yAxis: { ...axis, type: "category", data: rows.map((row) => row[labelKey]), axisLabel: { ...axis.axisLabel, interval: 0, width: 150, overflow: "truncate", fontSize: 12 } }, series: [{ type: "bar", data: values, barMaxWidth: 18, label: { show: true, position: "right", color: theme.label, fontSize: 12, formatter: (params: any) => formatValue(params.value) }, itemStyle: { color: (params: any) => Number(params.value) < 0 ? "#8e4d48" : color }, markLine: canUseLog ? undefined : { silent: true, symbol: "none", lineStyle: { color: theme.axis, width: 1 }, data: [{ xAxis: 0 }] } }] }} />;
}

export function ResearchLineChart({ series, labels }: { series: Series[]; labels: string[] }) {
  const theme = readChartTheme();
  const axis = { axisLine: { lineStyle: { color: theme.axis } }, axisLabel: { color: theme.axis } };
  return <Chart option={{ animationDuration: 220, tooltip: { trigger: "axis" }, dataZoom: [{ type: "inside" }, { type: "slider", height: 12, bottom: 8, showDetail: false }], grid, xAxis: { ...axis, type: "category", data: labels, axisLabel: { ...axis.axisLabel, hideOverlap: true, formatter: (value: string) => value.length > 7 ? value.slice(0, 7) : value } }, yAxis: { ...axis, type: "value", scale: true, splitLine: { lineStyle: { color: theme.grid } } }, series: series.map((item) => ({ name: item.name, type: "line", showSymbol: false, smooth: true, data: item.values, lineStyle: { width: 2.5, color: item.color }, areaStyle: series.length === 1 ? { color: `${item.color}18` } : undefined })) }} />;
}
