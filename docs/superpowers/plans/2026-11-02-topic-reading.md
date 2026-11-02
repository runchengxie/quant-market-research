# Complete Topic Reading Implementation Plan

> Use superpowers:executing-plans inline. Obtain one fresh-context whole-branch review before merge.

**Goal:** Separate cash-flow and asset questions into complete, expanded research topics for new readers.
**Architecture:** Reuse reviewed evidence components with explicit topic ownership, a shared asset reading layout and catalog, and legacy destination routing. Preserve research data and old downloads.
**Tech Stack:** Astro, TypeScript, ECharts, Node tests, Playwright.
**Spec:** ../specs/2026-11-02-topic-reading-design.md

## Global Constraints

Keep all original evidence and limitations. English default; Chinese copy follows the owner's plain-language and punctuation rules. No auto-folding. Generated validation outputs remain outside source. Use the existing repository PR/merge workflow and retain other worktrees.

## Review Focus

Mixed asset and cash-flow hash URLs retain locale and destination. Missing dates do not appear as unexplained dashes. No-JS readers can access all evidence. Costs/spending controls remain paired with source rows. Split ownership does not duplicate or omit research blocks.

### Task 1: Topic ownership and routing
**Files:** asset topic catalog/tests, public registry/copy, library, cash-flow sections, legacy destination component.
**Interfaces:** topic keys `returns`, `allocation`, `implementation`; routes as specified in the design; a pure legacy-target helper retains hashes and query.
- [ ] Write and run failing ownership, route and source-preservation tests.
- [ ] Add topic metadata, discoverability and legacy destinations.
- [ ] Verify focused tests and commit.

### Task 2: Full evidence pages and reading flow
**Files:** AssetStudyPage, three asset route pages, AssetRobustnessEvidence and AssetDecisionEvidence topic props, AssetReturnEvidence, AssetInteractiveChart/controller, scoped cash-flow disclosure behavior.
**Interfaces:** components consume topic ownership and original reviewed JSON; every research block renders on one topic. Tables remain open after chart mount.
- [ ] Add browser assertions for topic chart membership, full evidence and no auto-fold.
- [ ] Split component blocks without deleting their content, add full-width figure/narrow prose layout and plain-language reading notes.
- [ ] Update affected tests to their owning routes without weakening numeric assertions. Verify and commit.

### Task 3: Verification and publication
**Files:** migration coverage/validation record and external runtime evidence.
- [ ] Run required checks, source/rendered prose audit and screenshots in both languages and device sizes.
- [ ] Obtain whole-branch review, repair important findings, validate current main and publish PR.
- [ ] Merge only after required checks pass, verify live pages/download hashes, retain logs and retire only this task's clean worktree.
