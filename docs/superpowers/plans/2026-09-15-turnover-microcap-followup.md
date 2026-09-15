# Low-Turnover Attribution and Microcap Drawdown Follow-Up Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the existing low-turnover factor evidence into a staged attribution and investability readout, and extend microcap underwater-risk evidence as far back as the available daily data can support.

**Architecture:** Reuse audited derived factor artifacts from the separate `quant-research` repository as read-only inputs. In `quant-market-research`, add a tested underwater-episode summarizer and a reproducible analysis runner that consumes local-derived NAV and historical market data, writes full outputs outside Git, and stores only methods, compact reviewed results, and provenance in Git. Treat the 2008–2014 series as a separate historical regime and fail closed when price marks or status evidence are insufficient.

**Tech Stack:** Python 3.13, pandas, DuckDB, pytest, Parquet/CSV/JSON, Markdown.

**Spec:** User-approved follow-up to the recommended low-turnover attribution and 2008+ microcap underwater-risk studies; repository constraints are in `AGENTS.md` and `docs/data-storage-and-publication.md`.

## Global Constraints

- Raw supplier data, credentials, complete stock-level panels, and large run outputs stay outside this repository.
- Reconstructed historical status is labelled reconstructed and is not described as revision-safe PIT.
- A missing holding price is never silently dropped or replaced with an unlabelled return assumption.
- Factor residualization, double sorts, and regime comparisons are conditional diagnostics, not causal identification.
- Do not publish unverified local `SMICRO.TI` or other daily index inputs as official index data.
- The 2015–2023 development sample and 2024+ descriptive sample must remain separately identified.

---

### Task 1: Freeze provenance and run scope

**Files:**
- Create: `docs/research/experiments/turnover-microcap-followup-20260915.md`
- Read: `docs/data-storage-and-publication.md`
- Read: `web/public/data/barra/historical_report.md`
- Read-only external reference: `<quant-research-repo>/docs/research/experiments/style_factors/low-turnover-factor-diagnostics-2008-2026.md`
- Read-only external reference: `<shared-data-root>/research/style_factors/microcap_100_20260911/`

**Interfaces:**
- Consumes: Existing reported factor summaries and their run manifests; historical and clean daily source manifests.
- Produces: A provenance table with source path, range, owner commit/data fingerprint when present, quality status, and permitted interpretation.

- [ ] Confirm current low-turnover stage artifacts against their run metadata; record hashes and reject artifacts with missing or mismatched manifests.
- [ ] Confirm whether a true 2008–2014 smallest-N return series can be built with the required as-of market-cap, adjusted-close, listing, ST, and suspension inputs.
- [ ] Freeze N values `50, 100, 200, 400, 800`, the reported regime windows, and missing-mark handling before computing underwater outcomes.
- [ ] Run only diagnostics supported by the frozen input contract; list unavailable characteristics explicitly instead of proxying them silently.

### Task 2: Summarize low-turnover deconfounding and conditional sorts

**Files:**
- Modify: `docs/research/experiments/turnover-microcap-followup-20260915.md`
- Read-only external inputs: `candidate_turnover_deconfounding.csv`, `candidate_turnover_anatomy.csv`, `candidate_size_turnover_double_sort.csv`, `candidate_size_turnover_sequential_sort.csv`

**Interfaces:**
- Consumes: Existing 2015–2023 development and 2024–2026 descriptive formation-date artifacts on common support.
- Produces: Per-stage rank-IC and low/high-leg summaries plus 5×5 conditional low-minus-high spreads by size bucket and period.

- [ ] Recompute aggregate tables from the versioned CSV inputs with the final formation date removed when no forward outcome exists.
- [ ] Report raw, size, size+low-volatility, +activity/illiquidity, and +momentum/reversal stages; show low leg, high-leg avoidance, long-short spread, and sample size together.
- [ ] Aggregate both the independent and sequential size×turnover sorts by size quintile and period; report each bucket's low-minus-high turnover spread and the share of positive formation months.
- [ ] Interpret residual return decay, sample support, factor sign conventions, nonlinear residual exposures, and costs without calling the regression a causal model.

### Task 3: Build tested underwater episode distribution summaries

**Files:**
- Create: `src/market_research/underwater.py`
- Create: `tests/test_underwater.py`
- Modify: `src/market_research/__init__.py` only if the package exposes public helpers there.

**Interfaces:**
- Consumes: A strictly ordered `date, nav` series and an optional named episode table.
- Produces: `build_underwater_episodes(nav) -> pandas.DataFrame` with peak, first-underwater, trough, recovery, underwater-session count, peak-to-recovery sessions, max drawdown, and right-censor status; `summarize_underwater(episodes) -> dict` with completed/right-censored counts, duration quantiles, and threshold probabilities.

- [ ] Write deterministic tests for a recovered episode, multiple peaks, one-session episode, no drawdown, and an episode censored at sample end.
- [ ] Run `uv run pytest tests/test_underwater.py -q` and confirm the tests fail because the new helpers are absent.
- [ ] Implement the minimal two helpers with stable date ordering, explicit equal-high recovery semantics, and separate counts for time-under-water versus peak-to-recovery duration.
- [ ] Run the focused tests and `git diff --check`.

### Task 4: Reconstruct and audit 2008–2014 microcap daily marks

**Files:**
- Create: `scripts/analyze_microcap_history.py`
- Create: `tests/test_microcap_history_analysis.py`
- Modify: `docs/runbook-local.md`
- External outputs only: `<external-research-output>/outputs/microcap_history_2008_2026/`

**Interfaces:**
- Consumes: Daily bars, daily-basic valuation, adjustment factors, exchange calendar, point-in-time listing dates, historical name-change/ST status, and suspension-event records.
- Produces: `microcap_nav_by_n.csv`, `microcap_underwater_episodes_by_n.csv`, `microcap_data_coverage_by_n.csv`, `microcap_underwater_summary.json`, and a manifest with source hashes.

- [ ] Add fixture tests that prove formation-date market caps choose the expected bottom-N names, next-session returns do not use formation-session return, explicit suspensions are not silently removed, missing unclassified terminal marks fail closed, and each N gets a separate NAV.
- [ ] Run the focused tests and observe the expected failures before implementation.
- [ ] Implement DuckDB extraction in temporary tables, key uniqueness checks, point-in-time status filtering, and adjusted-close validation; keep only aggregate outputs in memory.
- [ ] Produce a strict quoted-constituent coverage table and a marked-to-last-price diagnostic only for explicitly identified suspended rows; quarantine any remaining unknown missing mark from the headline NAV.
- [ ] Reconstruct 2008–2014 first, then construct a method-matched 2015+ series and compare its overlap against the existing 2015+ clean reconstruction before joining histories.
- [ ] Produce N=50/100/200/400/800 return streams only for intervals passing the same price-mark and status gates; otherwise report the exact blocked dates and do not interpolate NAV.
- [ ] Run the analysis in the external output directory, verify hashes and row counts, and retain detailed stock-level intermediates outside Git.

### Task 5: Compare historical underwater and market-regime evidence

**Files:**
- Modify: `docs/research/experiments/turnover-microcap-followup-20260915.md`
- External outputs: `microcap_underwater_episodes_by_n.csv`, `microcap_underwater_summary.json`

**Interfaces:**
- Consumes: Matched method-specific daily NAV for the validated 2008–2014 and 2015+ portions, plus the current 2015+ reconstruction for reconciliation.
- Produces: Episode-level peak/trough/recovery chronology, completed and right-censored duration distributions, and descriptive subperiod metrics for 2008–2012, 2013–2016, 2017–2019, 2020–2023, and 2024+.

- [ ] Report both underwater sessions and peak-to-recovery sessions, longest completed and longest observed episode, MaxDD, and P(T>1/2/3/5 years).
- [ ] Separate episodes that began before a regime window from episodes that started inside it; label boundary censoring and never reset global highs silently.
- [ ] Show N dose-response for returns, MaxDD, and underwater durations; treat shifts in weighting, turnover, and capacity as parallel diagnostics.
- [ ] Cross-check the unverified daily synthetic micro index against the public annual reference; use it only as a quarantined reference sensitivity if provenance remains absent.

### Task 6: Verify and deliver

**Files:**
- Modify: `docs/research/experiments/turnover-microcap-followup-20260915.md`
- Modify: `docs/runbook-local.md`

- [ ] Run focused tests and the repository's full `uv run --extra duckdb --with pytest pytest -q` suite.
- [ ] Run `git diff --check` and verify no local config, raw data, generated bulk output, or credentials entered Git.
- [ ] Review all headline results against source manifests and the written quality status; report unavailable/blocked intervals plainly.
- [ ] Commit and push the task branch, create a PR to `main`, and follow repository review/check/merge/cleanup rules only if remote access succeeds.
