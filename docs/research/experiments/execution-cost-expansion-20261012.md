# Trading costs: historical books, event fitness and strategy sensitivity

[Chinese report](execution-cost-expansion-20261012.zh-CN.md)

The study now contains ten selected L2 dates and 306,483 valid two-sided security-minute books. Median static costs for CNY 100k reference orders are 9.27/8.87 basis points for buys/sells; full ten-level coverage for CNY 1m orders is 62.12%/67.68%. These are conditional book measurements, not observed execution slippage.

Earlier data has different strengths by market. Among 106 securities observed on both 2021-01-04 and 2026-04-16, earlier minute coverage is 100%, versus 96.99% in the recent file. However, earlier Shanghai trades have no corresponding order records in this selected sample. Shenzhen candidate order-ID match rates are 99.68%/99.75%. Precise event replay is not established for either period.

An existing microcap diagnostic was rerun through the shared quant-platform simulator in eighteen capital/cost scenarios. This connects cost assumptions to constrained fills and cash, but does not establish verified net alpha or real strategy capacity.

## Data and measurement scope

Dates were fixed before inspecting cost distributions: 2021-01-04/15/29, 2025-01-02/15/27, 2026-04-07/16/24 and 2026-07-20. The first two windows use standardized monthly books; recent files use native books. The months, dates and securities are not probability samples. January seasonality and period differences are confounded; common-security comparisons also condition on survival.

Selection retains stock-like Shanghai/Shenzhen prefixes with numeric security code modulo 37 equal to zero. For each security/minute, choose the earliest timestamp, breaking ties by original row, before checking book validity. Continuous sessions are [09:30,11:30) and [13:00,14:57). There are 311,395 observed minute books and 4,912 one-sided exclusions; 306,483 valid books remain across 1,317 valid security-days. Minute coverage conditions on securities observed on that date, using 237 expected bins each; it is not an audit of all historically eligible stocks.

Clock profiles are explicit. Historical `time_ms` is relative to 09:30 and retains lunch, while native clocks use `HHMMSSmmm`. Preopening/closing boundary probes and selected-source checks corroborate these bindings; field aliases alone do not convert clocks. Source prices are cents and quantities shares. Sampled cumulative-turnover/volume/price scale checks are within [0.8,1.2], not exact cash reconciliation or a replacement for supplier specifications.

Static costs use the contemporaneous midpoint and include half-spread and displayed-depth consumption. Reference notional equals midpoint×analytical shares; fractional shares are permitted, and it is not a cash budget or executable round-lot order. Costs are missing when ten levels cannot fill the entire order. Taxes, latency, replenishment, queues and causal own-order impact are excluded. Do not add spread again.

The CNY 1m buy coverage is 43.56% in the low lagged-ADV group and 77.53% in the high group. Group labels use 20 prior daily sessions and available daily cross-section terciles, including Beijing in the reference cross-section. The books themselves exclude Beijing. ADV uses daily amount× 1000; market value uses prior circulating market value× 10000; volatility uses prior close/pre-close log returns. There are 2,481 valid books with incomplete ADV/volatility histories, retained as unavailable. Reconstructed daily valuations do not verify historical release-time availability. Group quantiles are descriptive, not a calibrated cost model or population confidence intervals.

## Order-flow fitness

The common-security audit retains all observed source events, including special records, and preserves source order. It separates raw-event duplicates, timestamp regressions, zero business indexes and positive-sequence regressions. The common valid-minute comparison contains 23,297 pairs; it is distinct from the broader common-security comparison.

| Common-sample stream | 2021-01-04 | 2026-04-16 |
| --- | ---: | ---: |
| Continuous order rows | 1,506,074 | 6,787,780 |
| Trade/event rows | 1,596,501 | 4,189,318 |
| Nonpositive-price event rows | 0 | 715,285 |
| Positive-price trade timestamp regressions | 0 | 64,245 |
| Positive business-sequence regressions in positive-price trades | unavailable | 22,694 |

Early preopening orders are separate: 25,785 selected rows with zero exact overlap with continuous orders. Reference lookup reports their union; it does not silently discard repeated or ambiguous candidate keys. Earlier keys have no channel, while native lookup includes channel. Presence does not authenticate order semantics or cancellation links. A field containing zeros does not provide a usable exchange sequence.

Within the recent selected sample, positive trade time regressions occur in both Shanghai (22,694) and Shenzhen (41,551). Shenzhen business indexes are zero; Shanghai positive indexes also regress. No original flow is reordered to hide these observations. Older standardized files being monotone does not prove original exchange order was preserved. Dynamic replay and causal impact remain unvalidated; supplier event dictionaries, cross-stream ordering and actual order feedback are still required.

## Existing-strategy comparison

The diagnostic spans 2025-01-03 to 2025-03-31, 56 sessions. Gross, assumed-fee and borrowed static-cost scenarios share the same public execution engine, 5% daily trading-amount participation limit,T+1 and price-limit flags. Prices are adjusted-close proxies and shares are fractional. Source release times, corporate actions and delisting settlement remain unverified. The original CNY 1m/5bp reference replay reproduced all 56 daily NAVs exactly; this validates reproduction, not those input assumptions.

Original 5 bp simulator costs are removed before replacement. Fee sensitivity assumes 1 bp inclusive commission each side, 5 bp seller stamp duty, zero minimum commission and no additional transfer fee. The seller-tax scenario records the [2023-08-28 tax reduction announcement](https://shanghai.chinatax.gov.cn/zcfw/zcfgk/yhs/202308/t468451.html); commission is an assumption, not a broker contract. Static costs are cash debits, not an intraday price/impact simulation.

Twelve baseline scenarios use the prior three-day cost anchors; six additional scenarios use the expanded CNY 100k/CNY 1m conditional medians. References include later 2026 observations, so they are counterfactual sensitivities, not an ex-ante 2025 cost model. They do not change with each order's actual size, depth or execution time.

| Initial capital | Gross terminal NAV | Assumed fees | Fees + expanded 100k costs | Fees + expanded 1m costs |
| --- | ---: | ---: | ---: | ---: |
| CNY 10m | 1.307825 | 1.305736 | 1.299470 | 1.291617 |
| CNY 100m | 1.307982 | 1.305893 | 1.299624 | 1.291767 |
| CNY 1bn | 1.299669 | 1.297823 | 1.292200 | 1.285138 |

All eighteen constrained runs maintain nonnegative daily cash. Gross modeled cumulative buy completion falls from 95.3% at CNY 10m to 68.6% at CNY 1bn; the ratio uses total executed/(executed+unfilled) order amounts, not terminal backlog. Mean one-way executed turnover is about 4.74% at CNY 10m and 4.31% at CNY 1bn. This differs from the separate 60% stress assumption. Cost changes alter later funded orders, so terminal-NAV differences are not just summed cash fees, and lower total unfilled amounts need not mean improved fillability.

Twelve frozen-path overlays replace fees on original fills while retaining holdings P&L and missed fills. They expose negative counterfactual cash rather than pretending feasible reexecution. The 250-session/60%-each-side cost-only stress separately reports linear expenditure and compounding; neither is realized strategy return or an annualized version of this 56-day diagnostic.

## Reproduction and next gates

[Study protocol and commands](../../../studies/ashare_execution_costs/README.md), [input example](../../../studies/ashare_execution_costs/expansion.spec.example.json), [source audit and measurement runner](../../../src/market_research/studies/ashare_execution_costs/expansion.py), [saved-output review](../../../src/market_research/studies/ashare_execution_costs/review.py), [notebook source](../../../studies/ashare_execution_costs/expansion_review.ipynb), and [strategy runner](../../../scripts/run_execution_cost_strategy.py) retain the methods. Resolve local roots from workspace settings and provide private source paths; do not replace previous outputs.

The private record retains input/code/engine SHA256s, source-stat checks, selected book/event ledgers, reference bytes, all eighteen aggregate daily ledgers and an executed notebook. Independent notebook checks reproduce pooled/daily quantiles, coverage masks, groups, paired counts, ledger identities and output hashes. Six bilingual SVGs have been inspected. Public JSON uses allowlists; raw records, security/time identifiers and private paths remain outside Git. Owner-confirmed aggregate publication permission is recorded as 2026-10-12.

Next work should prioritize Shenzhen event semantics and cancellation links, investigate native timestamp resets, add independent dates and PIT eligibility, then calibrate against actual orders. More data alone does not establish causal impact or executable capacity.
