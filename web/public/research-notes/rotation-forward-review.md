# Rotation follow-up: sources, methods and review

The follow-up recovers two missing ETF histories and makes all 24 existing weekly configurations runnable. It adds cost and execution-delay diagnostics and a registered manual forward ledger. It does not supply a validated theme advantage or prospective returns.

The old 13-column pool panel lacked 515910 and 512890. Both were recovered from the data owner's retained adjusted daily snapshot. Adjusted prices for the overlapping CSI 300 and Treasury references match the old panel exactly. The new panel has 15 columns and preserves the old calendar. Recovery proves snapshot identity, not historical information availability. First observed prices do not independently establish official listing dates.

The industry price panel contains 36 columns. The original snapshot rule admits 32 assets; four columns fail the median-amount threshold of 10,000 in source units. Their snapshot medians are 1,892.617 (159328), 2,388.208 (159827), 686.346 (159931) and 2,695.391 (512220). This resolves the count discrepancy. Full-history liquidity summaries are not a historical point-in-time liquidity test; the industry panel is not added to this robustness matrix.

## Reading the diagnostics

The matrix contains 24 configurations, costs of 0/5/10 basis points and execution at the first or second observed session close after each signal. Delays alter actual fills and holdings. Costs are charged on gross traded notional, and are scenarios rather than broker quotes. Cost repricing reuses actual ledger turnover after a regression proved parity with separate engine runs; it would need revalidation for a future cost-aware optimizer.

There are 34,314 strategy/window records: 26,724 available and 7,590 unavailable. There are 12,924 benchmark/window records: 9,768 available and 3,156 unavailable. These are overlapping diagnostics, not independent experiments. Missing records are not assigned zero returns. Complete calendar years, trailing 252/756-session windows and monthly rolling samples retain actual warmed holdings. A final partial-month snapshot is dated explicitly. Existing parameter values are a coarse sensitivity set, not a parameter search.

Risk and pool comparisons span 2017-08-29–2026-08-24, 2,181 sessions, aligned after every selected variant's first execution, including delayed execution. The earlier release begins a day earlier and has 2,182 sessions. It remains a separate source vintage; comparisons with changed calendars suppress numerical deltas.

At 5 bps, the defensive core pool has 6.7141% annualized return and -8.5646% maximum drawdown with one-session execution, versus 6.4979% and -10.1258% with two-session execution. Recovered quality/dividend/combined candidates have one-session annualized returns of 6.3438%, 6.4124% and 6.0578% on that same window. These reused historical observations do not select a new preferred strategy. An apparent advantage of another execution delay elsewhere in the matrix is also not prospective evidence.

Benchmarks are CSI 300 ETF buy-and-hold, Treasury ETF buy-and-hold, and static initial 50/50 equity/bond allocation with drift and no rebalancing. Entry cost occurs at each actual reference path start and is not charged again at a later evaluation slice. A fund cannot supply returns before its observed history. After observed inception, the previous valuation may carry for one session, matching the strategy; longer gaps make affected windows unavailable. Mean bond exposure uses daily beginning-of-session weights. Cost drag is a cumulative return difference on identical holdings, not an annual expense. Risk/bond/cost contributions reconcile to cumulative return, not to CAGR or causal selection value.

## Forward and theme status

The manual shadow ledger is registered to begin on 2026-10-23 for the existing fixed-base and pool-core baselines. It has zero captured and settled weeks. Current retained prices end on 2026-08-24 and cannot support an October prospective signal. A current source receipt and timely capture are still required. The workflow installs no unattended schedule and places no orders. Missing captures and separate baseline coverage remain visible.

Theme capture preparation preserves original content hashes, actual capture time and dated mapping versions; preparation does not certify independence. Historical mapping and independent availability evidence remain missing. The theme result is blocked and its metrics are null. A later admitted paired diagnostic must keep identical calendars and distinguish target budget matching from realized exposure and execution differences.

## Release review

The source audit recomputed all 144 common-window returns, annualized returns and drawdowns from retained daily paths and checked weighted returns minus recorded costs. Maximum daily accounting residual was zero. Failed/interrupted runs remain retained privately; only the complete reviewed aggregate projection is published.

Release: `rotation-forward-20261017-v1`.

- Reviewed source SHA-256: `6a0c7806bae354cd1880422a3cc91eb4bf7f9c58c7939725799b7e899ea09ec8`.
- Canonical content SHA-256: `199f6985959f15a18c0b9c089a0b3500846b7b533ac1f93e2f49bb554f856ce2`.
- Canonical asset bytes SHA-256: `40fdead4de2ef96a2886e439bcac5c5b1681f84da38ab181e7163e8a24604e8a`.

The public contract excludes source filesystem paths, raw provider rows, raw theme text, private scores, security-level shadow positions and per-security P&L. Immutable reviewed assets are indexed only after verification; a failed import preserves the prior valid index. The original release and archived research remain available. Browser calculations filter and compare reviewed results; they do not run a new backtest.
