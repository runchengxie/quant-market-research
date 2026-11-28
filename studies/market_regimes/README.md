# Market states: availability-aware baseline

[简体中文](README.zh-CN.md)

**Evidence status: synthetic method validation only.** This study supplies a
simple trend/volatility/dispersion classifier with a fixed calibration window.
It has not established CSI1000 risk predictability, trading value or unseen
performance. No forward observation window is registered by this document.

Use `market_research.studies.market_regimes.classify_market_states`. Supply
`feature_time`, timezone-aware `available_at`, `trend`, nonnegative
`realized_volatility` and `dispersion`; explicitly declare asset identity,
price/total-return basis, calibration end, minimum observations and quantile.
Every decision must follow calibration. Thresholds fit once on complete rows
visible by training end. A decision uses the latest feature observation strictly
available beforehand. Missing latest features do not fall back to an older
complete row. All timestamps are normalized to UTC in output.

The return value has `states` and `calibration`. States separate `state_label`,
missing `state_probability` and `change_event` (a descriptive label switch, not a
statistical change-point finding). Missing observations break transition chains.
Calibration carries training boundaries, thresholds, asset identity and a content
hash. The mechanism cannot verify historical vintage from timestamps alone;
`historical_vintage_verified` therefore remains false.

## Before a CSI1000 run

Freeze feature formulas and lookbacks before evaluating outcomes. Confirm the
index price/total-return identity, actual trading calendar, constituent
eligibility, corporate-action basis and cross-sectional coverage. Dispersion
must use the point-in-time eligible universe, not current constituents. Source
observation time and vendor retrieval time are different. Do not backdate a
revised macro snapshot to its original period.

Predeclare the comparison windows and simple baseline. Measure state duration,
switch frequency, missing-state coverage, and subsequent drawdown/tail outcomes
with uncertainty and sample counts. Define transition latency against an
explicit event reference before measuring it. Do not select thresholds using
those outcomes. Follow-up HMM probabilities must be filtered at the decision,
not smoothed using the whole sample. Risk association does not prove causality
or net timing returns.

## Crowding intake

Audit existing owner-produced style proxies before extending them. Record the
source, lag, universe, liquidity coverage and whether evidence comes from
returns, holdings or actual trading. Return-only indicators must be labeled
return-implied crowding. Low pair correlation does not prove independent
failure risk. Reuse approved aggregate evidence only; no private signals or
portfolio rules belong in this public study. See the [intake and resumption
criteria](../../docs/research/literature-intake-20261128.md).
