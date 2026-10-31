# Asset evidence closure implementation plan

> **For agentic workers:** Execute inline with superpowers:executing-plans; independent whole-branch review before merge.

**Goal:** Investigate ETF/missing-member anomalies, add update gates and prospective protocol registration, and verify the reader-facing release.
**Architecture:** Reuse frozen studies and existing registration receipts. Add study-specific evidence and validation modules; no automatic production or publication mutation.
**Tech Stack:** Python/pandas/pytest, existing Astro and Playwright.
**Spec:** ../specs/2026-10-31-asset-evidence-closure-design.md

## Global constraints

Raw records and complete runs outside source. No old snapshot replacement. No invented missing profits, future formations or causal alpha. English default, Chinese catalog text, explicit cost semantics.

## Review focus

Corporate identity versus ticker; delisting versus economic recovery; adjusted NAV versus independent issuer returns; unchanged overlap versus revised history; external timestamp proof versus local/Git-author time; observable calendar endpoints versus future/outcome data.

## Tasks

- [ ] Verify isolated baseline and retain read-only live-site status.
- [ ] Acquire bounded missing-member master/name/income records and primary issuer reports; preserve raw provenance.
- [ ] Add failing tests, implement yearly ETF attribution and identity audit; run and report actual evidence and unresolved cases.
- [ ] Add failing tests, implement monthly update/release gates and extend the existing registration study; freeze prospective protocol and exercise pending/rejection paths.
- [ ] Publish reviewed closure aggregates, bilingual findings and cost-basis explanation; verify both locales, mobile and downloads.
- [ ] Run full checks and independent review, reconcile current main, PR merge, retain external time/CI/closeout evidence and clean this task only.
