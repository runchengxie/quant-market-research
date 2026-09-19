import type { FactorRecord } from './factor-records.server';

function escapeCell(value: string) { return value.replaceAll('|', '\\|').replaceAll('\n', ' '); }
export function expandPublicFragments(body: string, records: readonly FactorRecord[]): string {
  const groups: Record<string, string> = {
    'core-proxy': records.filter((record) => record.model === 'core-proxy').slice(0, 19).map((r) => `| ${escapeCell(r.name)} | ${escapeCell(r.direction)} | ${escapeCell(r.calculation)} |`).join('\n'),
    inspected: records.filter((record) => record.model === 'inspected').map((r) => `| ${escapeCell(r.name)} | ${escapeCell(r.feature)} | ${escapeCell(r.verification)} |`).join('\n'),
    historical: records.filter((record) => record.model === 'historical').map((r) => `| ${escapeCell(r.name)} | ${escapeCell(r.direction)} | ${escapeCell(r.verification)} |`).join('\n'),
  };
  return body.replace(/<!--\s*qmr:(core-proxy|inspected-factors|historical-factors)\s*-->/g, (_, name) => groups[name.replace('-factors', '')] ?? '');
}
