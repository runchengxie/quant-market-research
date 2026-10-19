export type CostRow = { target: string; lag_sessions: number; model: string; scenario: string; round_trip_bp?: number; mean_daily_net_bp: number | null; n: number };
export const costModels = ['domestic_fx', 'global', 'all_overseas', 'always_long'] as const;
export function selectCostRows(rows: readonly CostRow[], target: string, lag: number) {
 return rows.filter(r => r.scenario === 'flat_bps' && r.target === target && r.lag_sessions === lag && Number.isFinite(r.round_trip_bp)).sort((a,b) => a.round_trip_bp! - b.round_trip_bp!);
}
export const costValue = (value: number | null | undefined) => value == null || !Number.isFinite(value) ? null : value;
