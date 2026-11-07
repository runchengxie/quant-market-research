# China commodity futures and equity returns

[Chinese version](china-commodity-equity.zh-CN.md)

## First-round finding

In the gap-free December 2006–December 2025 sample, equities compounded faster than commodities. A fixed 80/20 monthly equity/commodity mix reduced maximum drawdown from 72.04% to 65.91%, with gross CAGR of 6.54% versus 6.45% for equities. Collateral interest and calibrated implementation costs remain unresolved.

| Comparison | Commodity | CSI 300 total return |
| --- | --- | --- |
| Historical CAGR, 2006-12-29 to 2025-12-31 | 4.01% | 6.45% |
| Historical daily maximum drawdown | −51.94% | −72.04% |
| 2026 YTD, ending November 6 | 7.24% | −10.57% |

**Evidence stage is descriptive index history.** The attempted earlier full sample failed source/calendar checks and remains separately recorded. Sector histories have different starts. Seven year-end publisher point checks passed, but complete annual-return and historical-methodology reconciliation remain open. No investable futures-account result is claimed.

Read the [full findings](https://github.com/runchengxie/quant-market-research/blob/main/studies/china_commodity_equity/findings-20261107.md), [reviewed aggregate](https://github.com/runchengxie/quant-market-research/blob/main/studies/china_commodity_equity/reviewed-summary-20261107.json), and [reproduction record](https://github.com/runchengxie/quant-market-research/blob/main/studies/china_commodity_equity/validation-20261107.md). Next priorities are unresolved source gaps, original annual-return conventions and contract-level implementation.

<details>
<summary>Registered research protocol</summary>

This topic asks whether Chinese commodity futures indices improve the long-term outcomes of an A-share portfolio. This paragraph records the original registration; current evidence is above. The target historical sample is December 2004–December 2025; actual comparisons must use verified common coverage. A separate recent panel will end on the latest verified common session and never extend the frozen historical sample silently.

## Questions and scope

| Module | Planned comparison | Main unresolved evidence |
| --- | --- | --- |
| Returns | Commodity composite and sectors versus equity total returns; price returns as a separate diagnostic | Index definitions and common history |
| Cycles and losses | Drawdowns, recovery and rolling holding periods | Daily coverage and censored recoveries |
| Commodity structure | Industrial, agriculture, precious metals, nonferrous, ferrous and energy/chemicals | Historical weights needed for contribution attribution |
| Diversification | Monthly correlations, rolling 36-month correlations and negative equity months | Diversification may change across regimes |
| Allocation and implementation | Fixed commodity weights of 0%, 10%, 20%, 30%, 40%; indices versus investable instruments | Roll, collateral, costs and product histories |

The primary candidates are the Nanhua commodity composite, industrial, agricultural and precious-metal indices, paired with CSI 300 total return. CSI All Share and CSI 1000 total return are secondary comparisons if their identities and coverage can be verified. Supplier identifiers are candidates until checked. An unavailable total-return series must remain unavailable rather than be replaced silently by a price index.

## Return definitions

Establish from the original methodology whether each commodity index includes contract rolls, collateral interest and costs. Do not add roll returns a second time to a series that already incorporates them. A back-adjusted futures price is a diagnostic series, not an investable account. Separate index-level observations, fully collateralized unlevered futures simulations, and ETF or CTA net values. CTA can take short positions and is not a commodity long-only proxy.

Use CNY nominal returns first. CPI-deflated results require a verified chained price level. Stock total return includes dividend reinvestment; price return is always labeled separately. Index comparisons do not establish attainable investor returns.

## Fixed analysis rules

- Use exact verified common trading sessions for daily comparisons and verified final common sessions for monthly endpoints. Publish calendar differences and missingness; never forward-fill prices or zero-fill returns.
- Report the last common week, calendar month, year to date and trailing 12 months with exact endpoints. Historical results include calendar years, common inception, fixed 3/5/10-year endpoints and rolling 12/36/60/120-month holdings. Missing windows remain unavailable.
- Calculate geometric wealth, CAGR using actual elapsed years, sample daily volatility annualized by sqrt(252), daily peak-to-trough drawdown, recovery duration and unrecovered censored episodes. Report monthly drawdown separately. Rolling loss frequencies use overlapping windows and are descriptive, not independent future probabilities.
- Report worst annualized 60-month return, nominal loss-window share, monthly Pearson correlation and rolling 36-month correlation. Constant or insufficient samples produce unavailable values. Sharpe ratios require a documented contemporaneous CNY cash series and matching periodic excess returns; otherwise omit them.
- Rebalance fixed equity/commodity weights at each common month end, applying the new weights to the next month's returns. Compare annual rebalancing as a sensitivity. Show 0/50/100 basis-point annual wealth drags as hypothetical cost sensitivities, not calibrated execution costs. Do not select weights using realized optimal performance.
- Treat historical cycle labels as retrospective hypotheses. Define any macro regime before testing, retain original release timestamps and revisions, and align PMI/PPI to information actually available. Correlation does not establish a predictive or causal relationship.

## Data and reproducibility

`quant-market-data-platform` owns supplier ingestion and raw receipts. The candidate Tushare inventory is `fut_index_daily`, `index_daily`, `fut_basic`, `fut_daily`, `fut_mapping`, `fut_daily_adj`, `fut_adjfactor`, then `fut_wsr`, `fut_inv_weekly`, `cn_pmi`, and `cn_ppi`. Account points do not certify current permission, complete coverage or redistribution rights. Verify official documentation and actual responses before using any endpoint; no new API access is asserted here.

Retain inputs and full outputs under the configured owning project data directory, `DATA_ROOT/quant/quant-market-research/china_commodity_equity/<task-id>/`. Keep authoritative raw data with its owner and reference it by receipt instead of copying it. Each run records source code revision, provider and methodology versions, retrieval time, series identity, currency, return basis, calendar, observed coverage, missing dates, input hashes and output hashes. Never change a shared latest/current alias as part of an exploratory run.

Reusable accounting may come from `quant-platform`; this topic owns its research definitions. The existing long-horizon asset study remains frozen. Methods may be reused after suitability checks, but its conclusions and publication manifest are not extended by this registration.

## Validation and next action

First audit endpoint identity, permission, methodology and history. Then freeze inputs, reproduce daily/monthly endpoints independently and reconcile selected annual returns with original publishers. Test return compounding, fixed-weight accounting, missing-window handling and censored recoveries before producing results. Retain baseline-versus-sensitivity tables, exact tested code/input revisions and an explicit list of failed checks.

Publication requires reviewed derived aggregates, data rights, a reproducible run receipt and a conclusion register linking each claim to its evidence and limitations. Conversation figures and third-party annual tables are unverified leads; they are not accepted input or findings. No previous claim that commodities outperformed equities is inherited.

The first deliverable is a coverage and return-definition audit, followed by a common-sample descriptive comparison. Futures implementation and macro attribution follow only when their own data gates pass. The machine-readable study contracts are in the [study directory](https://github.com/runchengxie/quant-market-research/tree/main/studies/china_commodity_equity); related evidence is in the [existing asset-return study](https://github.com/runchengxie/quant-market-research/tree/main/studies/asset_returns).

</details>
