# Four-line exploration validation

[English findings](exploration-20261108.md) · [Chinese findings](exploration-20261108.zh-CN.md)

## Scope and frozen identities

Analysis revision `0677ed5` implements entry-reset rolling windows, funded rebalance-cost accounts, hypothetical collateral income, sector ETF proxies and macro classification with separate timestamp/vintage gates. The source revision, exact manifest hash and five analysis-file hashes are in `exploration-summary-20261108.json`. This extends the first-round study without editing its frozen inputs, original raw responses, publication record or reviewed summary.

Resolve `RESEARCH_TASK` to `DATA_ROOT/quant/quant-market-research/china_commodity_equity/exploration-20261108` and `OWNER_TASK` to the data owner's `tasks/commodity-exploration-20261108`. The new private manifest references the first-round `baseline-reviewed-manifest.json` by path and hash, the new owner receipts by path and hash, and the explicitly selected immutable context snapshot. The selected snapshot is the August 28, 2026 build for as-of August 31; its historical PMI values have availability at observation time in 2026, not in earlier sample years. No shared alias was written or moved.

The supplier acquisition retained 56 bounded probes plus 32 filtered annual economic-event queries, all with request parameters, timestamps, row counts and raw SHA-256 receipts. Three-year fund/rate windows stay below endpoint limits. `eco_cal` responses at its 100-row cap are rejected rather than accepted as complete. Non-manufacturing and Caixin events are excluded from official manufacturing PMI. Raw fund identities must match each query. Duplicate or invalid export values fail. Empty/nonzero responses remain explicit, including all five gap requests and empty historical release schedules. Original publisher documents are retained separately with URL and file hashes; HTTP success alone was not taken as content validation.

## Reproduction

```bash
uv run --locked --extra dev python -m market_research.studies.commodity_equity.followup_run \
  --manifest "$RESEARCH_TASK/manifest-reviewed.json" \
  --output "$RESEARCH_TASK/reproduction-NEW"
```

`manifest-reviewed.json` contains `source_revision`, `baseline_manifest_path`, `baseline_manifest_sha256`, an `exports` list of receipt path/hash objects, and context snapshot path/hash. The runner refuses existing destinations and repository-contained outputs. It writes a derived `reviewed-candidate.json` and private `full-diagnostics.json`; the latter retains all window rows and macro decisions and is never projected. Public publication still requires review of the candidate, report numbers and evidence limitations. No code downloads supplier data or opens credentials during a numerical run.

## Calculation rules

- All rolling 60/120-month windows begin with fresh registered 10/20/30/40% commodity allocations. Monthly policies reset at actual common month ends; annual policies at December common month ends. A window does not inherit holdings from an older global account. CAGR uses the fixed month horizon; base/subperiod summaries use actual elapsed days/365.25. Daily drawdown includes intramonth losses.
- Improvement counts use the identical stock-only window and a numerical tolerance of `1e-12`. Return/drawdown/both/neither counts are descriptive. Annual entry cohorts and three contiguous subperiods are separate diagnostics. Crises are not removed and neighboring periods are not spliced.
- Rebalance fees solve `fee = rate × sum(abs(target × (wealth-fee) - holdings))`, with both sides charged. They are paid after current-period returns and before setting funded target holdings. Initial purchase and final liquidation are excluded. The break-even fee search is bounded at 1,000 bp. This models sleeve rebalance costs, not contract rolls, integer quantities, margin or calibrated execution.
- Extra annual portfolio drag budget is `max(0, 1-(stock_wealth/mix_wealth)^(1/years)) × 10000`. Losing windows have zero positive cost budget. This is distinct from fees on turnover or costs applied only to the commodity sleeve.
- Collateral income adds a chosen 0/50/100% of a prior available overnight Shibor quote to the commodity sleeve's daily index return, using simple actual/365 accrual. Rate quotes may be carried across market closures for at most 14 days; no future rate or missing price is filled. These scenarios assume the commodity index excludes collateral interest; that historical semantic gate remains unresolved. No income is added to NAV already containing cash. Missing earlier quotes force a separately labeled shorter sample. Shibor is not an investable yield.
- ETF market proxies are close × adjustment factor; NAV proxies use provider adjusted NAV on valuation dates. Exact common trading sessions are required; extra weekend NAV observations are not fabricated market sessions. NAV announcement dates are not trading signals. Management fees are embedded, not subtracted again. Each issuer benchmark is preserved; tracking error against NHCI is unavailable for these mismatched products. No complete CTA universe was admitted.
- Economic-event reconstructions use the next full local day because the vendor clock timezone is not certified. Regimes are chosen at the actual prior month-end session for next-month returns, with PMI ≥50 and PPI YoY ≥0. Date-only or timezone-naive availability cannot receive strict certification, even if a vintage flag is set. Strict admission requires explicit timezone-aware availability and verified-vintage flags strictly before 15:00 Asia/Shanghai; UTC decisions convert to Shanghai before normalization. A publication date alone does not certify historical values. All current event/snapshot reconstructions remain unverified. Macro group months are never concatenated into hypothetical continuous wealth.

## Independent checks

Twelve representative rolling windows, selected as first/middle/last for each 80/20 policy/horizon, were recomputed using the first-round daily path engine rather than the new segment implementation. Maximum terminal wealth error was `1.23e-14`, maximum drawdown error `2.67e-15`, both within `1e-11`. The external task retains the independent recipe and result receipt.

The three 2025 NAV returns match original annual reports at their disclosed 0.01-percentage-point precision: 159980 22.28%, 159981 −11.84%, 159985 4.18%. Report pages 7, 7 and 6 were visually inspected. The selected market/NAV histories remain revised provider proxies; this cross-check does not certify every daily value. The issuer reports also confirm different contract benchmarks, so NHCI differences are not tracking errors.

Independent review found that date-only timestamps and exact-close releases could pass strict macro admission. Tests reproduced the problem, then passed after the explicit-timezone/strict-cutoff fix. Current reconstructed/strict counts remained 227/0. No remaining important code issue was identified in re-review.

The bilingual figures use Matplotlib 3.10.7 and only the derived reviewed candidate. Plotting code, render-library version, source result hash and SVG hashes are retained with external task figures. Figures were visually inspected; the initial title/legend overlap was repaired in a new version. Reviewed SVGs and source embeds match the final figure hashes.

## Validation outcome

The full local Python suite passed 962 tests, with 22 skips for optional formal/integration providers. All 332 web tests passed. Ruff, Astro build, static public-boundary verification, local study links, JSON parsing and summary/figure/source hash checks passed. The final responsive figures were rebuilt and reverified. Final independent evidence review found no important findings. Remote execution-provider, synthetic-chain and complete build/browser checks remain the merge gates.

## Remaining evidence

The new 2012/2022 methodology documents do not resolve the effective historical roll ledger, and the two-day commodity gaps and equity launch-day gap remain empty. Another original daily-report point check cannot replace annual-return reconciliation. Actual collateral investments, contract-level transactions and margin events, a controlled CTA universe, and an authentic macro-vintage archive remain prerequisites for implementation or timing claims. Source evidence is recorded as recovered, checked or unresolved; an exploratory positive conditional return does not promote a failed admission gate.
