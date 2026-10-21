# Grouped Valuation Round Two Implementation Plan

> **For agentic workers:** Use the scoped task below and the companion design. User explicitly authorizes parallel independent work. Only the coordinator commits; no shared file has concurrent owners.

**Goal:** Explain the frozen valuation portfolio differences with auditable attribution, comparable-support analysis, selected primary-source cases and honestly labelled validation, then integrate one existing topic.

**Architecture:** Read frozen external artifacts. Independent scripts write new external directories; an allowlist projection feeds the existing multilingual topic. A reviewer evaluates methodology and the final diff; the coordinator owns design, reports and Git.

**Tech Stack:** Existing locked Python, pandas, pyarrow, DuckDB and pytest; existing Astro/React/TypeScript/Vitest/Playwright toolchain. No new dependencies.

**Spec:** `docs/research/experiments/grouped-valuation-round2-design-20261021.md` and its adjacent rules JSON.

## Global Constraints

- Resume `726009bc8f6dc9b4771d5a63d1d48caf5da99328` in the existing isolated research worktree.
- No push, merge, deploy, evening-report work, source-data overwrite, credential/security edits, purchases or unbounded collection.
- Preserve all original 40 portfolios and prior outputs; no backtest regeneration.
- `revision_safe=false`, `raw_share_ready=false`; strict unknown values remain null.
- Public projections contain reviewed aggregates, no private lot identities, vendor raw amounts or machine paths.

## Review Focus

1. Lot accounting and yearly carry must reconcile, including no-fill members and old unresolved lots.
2. Entry-date cohort must map one-to-one to formation date; no historical feature uses future observations.
3. Matching excludes no members on outcomes; missing/common support and revised snapshots stay visible.
4. Sensitivities do not create cash or turn unknown strict results into known results.
5. A frozen retrospective rule is not an untouched holdout; future protocol is not a completed test.

### Task 1: Freeze design and inputs — coordinator

- [ ] Save rules, design and this plan before new result calculations.
- [ ] Create external `round2_design01/receipt.json` exclusively with actual UTC time, baseline commit and hashes of rules, design, source receipts and feature panel/members.
- [ ] Record each later rule change as a new version before affected calculation; never overwrite frozen rules.

### Task 2: Auditable attribution — attribution agent

Files: create `scripts/decompose_grouped_valuation.py`, `tests/test_grouped_valuation_attribution.py`.

Consumes `--run`, `--unresolved`, `--members`, `--rules`; produces `round2_attribution01` with lot/symbol/month/member contributions, annual carry, daily cash, selected case list, reconciliation and receipt. `private_member_outcomes.parquet` must identify portfolio/metric/quintile/scenario/symbol/entry_date/formation_date, buy state, verified intended budget, net P&L at 0/.5/1 and strict, and normalized outcome. Missing intended budget must fail or label fallback, never guess.

- [ ] Test fees, no-fill member, duplicate mapping, cross-year holding, unknown strict terminal, all-cash case, cash-year leap/calendar intervals and 0/.5/1 reconciliation.
- [ ] Implement additive decomposition and fixed case selection; run directed tests.
- [ ] Run once against existing artifacts with bounded memory and input hashes before/after; validate identities and output receipt.

### Task 3: Comparable controls and historical stability — controls agent

Files: create `scripts/analyze_grouped_valuation_controls.py`, `tests/test_grouped_valuation_controls.py`.

Consumes frozen rules, panel/members and Task 2 member outcomes; produces `round2_controls01` with primary/all-pair comparisons, full/complete/common/overlap counts, fixed quality/leverage secondary analyses, feature balance, yearly/leave-year-out/block-bootstrap results, limitations and receipt.

- [ ] Test outcome-independent support, no-fill retention, deterministic weighting, no date compression, period/announcement filter, common-sample original quintile retention, insufficient support and unknown strict outcomes.
- [ ] Implement fixed layers and optional predeclared secondary fields; never tune thresholds on outcomes.
- [ ] Run once after member schema is verified, publish aggregate results and exact unavailable fields.

### Task 4: Selected fact checks and protocol — coordinator/case agent

Files: documentation only plus `round2_cases01` evidence artifacts outside repo.

Consumes Task 2 frozen selection. Produces dated source matrix, per-case statement/state/disposal checks, known gaps, bounded research-copy corrections if verified, and forward protocol status `not_started`.

- [ ] Confirm selected identities and retained positive/negative/risk roles before browsing.
- [ ] Query existing evidence, then issuer/exchange primary documents; retain URLs, exact evidence dates and quotes only as needed.
- [ ] Separate event/announcement/observation dates, retrospective facts and historical eligibility; record not-found outcomes.

### Task 5: One topic and acceptance — topic agent

Files: exclusively `web/`; create `valuation-round2` data/lib/content/component/preparation/tests and modify existing overview/registry/styles only as needed.

Consumes reviewed Tasks 2–4 and prior `ledger_unresolved01`, preserving existing topic and cashflow links. Produces `valuation_round2.v1` allowlisted aggregate and one-topic evidence directory with explicit status tags.

- [ ] Implement schema and boundary tests using synthetic fixtures; reject unsupported strict results, identity/raw amount/path leakage and malformed sensitivity fractions.
- [ ] Project actual reviewed results with source/rules receipts; no placeholder numeric conclusions.
- [ ] Run node tests, applicable type check, build:pages, related e2e on exclusive port4591 and desktop/mobile visual review.

### Task 6: Independent review, seal and native report — coordinator/reviewer

- [ ] Review each task for spec and code quality, address important findings, retain unresolved limits.
- [ ] Produce final diff from baseline for a fresh whole-branch reviewer.
- [ ] Run full Python/Ruff/diff checks and use final web acceptance evidence; avoid unnecessary repeated full runs.
- [ ] Commit only the isolated branch, bind final source/tests/artifact hashes, deliver readable Chinese report through official Library upload.

## Dependency and ownership review

| Tasks | Shared interface | Ruling |
| --- | --- | --- |
| 1→2/3/4/5 | Frozen rules/hash | All implementations consume one coordinator-owned immutable version. |
| 2→3 | Member outcomes | Formation date comes from members; no-fill members retained; schema finalized before controls run. |
| 2→4 | Case selection | Primary contrasts and ranking fixed before contributions calculated; no discretionary backfill. |
| 2/3/4→5 | Public aggregate | Web agent owns all web files and waits for reviewed numerical results. |
| 2/3 | Python scripts/tests | Distinct owners and files; no concurrent shared edits. |
| 1/4/6 | Docs/Git | Coordinator alone edits design/report and stages/commits. |

Ruling: use the explicitly requested parallel workflow for independent file owners, despite generic skill serial-implementation guidance. Cost if boundaries are wrong: integration rework; final method review and combined tests remain required.

Ruling: current historical industry is not eligible for primary controls; dated revised financial fields are proxies with revision risk. Cost: a narrower, less causal explanation than a complete historical industry/financial dataset could support.

Ruling: no untouched historical holdout can currently be established. Report fixed retrospective stability plus an unexecuted forward protocol; this forgoes any claim of out-of-sample success.
