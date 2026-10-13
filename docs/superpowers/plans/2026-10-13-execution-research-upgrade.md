# Execution research implementation plan

**Goal:** Make current execution evidence easier to read and run reproducible, funded minute execution scenarios on available historical data.

**Architecture:** Data ingestion and source fitness remain in quant-market-data-platform. A strategy-neutral opt-in minute execution mechanism lives in quant-platform. This repository owns public small-cap diagnostic targets, scenario comparisons and reviewed aggregate publication.

**Authorization:** The owner requested implementation of the preceding page, data and backtest recommendations. Retain existing private strategy and production boundaries. No real orders are placed.

## Constraints

- Separate task worktrees; merge providers before consumers; never publish a dependency on an unmerged branch.
- Inputs, detailed orders and generated results remain under configured external data roots. Public outputs contain reviewed aggregate fields only.
- Preserve static cost coverage and conditional-sample caveats. Neither historical bar execution nor reconstructed PIT establishes live capacity or causal impact.
- Decision data precede entry; minute OHLCV is an ex-post fill proxy, never an input to an earlier release schedule.
- Use raw execution prices, share volume and CNY amount; corporate cash/share rights and missing-event gates remain explicit.
- Current minute partitions cover complete 2024/2025 calendars, but only 185 sessions in 2023. Audit before claiming full coverage.

## Tasks

- [x] Inspect repository instructions, assets and baseline research tests (33 passed).
- [x] Consolidate the current web presentation; remove stale three-day display, preserve historical sources; validate both locales and mobile layout.
- [x] Audit source coverage and reuse historical constraints; download only missing eligible source slices into a new task directory.
- [x] Add opt-in generic minute execution with fixed release schedule, latency, per-bar volume cap, cash, fees, lots, T+1, limit rules, pending order lifecycle and corporate rights. Test temporal and accounting invariants.
- [x] Add research input preparation with dated eligibility, raw marks, corporate-event validation, buffer and rebalance variants, minute coverage and explicit source hashes.
- [x] Run 2024 H2/2025 public small-cap scenarios with capital, frequency, buffer and execution-window comparisons. Keep any incomplete run visibly incomplete.
- [x] Validate private ledgers; publish reviewed aggregates and methodology on the existing execution topic.
- [ ] Run required checks, review combined changes, commit/PR/merge providers first, verify deployment and clean only task resources.

## Review focus

Future records must not change prior fills; incomplete dividends must not vanish; volume cannot be reused by sibling orders; zero/partial fills cannot disappear; fees must alter funded orders; unknown eligibility and missing source days cannot be treated as normal trading.

## Reviewed outcome

18 scenarios completed across 125-session 2024 H2 and 243-session 2025, independently audited with zero ledger errors. Full 2024 remains blocked by 21 unresolved factor events after re-observation; 2023 minute coverage remains partial. See [methodology](../../execution-minute-study.md). Data provider PR #91 merged at `52179bab37e73012e43bcde92d0cf439cc86bbc8`. Public presentation removes stale three-day panels while retaining archival sources.

Execution provider PR #153 merged at `fc718cb23b622ebb96d20da1e20e9311e5c4e4f2`. Formal locked install passes 356 research tests; provider passes 1727 tests (13 skips), data owner 1174 (1 skip). Website passes 135 unit tests, static verification and 16 affected browser checks, including 8 execution-topic checks. Final remote publication verification remains pending.
