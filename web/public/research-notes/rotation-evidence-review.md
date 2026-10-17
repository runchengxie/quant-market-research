# Weekly rotation: reproduced evidence and publication review

Twenty-one of 24 registered weekly configurations were reproduced on retained historical price panels. Three quality/dividend configurations remain unavailable because required price columns are missing. The theme-to-ETF incremental test has an implemented, tested runner but no admitted historical theme data or performance result.

The workbench separates five capabilities:

| Capability | Current evidence |
| --- | --- |
| Comparable experiments | 18 precomputed group/allocation/window combinations, using full common, last 252 and last 756 sessions |
| Theme increment at matched risk | Runner tested; real historical mappings and independently captured content/availability missing |
| Historical replay | 972 public events across two representative baselines; observed eligibility, execution states and aggregate allocation |
| Return contributions | 63 available and 9 unavailable rows; risk assets, bonds, costs and reconciliation residual |
| Research-to-web publication | Versioned schema, explicit review, three bound digests, atomic import, build validation and lazy replay verification |

## Comparability

The risk-budget and candidate-pool groups use 2017-08-28–2026-08-24, 2,182 sessions. Holdover and score groups use 2016-08-22–2026-08-24, 2,429 sessions. Input panel coverage (2015-01-05–2026-08-24) is distinct from portfolio evaluation coverage.

An uncapped fixed-slot baseline has 6.8010% annualized return on the risk group's shorter common calendar, versus 6.3653% on its own longer calendar. This difference reflects the evaluation window. The original rounded notes remain archived under their original definitions.

Within the defensive risk-budget group, uncapped versus 75%-capped configurations show 9.2001% versus 6.7048% CAGR, −20.2084% versus −8.5646% maximum drawdown, and 40.38% versus 64.17% daily-average bonds. More bonds and lower risk cannot establish superior theme selection. The cash-flow candidate and core defensive baseline have identical metrics on this common window. All results reuse historical data and remain exploratory.

## Protocol and accounting

Prices are adjusted-price valuations. Signal decisions use history through the signal date; execution is at the next observed session close. The cost scenario is 5 basis points per gross traded notional; annualization uses 252 sessions. Costs are assumptions, not broker quotes. The accounting is not an audited broker cash ledger.

Windows slice preserved daily paths without restarting portfolio state. Average bond weights are means of beginning-of-session daily weights, distinct from older event-average definitions. Return contributions link through prior NAV and sum to cumulative return, not CAGR. Public reconciliation tolerance is 1e-10; private full-precision paths are separately hash-bound.

Replay is historical explanation, not current holdings or a trading signal. First observed prices are not verified listing dates. Public replay contains approved ETF identifiers, eligibility/reasons and aggregate risk/bond weights, without private scores or security-level holdings/P&L. Blocked/no-trade events are distinguished from executions.

## Missing evidence

The pinned pool panel lacks `515910` and `512890`, so `pool-quality`, `pool-dividend` and `pool-both` cannot be reproduced. Other style ETFs are not substituted. The industry panel's 36 columns do not yet reconcile to an earlier note's 32 admitted assets and are excluded.

File hashes bind current input identity, not historical information availability. Both source panels remain unverified on independent historical availability. The theme test requires captured observation/mapping content hashes, aware availability timestamps, complete eligible mappings, identical paired evaluation calendars, matched post-optimizer signal target risk budgets and a frozen forward registration. Missing evidence produces no performance metric.

## Exact release

Evidence ID: `rotation-evidence-20261017-native-v2`.

- Reviewed source: `0c141d4c67ef7ecfbb147a352001b2742b1604e9d8c450e980a8349200a5ff61`.
- Canonical public content: `fab5418abd6477a045f485f68235b2c11a4a2ae8bff945049f40355965d963cd`.
- Canonical asset bytes: `c39991502b5e8e4dcf6ff0de3539ed1425543cedcaae1e0681289ada6fc23cad`.

The downloadable release contains the public asset and its explicit review record. Canonical numeric serialization uses at most 12 decimals. Invalid/stale review pairs fail import without replacing the last valid release. Replay downloads are also checked against the exact release hash bound into the generated page. No shared production job or trading configuration is changed by this publication.
