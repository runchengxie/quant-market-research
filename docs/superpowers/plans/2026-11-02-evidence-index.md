# Evidence Index Implementation Plan

> Use superpowers:executing-plans inline and one fresh-context whole-branch reviewer.

**Goal:** Finish non-chart topic navigation and source-backed evidence version dates.
**Architecture:** Shared localized directory metadata, anchors on existing blocks, and validated publication metadata separate from sealed data. Reuse existing reading-summary/date fields and date consumers.
**Tech Stack:** Astro, TypeScript, Node tests, Playwright.
**Spec:** ../specs/2026-11-02-evidence-index-design.md

## Global Constraints

Full text and all original numbers remain. Tables stay expanded. Chinese prose follows owner rules. English default, explicit locale switch. Runtime outputs outside source. Version dates and acquisition dates remain distinct.

## Review Focus

Directory order matches displayed content. All old anchor IDs survive. Dates use Asia/Shanghai and link to the immutable publication revision. A changed evidence manifest fails validation. No dates are filled from unrelated current timestamps.

### Task 1: Directory and publication contracts
- [ ] Add failing tests for full section coverage and version validation.
- [ ] Implement localized directory metadata and an exact-manifest publication record/helper.
- [ ] Verify focused tests and commit.

### Task 2: Page integration
- [ ] Add browser checks for all directory targets and visible source-backed dates.
- [ ] Anchor existing evidence blocks and integrate dates into topic headers, summaries and catalog.
- [ ] Verify type/build, browser checks and prose; commit.

### Task 3: Verification and delivery
- [ ] Run required checks and independent whole-branch review; fix material findings.
- [ ] Publish PR, verify current main and required CI, merge and verify the public site.
- [ ] Retain exact validation and retire only the clean merged task worktree/branch.
