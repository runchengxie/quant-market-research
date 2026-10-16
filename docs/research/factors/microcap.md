# Microcaps: return evidence and underwater periods

[Chinese version](microcap.zh-CN.md)

This page describes reconstructed historical rules and risk characteristics. It is not a Wind index replication and does not represent a directly tradable strategy.

## Plain-language takeaway

The clearest result here is about risk: portfolios rebuilt from small stocks had deep losses and sometimes took years to recover their previous highs. Some early returns are still being checked, and delisted stocks, historical membership, and actual trading have not been fully reconstructed. Treat the return series as a research record, not as an index or an account result.

An **underwater period** is the time a portfolio stays below its previous high until it passes that high again. **Maximum drawdown** is the largest fall from a high to a later low. **NAV** (net asset value) is the portfolio-value series scaled to a starting level. For each measure, missing-price rules also matter.

The current source coverage extends through 2026-09-17. The next-day return audit for the minimum-market-cap proxy is computable through 2026-09-16. Portfolio sizes are N = 50, 100, 200, 400, and 800.

The [microcap execution diagnostic](../experiments/microcap-execution-diagnostic-20260928.md) uses a separate public execution-simulation ledger and must not be joined directly to historical paper returns. Differences in data cleaning, decision clocks, fills, and cost assumptions remain part of the evidence boundary.

## Research map: history, factors and execution

Public evidence synthesis reviewed on 2026-10-16. This review did not rerun the studies or extend their sample dates. The [micro-cap topic page](https://runchengxie.github.io/quant-market-research/research/microcap/) connects the following questions without treating them as one strategy.

| Question | Available public evidence | Important boundary | Next useful evidence |
| --- | --- | --- | --- |
| What did the smallest stocks return and lose? | Reconstructed N = 50, 100, 200, 400 and 800 baskets, drawdown and underwater statistics, missing-price sensitivities | Historical eligibility, company actions and delisting prices remain incomplete; strict and partial treatments have different valid sessions | Reconcile holding-level missing quotes and settlement events |
| Is the result a size exposure? | Historical style-factor research, including size and market regimes | Factor sign and long-short construction differ from a long-only micro-cap basket | Matched tail-exclusion tests with recomputed formation signals |
| What does low turnover add? | [Low-turnover evidence](low-turnover.md): common-sample controls, confidence intervals and a short forward record | Conditional association is not a causal premium; theoretical stock-group returns are not executable portfolios | Freeze prospective rules and accumulate additional observations |
| Do portfolio rules change the result? | Published 20-, 60- and 120-session window sensitivity | Repeatedly inspected historical sample; cannot select an independently confirmed optimum | Repeat frozen comparisons under consistent share accounting |
| Could the portfolio trade? | [Public execution diagnostic](../experiments/microcap-execution-diagnostic-20260928.md), cash and blocked-trade accounting | Separate short sample, adjusted-price proxy and assumed cost; not a capacity certification | Identical targets and dates, reconciled accounting and calibrated impact |
| Are small stocks equally liquid across markets? | Market-cap group traded-value and coverage comparisons; [early A-share turnover context](smallcap-turnover-history.md) | Currencies, dates and eligibility differ; turnover rate and traded value are distinct measures | Align samples, currency conversion and execution constraints |

### Keep portfolio identities separate

A vendor reference index, a daily smallest-N reconstruction, a monthly low-turnover candidate and the short execution diagnostic have different identities. Neither a shared label such as “micro-cap” nor equal portfolio size makes their results comparable. Record the sample, formation and execution clock, weighting, buffer, missing-price treatment, costs and simulator before comparing any two figures. Do not join their NAVs.

The new window-comparison chart reads `window_sensitivity` directly from the existing public `low_turnover_exploration.json` snapshot, generated on 2026-09-16 with overall coverage through 2026-07-31. Its public method describes 2015–2026 daily data, monthly formation, 40 target holdings, a 60-name buffer and a 10 bp fee. These are low-turnover window results, not the small-cap-plus-low-turnover composite. Returns and drawdowns in this snapshot are percentage values; annual turnover is a multiple. A later note with different source figures must not silently replace these values while keeping the old provenance.

### Revisions that affect interpretation

- Early reconstructions that used post-close market capitalization with same-close execution were superseded. The reconstruction now separates the decision close and next-session execution close.
- An old 2014–2015 holding interval used execution and valuation prices from different sources. That interval was removed. Early-period eligibility remains incomplete.
- Later low-turnover validation changed to next-session open through period-end close, requiring both endpoints. Its revised 86-month common sample must not be merged with older attribution tables. See the latest-validation section in the [Chinese source record](low-turnover.zh-CN.md).
- Share accounting, idle cash and delayed fills can change return and cadence rankings. Results from a weight-level screening simulator and a share ledger must retain their engine identity. An apparent gain from tighter participation limits is execution-path sensitivity, not evidence of additional signal alpha.
- The 2024–2026 sample has already been examined across several historical comparisons. It is descriptive evidence rather than an untouched final holdout.

The public revision history is preserved in the existing [follow-up research source record](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/experiments/turnover-microcap-followup-20260915.md), which explicitly marks superseded low-turnover results. Those old figures are not reused as current headline returns.

### Open comparisons and publication requirements

The recovered 0% / 10% / 20% / 30% exclusion and weighting aggregate matrix is now published in the topic report, alongside separate cash-ledger capacity outputs. Historical code and actual fees remain unbound; these retained outputs are not a same-ledger execution reconciliation. Remaining work is to authenticate the historical setup, separate size from liquidity, extreme returns, idiosyncratic volatility, turnover and quality on common support, and reconcile ideal held shares with constrained cash ledgers over identical targets and dates. The new window reconstruction matches 20/60 sessions but yields 4.22% annual return for 120, against the published 7.60%; the earlier ascending ranking is not reproduced.

For each addition, preserve a stable experiment identity, source version, sample dates, formation-time availability, universe, benchmark, metric units, costs, missingness policy, simulator and limitations. Publish reviewed aggregate outputs only. Raw vendor data, private strategy configurations and private reproduction locators remain outside this public site. A source-reported historical number without recoverable provenance should remain labeled as such until reproduced; no return series should be invented from summary metrics.
