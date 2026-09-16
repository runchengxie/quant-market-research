export const displayLabels: Record<string, string> = {
  quarterly: "季度调仓",
  semiannual: "半年调仓",
  price_return: "价格回报",
  gross_total_return: "税前全收益",
  last_week: "近一周",
  last_month: "近一个月",
  last_3_months: "近三个月",
  last_6_months: "近六个月",
  ytd: "年初至今",
  rolling_1_year: "近一年",
  year_2025: "2025 年全年",
  since_20240924: "自 2024 年 9 月 24 日以来",
  last_3_years: "近三年",
  last_5_years: "近五年",
  last_10_years: "近十年",
  last_15_years: "近十五年",
  "N/A": "未提供",
};

export function asNumber(value: string | number | null | undefined): number {
  return value == null || value === "" ? Number.NaN : Number(value);
}

export function formatPercent(value: number | null | undefined): string {
  return value == null || Number.isNaN(value) ? "未提供" : `${(value * 100).toFixed(1)}%`;
}

export function formatNumber(value: number | string | null | undefined): string {
  return value == null || value === "" || Number.isNaN(Number(value))
    ? "未提供"
    : new Intl.NumberFormat("zh-CN", { maximumFractionDigits: 2 }).format(Number(value));
}

export function displayValue(_key: string, value: string): string {
  return displayLabels[value] ?? value;
}
