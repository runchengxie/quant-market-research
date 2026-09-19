export type SnapshotCard = {
  id: string;
  generatedAt: string | null;
  coverageStart: string | null;
  coverageEnd: string | null;
  status: string;
  source: string;
  caveats: string[];
};

export function snapshotCards(manifest: unknown): SnapshotCard[] {
  if (!manifest || typeof manifest !== 'object' || !('snapshots' in manifest) || !manifest.snapshots || typeof manifest.snapshots !== 'object' || Array.isArray(manifest.snapshots)) {
    throw new Error('manifest.snapshots must be an object');
  }
  return Object.entries(manifest.snapshots).map(([id, value]) => {
    if (!value || typeof value !== 'object') throw new Error(`manifest snapshot ${id} is invalid`);
    const item = value as Record<string, unknown>;
    return {
      id,
      generatedAt: typeof item.generated_at === 'string' ? item.generated_at : null,
      coverageStart: typeof item.coverage_start === 'string' ? item.coverage_start : null,
      coverageEnd: typeof item.coverage_end === 'string' ? item.coverage_end : null,
      status: typeof item.quality_status === 'string' ? item.quality_status : 'unknown',
      source: typeof item.source === 'string' ? item.source : '未提供',
      caveats: Array.isArray(item.caveats) ? item.caveats.filter((v): v is string => typeof v === 'string') : [],
    };
  });
}
