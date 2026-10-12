import { selectSurface } from './execution-expansion';
const finite = (v: unknown): number | null => typeof v === 'number' && Number.isFinite(v) ? v : null;
export function surfaceChartRows(groups: Record<string, any>, side: string, notional: number) {
 return Object.entries(groups).map(([key, group]) => {
  const s = selectSurface(group.cost_surface ?? [], side, notional);
  return {key, books: finite(group.snapshots), filled: finite(s?.full_order_cost_bp?.count), p50: finite(s?.full_order_cost_bp?.p50), p90: finite(s?.full_order_cost_bp?.p90), coverage: finite(s?.full_coverage_rate)};
 });
}
export function strategyChartRows(rows: any[], capital: number) {
 return rows.filter(r => r.capital_cny === capital && ['gross','fee_only','fee_expanded_100k','fee_expanded_1m'].includes(r.scenario));
}
