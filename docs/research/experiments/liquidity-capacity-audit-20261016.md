# Liquidity and capacity evidence audit — 2026-10-16

> This is the archived audit of the inherited release. The [subsequent reconstruction](liquidity-rebuild-20261016.md) supplies the current four-market evidence; the old count conflicts remain unresolved.

[中文](liquidity-capacity-audit-20261016.zh-CN.md)

The unified [liquidity, costs and capacity study](https://runchengxie.github.io/quant-market-research/research/liquidity/) distinguishes historical activity, static book costs, execution simulation and actual-order calibration. The last remains open. Inherited cross-market aggregates contain confirmed inconsistencies and must not establish a market ranking or portfolio capacity.

| Check | Evidence | Action |
| --- | --- | --- |
| A-share total count | Reported 5,321; five bucket counts sum to 5,461 | Exclude from comparison; preserve source numbers |
| A-share below USD 100m | Reported 125; first two buckets sum to 177 | Do not guess which total is correct |
| Missing P90 | All five HK and A-share buckets lack P90 | Retain missing values; remove median fallback |
| Snapshot dates | US 2025-10-03; HK 2026-05-26; A-share 2026-09-07 | Show market dates; no common-date interpretation |
| Historical periods | Three pending periods have no market rows | Show pending state, never latest data |
| Counts and grain | Bucket count is stocks; security-day observations absent | Separate columns; do not substitute grains |
| Inherited metric lineage | Release says 20-day mean; current helper prefers medadv20, falling back to turnover | Flag unverified lineage; helper provenance is not established |
| Ten-date book accounting | 311,395 sampled = 306,483 valid + 4,912 excluded | Daily count conservation reconciles |
| Missing minutes | 971 total, 960 on 2026-04-16 | Concentrated gap requires explanation |
| Historical order references | 2021-01-04 Shanghai: 758,422 trades, zero orders in audited sample | Not suitable for full book reconstruction |

Chart and table use the same selected market-cap bucket. Cross-sectional median/mean/P90 describe the distribution across stocks, distinct from each stock's rolling statistic. Count-consistent US/HK aggregates remain historical, not fully verified. Japan has no comparable published snapshot. Missing A-share suspended sessions cannot be interpreted as zero activity.

The participation calculator is independent arithmetic using a user-supplied turnover assumption. It establishes neither fills nor portfolio capacity.

## Reproduce and scope

Run from `web/`:

```sh
node --import tsx --test src/liquidity-quality.test.mjs
npm test
npm run build:pages
PORT=4367 npx playwright test tests/e2e/capacity-research.spec.ts --workers=1
```

`src/lib/liquidity-quality.ts` checks counts and controls inclusion. Tests exercise published counts, absent metrics, pending periods, bucket selection and arithmetic bounds. This audit inspected public aggregates and existing audit records, not every vendor row. It does not certify raw data, historical eligibility, FX, corporate actions or execution semantics. Reviewed execution aggregates remain unchanged.

## Next evidence

Regenerate snapshots from versioned inputs with checksums, common-date windows, per-security freshness, FX dates and units, point-in-time universes including delistings, and suspended-session handling. Record mean ADV20 and median daily turnover separately; fail publication on inconsistent counts. Generate historical windows only with comparable coverage. Explain execution missing minutes, verify order-type/cancellation and cross-stream semantics, broaden preselected dates, and validate against real orders before estimating actual capacity.
