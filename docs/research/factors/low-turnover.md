# Low-turnover stocks and subsequent returns

[Chinese methodology and historical records](low-turnover.zh-CN.md)

Evidence snapshot dated 16 September 2026. Text and source hashes checked on 22 October 2026. This edit adds no new observation months.

## Current findings

In the reviewed historical sample, the low-turnover group averaged 1.38 percentage points more per month than the high-turnover group. After the full listed controls and regrouping on the adjusted signal, the gap was about 1.20 points. After-cost portfolio performance still requires a consistent trading test.

The 86 selection dates run from May 2019 through June 2026, with holding periods from June 2019 through July 2026. Positive PE and usable control data restrict the common sample. The repeatedly examined history does not establish performance for all A-shares or in an untouched test set.

## Signal and result version

The main signal averages daily share turnover over the preceding 60 trading sessions, excluding selection day. The reviewed revision fixes deciles before filtering for future return availability. Controls change the ranking and membership of each group. Missing returns and historical revisions remain limitations.

| Signal stage | Low-turnover end return | High-turnover end return | Mean monthly gap in percentage points | 95% block interval in percentage points |
| --- | ---: | ---: | ---: | ---: |
| Raw low-turnover signal | 1.08% | -0.30% | 1.38 | 0.94 to 1.92 |
| Size control | 1.29% | -0.34% | 1.63 | 1.23 to 2.06 |
| Add low volatility | 0.73% | -0.13% | 0.86 | 0.57 to 1.18 |
| Full listed controls | 1.03% | -0.17% | 1.20 | 0.87 to 1.62 |

The low-turnover-score end is the group favored by the low-turnover signal, including after adjustments. The full controls include size, low volatility, trading activity, Amihud illiquidity, momentum, reversal, beta and valuation. Intervals resample 12-month blocks 2,000 times. They describe uncertainty within this history and do not account for every specification tried during the research.

The separate joint cross-sectional regression estimates about 0.60 percentage points more next-period return per one-standard-deviation higher low-turnover score, with positive coefficients in 76.7% of months. This is a conditional historical relationship, without a causal or executable-return conclusion.

Earlier displayed values, including a 1.21-point full-control gap, remain labeled in the Chinese historical record. The 1.1795-point result belongs to the intermediate stage before beta and valuation. The full reviewed stage is 1.2001 points.

Manifest SHA-256 `9638fd5f4a3edc39896ac20dcfb7e47ddb4cd0f0d861e4033a4751e82b5f543f`.

Effect summary SHA-256 `3d52f7713be407752fc0dc36252fb1830f3b214a31ac4720f8314d2a65b243e4`.

## Later observation and registration limits

The archive dated 16 September contains one completed August 2026 window and one pending window. Its July formation-data cutoff does not establish that registration occurred before August, particularly as the manifest references a September data product. Verifiable pre-period registration evidence is still needed. The archive also does not prove that records were altered retrospectively. Retain this window as a later observation until that evidence is recovered.

The protocol requires 24 completed months, but month count alone does not establish reliable performance. Effect size, variability and the number of specifications tried also matter.

## Trading simulations and next tests

Theoretical long-short spreads and net long-only simulations differ in portfolio direction, construction and accounting. Their difference cannot measure trading costs. Test execution constraints with a matched signal, universe and period, changing only the execution assumption.

ADV20 is average traded value over the prior 20 sessions. Participation and slippage settings remain scenarios without broker execution calibration. Portfolio turnover measures the strategy's own trading and differs from stock-level share turnover.

Compare a benchmark with portfolios excluding the highest-turnover group or favoring low turnover under one ledger and cost model. The existing exclusion test found only a small difference, about 5.46% versus 5.33% annualized net returns. Preserve timestamped registration before future holding periods and retain every specification tried.

The 120-session snapshot reports 7.60% net annualized return. A later same-input replay gives about 4.22% at a 90-observation minimum and 6.26% at 45. The original run remains unrecovered and the discrepancy is unresolved. Retain the plot as a historical record rather than selecting a best window from it. [Window review](https://runchengxie.github.io/quant-market-research/research/microcap/#microcap-window-evidence)

The Chinese companion retains the complete early definitions, window tests, execution scenarios, conflicting archives and reproduction instructions.

## Method references and applicability

Harvey, Liu and Zhu (2016) discuss multiple testing in factor discovery. This remains relevant to repeated specification searches, without imposing a universal significance cutoff. [Paper](https://people.duke.edu/~charvey/Research/Published_Papers/P118_and_the_cross.PDF)

Frazzini, Israel and Moskowitz's Trading Costs, dated 7 April 2018, calibrates models with institutional executions. The calibration approach remains relevant; its developed-market parameters do not validate current A-share costs. [Paper and publication information](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3229719)
