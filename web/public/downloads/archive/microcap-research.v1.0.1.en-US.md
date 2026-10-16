# Small- and micro-cap research: evidence, methods and open questions

Public evidence review: 2026-10-16. This editorial date is not a data cutoff. The portfolio snapshot was generated on 2026-09-16, covering 2015-01-01 to 2026-07-31; each appendix retains its own dates. Stored exclusion results were reviewed without rerunning that experiment. Separately identified window checks do not overwrite historical outputs.

This report assembles the reviewed public record. It is not an inventory of every private experiment or a statement of strategy readiness. Missing comparisons remain open questions. All figures are historical, modeled or source-reported within their stated scope.

## Current conclusion

The clearest micro-cap finding is substantial downside risk and potentially long recovery waits. Returns remain sensitive to eligibility, missing quotes, execution clocks and portfolio construction. Low turnover has historical conditional associations, but an independent causal premium and practical capacity have not been established.

The fixed monthly low-turnover simulation reports net annual returns of 3.52%, 5.33% and 7.60% for 20-, 60- and 120-session windows. The new 120-session run gives 4.22% with 90 valid observations; a same-input sensitivity with 45 gives 6.26%. The threshold changes the result but does not identify the historical method or fully explain the gap. These inspected figures are not a prospective ranking.

## Contents

1. Research map and evidence status
2. Comparable portfolio definitions
3. Turnover-window comparison
4. Definition × rebalance matrix
5. Research history and coverage register
6. All published snapshot table families
7. Revisions and limits
8. Open questions and resumption criteria
9. Public methodology appendices and sources

## Report version and changes

Version 1.0.1 · reviewed 2026-10-16. This update adds the 45-observation 120-session sensitivity and clarifies historical fee and capital provenance.

Added a same-input 120-session sensitivity with a 45-observation minimum, clarifying that warm-up support changes the result but does not recover the historical method. Clarified that 10 bp is reported in dated research notes, the primary exclusion matrix is not verified at CNY 100 million, and original code identity remains unknown.

[Download fixed version 1.0.1](https://runchengxie.github.io/quant-market-research/downloads/archive/microcap-research.v1.0.1.en-US.md)

[Previous fixed version 1.0.0](https://runchengxie.github.io/quant-market-research/downloads/archive/microcap-research.v1.0.0.en-US.md)

Each fixed Markdown edition is preserved independently; linked online chart assets are not a complete frozen website snapshot.

## Research map

### What did the smallest-stock baskets return and lose?

**Historical reconstruction · data audit**

Drawdowns and time below prior highs are central findings. Some early returns and missing-price treatments remain under review.

**Sample and construction：** N = 50 / 100 / 200 / 400 / 800; early 2008–2014 history is separate from the cleaned 2015+ sample.

**Open question：** How much do delistings, missing quotes and company actions change the result?

[Explore historical charts](https://runchengxie.github.io/quant-market-research/research/microcap/#microcap-history-evidence)

### Is the return primarily a size exposure?

**Historical factor evidence**

Style-factor tests help describe size exposure. Long-short factor returns and long-only micro-cap portfolios answer different questions.

**Sample and construction：** 18-year style research; see each factor’s source, sign convention and construction.

**Open question：** Does the result survive removing the smallest market-cap tail under the same ledger?

[Explore size-factor evidence](https://runchengxie.github.io/quant-market-research/research/style-factors-18y/?factor=size)

### What does low turnover add?

**Conditional association · exploratory**

The historical return spread changes with controls. Neither an independent premium nor stable synergy has been established.

**Sample and construction：** Latest common cross-sectional sample: 86 months, 2019-05 to 2026-06. One completed forward month in the published record.

**Open question：** Is avoiding the high-turnover tail enough, and does the relation persist prospectively?

[Read controls, intervals and execution](https://runchengxie.github.io/quant-market-research/research/factors/low-turnover/)

### How sensitive is the result to portfolio rules?

**Historical sensitivity comparison**

Turnover-window length changes return, drawdown and turnover in a fixed portfolio setup. It is not a fresh out-of-sample selection.

**Sample and construction：** 20 / 60 / 120 prior trading sessions; monthly, 40 target names and a 60-name buffer.

**Open question：** Can the ordering repeat under a frozen prospective rule and consistent share accounting?

[Compare the three windows](https://runchengxie.github.io/quant-market-research/research/microcap/#microcap-window-evidence)

### Could the portfolio actually trade?

**Simulation diagnostic · costs uncalibrated**

A public execution ledger tests participation limits, blocked trades and cash. Its short sample cannot establish profitable capacity.

**Sample and construction：** Separate short-sample diagnostic: 5% participation, T+1, daily price limits and 5 bp assumed cost.

**Open question：** Can fills, cash, corporate actions and calibrated impact reconcile in one ledger?

[Read the execution diagnostic](https://runchengxie.github.io/quant-market-research/docs/research/experiments/microcap-execution-diagnostic-20260928/)

### Are small stocks equally liquid across markets?

**Exploratory cross-market comparison**

Market-cap groups reveal differences in traded value and coverage. Aggregate trading activity is not a capacity estimate.

**Sample and construction：** Latest available observations by market; currencies, dates and eligibility vary.

**Open question：** Can currencies, trading calendars and eligibility be aligned before cost comparisons?

[Compare market coverage and liquidity](https://runchengxie.github.io/quant-market-research/research/liquidity/#market-profiles)

## Keep portfolio definitions separate

| Object | Formation and return basis | Purpose and limit |
| --- | --- | --- |
| Vendor reference index | Provider points and available membership; dividend conventions need review | Reference comparison, not an executable account |
| Smallest-N reconstruction | Post-close ranking, next-session close execution, following close valuation; early and cleaned sources kept separate | Historical return and risk with explicit missing-price policies |
| Low-turnover candidate | Monthly; 40 target names, 60-name buffer, 10 bp fee in the window comparison | Portfolio sensitivity; not the cross-sectional low-minus-high spread |
| Small-cap plus low-turnover composite | Definition × cadence grid from a historical weight-level screening engine | Requires consistent share-ledger confirmation before selection |
| Public execution diagnostic | Separate continuous holdings and cash; 5% participation, T+1, price limits, assumed 5 bp cost | Short-sample mechanism check; not full historical performance or certified capacity |

## Does smoothing turnover change the result?

The original published snapshot shows higher returns and smaller drawdowns for longer windows. A new documented run matches 20/60 sessions but gives 4.22% for 120, against the original 7.60%; that return ordering is not reproduced. Both versions are retained below.

2015–2026 daily-data study; monthly formation, 40 target names, 60-name holding buffer and 10 bp trading fee. Values come directly from window_sensitivity in the public exploratory snapshot dated 2026-09-16. The snapshot coverage ends on 2026-07-31. This panel does not reuse the separate small-cap-plus-low-turnover composite results.

![Does smoothing turnover change the result?](https://runchengxie.github.io/quant-market-research/downloads/microcap-windows.en-US.svg)

| Trading-day lookback | Net annual return | Maximum drawdown | Sharpe | Annual trading turnover |
| --- | --- | --- | --- | --- |
| 20 | 3.52% | -65.01% | 0.264 | 11.59× |
| 60 | 5.33% | -52.39% | 0.331 | 6.79× |
| 120 | 7.60% | -45.61% | 0.411 | 4.47× |

Historical, repeatedly inspected evidence; no independent final holdout or broker-calibrated impact estimate. The daily traded-value proxy and simulator assumptions limit implementation claims. Do not interpret these bars as an executable return forecast.

### Window reproduction check · 2026-10-16

The 20- and 60-session runs match all four rounded published metrics. For 120 sessions, the completed 90-observation run gives 4.22% net annual return versus 7.60% published. A same-input sensitivity requiring 45 observations gives 6.26%. The support threshold changes the result, but does not establish which run matches the historical method or fully resolve the gap.

Both are new observations, not recovered historical executions. They use 2,778 return sessions over 2015-01-01–2026-07-31, current input vintage and retained monthly controls. Monthly, 40 targets, 60-name buffer, 180-day listing minimum and an assumed 10 bp per traded notional; continuous weights, without lot-size, market-impact or capacity calibration. The 120-session sensitivity changes only minimum support from 90 observations (75% of window) to 45.

The completed receipts bind code, locked dependencies and before/after input hashes; counts match the retained cache but do not prove historical byte identity. ST history is reconstructed and not revision-safe. The 45-observation version first trades 2015-04-01; the 90-observation version first trades 2015-06-01. The original support rule, historical 20/120 daily artifacts and joint original runtime receipt remain missing. The fee is an assumed replay setting, not authentication of the historical run. Treat the sensitivity as evidence that warm-up affects results, not proof that it explains the original gap.

90-observation run: low-turnover-windows-9d92f18f-b2d9-43d0-924b-237572f635a3; driver SHA-256 8316cdd8c9416f2c7cc5e35d43b14337967590c9f539051c37170f47f9568483. 45-observation sensitivity: low-turnover-windows-c7c46929-0fe5-4285-837b-986169908b1b; variant SHA-256 39f76f268df461ef838c192618e6821ef5ec5d312e18fccb0787df9f93b29d9f. Both runs completed with unchanged input hashes.

| Window (sessions) | Vintage | Net annual % | Sharpe | Net drawdown % | Annual turnover × |
| --- | --- | --- | --- | --- | --- |
| 20 | Published snapshot | 3.519612 | 0.263731 | -65.009288 | 11.592836 |
| 20 | New run | 3.519612 | 0.263731 | -65.009288 | 11.592836 |
| 60 | Published snapshot | 5.334535 | 0.330517 | -52.389378 | 6.785942 |
| 60 | New run | 5.334535 | 0.330517 | -52.389378 | 6.785942 |
| 120 | Published snapshot | 7.601898 | 0.411345 | -45.607451 | 4.474725 |
| 120 | New run (90-observation minimum) | 4.224513 | 0.289023 | -58.259876 | 4.440654 |
| 120 | Same-input sensitivity (45-observation minimum) | 6.255876 | 0.361123 | -58.631610 | 4.633872 |

## Turnover definition × rebalance cadence

Sixteen historical screening configurations are preserved here to show how much was explored. These small-cap-plus-low-turnover composite results use a weight-level screening engine. They are a different portfolio from the three-window low-turnover chart above.

Net annual return, percent, from the 2026-09-16 exploratory snapshot. Shading encodes historical return, not confidence. All cells need consistent share-ledger confirmation before cadence or parameter selection. The previously inspected 2024–2026 segment is descriptive only.

| Definition | Weekly | Biweekly | Monthly | Quarterly |
| --- | --- | --- | --- | --- |
| 20-day mean | 8.68% | 17.07% | 7.81% | 7.35% |
| 60-day mean | 9.56% | 19.00% | 7.73% | 8.33% |
| 60-day median | 9.52% | 18.60% | 7.91% | 9.16% |
| 120-day mean | 13.20% | 21.18% | 13.88% | 10.53% |

## What survives excluding the smallest stocks?

Recovered historical outputs · reviewed 2026-10-16 · no research rerun

[Download reviewed aggregate JSON, including all 288 yearly rows and source hashes](https://runchengxie.github.io/quant-market-research/data/microcap_exclusion_review.json)

Dependence on the smallest stocks varies by candidate. With a buffer and equal weights, excluding 30% changes small-cap net annual return from 5.24% to −2.17%, low turnover from 5.33% to 7.76%, and the composite from 11.28% to 9.71%. These are portfolio sensitivities, not evidence of a causal premium.

Weighting matters: value-weighted low turnover is negative at every exclusion level, while the composite stays positive under both weighting modes. The 10% composite peak is an inspected grid result, not a validated optimum.

Buffers lower turnover in all 24 candidate comparisons, but improve net annual return in only 8. Lower trading does not guarantee a better net result. Full tables retain every reviewed comparison.

Input scope 2015-01-01–2026-07-31; 138 monthly formation dates, 2015-02-27–2026-07-31. Candidate comparisons share 2,778 return sessions. The input start is not the first return date; exact daily return endpoints are not retained in these tables.

Exclusions remove 0%, 10%, 20% or 30% of eligible names ranked by formation-date total market capitalization, not that share of market value. The current protocol reconstructs formation-date A-share eligibility with 180 listed days, positive traded amount, non-ST status and finite positive capitalization. Signals are recomputed after exclusion. The protocol specifies 40 monthly targets and a 60-name retention band, with weighting on the same selected names; historical run parameters are not fully authenticated.

Historical fees were not recorded in the retained manifest; the current protocol default of 10 bp is not an authenticated historical fee. Both historical owner-code revisions are unknown. Net results are retained post-cost outputs, not independently reproduced performance.

Development has 2,154 sessions through 2023; the later 2024–July 2026 sample has 624 and has been inspected. Era returns are compounded from retained yearly rows. Registration-period differences are descriptive and do not identify a policy effect.

Capacity rows use a separate cash-ledger engine with modeled participation, lots, T+1 and delayed execution. They are not a haircut on the weight-engine returns. Exact capacity return dates and observation counts are unbound; simulated results do not certify live capacity.

Returns and drawdowns: %. Cost drag: percentage points. Sharpe: unitless. Turnover: annual multiples; fill and cash: %. All chart facets use the same linear scale and include zero.

![Net annual return across exclusions](https://runchengxie.github.io/quant-market-research/downloads/microcap-exclusions.en-US.svg)

<details>
<summary>Buffer comparison · 48 rows</summary>

| Candidate | Excluded names | Weight | Buffer | Gross annual % | Net annual % | Turnover ×/year | Cost drag pp | Net Sharpe | Net drawdown % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Small cap | 0% | Equal weight | No buffer | 6.351 | 5.846 | 4.776 | 0.505 | 0.342 | -60.133 |
| Small cap | 0% | Value weight | No buffer | 3.639 | 3.197 | 4.282 | 0.442 | 0.254 | -59.826 |
| Small cap | 0% | Equal weight | Buffered | 5.567 | 5.240 | 3.114 | 0.327 | 0.323 | -63.136 |
| Small cap | 0% | Value weight | Buffered | 3.082 | 2.787 | 2.867 | 0.295 | 0.239 | -62.041 |
| Low turnover | 0% | Equal weight | No buffer | 5.235 | 4.342 | 8.564 | 0.893 | 0.294 | -56.024 |
| Low turnover | 0% | Value weight | No buffer | -7.592 | -8.400 | 8.806 | 0.807 | -0.220 | -71.376 |
| Low turnover | 0% | Equal weight | Buffered | 6.047 | 5.325 | 6.866 | 0.722 | 0.329 | -57.223 |
| Low turnover | 0% | Value weight | Buffered | -4.597 | -5.283 | 7.229 | 0.685 | -0.083 | -65.405 |
| Composite | 0% | Equal weight | No buffer | 12.570 | 11.506 | 9.536 | 1.064 | 0.512 | -61.885 |
| Composite | 0% | Value weight | No buffer | 15.592 | 14.406 | 10.357 | 1.186 | 0.597 | -51.577 |
| Composite | 0% | Equal weight | Buffered | 12.099 | 11.278 | 7.377 | 0.821 | 0.509 | -61.285 |
| Composite | 0% | Value weight | Buffered | 14.387 | 13.472 | 8.068 | 0.915 | 0.575 | -51.110 |
| Small cap | 10% | Equal weight | No buffer | 7.475 | 6.732 | 6.969 | 0.743 | 0.374 | -60.166 |
| Small cap | 10% | Value weight | No buffer | 3.436 | 2.883 | 5.382 | 0.553 | 0.241 | -61.384 |
| Small cap | 10% | Equal weight | Buffered | 6.793 | 6.288 | 4.760 | 0.505 | 0.360 | -61.897 |
| Small cap | 10% | Value weight | Buffered | 2.594 | 2.236 | 3.519 | 0.359 | 0.216 | -63.687 |
| Low turnover | 10% | Equal weight | No buffer | 6.599 | 5.690 | 8.613 | 0.909 | 0.345 | -55.719 |
| Low turnover | 10% | Value weight | No buffer | -3.419 | -4.284 | 9.029 | 0.865 | -0.047 | -59.980 |
| Low turnover | 10% | Equal weight | Buffered | 7.420 | 6.694 | 6.817 | 0.726 | 0.383 | -55.000 |
| Low turnover | 10% | Value weight | Buffered | -2.258 | -2.960 | 7.240 | 0.703 | 0.007 | -53.841 |
| Composite | 10% | Equal weight | No buffer | 19.517 | 18.239 | 10.794 | 1.278 | 0.700 | -54.440 |
| Composite | 10% | Value weight | No buffer | 18.397 | 17.131 | 10.792 | 1.266 | 0.670 | -55.060 |
| Composite | 10% | Equal weight | Buffered | 17.574 | 16.567 | 8.635 | 1.006 | 0.658 | -54.191 |
| Composite | 10% | Value weight | Buffered | 16.222 | 15.228 | 8.627 | 0.994 | 0.619 | -55.176 |
| Small cap | 20% | Equal weight | No buffer | 3.351 | 2.592 | 7.400 | 0.759 | 0.232 | -64.366 |
| Small cap | 20% | Value weight | No buffer | 1.614 | 1.058 | 5.508 | 0.556 | 0.169 | -61.705 |
| Small cap | 20% | Equal weight | Buffered | 1.926 | 1.397 | 5.220 | 0.529 | 0.189 | -66.991 |
| Small cap | 20% | Value weight | Buffered | 0.759 | 0.387 | 3.714 | 0.372 | 0.143 | -63.866 |
| Low turnover | 20% | Equal weight | No buffer | 5.741 | 4.852 | 8.488 | 0.889 | 0.314 | -59.625 |
| Low turnover | 20% | Value weight | No buffer | -2.873 | -3.701 | 8.595 | 0.828 | -0.025 | -59.436 |
| Low turnover | 20% | Equal weight | Buffered | 7.438 | 6.728 | 6.663 | 0.710 | 0.384 | -54.269 |
| Low turnover | 20% | Value weight | Buffered | -1.761 | -2.437 | 6.934 | 0.676 | 0.027 | -57.333 |
| Composite | 20% | Equal weight | No buffer | 16.362 | 15.130 | 10.692 | 1.232 | 0.619 | -58.902 |
| Composite | 20% | Value weight | No buffer | 14.584 | 13.388 | 10.539 | 1.196 | 0.569 | -60.380 |
| Composite | 20% | Equal weight | Buffered | 15.319 | 14.333 | 8.621 | 0.986 | 0.597 | -59.170 |
| Composite | 20% | Value weight | Buffered | 13.727 | 12.772 | 8.468 | 0.955 | 0.552 | -59.803 |
| Small cap | 30% | Equal weight | No buffer | -0.657 | -1.402 | 7.548 | 0.744 | 0.082 | -69.257 |
| Small cap | 30% | Value weight | No buffer | -1.929 | -2.467 | 5.532 | 0.539 | 0.026 | -69.366 |
| Small cap | 30% | Equal weight | Buffered | -1.634 | -2.170 | 5.483 | 0.536 | 0.051 | -71.917 |
| Small cap | 30% | Value weight | Buffered | -1.938 | -2.311 | 3.831 | 0.373 | 0.031 | -69.748 |
| Low turnover | 30% | Equal weight | No buffer | 6.931 | 6.047 | 8.345 | 0.884 | 0.358 | -54.224 |
| Low turnover | 30% | Value weight | No buffer | 0.240 | -0.585 | 8.299 | 0.825 | 0.102 | -53.030 |
| Low turnover | 30% | Equal weight | Buffered | 8.449 | 7.756 | 6.444 | 0.693 | 0.420 | -50.942 |
| Low turnover | 30% | Value weight | Buffered | -0.178 | -0.841 | 6.683 | 0.663 | 0.092 | -56.328 |
| Composite | 30% | Equal weight | No buffer | 11.072 | 9.896 | 10.681 | 1.176 | 0.467 | -61.097 |
| Composite | 30% | Value weight | No buffer | 10.236 | 9.090 | 10.492 | 1.146 | 0.443 | -61.776 |
| Composite | 30% | Equal weight | Buffered | 10.641 | 9.707 | 8.504 | 0.934 | 0.463 | -59.813 |
| Composite | 30% | Value weight | Buffered | 9.508 | 8.611 | 8.251 | 0.897 | 0.430 | -59.568 |

</details>

<details>
<summary>Development and inspected later sample · 48 rows</summary>

| Candidate | Excluded names | Weight | Buffer | Era | Sessions | Net annual % | Cumulative % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Small cap | 0% | Equal weight | Buffered | Development through 2023 | 2154 | 3.171 | 30.581 |
| Small cap | 0% | Equal weight | Buffered | Inspected 2024–July 2026 | 624 | 12.707 | 34.475 |
| Small cap | 0% | Value weight | Buffered | Development through 2023 | 2154 | 0.817 | 7.200 |
| Small cap | 0% | Value weight | Buffered | Inspected 2024–July 2026 | 624 | 9.891 | 26.308 |
| Small cap | 10% | Equal weight | Buffered | Development through 2023 | 2154 | 3.803 | 37.582 |
| Small cap | 10% | Equal weight | Buffered | Inspected 2024–July 2026 | 624 | 15.333 | 42.368 |
| Small cap | 10% | Value weight | Buffered | Development through 2023 | 2154 | -0.408 | -3.434 |
| Small cap | 10% | Value weight | Buffered | Inspected 2024–July 2026 | 624 | 11.912 | 32.137 |
| Small cap | 20% | Equal weight | Buffered | Development through 2023 | 2154 | 0.715 | 6.275 |
| Small cap | 20% | Equal weight | Buffered | Inspected 2024–July 2026 | 624 | 3.790 | 9.650 |
| Small cap | 20% | Value weight | Buffered | Development through 2023 | 2154 | -1.059 | -8.696 |
| Small cap | 20% | Value weight | Buffered | Inspected 2024–July 2026 | 624 | 5.540 | 14.283 |
| Small cap | 30% | Equal weight | Buffered | Development through 2023 | 2154 | -4.008 | -29.504 |
| Small cap | 30% | Equal weight | Buffered | Inspected 2024–July 2026 | 624 | 4.447 | 11.375 |
| Small cap | 30% | Value weight | Buffered | Development through 2023 | 2154 | -4.748 | -34.021 |
| Small cap | 30% | Value weight | Buffered | Inspected 2024–July 2026 | 624 | 6.591 | 17.124 |
| Low turnover | 0% | Equal weight | Buffered | Development through 2023 | 2154 | 4.001 | 39.836 |
| Low turnover | 0% | Equal weight | Buffered | Inspected 2024–July 2026 | 624 | 10.027 | 26.697 |
| Low turnover | 0% | Value weight | Buffered | Development through 2023 | 2154 | -8.634 | -53.784 |
| Low turnover | 0% | Value weight | Buffered | Inspected 2024–July 2026 | 624 | 7.259 | 18.950 |
| Low turnover | 10% | Equal weight | Buffered | Development through 2023 | 2154 | 5.103 | 53.029 |
| Low turnover | 10% | Equal weight | Buffered | Inspected 2024–July 2026 | 624 | 12.372 | 33.488 |
| Low turnover | 10% | Value weight | Buffered | Development through 2023 | 2154 | -5.541 | -38.568 |
| Low turnover | 10% | Value weight | Buffered | Inspected 2024–July 2026 | 624 | 6.501 | 16.878 |
| Low turnover | 20% | Equal weight | Buffered | Development through 2023 | 2154 | 5.515 | 58.225 |
| Low turnover | 20% | Equal weight | Buffered | Inspected 2024–July 2026 | 624 | 11.025 | 29.561 |
| Low turnover | 20% | Value weight | Buffered | Development through 2023 | 2154 | -5.011 | -35.561 |
| Low turnover | 20% | Value weight | Buffered | Inspected 2024–July 2026 | 624 | 6.995 | 18.225 |
| Low turnover | 30% | Equal weight | Buffered | Development through 2023 | 2154 | 6.785 | 75.266 |
| Low turnover | 30% | Equal weight | Buffered | Inspected 2024–July 2026 | 624 | 11.176 | 29.997 |
| Low turnover | 30% | Value weight | Buffered | Development through 2023 | 2154 | -3.061 | -23.332 |
| Low turnover | 30% | Value weight | Buffered | Inspected 2024–July 2026 | 624 | 7.219 | 18.840 |
| Composite | 0% | Equal weight | Buffered | Development through 2023 | 2154 | 9.301 | 113.860 |
| Composite | 0% | Equal weight | Buffered | Inspected 2024–July 2026 | 624 | 18.384 | 51.876 |
| Composite | 0% | Value weight | Buffered | Development through 2023 | 2154 | 12.320 | 169.948 |
| Composite | 0% | Value weight | Buffered | Inspected 2024–July 2026 | 624 | 17.540 | 49.209 |
| Composite | 10% | Equal weight | Buffered | Development through 2023 | 2154 | 17.035 | 283.665 |
| Composite | 10% | Equal weight | Buffered | Inspected 2024–July 2026 | 624 | 14.965 | 41.246 |
| Composite | 10% | Value weight | Buffered | Development through 2023 | 2154 | 15.961 | 254.585 |
| Composite | 10% | Value weight | Buffered | Inspected 2024–July 2026 | 624 | 12.733 | 34.552 |
| Composite | 20% | Equal weight | Buffered | Development through 2023 | 2154 | 14.318 | 213.873 |
| Composite | 20% | Equal weight | Buffered | Inspected 2024–July 2026 | 624 | 14.386 | 39.489 |
| Composite | 20% | Value weight | Buffered | Development through 2023 | 2154 | 12.800 | 179.964 |
| Composite | 20% | Value weight | Buffered | Inspected 2024–July 2026 | 624 | 12.677 | 34.387 |
| Composite | 30% | Equal weight | Buffered | Development through 2023 | 2154 | 8.368 | 98.759 |
| Composite | 30% | Equal weight | Buffered | Inspected 2024–July 2026 | 624 | 14.457 | 39.705 |
| Composite | 30% | Value weight | Buffered | Development through 2023 | 2154 | 7.227 | 81.566 |
| Composite | 30% | Value weight | Buffered | Inspected 2024–July 2026 | 624 | 13.526 | 36.907 |

</details>

<details>
<summary>Descriptive registration periods · 72 rows</summary>

| Candidate | Excluded names | Weight | Buffer | Period | Sessions | Net period % | Net annual % | Sharpe | Drawdown % | Mean daily turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Composite | 0% | Equal weight | Buffered | Full registration | 838 | 27.144 | 7.489 | 0.385 | -47.930 | 0.028 |
| Composite | 0% | Value weight | Buffered | Full registration | 838 | 36.832 | 9.889 | 0.451 | -43.563 | 0.032 |
| Composite | 10% | Equal weight | Buffered | Full registration | 838 | 64.740 | 16.197 | 0.614 | -44.521 | 0.031 |
| Composite | 10% | Value weight | Buffered | Full registration | 838 | 55.816 | 14.267 | 0.566 | -44.494 | 0.031 |
| Composite | 20% | Equal weight | Buffered | Full registration | 838 | 61.480 | 15.501 | 0.606 | -44.278 | 0.033 |
| Composite | 20% | Value weight | Buffered | Full registration | 838 | 53.020 | 13.647 | 0.557 | -43.987 | 0.032 |
| Composite | 30% | Equal weight | Buffered | Full registration | 838 | 48.094 | 12.534 | 0.530 | -40.837 | 0.034 |
| Composite | 30% | Value weight | Buffered | Full registration | 838 | 43.501 | 11.473 | 0.501 | -40.402 | 0.033 |
| Low turnover | 0% | Equal weight | Buffered | Full registration | 838 | 23.004 | 6.424 | 0.361 | -39.813 | 0.029 |
| Low turnover | 0% | Value weight | Buffered | Full registration | 838 | 1.159 | 0.347 | 0.129 | -27.025 | 0.032 |
| Low turnover | 10% | Equal weight | Buffered | Full registration | 838 | 28.917 | 7.937 | 0.420 | -30.750 | 0.028 |
| Low turnover | 10% | Value weight | Buffered | Full registration | 838 | 8.138 | 2.381 | 0.216 | -24.066 | 0.027 |
| Low turnover | 20% | Equal weight | Buffered | Full registration | 838 | 30.219 | 8.264 | 0.430 | -33.963 | 0.026 |
| Low turnover | 20% | Value weight | Buffered | Full registration | 838 | 9.738 | 2.834 | 0.235 | -23.681 | 0.024 |
| Low turnover | 30% | Equal weight | Buffered | Full registration | 838 | 32.808 | 8.907 | 0.451 | -36.031 | 0.025 |
| Low turnover | 30% | Value weight | Buffered | Full registration | 838 | 12.776 | 3.682 | 0.271 | -22.972 | 0.023 |
| Small cap | 0% | Equal weight | Buffered | Full registration | 838 | 21.238 | 5.962 | 0.349 | -40.716 | 0.013 |
| Small cap | 0% | Value weight | Buffered | Full registration | 838 | 15.207 | 4.349 | 0.302 | -29.989 | 0.011 |
| Small cap | 10% | Equal weight | Buffered | Full registration | 838 | 46.972 | 12.277 | 0.581 | -30.945 | 0.014 |
| Small cap | 10% | Value weight | Buffered | Full registration | 838 | 30.621 | 8.364 | 0.475 | -25.298 | 0.010 |
| Small cap | 20% | Equal weight | Buffered | Full registration | 838 | 10.468 | 3.039 | 0.245 | -28.735 | 0.016 |
| Small cap | 20% | Value weight | Buffered | Full registration | 838 | 11.232 | 3.253 | 0.257 | -24.300 | 0.011 |
| Small cap | 30% | Equal weight | Buffered | Full registration | 838 | 7.768 | 2.275 | 0.213 | -28.054 | 0.016 |
| Small cap | 30% | Value weight | Buffered | Full registration | 838 | 10.703 | 3.105 | 0.252 | -25.468 | 0.011 |
| Composite | 0% | Equal weight | Buffered | Before registration pilot | 1073 | 106.170 | 18.522 | 0.690 | -52.138 | 0.032 |
| Composite | 0% | Value weight | Buffered | Before registration pilot | 1073 | 83.995 | 15.396 | 0.608 | -51.110 | 0.034 |
| Composite | 10% | Equal weight | Buffered | Before registration pilot | 1073 | 60.085 | 11.684 | 0.504 | -54.191 | 0.038 |
| Composite | 10% | Value weight | Buffered | Before registration pilot | 1073 | 48.244 | 9.687 | 0.447 | -55.176 | 0.038 |
| Composite | 20% | Equal weight | Buffered | Before registration pilot | 1073 | 29.859 | 6.328 | 0.353 | -59.170 | 0.035 |
| Composite | 20% | Value weight | Buffered | Before registration pilot | 1073 | 21.734 | 4.727 | 0.308 | -59.803 | 0.035 |
| Composite | 30% | Equal weight | Buffered | Before registration pilot | 1073 | 14.201 | 3.168 | 0.261 | -59.813 | 0.036 |
| Composite | 30% | Value weight | Buffered | Before registration pilot | 1073 | 8.137 | 1.854 | 0.221 | -59.568 | 0.035 |
| Low turnover | 0% | Equal weight | Buffered | Before registration pilot | 1073 | -3.302 | -0.785 | 0.118 | -57.223 | 0.021 |
| Low turnover | 0% | Value weight | Buffered | Before registration pilot | 1073 | -37.474 | -10.442 | -0.268 | -54.323 | 0.021 |
| Low turnover | 10% | Equal weight | Buffered | Before registration pilot | 1073 | -0.996 | -0.235 | 0.133 | -55.000 | 0.021 |
| Low turnover | 10% | Value weight | Buffered | Before registration pilot | 1073 | -30.361 | -8.147 | -0.183 | -49.505 | 0.023 |
| Low turnover | 20% | Equal weight | Buffered | Before registration pilot | 1073 | -1.367 | -0.323 | 0.129 | -54.269 | 0.022 |
| Low turnover | 20% | Value weight | Buffered | Before registration pilot | 1073 | -25.024 | -6.540 | -0.126 | -45.350 | 0.026 |
| Low turnover | 30% | Equal weight | Buffered | Before registration pilot | 1073 | 3.896 | 0.902 | 0.173 | -50.942 | 0.022 |
| Low turnover | 30% | Value weight | Buffered | Before registration pilot | 1073 | -15.201 | -3.798 | -0.014 | -50.098 | 0.026 |
| Small cap | 0% | Equal weight | Buffered | Before registration pilot | 1073 | 31.994 | 6.736 | 0.364 | -61.020 | 0.012 |
| Small cap | 0% | Value weight | Buffered | Before registration pilot | 1073 | -1.486 | -0.351 | 0.162 | -62.041 | 0.012 |
| Small cap | 10% | Equal weight | Buffered | Before registration pilot | 1073 | -4.733 | -1.132 | 0.130 | -61.897 | 0.022 |
| Small cap | 10% | Value weight | Buffered | Before registration pilot | 1073 | -14.550 | -3.626 | 0.036 | -63.687 | 0.017 |
| Small cap | 20% | Equal weight | Buffered | Before registration pilot | 1073 | -20.828 | -5.337 | -0.002 | -66.991 | 0.023 |
| Small cap | 20% | Value weight | Buffered | Before registration pilot | 1073 | -18.959 | -4.817 | -0.010 | -63.866 | 0.016 |
| Small cap | 30% | Equal weight | Buffered | Before registration pilot | 1073 | -28.465 | -7.566 | -0.085 | -69.727 | 0.025 |
| Small cap | 30% | Value weight | Buffered | Before registration pilot | 1073 | -23.640 | -6.138 | -0.058 | -66.149 | 0.017 |
| Composite | 0% | Equal weight | Buffered | Registration pilot | 867 | 23.908 | 6.429 | 0.389 | -30.799 | 0.026 |
| Composite | 0% | Value weight | Buffered | Registration pilot | 867 | 59.986 | 14.635 | 0.724 | -26.699 | 0.029 |
| Composite | 10% | Equal weight | Buffered | Registration pilot | 867 | 105.483 | 23.285 | 1.024 | -26.951 | 0.033 |
| Composite | 10% | Value weight | Buffered | Registration pilot | 867 | 106.550 | 23.471 | 1.040 | -26.594 | 0.033 |
| Composite | 20% | Equal weight | Buffered | Registration pilot | 867 | 108.787 | 23.858 | 1.070 | -25.595 | 0.034 |
| Composite | 20% | Value weight | Buffered | Registration pilot | 867 | 101.976 | 22.670 | 1.036 | -25.359 | 0.033 |
| Composite | 30% | Equal weight | Buffered | Registration pilot | 867 | 64.184 | 15.501 | 0.774 | -27.069 | 0.031 |
| Composite | 30% | Value weight | Buffered | Registration pilot | 867 | 60.188 | 14.677 | 0.744 | -27.076 | 0.030 |
| Low turnover | 0% | Equal weight | Buffered | Registration pilot | 867 | 48.952 | 12.279 | 0.672 | -31.696 | 0.034 |
| Low turnover | 0% | Value weight | Buffered | Registration pilot | 867 | -13.085 | -3.994 | -0.026 | -58.842 | 0.035 |
| Low turnover | 10% | Equal weight | Buffered | Registration pilot | 867 | 60.049 | 14.648 | 0.774 | -30.227 | 0.033 |
| Low turnover | 10% | Value weight | Buffered | Registration pilot | 867 | -4.655 | -1.376 | 0.074 | -53.467 | 0.037 |
| Low turnover | 20% | Equal weight | Buffered | Registration pilot | 867 | 59.607 | 14.556 | 0.768 | -29.254 | 0.033 |
| Low turnover | 20% | Value weight | Buffered | Registration pilot | 867 | -7.407 | -2.212 | 0.043 | -57.047 | 0.033 |
| Low turnover | 30% | Equal weight | Buffered | Registration pilot | 867 | 65.124 | 15.693 | 0.798 | -31.491 | 0.031 |
| Low turnover | 30% | Value weight | Buffered | Registration pilot | 867 | -4.727 | -1.397 | 0.075 | -56.328 | 0.031 |
| Small cap | 0% | Equal weight | Buffered | Registration pilot | 867 | 9.730 | 2.736 | 0.233 | -28.924 | 0.012 |
| Small cap | 0% | Value weight | Buffered | Registration pilot | 867 | 19.302 | 5.264 | 0.342 | -23.937 | 0.011 |
| Small cap | 10% | Equal weight | Buffered | Registration pilot | 867 | 39.894 | 10.250 | 0.534 | -22.741 | 0.019 |
| Small cap | 10% | Value weight | Buffered | Registration pilot | 867 | 14.322 | 3.967 | 0.287 | -20.546 | 0.013 |
| Small cap | 20% | Equal weight | Buffered | Registration pilot | 867 | 33.239 | 8.699 | 0.485 | -22.403 | 0.022 |
| Small cap | 20% | Value weight | Buffered | Registration pilot | 867 | 15.754 | 4.344 | 0.306 | -20.417 | 0.016 |
| Small cap | 30% | Equal weight | Buffered | Registration pilot | 867 | 1.845 | 0.533 | 0.134 | -24.583 | 0.024 |
| Small cap | 30% | Value weight | Buffered | Registration pilot | 867 | -8.583 | -2.575 | -0.018 | -26.630 | 0.017 |

</details>

<details>
<summary>Separate cash-ledger capacity simulation · 24 rows</summary>

| Candidate | Excluded names | Weight | Buffer | Capital CNY million | Net annual % | Sharpe | Drawdown % | Fill % | Cash % | Cumulative turnover × |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Small cap | 0% | Equal weight | Buffered | 10 | 11.714 | 0.538 | -59.617 | 26.263 | 0.349 | 48.014 |
| Small cap | 0% | Equal weight | Buffered | 100 | 11.837 | 0.545 | -59.643 | 34.870 | 4.053 | 51.307 |
| Small cap | 0% | Equal weight | Buffered | 500 | 9.625 | 0.477 | -58.609 | 40.762 | 10.663 | 43.794 |
| Small cap | 0% | Value weight | Buffered | 10 | 4.466 | 0.298 | -62.120 | 53.367 | 0.366 | 35.716 |
| Small cap | 0% | Value weight | Buffered | 100 | 5.697 | 0.342 | -62.422 | 49.925 | 1.153 | 36.522 |
| Small cap | 0% | Value weight | Buffered | 500 | 4.571 | 0.302 | -63.298 | 46.533 | 4.459 | 32.048 |
| Composite | 0% | Equal weight | Buffered | 10 | 21.880 | 0.639 | -50.998 | 23.805 | 0.791 | 174.605 |
| Composite | 0% | Equal weight | Buffered | 100 | 16.888 | 0.725 | -52.215 | 48.831 | 12.430 | 171.573 |
| Composite | 0% | Equal weight | Buffered | 500 | 13.533 | 0.693 | -48.702 | 31.589 | 38.022 | 93.075 |
| Composite | 0% | Value weight | Buffered | 10 | 17.643 | 0.722 | -50.427 | 54.751 | 0.905 | 204.940 |
| Composite | 0% | Value weight | Buffered | 100 | 15.427 | 0.676 | -51.793 | 51.814 | 10.267 | 166.422 |
| Composite | 0% | Value weight | Buffered | 500 | 12.557 | 0.652 | -48.563 | 33.076 | 37.873 | 91.712 |
| Small cap | 30% | Equal weight | Buffered | 10 | -1.457 | 0.075 | -69.667 | 81.778 | 0.704 | 54.129 |
| Small cap | 30% | Equal weight | Buffered | 100 | -1.783 | 0.064 | -70.954 | 81.999 | 0.238 | 52.725 |
| Small cap | 30% | Equal weight | Buffered | 500 | -1.719 | 0.064 | -70.530 | 75.369 | 2.341 | 49.815 |
| Small cap | 30% | Value weight | Buffered | 10 | -1.900 | 0.045 | -68.285 | 79.102 | 0.614 | 36.485 |
| Small cap | 30% | Value weight | Buffered | 100 | -2.145 | 0.036 | -69.226 | 79.852 | 0.144 | 36.160 |
| Small cap | 30% | Value weight | Buffered | 500 | -2.480 | 0.021 | -70.653 | 75.913 | 1.294 | 34.773 |
| Composite | 30% | Equal weight | Buffered | 10 | 10.206 | 0.480 | -57.786 | 93.620 | 0.988 | 156.476 |
| Composite | 30% | Equal weight | Buffered | 100 | 10.135 | 0.478 | -57.736 | 90.459 | 2.418 | 153.777 |
| Composite | 30% | Equal weight | Buffered | 500 | 7.857 | 0.422 | -55.705 | 61.679 | 17.588 | 112.464 |
| Composite | 30% | Value weight | Buffered | 10 | 9.339 | 0.454 | -57.906 | 93.108 | 1.001 | 143.704 |
| Composite | 30% | Value weight | Buffered | 100 | 9.216 | 0.450 | -58.107 | 90.902 | 1.967 | 142.292 |
| Composite | 30% | Value weight | Buffered | 500 | 7.593 | 0.414 | -54.556 | 61.880 | 17.379 | 112.988 |

</details>

## How the conclusions developed

Dates refer to dated research records or this editorial review. They are not proof of immutable runtime identity. A later correction applies to its stated study and does not automatically rerun other experiments.

### Early factor exploration · Spread results and long-only accounts

Long-short size and turnover observations motivated portfolio tests; universe and starting-date changes weakened mechanical translation to long-only performance.

Factor direction, selected combinations and overlapping windows must remain explicit.

### 2026-08-26 record · Small-cap and low-turnover exploration

Candidate, residualization and cadence comparisons exposed sensitivity and substantial drawdowns.

Repeated inspection makes later history descriptive; selected grid winners are not prospective evidence.

### 2026-09-09 audit · Historical eligibility and missing marks

Future-quote and current-membership filters were removed; historical targets were re-formed and unknown status retained.

Rebuilt targets and suspension-event matches do not supply a complete account NAV.

### 2026-09-15–16 records · Return clocks, controls and suspensions

Later conditional-association tests use a corrected execution return window; a separate suspension-corrected daily portfolio reports a lower return.

The control regression, weight-level portfolio and continuous-share ledger are different objects.

### 2026-09-28 public diagnostic · Continuous holdings and cash

A separate public execution diagnostic made blocked fills, inventory and cash visible.

Short-sample assumed execution costs do not certify historical capacity.

### 2026-10-16 recovery review · Stored results recovered

Documented migration revealed the 100-name and full exclusion bundles; notebook inspection added size/beta feasibility evidence.

Matching artifacts improves provenance but does not establish historical code or execution authenticity.

### 2026-10-16 comparison review · Different candidates respond differently

Small-cap, low-turnover and composite outputs have different exclusion and weighting sensitivities. Buffers consistently lower turnover but improve return in only eight of 24 comparisons.

Dated notes report 10 bp costs but do not authenticate the run; the primary capital argument and historical code remain unknown. The 2024+ sample is inspected, and capacity remains a separate engine.

### 2026-10-16 window sensitivity · The 120-session support threshold changes the result

The same current-input replay reports 4.22% net annual return at a 90-observation minimum and 6.26% at 45, versus 7.60% in the published snapshot.

This narrows but does not resolve the discrepancy or identify the original method.

## Research history and coverage register

This is an editorial register of 35 reviewed research families, not 35 independent experiments. The review covers the known quantitative research repositories and selected adjacent infrastructure as of 2026-10-16. Language companions, migration copies and synthesis notes are deduplicated. A follow-up inventory below records which notebooks and migrated result bundles were located; unresolved items have named evidence requirements.

The web report and downloadable Markdown use this same register. Restricted studies are represented only by reviewed high-level findings and limitations; private parameters, raw inputs and reproduction locations are excluded. Their source identities remain in the restricted provenance ledger. Public evidence links below support the public subset, not every restricted historical claim.

### H01 · Size across market regimes

**Historical association · 2008–2026 · 223 month ends**

Industry-demeaned factor spreads vary across regimes. Size is defined in the large-cap direction; a negative spread cannot be described as small-cap underperformance.

The claim that 2026 was the first positive large-cap year conflicts with positive years listed in the same record. Early fundamentals are reconstructed; 2026 is incomplete.

### H02 · Early multi-factor spread stability

**Exploratory comparison · Overlapping starts in 2019–2022, ending in 2026**

Selected long-short combinations appeared stable across several starts. These are overlapping histories rather than independent tests.

A factor that helped a long-short spread need not help a long-only account. Keep selected model weights restricted and require a frozen future comparison.

### H03 · Minimum-cap threshold and endpoint reversal

**Endpoint-sensitive · Historical windows ending in 2026**

An attractive minimum-cap filter depended on the ending period. Changing the endpoint weakened the original interpretation.

Neither a permanent size floor nor unrestricted micro-cap exposure is established as the long-run optimum.

### H04 · Long-only translation and universe choice

**Historical simulation · 2008–2026; separate post-2015 universe**

Long-short findings did not transfer mechanically to long-only portfolios. Results changed materially with the universe and starting date.

Early unadjusted returns and incomplete eligibility require repair. A broad-universe result cannot certify a more restricted investable universe.

### H05 · Broad factor-combination search

**Selection-sensitive search · 455 combinations of 14 factors**

The historical search found attractive selected combinations, with substantial drawdowns and weaker later-period results.

The selected winner is not independent proof of optimal synergy. Conflicting annualizations and an inconsistent yearly win count remain unresolved.

### H06 · Combined scores versus independent sleeves

**Construction sensitivity · 2016–August 2026**

A combined-score screen exceeded separate sleeves in the inspected history; much of the advantage appeared after 2021.

Full-sample selection prevents a strict out-of-sample claim. Match the eligibility, cash, costs and execution clock before selecting a construction.

### H07 · Capital and traded-amount unit corrections

**Corrected assumptions · Separate 2019–2026 execution checks**

Capital assumptions and a 1,000-fold traded-amount unit error changed earlier liquidity interpretations. A high simulated fill ratio followed the correction.

A high fill ratio under an assumed model does not establish unconstrained liquidity or calibrated market impact.

### H08 · Model attribution and equal-weight benchmark

**Diagnostic, incomplete evidence · 2025–2026 attribution; 2016–2026 benchmark**

Style covariance explained part of a model return series. A separate equal-weight benchmark diagnosis exposed universe, new-listing and return-clipping defects.

Covariance is not causal skill attribution. Revised benchmarks still zero-filled missing stock-days and omitted costs; they cannot establish model promotion.

### H09 · Small-cap × low-turnover screening

**Historical exploration · 2015–July 2026; development through 2023**

Raw, residualized and combined screens gave different results and large drawdowns. Public candidate and cadence tables are retained below.

The repeatedly inspected 2024+ segment is descriptive. Narrative and snapshot versions differ; do not splice them into a single final backtest.

### H10 · Turnover definition sensitivity

**Historical cross-section · 2008–July 2026; 223 formations**

Point-in-time turnover and prior-window means or medians answer different questions. Quintile diagnostics are separate from later decile controls.

Alternative definitions require their own executable comparison. Definition sensitivity alone does not identify a unique premium.

### H11 · Deconfounding: early and corrected controls

**Conditional association · Early 133 formations; later 86 common-support months**

Later matched-stock controls retained a low-turnover association after size, risk, liquidity and return controls. A regression check also remained positive.

Earlier anatomy tables use a different sample and ranking basis. Neither double sorts nor regressions identify a causal or executable premium.

### H12 · Frozen prospective observation

**One-month observation · One completed month: August 2026**

The frozen July-end signal produced opposite raw and controlled spreads in August. Only one completed month is reported by the reviewed source.

Do not mark later pending months complete merely because time has passed. Require actual receipts and multiple new observations.

### H13 · Daily investability and intraday coverage

**Simulation; partial coverage · Separate daily portfolio and intraday samples**

An explicit suspension correction lowered the daily simulation’s annual return from 7.04% to 5.33%. Minute coverage was about 80.8%; quote-level coverage was lower.

Missing quotes are not proven suspensions or zero returns. Incomplete minute and order-book records cannot support a full-history fill-cost replay.

### H14 · Window × cadence comparisons

**Historical sensitivity · Public snapshot: 3 windows and 16 grid cells**

The complete published grid is available, alongside three fixed monthly low-turnover windows. Definitions and engine scope differ between the tables.

A source caveat says the grid was pending while the same snapshot contains 16 rows. Preserve the inconsistency and inspect actual rows; do not infer independent confirmation.

### H15 · Weight targets, shares and cash reconciliation

**Unreconciled comparison · Monthly and biweekly ledgers**

Weight-level, ideal-share and continuous-ledger results differ. Formation counts, target counts and owner replay periods also differ.

Do not splice return series or declare one canonical result. Zero modeled impact is an assumption, not evidence of zero realized cost.

### H16 · Capital, lots and delayed fills

**Path-dependent simulation · Seven public capital scenarios; separate lot checks**

Cash, lot rounding and delayed orders changed outcomes. The published capital sweep has rising returns at larger capital.

This is not an economic capacity curve: deferred orders can skip later losers, and impact is uncalibrated. Opportunity-cost figures are diagnostic.

### H17 · Monthly micro-cap exclusion scorecard

**Source-reported historical results · 2015–July 2026; selected monthly 40-name results**

Removing different bottom-cap fractions did not produce a monotonic improvement; large drawdowns remained.

A selected scorecard is not completion of the full weighting, buffer, cost and capacity protocol. Restricted configurations are not republished.

### H18 · Monthly 100-name and weekly 200-name proxies

**Historical bundles recovered; partial provenance · Different 2015+ and 2023+ samples**

The dated monthly 100-name bundle was recovered through a documented storage migration; its stored full-sample summary agrees with the rounded source-note figures. The weekly 200-name proxy remains a separate comparison.

No performance was rerun. The recent-window comparison receipt and immutable code/input/output binding remain missing. A separate weekly proxy cumulative-excess label still fails percentage-point subtraction; do not pool or reinterpret these returns.

### H19 · Complete exclusion robustness protocol

**Outputs recovered; structural checks passed · Bottom 0/10/20/30%; weighting and buffer controls**

The migrated bundle contains 112 factor rows, 56 weighting comparisons, 80 buffer rows and 24 capacity rows. The factor, buffer and capacity grids have unique keys, no blank cells and complete declared axes; four checkpoint files match final outputs byte-for-byte.

The recorded owner-code commit fields are unknown. This artifact audit does not rerun performance, authenticate every historical input, establish an untouched holdout or promote a strategy. The separate characteristic-decomposition protocol still has no located result bundle.

### H20 · Characteristic decomposition protocol

**Protocol only · Size, illiquidity, extreme returns, volatility and quality**

Double sorts and regression designs would test which characteristics accompany the apparent micro-cap effect.

No verified outputs were found for this protocol. Mechanism claims remain open, including delisting and shell-value effects.

### H21 · Future-quote and current-membership repair

**Replay blocked · 2015–September 2026 validity audit**

Earlier targets used future quote availability and current membership. Removing these filters changes the sample and invalidates direct reuse of old results.

A current membership snapshot cannot reconstruct historical membership. Missing held-security marks block a complete validated NAV.

### H22 · Historical names, ST status and date parsing

**Data repair, not return evidence · Historical-status supplement, September 2026**

Historical names replace current-name ST inference. Strict date parsing exposed nullable export strings and previously admitted delisted securities.

A documented nullable adapter repairs representation only. Suspension-event matches do not prove a tradable price or settlement value.

### H23 · Frozen target re-formation

**Targets rebuilt; NAV unverified · Protocol frozen before new performance inspection**

Historical eligibility is reconstructed without future-price filters; unknown status stays unknown. Old-target audits and new targets remain separate.

Targets are not a validated account. Do not drop missing-price names and renormalize; engine installation and run verification need separate receipts.

### H24 · 400-name missing-quote audit

**Incomplete valuation · Multiple audits with different windows**

Public audits found 189 missing marks on 117 dates in one window; an older broader replay found 3,708 marks on 1,407 dates.

Counts are neither distinct delistings nor comparable rates without denominators. Remaining-name averaging silently renormalizes exposure; the return bias is not quantified.

### H25 · Early history, cleaned sources and recovery

**Historical return and risk · 2008–2014 extension; later overlapping sources**

The longer history adds earlier drawdowns and prolonged underwater intervals. Cleaned and earlier source series are shown separately.

Do not stitch sources without an overlap audit. An unfinished recovery is censored at the sample endpoint rather than assigned a completed waiting time.

### H26 · Vendor points versus membership replication

**Reference comparison · Vendor series, available membership and proxy indices**

Published index points support return comparisons, while current membership snapshots lack historical effective dates and weights.

Dividend conventions, pool differences and incomplete daily data prevent a certified index replication. A proxy index is a separate benchmark.

### H27 · Continuous-account execution diagnostic

**Short-sample mechanism check · Public diagnostic dated 2026-09-28**

Continuous holdings and cash expose effects of participation, T+1, price limits and assumed fees. The public bilingual source is included in the appendices.

This diagnostic does not certify full-history performance or actual capacity. A later method does not retroactively validate earlier ledgers.

### H28 · Cross-market small-cap liquidity

**Descriptive, quality-gated · A-share, Hong Kong, Japan and US; unmatched dates**

Market-cap quantiles and USD ADV20 provide context, but dates, security types, units and eligibility differ. Some A-share totals do not reconcile.

Exclude inconsistent slices from rankings. Missing P90 cannot be replaced by a median; mean-versus-median lineage remains unresolved.

### H29 · Order-book and impact calibration readiness

**Partial coverage · Ten-date book audit plus separate historical trades**

Published valid and excluded order-book counts reconcile, but missing minutes cluster on one date; a trades-only sample has no orders.

Book counts are not actual-order capacity calibration. Require aligned orders, trades, timestamps and observed fills before estimating implementation cost.

### H30 · Constrained full-history factor follow-up

**Promotion held · 2008–2026 matched raw, constrained and net comparisons**

Data checks passed, but only half of the core factor gates passed. Constraints and costs reduced apparent factor returns.

Theoretical shorts, terminal proxies and reconstructed point-in-time fundamentals remain limits. This does not rerun or validate every earlier long-only strategy.

### H31 · Small-cap sensitivity artifact contract

**Infrastructure only · Adjacent factor-framework infrastructure**

A small-cap sensitivity CSV is part of an output contract, with synthetic pipeline checks.

A file contract and synthetic test are not empirical small-cap evidence. No performance conclusion is added for this infrastructure.

### H32 · Hong Kong provider, PIT and size-control probes

**Diagnostic, source-reported · Archived monthly comparisons, March 2026**

Provider and point-in-time fundamental portfolios differed substantially. The provider result accompanied small-cap and short-horizon price exposures; size-neutral and softer controls changed that exposure.

Style correlation does not establish causality. Better-controlled size exposure did not establish stronger structural alpha, and this Hong Kong sample cannot validate A-share micro-caps.

### H33 · Four-stock micro-cap feasibility and cost stress

**Reconstructed proxy; substantial limits · September 2023–July 2026; 150 weekly formations**

The strict historical-status window produced four selections at every formation. The standalone concentrated sleeve was highly sensitive to trading costs and experienced severe drawdowns; common-week index comparisons showed only partial agreement.

This is a reconstructed proxy, with revision safety false, current master-data inputs and incomplete limit-price execution modeling. Historical ST coverage ends in July; do not extend the strict sample through August or call it index replication.

### H34 · Cash-flow plus micro-cap allocation studies

**Source-reported; share with caveats · Three-year studies; broad proxy and separate four-stock sleeve**

The broad proxy comparison and later unified four-stock sleeve replay are distinct studies. A shared weekly calendar, next-session open execution and portfolio-level costs permitted a combined-account comparison.

The combined outcome does not isolate a micro-cap premium. Reconstructed fundamentals may contain later revisions; large drawdowns, concentration and incomplete execution constraints prevent live-capacity or formal point-in-time claims.

### H35 · Weekly size and beta neutrality feasibility

**Cached exploratory evidence; not rerun · Cached notebook comparisons: 2025 and partial 2026**

A concentrated candidate pool could not consistently satisfy portfolio size and beta constraints. Widening the candidate pool improved feasibility, while hard exposure controls reduced historical selected-sample excess returns.

The notebook reads existing comparison files and retains cached outputs; execution counters do not authenticate a fresh run. Samples were reused, lineage was incomplete and missing-outcome weights were flagged. Neither independent micro-cap alpha nor untouched out-of-sample performance is established.

### Public evidence anchors

- [Micro-cap history and method](https://runchengxie.github.io/quant-market-research/docs/research/factors/microcap/)
- [Low-turnover history and corrections](https://runchengxie.github.io/quant-market-research/docs/research/factors/low-turnover/)
- [Published numerical snapshot](https://runchengxie.github.io/quant-market-research/data/low_turnover_exploration.json)
- [Index reconstruction findings](https://github.com/runchengxie/quant-market-research/blob/main/studies/index_replication/findings-20260909.md)
- [Liquidity evidence and quality gates](https://runchengxie.github.io/quant-market-research/research/liquidity/)

Resumption requires source receipts for missing outputs, frozen future observations for selected rules, matched accounting for engine comparisons, and complete held-security valuation for returns. No research is promoted by this editorial consolidation.

## Evidence recovery follow-up · 2026-10-16

This follow-up searched beyond source notes: tracked notebooks, retained derived reports, migration receipts and identified cold archives. Artifact recovery, structural checks and research reproduction are separate evidence stages.

The private ledger retains exact source identities, hashes, search roots and exclusions. The public build reads only this reviewed summary. The recovery inventory itself did not rerun backtests or notebooks. Subsequent window checks are identified separately; no shared input or latest pointer was changed.

### R01 · Notebook inventory

**Inspected; one family added**

Seven source notebooks were found, all tracked in the two research repositories. Eight retained notebook files were also inspected: three are byte-identical copies, five are separate executed reviews. No additional untracked notebook was found in these two repositories.

Cached size/beta feasibility evidence is now H35. Empty launcher notebooks, duplicate copies and synthetic calibration outputs do not count as independent empirical confirmations. No notebook was executed by this audit.

### R02 · Published snapshot lineage

**53 rows matched; 60-session metrics replayed**

All 53 published rows in six table families match retained CSV fields at numerical tolerance 1e-10. This covers candidates, anatomy, capital, cadence, ledgers and the joint grid. Separately, 2,778 retained suspension-corrected daily observations reproduce all four published 60-session-window metrics after rounding: 5.334535% annual return, 0.330517 Sharpe, −52.389378% drawdown and 6.785942 annual turnover.

The 20- and 120-session historical daily artifacts and a jointly bound three-window runtime remain missing. The 60-session metric replay establishes a retained daily source, not the original historical code, inputs or execution identity. A new current-inputs run matches the 20/60 rounded metrics but disagrees for 120 (4.22% versus 7.60% annual). It is a separate observation, not the missing historical binding; see the window recheck above.

### R03 · Historical 100-name bundle

**Recovered through migration**

The dated bundle and its self-referencing metadata were located after following a documented directory rename. All full-sample summary figures agree with the rounded source note; this closes the earlier blanket “bundle unavailable” gap.

The recent-window comparison receipt and immutable execution binding remain missing. Recovery of stored results does not reproduce performance, verify index membership or certify implementation.

### R04 · Micro-cap exclusion robustness

**Bundle recovered; provenance incomplete**

The full named artifact set and declared factor, weighting, buffer and capacity grids were recovered. Unique-key and completeness checks pass for 112 factor, 80 buffer and 24 capacity rows. Four checkpoint CSVs match final files.

The owner-code commit fields are unknown. Input-vintage authentication, matching historical code and an independent rerun remain requirements before stronger reproducibility or strategy claims.

### R05 · Frozen-target rebuild receipts

**Hashes agree; valuation remains blocked**

The stored readiness receipt and both target files match the hashes in the final verification receipt. Missing-mark table counts also agree with the stored audit.

The receipts explicitly say no NAV was published. Suspension matches do not supply settlement prices or prove fills, and this audit did not verify a new engine installation or replay.

### R06 · Attribution and characteristic decomposition

**Exact bundles still missing**

The exact historical Top800 attribution JSON and yearly CSV, its run-linked factor matrix, and the characteristic-decomposition output set were not found in the inventoried warm roots, migrated research subtree and identified cold archives.

Similarly named later matrices cannot substitute. These are bounded negative findings, not proof of deletion. Resolution needs an exact artifact or a documented historical run/code/input binding; a new run must be labeled separately.

### R07 · Later liquidity and execution reviews

**Executed reviews located**

Later executed notebooks preserve descriptive liquidity alignment and conditional execution-cost reviews. Synthetic calibration notebooks are separately identified as infrastructure evidence. The inspected cold-storage volume was available.

Later aligned samples do not erase older source discrepancies. Numeric notebook outputs with unresolved redistribution permission remain local; cached execution and synthetic tests do not establish actual-order capacity.

## Full published snapshot tables

The snapshot contains seven numerical families and 56 source rows: 9 candidates, 15 anatomy rows, 7 capital scenarios, 4 cadences, 2 ledgers, 16 joint cells and 3 windows. All rows are represented in this report; the three windows appear above. The JSON retains every machine field. Percentage return fields are already in percent; anatomy leg returns, fill ratios and cash weights are fractions and are converted for display. Rank IC and turnover multiples are not percentages.

### Nine candidates

![Nine historical candidates](https://runchengxie.github.io/quant-market-research/downloads/microcap-candidates.en-US.svg)

| Candidate | Annual net | Max drawdown | Sharpe | Annual turnover (×) | Blocked entry days | Blocked exit days |
| --- | --- | --- | --- | --- | --- | --- |
| Small cap | 2.05% | -73.78% | 0.218 | 2.97 | 605 | 1231 |
| Low turnover | 5.33% | -52.39% | 0.331 | 6.79 | 327 | 2383 |
| Residual turnover | -9.96% | -88.25% | -0.176 | 19.22 | 869 | 2735 |
| Industry-residual turnover | -7.62% | -84.49% | -0.086 | 19.95 | 724 | 1402 |
| Composite | 7.73% | -68.59% | 0.399 | 6.77 | 661 | 916 |
| Residual composite | 4.84% | -74.30% | 0.309 | 15.42 | 824 | 1502 |
| Industry-residual composite | 1.91% | -81.33% | 0.219 | 13.02 | 765 | 1305 |
| Large-cap control | 6.82% | -44.39% | 0.411 | 1.40 | 200 | 775 |
| Low-volatility control | 0.41% | -67.52% | 0.131 | 16.96 | 372 | 970 |

### Historical deconfounding anatomy

This earlier 133-formation panel is retained as history, not substituted for the later 86-month corrected common-support controls. Mean period returns are not annualized. The later inspected segment remains descriptive.

| Sample | Control stage | Formations | Stock observations | Mean rank IC | Low-turnover leg | High-turnover leg | Low − high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Development | Raw | 103 | 369066 | 0.0730 | 0.38% | -1.23% | 1.60% |
| Development | Size | 103 | 369066 | 0.0790 | 0.72% | -1.35% | 2.06% |
| Development | Size + low volatility | 103 | 369066 | 0.0262 | 0.01% | -0.95% | 0.96% |
| Development | + liquidity | 103 | 369066 | 0.0078 | -0.09% | -0.81% | 0.72% |
| Development | + past returns | 103 | 369066 | 0.0210 | 0.13% | -0.98% | 1.11% |
| Later descriptive | Raw | 30 | 160324 | 0.0600 | 2.54% | 0.82% | 1.72% |
| Later descriptive | Size | 30 | 160324 | 0.0727 | 2.76% | 0.93% | 1.83% |
| Later descriptive | Size + low volatility | 30 | 160324 | 0.0278 | 1.92% | 1.05% | 0.87% |
| Later descriptive | + liquidity | 30 | 160324 | 0.0180 | 2.22% | 0.94% | 1.28% |
| Later descriptive | + past returns | 30 | 160324 | 0.0179 | 2.16% | 1.04% | 1.12% |
| Full descriptive | Raw | 133 | 529390 | 0.0701 | 0.87% | -0.76% | 1.63% |
| Full descriptive | Size | 133 | 529390 | 0.0776 | 1.18% | -0.83% | 2.01% |
| Full descriptive | Size + low volatility | 133 | 529390 | 0.0265 | 0.44% | -0.50% | 0.94% |
| Full descriptive | + liquidity | 133 | 529390 | 0.0101 | 0.43% | -0.42% | 0.85% |
| Full descriptive | + past returns | 133 | 529390 | 0.0203 | 0.59% | -0.52% | 1.11% |

### Seven capital scenarios

All use the composite candidate and assumed 5% participation. Rising simulated returns do not certify scalable capacity. Cash, delayed fills and uncalibrated impact can change the path.

| Capital (CNY) | Annual net | Max drawdown | Sharpe | Fill ratio | Average cash | Delayed orders |
| --- | --- | --- | --- | --- | --- | --- |
| 100000 | 5.28% | -25.61% | 0.530 | 13.82% | 38.25% | 28 |
| 500000 | 11.46% | -48.69% | 0.587 | 40.94% | 5.11% | 37 |
| 1000000 | 11.85% | -49.94% | 0.585 | 43.89% | 2.54% | 38 |
| 5000000 | 12.48% | -51.59% | 0.596 | 44.48% | 0.71% | 40 |
| 10000000 | 13.00% | -51.67% | 0.608 | 45.74% | 0.66% | 44 |
| 30000000 | 14.47% | -51.40% | 0.645 | 47.71% | 2.04% | 41 |
| 50000000 | 15.07% | -51.70% | 0.664 | 48.29% | 6.18% | 40 |

### Four rebalance cadences

| Cadence | Annual net | Max drawdown | Sharpe | Annual turnover (×) | Development annual | Later descriptive annual |
| --- | --- | --- | --- | --- | --- | --- |
| Weekly | 9.56% | -61.56% | 0.452 | 5.18 | 6.44% | 21.07% |
| Biweekly | 19.00% | -59.37% | 0.703 | 3.25 | 17.86% | 23.04% |
| Monthly | 7.73% | -68.59% | 0.399 | 6.77 | 4.55% | 19.48% |
| Quarterly | 8.33% | -64.99% | 0.419 | 4.24 | 3.23% | 27.76% |

### Two continuous-share ledgers

These are comparison-only replays. Formations (139/296), weight targets (138/295) and owner replay periods (137/37) do not establish a matched sample. Cumulative-return machine fields have not been reinterpreted here. Modeled impact is zero; reported delay opportunity costs are uncalibrated and their currency basis needs confirmation.

| Cadence | Formations | Annual net | Max drawdown | Sharpe | Fill ratio | Average cash | Cumulative turnover (×) | Delayed orders | Reported delay cost |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Monthly | 139 | 15.06% | -51.07% | 0.658 | 50.56% | 12.63% | 147.43 | 40 | 291602.59 |
| Biweekly | 296 | 14.13% | -59.51% | 0.632 | 75.37% | 21.12% | 69.35 | 13 | -40144.76 |

### All 16 definition × cadence records

| Definition | Cadence | Formations | Annual net | Max drawdown | Sharpe | Annual turnover (×) | Development annual | Later descriptive annual |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20-day mean | Weekly | 592 | 8.68% | -58.55% | 0.428 | 6.13 | 6.75% | 15.59% |
| 60-day mean | Weekly | 592 | 9.56% | -61.56% | 0.452 | 5.18 | 6.44% | 21.07% |
| 60-day median | Weekly | 592 | 9.52% | -62.63% | 0.450 | 5.14 | 6.48% | 20.71% |
| 120-day mean | Weekly | 592 | 13.20% | -65.31% | 0.553 | 4.71 | 10.16% | 24.35% |
| 20-day mean | Biweekly | 296 | 17.07% | -60.16% | 0.649 | 3.68 | 16.53% | 18.95% |
| 60-day mean | Biweekly | 296 | 19.00% | -59.37% | 0.703 | 3.25 | 17.86% | 23.04% |
| 60-day median | Biweekly | 296 | 18.60% | -59.75% | 0.689 | 3.24 | 17.37% | 22.93% |
| 120-day mean | Biweekly | 296 | 21.18% | -60.48% | 0.746 | 3.11 | 20.72% | 22.76% |
| 20-day mean | Monthly | 139 | 7.81% | -68.42% | 0.402 | 8.60 | 3.11% | 25.75% |
| 60-day mean | Monthly | 139 | 7.73% | -68.59% | 0.399 | 6.77 | 4.55% | 19.48% |
| 60-day median | Monthly | 139 | 7.91% | -66.28% | 0.406 | 6.63 | 4.54% | 20.39% |
| 120-day mean | Monthly | 139 | 13.88% | -65.15% | 0.574 | 5.57 | 10.83% | 25.08% |
| 20-day mean | Quarterly | 47 | 7.35% | -58.34% | 0.387 | 4.69 | 3.13% | 23.12% |
| 60-day mean | Quarterly | 47 | 8.33% | -64.99% | 0.419 | 4.24 | 3.23% | 27.76% |
| 60-day median | Quarterly | 47 | 9.16% | -65.05% | 0.443 | 4.16 | 4.37% | 27.24% |
| 120-day mean | Quarterly | 47 | 10.53% | -65.07% | 0.479 | 4.21 | 6.18% | 26.77% |

Version warning: candidate, cadence and ledger numbers differ from earlier narrative reports. Apart from explicitly documented corrections, this compilation does not attribute every difference to a single cause. The snapshot also retains a stale caveat saying the joint grid is pending despite containing 16 cells. These conflicts remain visible rather than being silently reconciled.

## How the interpretation changed

Read revisions with the study they affect. A change in one return window or simulator does not automatically invalidate every related experiment.

### Next-session execution

Early reconstructions used post-close information with same-close execution. Those versions were superseded. Historical reconstruction now separates the decision close from the execution close.

### Data-source transitions

An old holding interval divided prices from different sources across the 2014–2015 boundary. That interval was removed; separate historical coverage must not be silently stitched together.

### Return-window correction

Later low-turnover validation uses next-session open to period-end close with both endpoints present. Earlier attribution tables use a different basis and must remain historical.

### Execution paths and accounting

Delayed fills, cash and held shares can change both performance and cadence rankings. Report simulator-specific results separately; a participation constraint improving simulated return is not proof of alpha.

### A repeatedly inspected holdout

2024–2026 has been examined across several historical sensitivity checks. It remains descriptive evidence; further parameter choices need genuinely prospective observations.

## Open research and publication gaps

### Micro-cap exclusion and weighting

The recovered 0% / 10% / 20% / 30% aggregate matrix is now published below. Dated research notes describe it as using 10 bp costs, but the original command and run receipt were not recovered. The primary screening matrix cannot be described as a CNY 100 million execution: its capital argument was not passed into the execution context. Historical source commits remain unknown. Next, authenticate the setup and rerun on a common share ledger with fixed universes, costs, buffers and dates.

### Size, liquidity and other characteristics

Separate size from illiquidity, extreme daily returns, idiosyncratic volatility, turnover and quality on common support. Conditional association would still not identify a causal mechanism.

### A comparable execution and capacity ladder

Use identical targets and dates to compare ideal held shares with a constrained cash ledger. Attribute differences to lot size, participation, delayed fills, costs and idle cash before publishing capacity claims.

### What would justify stronger conclusions?

Resume a return comparison only after the same universe, formation clock, source versions, benchmark, missing-price policy and held-share accounting reconcile. Capacity claims require fills, cash, costs and delayed-order opportunity costs under calibrated impact. Mechanism claims need common-support controls and prospective evidence; stage differences alone do not establish causal effects. Preserve failed and inconclusive tests.

## Sources and version boundaries

- [Interactive research page](https://runchengxie.github.io/quant-market-research/research/microcap/)
- [Published exploratory snapshot](https://runchengxie.github.io/quant-market-research/data/low_turnover_exploration.json)

The appendices below preserve the selected public language records in full. English and Chinese companions are not always equally detailed: the Chinese execution note contains additional historical receipts. Language selection does not certify equivalence of samples or authorize reusing superseded figures. Read correction notices beside their source results.

## Appendix 1 · Micro-cap Method

[Canonical web source](https://runchengxie.github.io/quant-market-research/docs/research/factors/microcap/)

## Microcaps: return evidence and underwater periods

[Chinese version](https://runchengxie.github.io/quant-market-research/docs/research/factors/microcap.zh-CN/?lang=zh-CN)

This page describes reconstructed historical rules and risk characteristics. It is not a Wind index replication and does not represent a directly tradable strategy.

### Plain-language takeaway

The clearest result here is about risk: portfolios rebuilt from small stocks had deep losses and sometimes took years to recover their previous highs. Some early returns are still being checked, and delisted stocks, historical membership, and actual trading have not been fully reconstructed. Treat the return series as a research record, not as an index or an account result.

An **underwater period** is the time a portfolio stays below its previous high until it passes that high again. **Maximum drawdown** is the largest fall from a high to a later low. **NAV** (net asset value) is the portfolio-value series scaled to a starting level. For each measure, missing-price rules also matter.

The current source coverage extends through 2026-09-17. The next-day return audit for the minimum-market-cap proxy is computable through 2026-09-16. Portfolio sizes are N = 50, 100, 200, 400, and 800.

The [microcap execution diagnostic](https://runchengxie.github.io/quant-market-research/docs/research/experiments/microcap-execution-diagnostic-20260928/) uses a separate public execution-simulation ledger and must not be joined directly to historical paper returns. Differences in data cleaning, decision clocks, fills, and cost assumptions remain part of the evidence boundary.

### Research map: history, factors and execution

Public evidence synthesis reviewed on 2026-10-16. This review did not rerun the studies or extend their sample dates. The [micro-cap topic page](https://runchengxie.github.io/quant-market-research/research/microcap/) connects the following questions without treating them as one strategy.

| Question | Available public evidence | Important boundary | Next useful evidence |
| --- | --- | --- | --- |
| What did the smallest stocks return and lose? | Reconstructed N = 50, 100, 200, 400 and 800 baskets, drawdown and underwater statistics, missing-price sensitivities | Historical eligibility, company actions and delisting prices remain incomplete; strict and partial treatments have different valid sessions | Reconcile holding-level missing quotes and settlement events |
| Is the result a size exposure? | Historical style-factor research, including size and market regimes | Factor sign and long-short construction differ from a long-only micro-cap basket | Matched tail-exclusion tests with recomputed formation signals |
| What does low turnover add? | [Low-turnover evidence](https://runchengxie.github.io/quant-market-research/docs/research/factors/low-turnover/): common-sample controls, confidence intervals and a short forward record | Conditional association is not a causal premium; theoretical stock-group returns are not executable portfolios | Freeze prospective rules and accumulate additional observations |
| Do portfolio rules change the result? | Published 20-, 60- and 120-session window sensitivity | Repeatedly inspected historical sample; cannot select an independently confirmed optimum | Repeat frozen comparisons under consistent share accounting |
| Could the portfolio trade? | [Public execution diagnostic](https://runchengxie.github.io/quant-market-research/docs/research/experiments/microcap-execution-diagnostic-20260928/), cash and blocked-trade accounting | Separate short sample, adjusted-price proxy and assumed cost; not a capacity certification | Identical targets and dates, reconciled accounting and calibrated impact |
| Are small stocks equally liquid across markets? | Market-cap group traded-value and coverage comparisons; [early A-share turnover context](https://runchengxie.github.io/quant-market-research/docs/research/factors/smallcap-turnover-history/) | Currencies, dates and eligibility differ; turnover rate and traded value are distinct measures | Align samples, currency conversion and execution constraints |

#### Keep portfolio identities separate

A vendor reference index, a daily smallest-N reconstruction, a monthly low-turnover candidate and the short execution diagnostic have different identities. Neither a shared label such as “micro-cap” nor equal portfolio size makes their results comparable. Record the sample, formation and execution clock, weighting, buffer, missing-price treatment, costs and simulator before comparing any two figures. Do not join their NAVs.

The new window-comparison chart reads `window_sensitivity` directly from the existing public `low_turnover_exploration.json` snapshot, generated on 2026-09-16 with overall coverage through 2026-07-31. Its public method describes 2015–2026 daily data, monthly formation, 40 target holdings, a 60-name buffer and a 10 bp fee. These are low-turnover window results, not the small-cap-plus-low-turnover composite. Returns and drawdowns in this snapshot are percentage values; annual turnover is a multiple. A later note with different source figures must not silently replace these values while keeping the old provenance.

#### Revisions that affect interpretation

- Early reconstructions that used post-close market capitalization with same-close execution were superseded. The reconstruction now separates the decision close and next-session execution close.
- An old 2014–2015 holding interval used execution and valuation prices from different sources. That interval was removed. Early-period eligibility remains incomplete.
- Later low-turnover validation changed to next-session open through period-end close, requiring both endpoints. Its revised 86-month common sample must not be merged with older attribution tables. See the latest-validation section in the [Chinese source record](https://runchengxie.github.io/quant-market-research/docs/research/factors/low-turnover.zh-CN/).
- Share accounting, idle cash and delayed fills can change return and cadence rankings. Results from a weight-level screening simulator and a share ledger must retain their engine identity. An apparent gain from tighter participation limits is execution-path sensitivity, not evidence of additional signal alpha.
- The 2024–2026 sample has already been examined across several historical comparisons. It is descriptive evidence rather than an untouched final holdout.

The public revision history is preserved in the existing [follow-up research source record](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/experiments/turnover-microcap-followup-20260915.md), which explicitly marks superseded low-turnover results. Those old figures are not reused as current headline returns.

#### Open comparisons and publication requirements

The recovered 0% / 10% / 20% / 30% exclusion and weighting aggregate matrix is now published in the topic report, alongside separate cash-ledger capacity outputs. Dated research notes describe the matrix as using 10 bp costs, but the original command and run receipt are missing. The primary screening table cannot be described as a CNY 100 million execution: its capital argument was not passed to the execution context. Historical source commits remain unknown, and these retained outputs are not a same-ledger execution reconciliation. Remaining work is to authenticate the historical setup, separate size from liquidity, extreme returns, idiosyncratic volatility, turnover and quality on common support, and reconcile ideal held shares with constrained cash ledgers over identical targets and dates. The new 120-session reconstruction yields 4.22% annual return with 90 valid observations and 6.26% with 45 on the same current inputs, against the published 7.60%. The threshold affects the result but neither identifies the historical method nor fully explains the gap.

For each addition, preserve a stable experiment identity, source version, sample dates, formation-time availability, universe, benchmark, metric units, costs, missingness policy, simulator and limitations. Publish reviewed aggregate outputs only. Raw vendor data, private strategy configurations and private reproduction locators remain outside this public site. A source-reported historical number without recoverable provenance should remain labeled as such until reproduced; no return series should be invented from summary metrics.


## Appendix 2 · Low-turnover Method

[Canonical web source](https://runchengxie.github.io/quant-market-research/docs/research/factors/low-turnover/)

## Low turnover: what might it represent?

[Chinese version](https://runchengxie.github.io/quant-market-research/docs/research/factors/low-turnover.zh-CN/?lang=zh-CN)

Current evidence is exploratory. An independent premium and practical tradability have not been established.

### Plain-language takeaway

In some historical samples, lower-turnover stocks did better. Low turnover also tends to appear alongside lower volatility and less active trading. The return gap changes when those features are included, so the evidence does not yet show that low turnover itself adds returns or that the pattern can be traded reliably.

In the tables, **low minus high** means the average return of the low-turnover group minus that of the high-turnover group. It is a historical group difference, not the return an investor would have earned. **Rank IC** measures whether the signal's stock rankings line up with later return rankings; a value near zero means the ranking added little information. **Point-in-time data** means information that was actually available on the date being studied. **ADV20** is the average trading value over the prior 20 sessions, used as a rough measure of how much a stock normally trades. One **basis point (bp)** is 0.01%; the slippage values below are assumptions, not broker-calibrated costs.

The candidate study covers 2015-02 through 2026-07. The development sample is 2015–2023; 2024–2026 is descriptive only. Historical style diagnostics cover 2008–2026.

The study separates turnover proxies from the economic interpretation of the signal, reports group ranking and implementation limits, and keeps unresolved data and execution questions explicit. See the Chinese companion for the historical tables and detailed experiment record.


## Appendix 3 · Micro-cap Execution Simulation Diagnostic

[Canonical web source](https://runchengxie.github.io/quant-market-research/docs/research/experiments/microcap-execution-diagnostic-20260928/)

## Microcap portfolio execution diagnostic

[Chinese version](https://runchengxie.github.io/quant-market-research/docs/research/experiments/microcap-execution-diagnostic-20260928.zh-CN/?lang=zh-CN)

### Plain-language takeaway

A short historical list of target stocks was sent through a public trading simulator to see what could be bought or sold under basic trading limits. This checks whether the simulation process runs; it does not show that a strategy makes money. The sample is short, and both prices and costs are simplified.

A **5% participation rate** limits simulated trading in a stock to 5% of its daily trading value. **T+1** means a stock bought today cannot be sold until the next trading day. **Five basis points** equals a 0.05% assumed cost per trade. Any unfilled amount stays in cash.

The `microcap-execution-diagnostic` experiment selects the smallest N eligible stocks from cleaned daily data using post-close market capitalization, ST status, suspension, and listing-state rules. Each decision date has an independent research clock. The input is submitted by content hash to `quant-backtest-runtime`, whose worker calls the public execution simulator in `quant-platform`.

The diagnostic uses a 5% participation rate, T+1, daily limit-up and limit-down blocking, unfilled cash, and a simplified 5-basis-point per-trade cost. Prices use the cleaned daily `adj_close` proxy. Targets, orders, fills, daily cash, and NAV ledgers remain outside the repository. Only runtime-validated ledgers are copied into the diagnostic directory, and `summary.json` records the job ID.

This diagnostic ledger is separate from historical paper returns. It is an execution feasibility check, not a live-trading result or strategy promotion.


## Appendix 4 · Small-cap Turnover History

[Canonical web source](https://runchengxie.github.io/quant-market-research/docs/research/factors/smallcap-turnover-history/)

## Small-cap turnover history, 2008–2014

[Chinese version](https://runchengxie.github.io/quant-market-research/docs/research/factors/smallcap-turnover-history.zh-CN/?lang=zh-CN)

### Plain-language takeaway

This note checks how actively smaller A-share stocks traded from 2008 to 2014. It adds background for later low-turnover and microcap studies; it does not test a strategy or show how much money could have been invested. **Turnover rate** here is the share of tradable stock that changed hands during the period. Missing historical eligibility and trading-status data limit what the sample can tell us.

This supplement uses published A-share `daily` and `daily_basic` assets from `quant-market-data-platform` to observe turnover among the N smallest stocks ranked by total market capitalization.

It supplies early-period liquidity context for the low-turnover and microcap studies. It is not a low-turnover strategy backtest. The data source, date range, ranking rule, and missing-data treatment remain part of the published research boundary.
