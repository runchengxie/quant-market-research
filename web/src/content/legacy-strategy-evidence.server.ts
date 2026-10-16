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
  for (const study of value.studies) {
    const studyKeys = ['id', 'evidence_id', 'question', 'conclusion', 'source_status', 'evidence_stage', 'sample_scope', 'baseline', 'metrics', 'limitations', 'factor_refs'];
    if (Object.keys(study).sort().join(',') !== studyKeys.sort().join(',') ||
        !['etf-rotation', 'hotsector'].includes(study.id) || !Array.isArray(study.metrics) || study.metrics.length > 70 ||
        !Array.isArray(study.limitations) || !Array.isArray(study.factor_refs) ||
        (['question', 'conclusion', 'sample_scope', 'baseline'] as const).some(key => typeof study[key] !== 'string')) {
      throw new Error('Unreviewed study or metric collection');
    }
    for (const metric of study.metrics) {
      if (Object.keys(metric).sort().join(',') !== 'definition,name,unit,value' ||
          !/^(etf\.cumulative_return\.(raw|factor_adjusted)\.(linear_rank|lightgbm_regression|lightgbm_ranker|fixed_share_basket|single_etf_baseline)\.cost_(0|10|25|50)_bps|etf\.maximum_drawdown\.(raw|factor_adjusted)\.(linear_rank|lightgbm_regression|lightgbm_ranker|fixed_share_basket|single_etf_baseline)\.cost_25_bps|etf\.calendar_return\.factor_adjusted\.(lightgbm_regression|fixed_share_basket)\.year_20(21|22|23|24|25)\.cost_25_bps|etf\.relative_log_return_ci95\.(linear_rank|lightgbm_regression|lightgbm_ranker)\.(low|high)\.cost_25_bps|hotspot\.(mean_event_delta|positive_event_count)\.cost_(0|25|50)_bps)$/.test(metric.name) ||
          !['percent', 'percentage_points', 'events'].includes(metric.unit) || !Number.isFinite(metric.value) ||
          typeof metric.definition !== 'string' || metric.definition.length > 320 ||
          /(?:\/home\/|\/tmp\/|\.parquet|\.csv|\.pkl|security.?code|constituent)/i.test(`${metric.name} ${metric.definition}`)) {
        throw new Error('Unreviewed public metric shape or content');
      }
    }
  }
  return value;
}
