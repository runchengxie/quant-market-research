const englishLocale = () => typeof document === "undefined" || document.documentElement.lang !== "zh-CN";

export const displayLabels: Record<string, [string, string]> = {
  quarterly: ["Quarterly rebalancing", "季度调仓"],
  semiannual: ["Semiannual rebalancing", "半年调仓"],
  price_return: ["Price return", "价格回报"],
  gross_total_return: ["Gross total return", "税前全收益"],
  last_week: ["Past week", "近一周"],
  last_month: ["Past month", "近一个月"],
  last_3_months: ["Past 3 months", "近三个月"],
  last_6_months: ["Past 6 months", "近六个月"],
  ytd: ["Year to date", "年初至今"],
  rolling_1_year: ["Past year", "近一年"],
  year_2025: ["Full year 2025", "2025 年全年"],
  since_20240924: ["Since 2024-09-24", "自 2024 年 9 月 24 日以来"],
  last_3_years: ["Past 3 years", "近三年"],
  last_5_years: ["Past 5 years", "近五年"],
  last_10_years: ["Past 10 years", "近十年"],
  last_15_years: ["Past 15 years", "近十五年"],
  "N/A": ["Not reported", "未提供"],
};

export function asNumber(value: string | number | null | undefined): number {
  return value == null || value === "" ? Number.NaN : Number(value);
}

export function formatPercent(value: number | null | undefined): string {
  return value == null || Number.isNaN(value) ? (englishLocale() ? "Not reported" : "未提供") : `${(value * 100).toFixed(1)}%`;
}

export function formatNumber(value: number | string | null | undefined): string {
  return value == null || value === "" || Number.isNaN(Number(value))
    ? (englishLocale() ? "Not reported" : "未提供")
    : new Intl.NumberFormat(englishLocale() ? "en-US" : "zh-CN", { maximumFractionDigits: 2 }).format(Number(value));
}

export function displayValue(_key: string, value: string): string {
  const label = displayLabels[value];
  if (label) return label[englishLocale() ? 0 : 1];
  return value === "未提供" && englishLocale() ? "Not reported" : value;
}
