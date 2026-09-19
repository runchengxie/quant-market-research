export type SizeRow = Record<string, string>;
type Period = "month" | "stage";

export function finiteNumber(value: string | number | null | undefined): number {
  if (value == null || (typeof value === "string" && !value.trim())) return NaN;
  const number = Number(value);
  return Number.isFinite(number) ? number : NaN;
}

export function average(values: number[]) {
  return values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : NaN;
}

export function stageForDate(date: string) {
  const year = Number(date.slice(0, 4));
  return year <= 2019 ? "2015–2019" : year <= 2024 ? "2020–2024" : "2025–当前";
}

export function compareSizeBuckets(left: string, right: string) {
  return left.localeCompare(right, "en", { numeric: true });
}

export function sizeDateRange(rows: SizeRow[]) {
  const dates = rows.map(row => row.formation_date).filter(Boolean).sort();
  return { start: dates[0] ?? null, end: dates.at(-1) ?? null };
}

// Old count-only snapshots do not establish coverage. Keep them usable, but
// reject explicit missing/invalid coverage in newer snapshots.
export function hasCompleteSizeCoverage(row: SizeRow): boolean {
  for (const key of ["formation_count", "count", "observed_return_count", "observed_count", "missing_return_count", "missing_count"]) {
    if (!(key in row)) continue;
    const value = finiteNumber(row[key]);
    if (!Number.isInteger(value) || value < 0 || (!key.startsWith("missing_") && value === 0)) return false;
  }
  for (const key of ["missing_return_count", "missing_count"]) {
    if (key in row && finiteNumber(row[key]) !== 0) return false;
  }
  for (const key of ["return_coverage", "coverage_ratio"]) {
    if (key in row && finiteNumber(row[key]) !== 1) return false;
  }
  const formation = finiteNumber(row.formation_count ?? row.count);
  for (const key of ["observed_return_count", "observed_count"]) {
    if (key in row && Number.isFinite(formation) && finiteNumber(row[key]) !== formation) return false;
  }
  return true;
}

const periodFor = (row: SizeRow, period: Period) => period === "month" ? row.formation_date.slice(0, 7) : stageForDate(row.formation_date);
const usable = (row: SizeRow) => Boolean(row.formation_date && row.bucket) && hasCompleteSizeCoverage(row) && Number.isFinite(finiteNumber(row.forward_return));

export function aggregateSizeRows(rows: SizeRow[], period: Period) {
  const groups = new Map<string, number[]>();
  for (const row of rows) {
    if (!usable(row)) continue;
    const key = `${periodFor(row, period)}|${row.bucket}`;
    const values = groups.get(key) ?? [];
    values.push(finiteNumber(row.forward_return));
    groups.set(key, values);
  }
  return [...groups.entries()].map(([key, values]) => {
    const [periodLabel, bucket] = key.split("|");
    return { period: periodLabel, bucket, value: average(values) };
  }).sort((a, b) => a.period.localeCompare(b.period) || compareSizeBuckets(a.bucket, b.bucket));
}

export function summarizeSizePeriods(rows: SizeRow[], period: Period) {
  const grouped = aggregateSizeRows(rows, period);
  const periods = [...new Set(rows.filter(row => row.formation_date).map(row => periodFor(row, period)))].sort();
  const byDate = new Map<string, Map<string, number[]>>();
  for (const row of rows) {
    if (!usable(row) || !["Q1", "Q10"].includes(row.bucket)) continue;
    const buckets = byDate.get(row.formation_date) ?? new Map<string, number[]>();
    const values = buckets.get(row.bucket) ?? [];
    values.push(finiteNumber(row.forward_return));
    buckets.set(row.bucket, values);
    byDate.set(row.formation_date, buckets);
  }
  return periods.map(periodLabel => {
    const pairs = [...byDate.entries()].filter(([date, buckets]) => periodFor({formation_date: date}, period) === periodLabel && buckets.has("Q1") && buckets.has("Q10"))
      .map(([, buckets]) => ({ q1: average(buckets.get("Q1")!), q10: average(buckets.get("Q10")!) }));
    return {
      period: periodLabel,
      q1: average(pairs.map(pair => pair.q1)),
      q10: average(pairs.map(pair => pair.q10)),
      spread: average(pairs.map(pair => pair.q1 - pair.q10)),
      observations: grouped.filter(row => row.period === periodLabel).length,
      pairedDates: pairs.length,
    };
  });
}

export function sizeMonthlyCurve(rows: SizeRow[]) {
  const monthly = aggregateSizeRows(rows, "month");
  return [...new Set(monthly.map(row => row.bucket))].sort(compareSizeBuckets).map(bucket => ({
    bucket, value: String(average(monthly.filter(row => row.bucket === bucket).map(row => row.value))),
  }));
}

/** Daily observations are equally weighted; an entirely missing bucket stays missing. */
export function dailySizeCurve(rows: SizeRow[]): SizeRow[] {
  const groups = new Map<string, number[]>();
  for (const row of rows) {
    if (!row.bucket) continue;
    const values = groups.get(row.bucket) ?? [];
    if (usable(row)) values.push(finiteNumber(row.forward_return));
    groups.set(row.bucket, values);
  }
  return [...groups].sort(([a], [b]) => compareSizeBuckets(a, b)).map(([bucket, values]) => ({
    bucket, value: values.length ? String(average(values)) : "",
  }));
}
