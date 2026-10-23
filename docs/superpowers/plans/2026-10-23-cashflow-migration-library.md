# Cash-flow migration and library implementation plan
> Execute inline with executing-plans; request independent whole-branch review.
**Spec:** ../specs/2026-10-23-cashflow-migration-library.md
**Goal:** Own the complete public cash-flow index replication record and present a grouped, scannable research library.
**Architecture:** Versioned public assets with explicit provenance; static bilingual report and grouped Astro directory; precise catalog removal in the observatory.
**Tech stack:** Existing Astro/React/TypeScript, Python content-contract validation, Playwright.
## Review focus
Preserved values and dates; omitted evidence; dangling study links; removed route behavior; mobile/keyboard/dark/locale usability.
## Task 1: Market publisher
- [x] Add behavioral tests for the grouped directory and migrated report completeness.
- [x] Copy and fingerprint public records; implement report, charts, source details and navigation.
- [x] Group the nine-topic directory with short summaries and retained detailed evidence.
- [x] Run frontend tests, build, static verification, browsers and visual checks.
## Task 2: Observatory removal
- [x] Test that cash-flow study/assets/associations are absent and old route is missing.
- [x] Remove only migrated records; update hashes only for reviewed relationship removals, never source baselines.
- [x] Run Python tests, source/public audits, build and browser suite.
## Task 3: Delivery
- [x] Independent review, fix findings, commit and open PRs.
- [ ] Publish and verify market provider first, then merge/verify observatory removal.
- [ ] Sync clean primary checkouts and remove only task branches/worktrees.

## Verification
302 frontend tests, production build, static verification and 270 browser tests passed. Migration hashes match the original reviewed study/exploration/navigation records. Desktop/mobile, bilingual and dark-theme visual checks passed; independent review found no blocking issues.
Publisher base 4eeb1eb and observatory base 03c1ab3 were checked together. The market publisher must be deployed and verified before the removal PR is merged.
