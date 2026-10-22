import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
// Reviewed projection lock. Changing any value requires source reconciliation and review.
const reviewedSha256 = '76f290142b01bb116e1e97f03b319bd3bdab9a2236c5f0760f89220aa931c50d';
export function validateReaderEvidence(bytes) {
  if (createHash('sha256').update(bytes).digest('hex') !== reviewedSha256) throw new Error('Reader evidence differs from reviewed hash');
  const d = JSON.parse(bytes);
  if (d.unit !== 'percentage_points' || d.months !== 86 || d.rankingMode !== 'formation_signal_support_fixed_before_forward_return_filter') throw new Error('Unreviewed units, count or ranking');
  if (d.controls.map(r => r.id).join(',') !== 'raw,size,size_lowvol,plus_beta_value') throw new Error('Unreviewed control stages');
  if (d.formationStart !== '2019-05-31' || d.formationEnd !== '2026-06-30' || d.firstReturnEnd !== '2019-06-28' || d.lastReturnEnd !== '2026-07-31') throw new Error('Unreviewed date bounds');
  for (const row of d.controls) if (![row.low,row.high,row.spread,row.ciLow,row.ciHigh].every(Number.isFinite) || row.ciLow > row.spread || row.ciHigh < row.spread || Math.abs(row.low-row.high-row.spread)>1e-8) throw new Error('Invalid reader estimate');
  return d;
}
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  validateReaderEvidence(readFileSync(new URL('../public/data/low_turnover_reader.json', import.meta.url)));
  console.log('Reviewed reader evidence verified');
}
