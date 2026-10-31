# Asset Return Research Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement task by task.

**Goal:** Deliver reproducible long-horizon asset-return diagnostics and evidence-backed data acquisition findings.
**Architecture:** Existing topics remain authoritative. A study-specific monthly input contract separates observations, arithmetic attribution and prospective scenarios. Data acquisition remains owned by the data platform.
**Tech Stack:** Python 3.11+, pandas, pytest, existing Astro site.
**Spec:** ../specs/2026-10-31-asset-return-framework-design.md

## Global Constraints

Raw data and run outputs outside repositories; no production alias changes. No fabricated history, silent missing-return filling or independent-fundamentals claims from inferred EPS. English default and Chinese locale copy for public additions.

## Review Focus

- Dividend accounting: ex-date entitlement versus payment date; no duplicated dividends.
- Missing observations: reject duplicate, nonfinite and discontinuous monthly input.
- Recovery: retain censored entries and include starting capital in drawdowns.
- Relative wealth: geometric ratios rather than subtracting CAGRs.
- API evidence: permission failures do not establish absent data; successful probes do not prove complete history.

## Task 1: Supplier and existing-data evidence

- [ ] Inspect documented TuShare/AKShare routes and configured provider contracts.
- [ ] Run bounded read-only probes, retain raw and sanitized receipts outside source.
- [ ] Record actual access, historical sample coverage, semantic limits and next acquisition actions.

## Task 2: Study calculations

Files: `src/market_research/studies/asset_returns/`, `tests/test_asset_returns.py`.

- [ ] Write tests for monthly return validation, exact geometric dividend attribution, CPI/FX normalization, horizon downside, censored recovery and down-market comparisons.
- [ ] Run tests and verify missing implementation failure.
- [ ] Implement study-specific functions with explicit input and output contracts.
- [ ] Add tested fixed-unit cash distribution and withdrawal scenarios; retain ex/payment timing and cash/wealth separately.
- [ ] Run focused tests, then full Python suite and Ruff.

## Task 3: Reproduction and reader evidence

- [ ] Add explicit frozen-input study runner, exclusive output directory and provenance hashes.
- [ ] Run available actual observations; do not publish unsupported estimates.
- [ ] Add bilingual protocol/results in existing topic paths with auditable completion status.
- [ ] Run web tests, build/static checks where touched; inspect all outgoing changes.
- [ ] Commit, push to verified owner repository, open PR, validate current main and merge when checks pass. Clean only this task after merge.
