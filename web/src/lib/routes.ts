export const PUBLIC_ROUTES = {
  overview: "/",
  cashflow: "/research/cashflow/",
  cashflowRecovery: "/research/cashflow/recovery/",
  microcap: "/research/microcap/",
  crossMarketLiquidity: "/research/microcap/cross-market-liquidity/",
  indices: "/research/indices/",
  styleFactors: "/research/style-factors-18y/",
  liquidity: "/research/liquidity/",
  lowTurnover: "/research/factors/low-turnover/",
} as const;

export const LEGACY_HASH_ROUTES: Record<string, string> = {
  "": PUBLIC_ROUTES.overview,
  "#overview": PUBLIC_ROUTES.overview,
  "#cashflow": PUBLIC_ROUTES.cashflow,
  "#cashflow-recovery": `${PUBLIC_ROUTES.cashflowRecovery}#cashflow-recovery`,
  "#microcap": PUBLIC_ROUTES.microcap,
  "#microcap-recovery": `${PUBLIC_ROUTES.microcap}#microcap-recovery`,
  "#cross-market": PUBLIC_ROUTES.crossMarketLiquidity,
  "#style": PUBLIC_ROUTES.indices,
  "#indices": PUBLIC_ROUTES.indices,
  "#style-factors-18y": PUBLIC_ROUTES.styleFactors,
  "#liquidity": PUBLIC_ROUTES.liquidity,
  "#low-turnover": PUBLIC_ROUTES.lowTurnover,
};

export function withBase(path: string, baseUrl: string): string {
  const base = baseUrl === "/" ? "" : baseUrl.replace(/\/$/, "");
  return `${base}/${path.replace(/^\//, "")}`;
}

export function legacyHashTarget(hash: string, baseUrl: string): string | null {
  if (!hash) return null;
  const target = LEGACY_HASH_ROUTES[hash];
  if (!target) return null;
  const [path, anchor] = target.split("#", 2);
  return `${withBase(path, baseUrl)}${anchor ? `#${anchor}` : ""}`;
}
