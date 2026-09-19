export type ChartMeta = {
  id: string;
  title: string;
  unit: string;
  sample: string;
  boundary: string;
  explanation: string;
  methodHref?: string;
};

export function chartLabel(value: number | null, unit: 'percent' | 'number'): string {
  if (value === null || !Number.isFinite(value)) return '未提供';
  return unit === 'percent' ? `${(value * 100).toFixed(1)}%` : value.toLocaleString('zh-CN');
}

export function baseChartOptions(theme: { axis: string; grid: string; label: string; tooltip: string }, reducedMotion: boolean) {
  return {
    animation: !reducedMotion,
    animationDuration: reducedMotion ? 0 : 220,
    textStyle: { color: theme.label, fontSize: 12 },
    tooltip: { backgroundColor: theme.tooltip, borderColor: theme.axis, textStyle: { color: theme.label, fontSize: 12 } },
    xAxis: { axisLine: { lineStyle: { color: theme.axis } }, axisLabel: { color: theme.label, fontSize: 12 }, splitLine: { lineStyle: { color: theme.grid } } },
    yAxis: { axisLine: { lineStyle: { color: theme.axis } }, axisLabel: { color: theme.label, fontSize: 12 }, splitLine: { lineStyle: { color: theme.grid } } },
  };
}
