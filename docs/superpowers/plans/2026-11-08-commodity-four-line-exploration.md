# Commodity follow-up exploration plan

**Goal:** Explore allocation robustness, implementation, source evidence and macro environments without extending first-round claims beyond their evidence.

**Architecture:** Reuse the hash-frozen first-round owner bundle. Keep new supplier responses and original publisher documents in a new data-owner task; preserve complete runs outside Git. Add focused study modules and reviewed bilingual findings to the existing topic.

**Spec:** The four next steps approved in conversation, and `docs/research/asset-returns/china-commodity-equity.md`.

**Execution:** Inline implementation, synthetic regression tests first, then independent final code/evidence review. Existing task authorization covers implementation, PR and merge subject to repository checks.

## Fixed research choices

- Primary 2006-12-29–2025-12-31 equity-total-return/commodity-index panel remains frozen. Report annual and monthly rebalancing, commodity weights 10/20/30/40%, all complete rolling 60/120-month windows, annual-entry cohorts and contiguous subperiods. Do not optimize weights or splice removed crises into fake continuous histories.
- Count windows improving CAGR, maximum drawdown, both and neither against identical stock-only windows. Report failures and exact sample counts; overlapping windows are descriptive.
- Compute the extra annual wealth drag that exhausts the 80/20 gross advantage. Distinguish total-portfolio drag from a fee on traded notional. Rebalance-cost and collateral-rate scenarios are hypothetical, not executable fills or guaranteed cash returns.
- Inspect 159980/159981/159985 commodity ETFs, with issuer benchmark identities, NAV, distributions, market adjustments and actual common coverage. Their sector exposures cannot represent NHCI tracking. CTA availability is audited; no survivorship-biased handpicked NAV history is substituted for a complete CTA universe.
- Requery precise source gaps and inspect additional original Nanhua reports/methodology versions. New observations do not overwrite old responses or silently fill frozen runs.
- Macro regime thresholds are fixed at manufacturing PMI 50 and PPI YoY 0. Separate revised-snapshot lag diagnostics, release-event reconstructions and truly timestamped historical observations. A date label alone cannot establish historical vintage. Use actual decision sessions and strictly prior availability; no same-month publication lookahead or causal/predictive claim.

## Tasks and files

- [ ] Freeze bounded macro, cash-rate, ETF and evidence probes with parameter/hash receipts under a new owner task.
- [ ] Add failing tests in `tests/studies/test_commodity_followup.py` for window resets, missing months, joint improvement counts, cost breakeven, cash double counting, macro availability and benchmark identity. Implement focused `robustness.py`, `implementation.py`, `regimes.py` and a frozen-input follow-up runner under `src/market_research/studies/commodity_equity/`.
- [ ] Run each research line, independently reconcile selected results, preserve failures and produce one reviewed aggregate plus bilingual findings/validation records. Add a source-backed visualization using existing site facilities if useful.
- [ ] Complete Python/web checks, independent review, commit/push/PR, remote required checks and merge; clean only this task's resources.

## Review focus

Window-specific starting weights, daily versus monthly drawdown scope, complete endpoint calendars, equal fee conventions on comparators, cash included once, actual fund distribution timing, denominator/sample selection, future economic releases and unverifiable historical revisions, supplier row caps and mixed benchmarks, raw-data/privacy boundaries.
