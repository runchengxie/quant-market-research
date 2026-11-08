# Fourth exploration validation

[English report](forward-20261108.md) · [中文报告](forward-20261108.zh-CN.md) · [Evidence hashes](forward-evidence-20261108.json)

- Frozen exports are bound by receipt and raw-response hashes. All four ETF products have finite positive price, factor and NAV observations on every expected common session; duplicate valuation dates are rejected.
- 108 product cases use matching dates and explicit return bases, cash assumptions and fees. Independent terminal-wealth and fee reconciliation agrees within 1e-12 for every case. Initial entry, non-cash rebalance legs and terminal liquidation are charged; cash is not charged as a second trade leg.
- Extended training passed its own stock and commodity calendars from 2006-02-06, after the known gaps. Only the 252-session rule has prior history for the full 2008 stress comparison; the longer rules are not backfilled. Cash yield sensitivity keeps the previously determined weights fixed.
- Canonical paper protocol hashing agrees with the registration. Tests reject past/current starts, nonfinite capital, existing registrations, pre-close marks, first marks that import prior returns, missing or rewritten dates, and reversed append-recording chronology.
- Eight focused tests cover the new accounting/registration methods and source bindings. Existing source-bound third-round tests remain unchanged.
- Website selectors are checked against all 12 fee/cash/basis combinations and nine rows per selection. Four browser tests pass at 390/1280px, including the original explorer and new product controls, languages, operating-state notices and page overflow.
- The systemd units passed verification. The timer was enabled and active; one complete three-dataset capture succeeded. Raw/receipt seals and nonempty payloads were independently checked. The pinned owner release, credential reference and machine paths remain private. No shared current/latest publication command is run.
- Independent review found missing finite-capital hardening and a recording-time inversion gap; both were fixed with regression coverage. This verifies local ingestion semantics, not the authenticity of arbitrary caller-supplied normalized owner growth data.

Full local suite passed 976 tests with 22 optional-provider skips and seven existing warnings. Website tests passed 334 cases; Astro build and static verification passed. Remote checks and the exact merge identity are recorded in the PR and external task completion record. Tests do not establish executable trades, continuous future service uptime, revision-safe historical macro values or future outperformance. Paper-price acquisition is not automated and forward outcomes remain zero.
