# Minute execution diagnostic

This study adds funded historical minute execution to the execution-cost topic. It does not establish live capacity or identify the impact caused by our own orders. The public diagnostic selects 40 Shanghai/Shenzhen main-board securities by historical total market value; it is a separate sample from the earlier 400-security, 56-session diagnostic.

The reviewed windows start independently in cash: 2024-07-01 through 2024-12-31 (125 sessions), and 2025-01-02 through 2025-12-31 (243 sessions). Each contains nine completed scenarios. Full-year 2024 is withheld: 183 original unexplained adjustment-factor discontinuities were investigated, but 21 remain unresolved after re-observation. Only 185 of 242 trading dates have minute partitions in 2023, so no continuous 2023 result is claimed.

## Decision and execution rules

Targets use the previous available daily records, announcement-dated name/ST eligibility, listing age of at least 120 calendar days and known suspension status. Decisions occur after the close; next-session orders start at 09:32 Asia/Shanghai. Retrospectively reconstructed reference histories are validated against their source receipt; this is not a complete revision-vintage PIT database.

Execution uses raw prices, volume in shares and turnover in CNY. Vendor timestamps receive a conservative one-minute availability delay and explicit interval starts. Entire intervals must follow release plus latency; auction records provide marks but cannot fill orders. The historical turnover/volume price proxy is bounded by OHLC. Orders share a 5% per-symbol minute-volume cap, with cash affordability, sell-before-buy processing, T+1 inventory, 100-share lots and side-specific limit-touch blocks. Unfilled orders remain visible and are cancelled by a superseding target snapshot or expire at the fixed deadline.

Release horizons are 30, 120 or 330 elapsed minutes, including lunch; the five-slice schedule is fixed in advance. Daily, five-session and five-session buffer rebalances use complete target snapshots. This is a bounded bar simulator, without intrabar queues, endogenous price impact, replenishment or adaptive broker execution.

The standard fee assumption is 1 bp commission per side plus 5 bp sell tax, without a commission minimum. A separate scenario charges a CNY 5 floor once per parent order, accumulated across its partial fills. Actual broker child-order billing is unverified. The gross scenario retains execution constraints and sets fees to zero.

## Corporate actions and valuation

Actual record-date holdings determine cash/share entitlements. Cash pays on its payment date; shares become tradable on their listing date. Unreleased rights enter valuation and target exposure without becoming sellable. Gross cash dividends are used, with no shareholder-specific withholding model. Announcement overrides are hash-linked to the downloaded source and primary PDFs; source rows remain unchanged. In particular, reorganization shares allocated only to creditors/investors are not treated as distributions to original holders.

Confirmed full-day suspensions with no minute bars receive nontradable valuation marks carried from a previously observed raw price and adjusted for intervening known ordinary actions. The 2024 half-year uses 17 such symbol-days, at most 7 calendar days old; 2025 uses 111, at most 22 days old. These marks cannot generate fills. Unknown or intraday suspension evidence is not silently filled. Missing owned marks invalidate NAV.

## Reading the results

Target-notional completion is cumulative executed quantity divided by cumulative requested quantity, weighted by each parent order's arrival reference across buys and sells. It is not the fraction of outstanding orders completed at the end. Arrival shortfall includes signed execution-price movement, unfilled opportunity cost at the fixed deadline and fees. Raw or synthetic arrival references are disclosed; missing references remain unavailable. It is an accounting measure, not causal market impact.

Capital changes alter affordability, partial fills and portfolio paths. A higher terminal NAV at larger capital therefore does not prove scalable alpha or a capacity threshold. Windows have different lengths and independent initial cash; their terminal NAVs are not annual return rankings. Real order/quote records are still needed to calibrate latency, queue position, commissions and the impact model.

Independent reconstruction checked all 18 ledgers: 596,564 fills, 89,088 orders and 3,312 daily records. Cash, holdings, fees, corporate rights, NAV, shortfall, participation, timing, T+1 and lot constraints passed. Public JSON exports only reviewed aggregate fields; vendor rows, symbols, detailed orders and machine paths remain outside this repository.

## Reproduce

Install the `formal` and `duckdb` extras on Python 3.12 or later. The immutable provider dependency must be merged before use. The root `uv` override aligns the runtime's older transitive platform pin with this reviewed revision; the formal install and replay tests validate the combined dependency graph. Resolve configured data roots, then use a new task output directory:

```bash
uv run --extra formal --extra duckdb python scripts/run_execution_cost_minute.py \
  --data-root "$QUANT_DATA_ROOT/quant-market-data-platform" \
  --dividends "$EXECUTION_SOURCES/dividend.parquet" \
  --dividend-coverage "$EXECUTION_SOURCES/coverage.json" \
  --action-overrides "$EXECUTION_SOURCES/corporate-action-overrides.json" \
  --suspensions "$SUSPENSION_SOURCE" \
  --start 20240701 --end 20241231 --count 40 --output "$EXECUTION_OUTPUT"
```

Repeat with `20250102` and `20251231` in a separate directory. Input preparation verifies calendars, coverage, manifests, action evidence and hashes. Scenario receipts bind inputs, implementation and output hashes; existing completed scenarios are reused only when all match. A failed gate must be resolved with evidence, never bypassed by filling gaps or smoothing prices. `--prepare-only` and `--run-prepared` separate preparation and simulation. Review the complete private ledgers before projecting public aggregates with `minute_publication.public_projection`; carried valuations require an explicit reviewed maximum age.

Primary action evidence includes [2024 capitalization announcement](https://epaper.stcn.com/pic/202406/26/8f7dd3652e682ceb00f5b19695fd561d.pdf), [2025 reorganization announcement](https://big5.sse.com.cn/site/cht/www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2025-11-20/600165_20251120_OSVA.pdf), and [2025 reorganization execution announcement](https://static.cninfo.com.cn/finalpage/2025-12-30/1224906744.PDF). These retrospectively checked facts do not establish historical publication-vintage completeness.

## Implementation provenance

The reviewed runs bind engine SHA-256 `59e39eae0a13fbb9eabd0af0624709be285cf6e60454040eee932c99c883dfdc`. The merged provider adds only normalized-date typing declarations, giving `42a2a417dc26e8b9b360fdb00e892633be3313d8091ae52dc694d4fb7b90539b`. Independent comparison found identical ASTs after removing identity `typing.cast` calls and the attribute type annotation. The corporate-action contract is unchanged. Original result receipts retain their original hashes; the runner will reject reuse under the new byte hash. A fresh reproduction uses a new output directory. This equivalence verification does not rewrite historical run provenance.
