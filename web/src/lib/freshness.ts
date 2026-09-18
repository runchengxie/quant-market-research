export type FreshnessStatus = "verified" | "derived" | "incomplete" | "exploration" | "pending";

export type SnapshotFreshness = {
  generatedAt: string | null;
  asOf: string | null;
  coverageStart: string | null;
  coverageEnd: string | null;
  source: string;
  qualityStatus: FreshnessStatus;
  markets?: Record<string, string | null>;
};

type RawSnapshot = {
  generated_at?: string;
  as_of?: string;
  coverage_start?: string;
  coverage_end?: string;
  source?: string;
  quality_status?: FreshnessStatus;
  caveats?: string[];
  markets?: Record<string, { as_of?: string; coverage_end?: string; status?: string }>;
};

export function snapshotFreshness(manifest: { snapshots?: Record<string, RawSnapshot> } | null | undefined, key: string): SnapshotFreshness {
  const raw = manifest?.snapshots?.[key] ?? {};
  const coverageEnd = raw.coverage_end ?? null;
  const markets = Object.fromEntries(Object.entries(raw.markets ?? {}).map(([market, value]) => [market, value.as_of ?? value.coverage_end ?? null]));
  return {
    generatedAt: raw.generated_at ?? null,
    asOf: raw.as_of ?? coverageEnd,
    coverageStart: raw.coverage_start ?? null,
    coverageEnd,
    source: raw.source ?? "来源待补",
    qualityStatus: raw.quality_status ?? "pending",
    ...(Object.keys(markets).length ? { markets } : {}),
  };
}

function dateOnly(value: string | null) {
  return value ? value.slice(0, 10) : "日期待补";
}

export function formatFreshness(value: SnapshotFreshness) {
  const coverage = value.coverageStart && value.coverageEnd
    ? `数据截至 ${value.coverageEnd}（${value.coverageStart} 至 ${value.coverageEnd}）`
    : `数据截至 ${dateOnly(value.asOf)}`;
  const generated = value.generatedAt ? `；快照生成于 ${dateOnly(value.generatedAt)}` : "；快照生成时间待补";
  return `${coverage}${generated}`;
}
