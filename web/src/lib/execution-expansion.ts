/** Published aggregate values only: missing observations must not become zero. */
export const formatEvidenceNumber = (value: unknown): string =>
 typeof value === 'number' && Number.isFinite(value)
  ? value.toLocaleString('en-US', {maximumFractionDigits: 2}) : '—';
export const formatEvidenceFraction = (value: unknown): string =>
 typeof value === 'number' && Number.isFinite(value) ? `${(value * 100).toFixed(2)}%` : '—';
export function selectSurface(rows: any[], side: string, notional: number) {
 return rows.find(row => row.side === side && row.reference_notional_cny === notional);
}
