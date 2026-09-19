import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { parse } from 'yaml';
import { factorDefinitions, factorDetails, factorIds, factorNames } from './factors';
import { commonFactorProcessing, currentFactorImplementations, implementationSource } from '../lib/factor-implementations';

export type FactorRecord = {
  key: string;
  factorId: string;
  name: string;
  family: string;
  model: 'historical' | 'inspected' | 'core-proxy';
  version: string;
  source: string;
  direction: string;
  feature: string;
  calculation: string;
  caveats: readonly string[];
  verification: 'unverified' | 'source-inspected' | 'dictionary-defined';
};

const historyVersion = 'legacy-factor-summary-v1';
const coreSource = 'studies/style_factors_18y/factor-descriptors.yml';

function key(model: FactorRecord['model'], version: string, factorId: string): string {
  return `${model}:${version}:${factorId}`;
}

function historicalRecords(): FactorRecord[] {
  return factorIds.map((factorId) => {
    const detail = factorDetails[factorId];
    const definition = factorDefinitions.find((item) => item.factor === factorId);
    return {
      key: key('historical', historyVersion, factorId), factorId, name: factorNames[factorId], family: detail.family,
      model: 'historical', version: historyVersion, source: 'web/public/data/barra/historical_factor_summary.json',
      direction: definition?.direction ?? '历史方向未确认', feature: detail.feature, calculation: detail.calculation,
      caveats: ['历史摘要保留了收益序列，但未随来源包完整保留原始 descriptor 与计算脚本。'], verification: 'unverified',
    };
  });
}

function inspectedRecords(document: any, version: string): FactorRecord[] {
  const records: FactorRecord[] = [];
  for (const [family, value] of Object.entries<any>(document.families ?? {})) {
    for (const item of value.factors ?? []) {
      const descriptors = (item.descriptors ?? []).map((descriptor: any) => `${descriptor.id} ← ${descriptor.source}; ${descriptor.transform}; PIT=${descriptor.pit}`).join('；');
      const qualityText = item.id === 'quality' ? factorDetails.quality.calculation : `${descriptors || '该记录为组合因子'}。`;
      records.push({
        key: key('inspected', version, item.id), factorId: item.id, name: item.name_zh ?? factorNames[item.id] ?? item.id,
        family, model: 'inspected', version, source: coreSource, direction: item.direction ?? '未指定',
        feature: descriptors || item.name_zh, calculation: qualityText, caveats: item.caveats ?? [], verification: 'source-inspected',
      });
    }
    for (const item of value.composites ?? []) {
      records.push({
        key: key('inspected', version, item.id), factorId: item.id, name: item.name_zh ?? factorNames[item.id] ?? item.id,
        family, model: 'inspected', version, source: coreSource, direction: 'high_minus_low',
        feature: (item.components ?? []).join(' + '), calculation: item.id === 'quality' ? factorDetails.quality.calculation : `${item.weighting ?? 'equal'} weighting of ${(item.components ?? []).join(', ')}。`,
        caveats: item.caveats ?? [], verification: 'source-inspected',
      });
    }
  }
  return records;
}

function coreRecords(version: string): FactorRecord[] {
  return factorIds.map((factorId) => {
    const detail = factorDetails[factorId];
    const definition = factorDefinitions.find((item) => item.factor === factorId);
    return {
      key: key('core-proxy', version, factorId), factorId, name: factorNames[factorId], family: detail.family,
      model: 'core-proxy', version, source: `${coreSource}#schema-1`, direction: definition?.direction ?? '未指定',
      feature: detail.current, calculation: currentFactorImplementations[factorId] ?? commonFactorProcessing,
      caveats: ['核心代理是当前可重算定义，不等同于历史收益序列的原始算法。'], verification: 'dictionary-defined',
    };
  });
}

export async function readFactorRecords(repoRoot?: string): Promise<FactorRecord[]> {
  const root = repoRoot ?? resolve(dirname(new URL(import.meta.url).pathname), '../../..');
  const raw = await readFile(resolve(root, 'studies/style_factors_18y/factor-descriptors.yml'), 'utf8');
  const digest = createHash('sha256').update(raw).digest('hex').slice(0, 16);
  const inspectedVersion = `source-${implementationSource.revision}`;
  const coreVersion = `schema-1:${digest}`;
  const records = [...historicalRecords(), ...inspectedRecords(parse(raw), inspectedVersion), ...coreRecords(coreVersion)];
  const ids = records.map((record) => record.key);
  if (new Set(ids).size !== ids.length) throw new Error('duplicate versioned factor record key');
  return records;
}
