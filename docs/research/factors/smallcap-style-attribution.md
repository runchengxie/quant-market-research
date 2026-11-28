# Small-cap signals need portfolio-level style checks

[简体中文](smallcap-style-attribution.zh-CN.md)

## Current assessment

A transparent public style decomposition is worth building. Start with holdings exposures and matched return attribution, then validate a risk forecast separately. The existing 19-factor historical snapshot is a collection of portfolio-sort results, not a complete commercial Barra reproduction. `risk_adapter.py` prepares caller-supplied panels; factor-return estimation, covariance and risk attribution already belong to `quant-platform.analytics.risk_model` and `quant-platform.analytics.factor_attribution`. Do not create a second risk engine in this repository.

This exploration reviews the low-turnover, execution-cost and liquidity evidence and adds an archived-panel breadth/exposure diagnostic. It does not add return observations, certify historical eligibility, establish an optimal holdings count or fit market impact.

## What a public style model should answer

1. **Exposure:** relative to a specified eligible-universe equal-weight or cap-weighted benchmark, what size, volatility, liquidity and industry positions did the account actually hold?
2. **Realized attribution:** with exposures known before the return interval, how much realized active return is represented by market, industry and style contributions, and what remains unexplained?
3. **Forecast risk:** does a lagged covariance/specific-risk estimate predict subsequent risk and coverage, including stress periods?

A descriptor's IC, a sorted high-minus-low return, a conditional regression coefficient and a portfolio risk contribution are different quantities. A positive factor premium does not make it an appropriate risk constraint. Regression residual return is unexplained return conditional on the model, not proof of stock-selection skill.

## Exposure diagnostic

The retained deconfounding panel has 566,283 security/formation rows and 138 monthly dates from February 2015 to July 2026. It contains archived descriptors and industry labels, without certified historical eligibility or industry-vintage evidence. The analysis compares raw low-turnover scores and the existing size/low-volatility/liquidity/return-controlled residual score. It does not recompute these archived signals or recover their original inputs.

Two universes are used: the full archived formation universe and its smallest 20% by size score. These are relative sample cohorts, not absolute microcap definitions. Within each, select descending scores at K = 10, 30, 50, 100, 150, 300 and 400. Compare equal weights and square-root rank weights. Use common formation dates across signals/scopes; do not filter on future returns. Descriptor standardization uses each full archived date's available mean and population standard deviation, with no new clipping. Show exposures relative to both the full universe and the local cohort. If any selected holding lacks a descriptor, that exposure remains unknown; it is not renormalized onto observed holdings. Unknown industries remain a separately reported bucket. Available names are resized when fewer than K qualify, with shortfalls reported.

On 134 common formation dates (June 2015–July 2026), the mean equal-weight exposures are:

| Archived universe / signal | K | Low-volatility exposure versus local universe | Size exposure versus full universe |
| --- | ---: | ---: | ---: |
| Full / raw low turnover | 50 | +0.908 | +0.699 |
| Full / controlled residual | 50 | −1.337 | +0.025 |
| Smallest 20% / raw low turnover | 50 | +0.697 | −1.176 |
| Smallest 20% / controlled residual | 50 | −0.922 | −1.183 |
| Smallest 20% / raw low turnover | 150 | +0.590 | −1.176 |
| Smallest 20% / controlled residual | 150 | −0.455 | −1.181 |

Units are full-archived-cross-section descriptor standard deviations, averaged equally across dates. Positive `lowvol_score` means the archive's lower-volatility direction. All six displayed rows have complete low-volatility/size coverage on all 134 dates. The residual row is not a calibrated alpha prediction. In the full universe, low turnover selects relatively larger stocks; within the smallest fifth it does not materially change broad size exposure as K rises. Increasing K reduces concentration but does not remove the cohort's market-wide size tilt.

Within the smallest fifth, raw low-turnover scores have mean monthly Spearman correlations of +0.477 with low-volatility score, −0.655 with traded-value activity and +0.499 with the illiquidity score. These are associations, not independent causal mechanisms. Industry labels are missing for about 14.2% of full-universe raw Top-50 weight and 15.6% of residual Top-50 weight. Unknown-industry HHI is therefore a bookkeeping diagnostic, not a fully identified industry concentration estimate.

Input SHA-256: `8dc7c10c3483163703dd1c0bf5cf03b82249d2ce471f676095ca7f2101efa3e5`. Common-date breadth-summary SHA-256: `bf172ed6743606234af7f9e568756bed7bee8058ba2acc2fc76d6b18a3f23b43`. The first unpaired-date run is retained but superseded for these comparisons.

The stronger concern is selection after residualization: removing a linear relation in the broad cross-section does not impose constraints on the highest residuals. Such tails can retain industry effects, nonlinear dependence, heteroskedasticity and missing-data selection. The result motivates direct portfolio constraints and matched controls; it does not identify a causal mechanism or show that the residual strategy loses money.

## Low turnover: evidence survives some controls, execution remains open

The source audit recovered the exact registered 86-period manifest and effect-summary hashes. In this repeatedly examined positive-PE/common-control sample (May 2019–June 2026 formations), raw low-minus-high monthly gross return is 1.3821 percentage points; after size and low-volatility adjustment it is 0.8598 points; the full listed control/regrouping stage is 1.2001 points. The full-stage 12-month-block interval is 0.8692–1.6184 points. Controls change stock ranking and membership: subtracting these stages is not a causal or additive attribution. The separate 136-period size-group comparison has a different sample and cannot be pooled with it. The 120-session window replay discrepancy also remains unresolved.

A low-turnover long-short spread can arise from avoiding high-turnover losers. Test three fully specified long-only accounts on the same dates: eligible-universe benchmark, exclusion of the highest-turnover group, and low-turnover tilt. Preserve both spread legs and the same share/cash ledger. The 86-period historical record is not untouched out-of-sample evidence. The 2021 China turnover paper's publisher abstract supports investigating the effect, but its 1995–2017 sample and 12-month signal differ from this 60-session archive. [Publisher](https://www.sciencedirect.com/science/article/pii/S0927538X21000585)

## Costs and stress: existing evidence is useful but answers narrower questions

The reviewed execution study's 2025-Q1 modeled-account scenarios already retain unfilled buys and sells. Its static quote/impact scenarios and ADV participation limits are sensitivity assumptions, not broker-calibrated execution costs. The fitness review covers two dates and 106 commonly observed securities, explicitly without verified event semantics or identified causal impact. Do not infer a universal basis-point charge or fit an impact curve from differences between these account scenarios.

The reviewed liquidity stress study defines stress as low-ADV months within each year and size bucket, not crash dates or forced-liquidation events. For the $100m–$1bn bucket in 2024, the median ADV measure in its low-activity months is 57.6% of the normal-month measure. This is a descriptive ratio, not a forecast fill fraction or a 42.4% reduction in executable capacity. Smaller buckets lack sufficient qualifying months. A complete pressure test must freeze holdings before a separately specified market/size drawdown event, retain nontrading and absent securities, align minute/quote clocks and reconcile remaining inventory. Do not replace unsold positions or infer a bid from a daily price.

## Minimal model and factor experiment

Use lagged market beta, log size and a separately specified nonlinear-size descriptor; short reversal and medium-term momentum; total and market-residual volatility; turnover, traded value and Amihud proxies. Include a historical industry classification and market intercept with an identified parameterization (drop one industry or impose a constraint). Report reference universe, winsorization, standardization, estimation weights, rank, condition number, missing exposures and residual diagnostics. Never include a composite quality factor and its components twice.

For quality, value and leverage, require announcement-dated historical financial vintages and explicit treatment of losses, negative equity and missing reports. Existing quality diagnostics cover a restricted post-2020, mainly top-800 universe and cannot establish an 18-year microcap result. Begin with low turnover, volatility, reversal/momentum and size; admit quality/valuation only after coverage is demonstrated. Keep raw and orthogonalized descriptors side by side, and test control-order sensitivity. Orthogonalizing the candidate against a liquidity risk descriptor may remove the economic effect under investigation; retain a model excluding the candidate and another including it.

Estimate factor returns on the broad eligible universe, then measure both broad-market and within-small-stock exposures. Do not standardize only within the small cohort and conclude that market-wide small-cap risk vanished. Keep equal-weight estimation as a sensitivity to capitalization weights; inspect how much weight actually reaches small stocks. Freeze interval definitions: explanatory close-to-close attribution and next-session-executable strategy returns are separate contracts.

## Research sequence and acceptance

| Workstream | What was explored here | What permits the next claim |
| --- | --- | --- |
| Historical low turnover | Hash/count audit and version reconciliation | Recovered source inputs; fixed support/missing rules; matched long-only ledger |
| Breadth/style exposure | New common-date archived-panel diagnostic | Historical eligibility and industries; unmodified formation records |
| Factor returns | Existing provider APIs and model specification checked | Lagged exposures paired with complete, reconciled return intervals |
| Risk prediction | Architecture and calibration requirements | Past-only covariance/specific risk; rolling coverage and forecast/realized-risk tests |
| Execution cost | Existing modeled/quote evidence reviewed | Matched order, arrival price, fill, fee and clock evidence; unfilled inventory retained |
| Stress/capacity | Existing low-activity evidence reviewed | Predeclared stress events and capital/participation scenarios, without survivor replacement |
| Candidate factors | Prioritized size, turnover, volatility, reversal/momentum; finance factors coverage-gated | Incremental prediction and matched net portfolio benefit, not only IC |

For each admitted factor family use ablation, common-date comparisons and missingness diagnostics. For K and weights, inspect a stable region rather than a maximum cell. Freeze the model, transformations, allocation and execution policy before genuinely new evaluation periods. Prior protocols disagree on 12 versus 24 complete holding periods; preserve that discrepancy and require a named, timestamped protocol for the next experiment. Neither count alone establishes significance. No new forward registration or production trading is performed by this exploration.

## Reproduction and source identity

Run `scripts/explore_smallcap_style_breadth.py --panel <retained-panel> --output <new-external-output>`. Exact input and output SHA-256 values, descriptor coverage and comparison dates are retained in the task manifest. Tests cover rank direction, weights, missing exposure, unknown industries, common dates and duplicate/infinite inputs. Numerical estimation remains with the existing platform provider.

Low-turnover manifest SHA-256: `9638fd5f4a3edc39896ac20dcfb7e47ddb4cd0f0d861e4033a4751e82b5f543f`; effect-summary SHA-256: `3d52f7713be407752fc0dc36252fb1830f3b214a31ac4720f8314d2a65b243e4`.

Related evidence: [factor dictionary](barra-factor-dictionary.md), [low turnover](low-turnover.md), [next experiments](../../next-explorations.md). [MSCI's CNE5 factsheet](https://www.msci.com/documents/10199/2935796a-0a80-4050-934a-12966d1e2518) describes a commercial risk model that also models factor covariance and specific risk; matching factor names does not reproduce it.
