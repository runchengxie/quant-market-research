export type SnapshotCard = {
  id: string;
  generatedAt: string | null;
  coverageStart: string | null;
  coverageEnd: string | null;
  status: string;
  source: string;
  caveats: string[];
};

const englishSnapshotCopy: Record<string, { source: string; caveats: string[] }> = {
  microcap: {
    source: "Tushare A-share daily data with reconstructed trading rules",
    caveats: ["Membership, delistings, suspensions, and trading restrictions still require external audit."],
  },
  microcap_repair: {
    source: "Tushare cleaned A-share daily data, suspension records, and special-treatment status audit",
    caveats: [
      "This is a missing-price classification and return-sensitivity audit only; it does not replace the strict primary NAV.",
      "Of 1,848 positions with missing prices, 1,848 have suspension evidence; 210 also have special-treatment evidence. Another 274 remain unclassified. No reliable delisting-date evidence is currently available.",
      "Read strict, partial, carry-all-missing, and carry-evidence-only as separate treatments.",
    ],
  },
  turnover: {
    source: "Tushare cleaned A-share daily prices and valuation data",
    caveats: [
      "The cleaned definition from 2015 onward is updated through the latest completed trading day, 2026-09-17.",
      "The historical definition from 2008 onward is also updated through 2026-09-17, but its special-treatment and suspension eligibility fields are incomplete.",
    ],
  },
  low_turnover: { source: "Reviewed exploratory turnover snapshot", caveats: ["Independent-sample, cost, and capacity validation is not complete."] },
  barra: { source: "Barra-style historical factor result package", caveats: ["This is a historical Barra-style reconstruction; point-in-time financial data and out-of-sample validation remain incomplete."] },
  cashflow: { source: "Cash-flow index recovery snapshot", caveats: ["Official index rules still need to be checked against the local constituent reconstruction."] },
  indices: { source: "Index catalog and representative ETF snapshot", caveats: ["Index returns are price returns. ETFs also incur fees and tracking error."] },
  liquidity: { source: "Cross-market liquidity summary", caveats: ["Market data has different as-of dates. Comparable Japan buckets have not been published."] },
};

export function localizeSnapshotCard(card: SnapshotCard, locale: "en-US" | "zh-CN"): SnapshotCard {
  if (locale === "zh-CN") return card;
  const copy = englishSnapshotCopy[card.id];
  if (!copy) return card;
  return {
    ...card,
    source: copy.source,
    caveats: card.caveats.map((caveat, index) => copy.caveats[index] ?? caveat),
  };
}

export function englishSnapshotSource(id: string, source: string): string {
  return englishSnapshotCopy[id]?.source ?? source;
}

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
