# Overseas semiconductor histories: opening-gap association, no robust ETF improvement

The source gap recorded in the [earlier October 29 inventory](overseas-theme-20261029.md) was subsequently resolved for this bounded exploration. Yahoo histories passed daily consistency checks and three existing theme experiments actually ran. The clearest pooled association is with the SW semiconductor opening gap; it disappears after one additional A-share observation delay. Neither the post-open outcome nor 512480 next-open prediction shows a pooled MSE improvement whose descriptive interval excludes zero. These are retrospective results, not a trading signal or model promotion. [中文](overseas-theme-source-results-20261029.zh-CN.md)

## Acquired histories and review scope

| Symbol | Rows | First / last session | Missing / extra / duplicate | Price / OHLC errors |
| --- | --- | --- | --- | --- |
| ^SOX | 2721 | 2016-01-04 / 2026-10-28 | 0 / 0 / 0 | 0 / 0 |
| SMH | 2721 | 2016-01-04 / 2026-10-28 | 0 / 0 / 0 | 0 / 0 |
| SOXX | 2721 | 2016-01-04 / 2026-10-28 | 0 / 0 / 0 | 0 / 0 |
| NVDA | 2721 | 2016-01-04 / 2026-10-28 | 0 / 0 / 0 | 0 / 0 |
| AMD | 2721 | 2016-01-04 / 2026-10-28 | 0 / 0 / 0 | 0 / 0 |
| AVGO | 2721 | 2016-01-04 / 2026-10-28 | 0 / 0 / 0 | 0 / 0 |

Daily requests covered 2016-01-01 inclusive to 2026-10-29 exclusive. October 29 US bars are excluded. All six series matched all 2,721 XNYS sessions; holidays, early closes and America/New_York DST are recorded in the retained calendar schedule. Finite positive OHLC/Adj Close, OHLC bounds and nonnegative volume checks passed. Actions and provider columns were retained. This establishes internal consistency, not independent price validation. Each provider request succeeded on its first attempt; a local calendar-start error before any request was corrected to January 4.

Retrieval began `2026-10-29T15:45:09.750364+00:00` and ended `2026-10-29T15:45:20.221737+00:00`. Versions: Python 3.13.14, yfinance 1.4.1, pandas 3.0.6, exchange_calendars 4.13.2. Explicit request parameters were `interval="1d", start="2016-01-01", end="2026-10-29", auto_adjust=False, actions=True, repair=False, keepna=True, raise_errors=True, timeout=25`. The policy bounded failures to three attempts per symbol with 2/4-second backoff; no provider retry was needed.

Yahoo OHLC returned with `auto_adjust=False` still includes historical split adjustments: it is not the contemporaneous pre-split nominal price series. `Adj Close` additionally carries provider cash-distribution adjustments, a total-return proxy without independent reinvestment certification. Split events and adjustment-factor ranges are recorded externally. SOX uses `Close` in index points; SMH/SOXX use `Adj Close` in USD/share. NVDA, AMD and AVGO were acquired and audited but were not used in the three theme experiments. No index-constituent reconstruction is claimed.

## Completed experiment comparisons

The generating source revision is `5122f1abd54bc69037631a4d45f8e28c24a29647`, checked clean before and after export by the unchanged runner. Across the study the observed forecast span is **2020-01-02 through 2026-10-16**, capped by existing domestic/control inputs; later Yahoo bars do not extend that study. ETF folds start in 2021 after the 252-row minimum training requirement. Existing audited controls include the known 512480 suspension on 2021-03-26 and exclusion of crossed FX quotes.

The baseline is `global` (domestic lags/momentum/volatility, CSI300, FX and SPX); the augmented model is `theme_residual`. Annual expanding training fits the intercept and SPX beta using training rows only, with labels purged before each first test decision. Residualization is a linear reparameterization with SPX already included and establishes no causality. Delay 0 uses the assumed latest available completed US close; delay 1 shifts aligned sources by one A-share observation. Decision time is 08:45 Asia/Shanghai. Regular US close plus one hour, with DST, is an assumption rather than measured historical provider delivery. Ten-observation paired-block intervals are descriptive and unadjusted for multiple tests. Positive MSE gain means lower augmented mean squared error; all table entries are percentages of baseline MSE, not percentage-point returns.

| Theme | Target / outcome | Delay | n | MSE gain % | Descriptive 95% interval % |
| --- | --- | --- | --- | --- | --- |
| SOX | sw_semiconductor / gap | 0 | 1643 | 5.800 | [3.405, 8.945] |
| SOX | sw_semiconductor / post_open | 0 | 1643 | 0.103 | [-0.317, 0.455] |
| SOX | sw_semiconductor / gap | 1 | 1634 | -0.165 | [-0.485, 0.125] |
| SOX | sw_semiconductor / post_open | 1 | 1634 | -0.020 | [-0.454, 0.395] |
| SOX | 512480 / next_tradable_open | 0 | 1398 | -0.104 | [-0.762, 0.544] |
| SOX | 512480 / next_tradable_open | 1 | 1390 | -0.582 | [-1.421, 0.235] |
| SMH | sw_semiconductor / gap | 0 | 1643 | 5.600 | [3.400, 8.461] |
| SMH | sw_semiconductor / post_open | 0 | 1643 | 0.044 | [-0.278, 0.344] |
| SMH | sw_semiconductor / gap | 1 | 1634 | -0.202 | [-0.558, 0.143] |
| SMH | sw_semiconductor / post_open | 1 | 1634 | -0.072 | [-0.564, 0.392] |
| SMH | 512480 / next_tradable_open | 0 | 1398 | -0.083 | [-0.748, 0.537] |
| SMH | 512480 / next_tradable_open | 1 | 1390 | -0.679 | [-1.576, 0.195] |
| SOXX | sw_semiconductor / gap | 0 | 1643 | 6.007 | [3.402, 9.359] |
| SOXX | sw_semiconductor / post_open | 0 | 1643 | 0.109 | [-0.313, 0.483] |
| SOXX | sw_semiconductor / gap | 1 | 1634 | -0.202 | [-0.547, 0.103] |
| SOXX | sw_semiconductor / post_open | 1 | 1634 | -0.040 | [-0.494, 0.395] |
| SOXX | 512480 / next_tradable_open | 0 | 1398 | -0.140 | [-0.846, 0.555] |
| SOXX | 512480 / next_tradable_open | 1 | 1390 | -0.614 | [-1.407, 0.174] |

## Annual stability

SOX annual MSE gains (%), including negative years and incomplete 2026:

| Year | SW gap d0 | SW post-open d0 | SW gap d1 | SW post-open d1 | ETF d0 | ETF d1 |
| --- | --- | --- | --- | --- | --- | --- |
| 2020 | 3.049 | 0.107 | 0.359 | 0.025 | — | — |
| 2021 | 9.697 | 0.375 | -1.620 | 0.248 | 0.813 | -1.346 |
| 2022 | 5.923 | 0.213 | 0.079 | -0.367 | 0.376 | -1.278 |
| 2023 | -0.982 | 0.820 | -0.731 | -0.037 | 0.212 | 0.249 |
| 2024 | 1.090 | -0.087 | 0.092 | 0.267 | -0.078 | 0.215 |
| 2025 | 0.151 | -0.271 | -0.629 | 0.141 | -0.797 | 0.117 |
| 2026 | 14.767 | -0.075 | -0.013 | -0.348 | -0.650 | -1.141 |

The zero-delay gap gain is not uniform: 2023 is negative, 2024/2025 are small, and 2026 is much larger. SOX annual zero-delay gap intervals exclude zero positively only in 2020, 2021 and 2026; other years span zero. Annual tables and descriptive intervals for every proxy and outcome remain in external diagnostics. Proxy agreement on the pooled gap result is correlated robustness evidence, not three independent replications. Negative pooled ETF MSE results are retained even where a sign-based trading proxy improves.

## ETF turnover-cost and delay sensitivity

Mean return in bp per replay row below. Gross means the zero-cost scenario. The other columns charge 5/10/20/40 bp round-trip, implemented as half that amount per actual one-way position change. Baseline and augmented models are compared under the same scenario:

| Theme | Delay | Model | Gross mean bp/day | Net 5 bp | Net 10 bp | Net 20 bp | Net 40 bp |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SOX | 0 | global | 10.725 | 9.566 | 8.407 | 6.089 | 1.454 |
| SOX | 0 | theme_residual | 9.965 | 8.810 | 7.655 | 5.344 | 0.723 |
| SOX | 1 | global | 7.110 | 6.048 | 4.986 | 2.861 | -1.388 |
| SOX | 1 | theme_residual | 9.411 | 8.284 | 7.158 | 4.904 | 0.398 |
| SMH | 0 | global | 10.725 | 9.566 | 8.407 | 6.089 | 1.454 |
| SMH | 0 | theme_residual | 9.294 | 8.143 | 6.991 | 4.688 | 0.081 |
| SMH | 1 | global | 7.110 | 6.048 | 4.986 | 2.861 | -1.388 |
| SMH | 1 | theme_residual | 9.788 | 8.643 | 7.499 | 5.210 | 0.632 |
| SOXX | 0 | global | 10.725 | 9.566 | 8.407 | 6.089 | 1.454 |
| SOXX | 0 | theme_residual | 9.629 | 8.489 | 7.348 | 5.066 | 0.502 |
| SOXX | 1 | global | 7.110 | 6.048 | 4.986 | 2.861 | -1.388 |
| SOXX | 1 | theme_residual | 9.312 | 8.193 | 7.073 | 4.834 | 0.356 |

All replay scenarios contain 1,398 rows, including the delay-1 run whose MSE comparison has only 1,390 forecast rows. On replay rows without a prediction, the desired position defaults to cash; the holding guards may retain an existing position. These counts therefore describe different denominators. This behavior is preserved, not silently aligned away.

For SOX at zero delay, augmented gross mean is 9.965 versus baseline 10.725 bp/day, and 10-bp round-trip net mean is 7.655 versus 8.407. At delay 1 the corresponding augmented means are higher (9.411 versus 7.110 gross; 7.158 versus 4.986 net), despite worse MSE. Thus “no demonstrated robust ETF improvement” does not mean every trading proxy is negative. It means the pooled forecast loss, latency sensitivity, annual variation and arbitrary sign rule do not establish a stable deployable advantage. At 40 bp both SOX models have negative compounded return at both delays, including the delayed augmented case with positive arithmetic mean. Compounded returns, Sharpe, drawdowns, exposure and trade counts remain in full diagnostics.

The proxy is long/cash, retains holdings, respects next-session selling, charges terminal liquidation, and uses opening-limit and prior-ADV admission guards at a CNY 1 million budget and 1% prior ADV. Those assumptions do not prove execution, liquidity or capacity. No fills, auction queue, real slippage, untouched holdout or tradable opening-gap capture were verified.

## Provenance and reproduction

The retained owner task is `quant-market-data-platform/research/tasks/overseas-theme-source-20261029` relative to its configured data root; study results are in `quant-market-research/tasks/overseas-theme-source-20261029`. `source_receipt.json` contains retrieval times, parameters, versions, per-symbol file SHA256 and QA; `price_semantics_review.json` records units/actions. `artifact_receipt.json` hashes the retained files. `existing_controls_inventory.json` records each reused control's coverage/hash. No vendor rows, raw prices, private absolute paths or daily predictions are copied into this repository.

The external `reproduce_source_probe.py` records the exact acquisition procedure; rerunning it can replace its fixed task files, so preserve receipts and choose a fresh external task directory before a new retrieval. The external `reproduce_experiment.py` records manifest generation and the three actual runner invocations; its fixed output paths are not a safe overwrite interface. Source acquisition remains the data owner's responsibility; the public research runner only consumes reviewed inputs. Current normalized theme-file hashes and original raw-file hashes are connected by the external acquisition/normalization scripts and artifact receipt.

| Theme | Input manifest SHA256 |
| --- | --- |
| SOX | f29e702cfbfb8476c51136e31cc06ce0ef9a5d52e3334f2893cf0276a30938ca |
| SMH | 7e6dfd992ececd3c722394d433bc6144647553b3e6b21d74c93aff93b9b65319 |
| SOXX | e7e0a4688ef714c4217e26aaf5cb73b9f43741674369ddeba4501c237b7f2ed8 |

```bash
# Resolve these roots from machine-local workspace settings; do not store credentials here.
export OWNER_TASK="$DATA_ROOT/quant/quant-market-data-platform/research/tasks/overseas-theme-source-20261029"
export STUDY_TASK="$DATA_ROOT/quant/quant-market-research/tasks/overseas-theme-source-20261029"
# From a clean checkout of 5122f1abd54bc69037631a4d45f8e28c24a29647:
PYTHONPATH=src python -m market_research.studies.overseas_leadlag.theme \
  --manifest "$STUDY_TASK/sox_reviewed_manifest.json" \
  --output "$STUDY_TASK/new-sox-reproduction"
```

Substitute `smh_reviewed_manifest.json` or `soxx_reviewed_manifest.json` and a fresh output directory for the two ETF-proxy experiments. The command requires an environment containing the existing runner dependencies. All consumed file hashes, manifest bytes and source revision are rechecked by the runner; the manifest digest is recorded in each `research_diagnostics.json`. The generating Git SHA above identifies the actual code run, independently of the later documentation commit. The final documentation commit is recorded in Git and the integration report.

## Alpaca and remaining limitations

Alpaca was **not tested**. Only presence flags for `APCA_API_KEY_ID`, `APCA_API_SECRET_KEY`, `ALPACA_API_KEY` and `ALPACA_SECRET_KEY` were checked; all were absent. Inspected project/shared guides did not identify an already configured loading interface. No credential contents, login, account, subscription or trading operation was accessed.

Official historical-bars documentation specifies pagination (`next_page_token`), adjustment choices (`raw`, `split`, `dividend`, `spin-off`, `all`), and feed selection. The FAQ distinguishes single-exchange IEX from consolidated SIP and describes account-dependent historical access. Those docs do not establish this user's entitlement, actual symbol coverage or returned prices. A future account-backed test must explicitly verify feed, adjustment, pagination, coverage and daily-bar timestamp semantics; ^SOX availability cannot be assumed from stock-symbol support.

The results retain `retrospective_exploratory` and `historical_pit_certified: false`. Current retrieval/final-vintage split and distribution adjustments are not historical retrieval vintages. No untouched holdout, historical universe-selection proof, independent provider cross-check, multiplicity-adjusted inference, actual delivery latency or fill/capacity proof exists. No production model, frozen forward-v1 rule, website selection, shared current/latest pointer or production data was changed.

Primary provider documentation checked for this exploration:

- [yfinance PriceHistory parameters](https://ranaroussi.github.io/yfinance/reference/yfinance.price_history.html)
- [Alpaca historical stock bars](https://docs.alpaca.markets/us/reference/stockbars)
- [Alpaca market-data FAQ](https://docs.alpaca.markets/us/docs/market-data-faq)
