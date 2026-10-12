# First L2 pilot: source audit and static measurement

[中文](pilot_findings.zh-CN.md)

The first local measurement is complete. It establishes a reproducible static-book exploration, not a general A-share slippage calibration. The owner confirmed aggregate-derivative publication permission on 2026-10-12. Reviewed aggregate costs and coverage are now public; security-level measurements, raw sources and executed private notebooks remain outside Git.

## Sample and audit

| Day | Source rows scanned | Selected security-days | Sampled minute books | Valid two-sided books | One-sided exclusions |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2026-04-16 | 21,075,449 | 142 | 32,694 | 32,341 | 353 |
| 2026-04-24 | 21,886,053 | 143 | 33,889 | 33,186 | 703 |
| 2026-07-20 | 22,712,123 | 142 | 33,653 | 32,545 | 1,108 |

65,673,625 rows were scanned; all scanned non-null identities/clocks had the expected date and valid native clock encoding. These checks do not establish correctness of every source book. Detailed book validation covers the 100,236 selected stock-minute snapshots, not all 65.7m rows. 98,072 books remain; 2,164 exclusions are one-sided. No crossed/locked or malformed book was observed in this sample. There are 427 selected security-days but only 426 valid-book security-days, because one security-day has no retained two-sided book.

The sample includes stock-like Shanghai/Shenzhen prefixes with integer security code modulo 37 equal to zero. For each day/security/minute, select the earliest native source timestamp, breaking ties by source-row number, **before** checking book validity. Sessions are [09:30, 11:30) and [13:00, 14:57); auctions and lunch are excluded. Missing bins are not filled. Final security-minute uniqueness is independently checked in the notebook. The run's timestamp-duplicate counter compares only the per-batch minute representatives; it is not an all-event duplicate or source-order audit. This is a convenience sample, not a probability sample. Point-in-time security eligibility is not independently verified; Beijing, funds and bonds are outside the prefix selection.

## Material findings

- Some lake copies replace native `TickTime` with `time_ms`, measured relative to 09:30. The platform's projection aliases names without converting that clock. This pilot explicitly rejects aliased sources and uses native `SecuCode`/`TickTime` files. This is a downstream input gate, not an upstream ingestion rewrite.
- The older 2026-04-24 canonical snapshot pilot has 21,482,680 rows versus 21,886,053 source rows: 403,373 rows were removed in that artifact. It must not be treated as an unfiltered population when studying absent or one-sided depth. The source was preserved and exclusions recorded explicitly in this run.
- Prices are interpreted as integer cents and quantities as shares. This agrees with the data platform's Guan trade convention. For the sampled snapshots, cumulative turnover / (cumulative volume × last price / 100) is within [0.8, 1.2] throughout. Since last price differs from the cumulative average, this is a scale sanity check, not exact reconciliation or supplier specification proof.

## What was measured

Quoted spread and ten-level bid/ask notional depth; static buy/sell costs at CNY 10k/100k/1m/10m reference notionals; full-order coverage; daily distributions; descriptive daily median-depth terciles; and a common fully covered population for comparing order sizes without changing the population. All are snapshot-weighted descriptive distributions, not population confidence intervals.

The reference notional equals midpoint × target shares. Fractional shares are permitted for analytical curves; this is neither a cash budget nor a lot-sized executable order. Costs use the current midpoint, already include half-spread and depth consumption, exclude fees, latency, replenishment and causal impact, and are missing for full orders that exceed observed depth. Conditional cost quantiles must always be read with full-coverage rates. Even the common covered population is a selected subset, not a capacity claim.

The daily depth groups use all sampled observations from the same day. They are descriptive labels, not lagged trading signals or market-cap groups. No strategy return has been recomputed. Three preselected dates do not cover market states representatively and do not constitute an out-of-sample validation.

## Reproduce and inspect

1. Use `pilot.spec.example.json` as a private spec; supply explicit native source paths and retain the unit/clock contract. The full run writes input SHA256s, schemas, code SHA256, row counts and exclusions to an external result directory. It fails on metadata-count/date discrepancies or changed source files.
2. Use `quant_market_data_platform.l2_views.iter_l2_batches` from the reviewed data-platform checkout (owner revision `8ca127c2d9304175fffc28e3d494dc1d0428a05a`). Its projection is reused; vendor normalization is not duplicated here. Add that checkout's `src` to `PYTHONPATH` alongside this repository's `src`.
3. Run from this repository:

```bash
PYTHONPATH="$MDP_SOURCE/src:src" uv run --locked --extra dev python \
  -m market_research.studies.ashare_execution_costs.pilot \
  --spec "$PILOT_SPEC" --output-root "$PILOT_OUTPUT"
```

`MDP_SOURCE` is the reviewed provider checkout; `PILOT_SPEC` is the private JSON; `PILOT_OUTPUT` is a **new**, absolute directory under the configured project data root. Never choose a source checkout or replace an existing run.

4. Set `EXECUTION_COST_PILOT_RUN` to the output directory and execute `pilot_review.ipynb` using a kernel with pandas, pyarrow, matplotlib, nbformat and nbclient. The notebook independently reconciles recorded measurements and renders conditional costs beside coverage and a fixed-population comparison. Keep executed outputs outside Git.

Next gates: point-in-time eligibility, price-limit states, lagged ADV/market cap, more predeclared dates, and actual orders before claiming calibrated impact or strategy capacity.

## Public aggregate release

The reviewed JSON is `web/public/data/execution-costs/pilot.json`; the [public topic](https://runchengxie.github.io/quant-market-research/research/execution-costs/) displays conditional costs, full coverage and a common-population comparison. The export allowlist excludes private paths, raw schemas, input specs and security/time identifiers. It retains input/code/source-summary SHA256s, aggregate counts and definitions. Permission is recorded as owner-confirmed on 2026-10-12; this is not a license for raw data or actual orders.

```bash
PYTHONPATH=src uv run --locked python \
  -m market_research.studies.ashare_execution_costs.publication \
  --summary "$PILOT_RUN/summary.json" --confirmed-on 2026-10-12 \
  --output web/public/data/execution-costs/pilot.json
```

Published reference-notional buy/sell P50 costs are 5.48/5.45 bp at CNY 10k, 8.48/8.37 bp at CNY 100k and 16.29/16.16 bp at CNY 1m. At CNY 1m, the full-coverage rates are only 64.41%/67.11%; at CNY 10m they are 12.49%/12.85%. Quantiles at each size are conditional on coverage and use different populations. The common subset has 8,480 snapshots; it is also selected, not a capacity estimate.
