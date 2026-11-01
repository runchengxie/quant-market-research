# Asset Decision Risk Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans inline, with a final independent whole-branch review.

**Goal:** Complete the five authorized research extensions on frozen data and publish reviewed evidence with explicit limitations.
**Architecture:** Study-only Python modules for resampling, spending, stress and investability; frozen result/projection and conclusion register; existing Astro topic.
**Tech Stack:** Python, NumPy, pandas, pytest, Astro, Playwright.
**Spec:** ../specs/2026-11-01-asset-decision-risk-design.md

## Global Constraints

No source raw data or generated full runs. No future or executable-return claims. Fixed parameters and seed; no optimized selection. Existing prospective protocol and evidence retained. All fractional frequencies describe overlapping historical windows or conditional resampling only.

## Review Focus

- Resampling preserves cross-asset pairing and recomputes policy paths; no IID window inference.
- Cash is funded, inflation applies to demands, failed demand stays in denominators, boundary equality is not failure.
- Stress masks are contemporaneous and noncausal; small correlations stay unavailable and recoveries are censored.
- Publication and product availability dates do not certify original total-return vintages or executable closes.
- Public register/projection and source/code hashes match reviewed full results, with both locales readable.

### Task 1: Paired uncertainty and fixed-era sensitivities
**Files:** uncertainty.py; tests/studies/test_asset_decision_risk.py.
**Interfaces:** consumes frozen monthly levels; produces deterministic JSON-native uncertainty summaries.
- [ ] Write paired deterministic/small-sample regression tests; run RED (missing module).
- [ ] Implement block resampling and fixed-policy paired differences; run GREEN.
- [ ] Commit and ledger test command/output.
Expected: paired identical series have zero relative CAGR uncertainty; no future-probability labels.

### Task 2: Spending and stress accounting
**Files:** spending.py, stress.py; same test file.
**Interfaces:** consumes validated levels; produces real-demand accounting and descriptive stress/recovery summaries.
- [ ] Write RED conservation, CPI, shortfall, sequence, conditional-count and censoring tests.
- [ ] Implement finite accounting and contemporaneous masks; run GREEN.
- [ ] Commit and ledger test command/output.
Expected: cash funded once, exact exhaustion satisfies demand, future gaps not filled, short samples reported unavailable.

### Task 3: Investability and conclusion contracts
**Files:** investability.py, conclusion-register.json; tests.
**Interfaces:** consumes publication/source records and frozen ETF levels; produces scoped comparisons and stable claim records.
- [ ] Write RED launch-month, fee identity and invalid evidence-stage tests.
- [ ] Verify official sources; implement and run GREEN.
- [ ] Commit and ledger test command/output.
Expected: partial launch month excluded; fees apply once on notional; no prospective upgrade.

### Task 4: Frozen run, reviewed projection and bilingual reader integration
**Files:** runner/projector scripts, findings/protocol/validation docs, Astro/copy/e2e files, release gate.
**Interfaces:** consumes Tasks 1–3; produces full external results and whitelisted reviewed aggregate projection.
- [ ] Verify frozen old hashes, run all fixed scenarios, inspect actual results, record provenance.
- [ ] Test public schema/release lock; integrate bilingual tables and claim register summary.
- [ ] Run Python/Ruff/web/build/static/browser checks; independent whole-branch review; fix material findings.
- [ ] Verify current target, publish PR, pass final CI, merge, retain closeout and clean task only.
Expected: all five workstreams have actual results or explicitly blocked evidence, with no silent stale publication or invented future observation.
