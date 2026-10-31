# Asset robustness follow-up implementation plan

> **For agentic workers:** Use superpowers:executing-plans inline; one independent whole-branch review at completion.

**Goal:** Advance all five follow-up questions with tested calculations, actual evidence and explicit unresolved prerequisites.
**Architecture:** Study-specific modules reuse the verified first-round monthly inputs. Frozen data-owner exports support ETF and constituent audits. Existing cash-flow topic hosts a reviewed aggregate projection.
**Tech Stack:** Python/pandas, pytest, existing Astro bilingual components.
**Spec:** ../specs/2026-10-31-asset-robustness-design.md

## Global constraints

No raw data or credentials in Git; no shared alias writes. No optimized portfolio parameters. No causal earnings or actual execution claims from descriptive data.

## Review focus

Chronological cost application; initial capital in drawdowns; censored recovery; ex-date versus pay-date and split basis; complete calendar endpoints; weights summing to one; actual returned API coverage; no fabricated missing returns.

## Tasks

- [ ] Record design and source baseline; run baseline tests in isolated worktree.
- [ ] Acquire bounded ETF and annual constituent snapshots through configured API; retain receipts and probe failures.
- [ ] Write failing tests for sensitivity and relative waiting; implement and run actual frozen histories.
- [ ] Write failing tests for fixed-rule allocation accounting; implement finite predeclared study scenarios and validate self-financing and costs.
- [ ] Write failing tests for ETF three-layer reconciliation and constituent retention; implement, audit actual data, retain unsupported results as blocked.
- [ ] Publish reviewed bilingual aggregates and findings through the existing topic; verify projection and privacy.
- [ ] Run complete checks, independent review, current-main reconciliation and PR integration; retain external closeout and clean only this task.
