import { createHash } from 'node:crypto';
import evidence from '../../public/data/legacy-strategy-evidence.json';
import review from '../../public/data/legacy-strategy-review.json';

function canonical(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value !== null && typeof value === 'object') {
    const record = value as Record<string, unknown>;
    return `{${Object.keys(record).sort().map(key => `${JSON.stringify(key)}:${canonical(record[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

export function validateLegacyStudyEvidence(value = evidence, record = review) {
  if (Object.keys(value).sort().join(',') !==
      ['schema_version', 'reviewed_source_digest', 'reviewed_content_digest', 'studies'].sort().join(',') ||
      Object.keys(record).sort().join(',') !==
      ['schema_version', 'source_sha256', 'content_sha256', 'asset_sha256', 'review_kind', 'reviewed_on'].sort().join(',')) {
    throw new Error('Unreviewed public envelope field');
  }
  const serialized = `${JSON.stringify(JSON.parse(canonical(value)), null, 2)}\n`;
  if (createHash('sha256').update(serialized).digest('hex') !== record.asset_sha256) {
    throw new Error('Reviewed public asset/content digest mismatch');
  }
  const digest = createHash('sha256').update(canonical(value.studies)).digest('hex');
  if (value.schema_version !== 'research.legacy_strategy_public.v1' ||
      value.reviewed_source_digest !== record.source_sha256 ||
      value.reviewed_content_digest !== record.content_sha256 || digest !== record.content_sha256) {
    throw new Error('Study review identity or content mismatch');
  }
  return value;
}
