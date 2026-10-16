# Liquidity Evidence Rebuild Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans inline. The owner authorized progression of the previously identified evidence gaps.

**Goal:** Replace unverifiable historical comparisons with reproducible, audited descriptive evidence from available local inputs.

**Architecture:** DuckDB normalizes read-only market inputs into task-specific research intermediates. Tested liquidity feature/aggregation functions and a reviewed exporter produce small public summaries; the existing interactive explorer displays provenance, grain and coverage.

**Tech Stack:** Python, DuckDB, pandas, Parquet, Jupyter, Astro/React/TypeScript, Playwright.

**Spec:** `docs/superpowers/specs/2026-10-16-liquidity-rebuild-design.md`

## Global Constraints

- Inputs remain read-only; task outputs use the owning project's external data directory.
- No raw vendor rows, security identifiers or private paths in published summaries.
- Prior 20 contiguous observed market sessions; no current-session turnover.
- FX date strictly earlier than observation date; no guessed correction of old totals.
- Retrospective/exploratory evidence is not calibrated executable capacity or historical PIT proof.

## Review Focus

- Duplicate security/date keys and one-to-many valuation joins must fail explicitly.
- Missing sessions cannot silently become zero turnover or extend the rolling window.
- Pooled unique stock counts can overlap buckets; security-day observations must reconcile.
- JP share coverage and historical eligibility limitations must remain visible.
- Pending/absent markets cannot be substituted with a different date or source.

### Task 1: Source receipts and feature contract

Files: `src/market_research/liquidity_rebuild.py`, `tests/test_liquidity_rebuild.py`, `scripts/rebuild_liquidity_evidence.py`.

- [x] Test lagged native mean/median turnover, calendar continuity, prior cap, duplicate keys and strict-prior FX conversion.
- [x] Normalize bounded local input columns and expose source profiles, exclusion counts and immutable receipts.
- [x] Generate four-market feature intermediates with no changes to source assets.

### Task 2: Aggregate, independently review and publish

- [x] Test latest/common-date snapshots, pooled security-day grain, empty groups and publication boundaries.
- [x] Generate source-hashed external results and a companion review notebook.
- [x] Independently recompute published counts/quantiles and archive the inherited release.
- [x] Publish reviewed aggregates and method/coverage metadata only.

### Task 3: Website and research evidence

Files: liquidity types/quality checks/explorer/catalog, bilingual audit notes and existing execution source receipts.

- [x] Display rebuilt metrics, actual common dates, historical windows and market-specific data/FX/coverage limitations.
- [x] Keep inherited conflicts accessible as history rather than current conclusions.
- [x] Investigate saved missing-minute evidence and record supported results without changing execution measurements.

### Task 4: Delivery

- [x] Run Python, lint, web, build/static and browser validation.
- [x] Independent read-only review and repair findings.
- [ ] Validate against current main, commit/push/PR/CI/merge, verify live page and clean only this task.

## Evidence collected

- Reviewed proposal SHA-256: `59eb7b76315cd0dddc90d557c377a662c5bb71aa70e0e3eef1daf33d94199b91`.
- Independent aggregate review: 760 cells; overlapping publication views explicitly disclosed.
- Source-window review: 48 stocks, 960 preceding rows, 336 numerical cells.
- Executed 13-cell notebook; inspected exported figures and corrected misleading bucket math typography and exclusion colors.
- Sparse source dates discovered in initial proposal; initial proposal never published; corrected calendar run and regression test reviewed.
- Code reviewer found no blocking defects; source-format hash mismatch resolved with verified AST/hash mapping and bilingual disclosure.
- Initial validation: 527 Python tests passed, 1 optional dependency skip; Ruff passed; 150 web unit tests; 141 browser tests; Astro 0 errors/warnings and static verification passed.
- Target main advanced during the task; combine and validate before merge.

- Combined validation at target `79fde7f`: 152 web unit tests and 142 browser tests passed; Astro 0 errors/warnings and static boundary validation passed. Python implementation unchanged by target integration. Desktop/phone Chinese dark-mode screenshots inspected without page overflow.
