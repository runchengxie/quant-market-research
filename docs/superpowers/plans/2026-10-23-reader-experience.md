# Reader experience implementation plan
> Execute inline with superpowers:executing-plans; request a fresh whole-branch review before integration.
**Goal:** Unify the public entry under Research topics.
**Architecture:** Keep both existing URLs usable with one shared topic landing component and one primary navigation entry. Preserve legacy hash destinations, locale state, all nine summaries and their method/archive links.
**Tech Stack:** Existing TypeScript frontend and repository validation tools.
**Spec:** ../specs/2026-10-23-reader-experience.md
## Global constraints
Preserve research values, public data boundaries, locale persistence, legacy links and source review warnings.
## Review focus
Direct entry and refresh; locale switching; missing data; mobile overflow; distinction between evidence and demonstration.
## Task 1: Implement the reading path
**Files:** web/src/components/ResearchLanding.astro; web/src/pages/index.astro; web/src/pages/research/index.astro; SiteHeader; registry and static contract.
- [x] Check current tests and add focused behavioral regression coverage where navigation or data loading changes.
- [x] Implement the shared entry and content hierarchy.
- [x] Run npm test; npm run build; npm run verify:static; PORT=4431 npm run e2e.
- [x] Inspect desktop/mobile rendering, both languages and themes.
## Task 2: Review and integrate
- [x] Review the complete diff, fix actionable issues, and validate the current target result.
- [ ] Commit, open a PR, wait for required checks, merge under standing authorization.
- [ ] Verify the deployed version and remove only this task's worktree and branches.

## Verification record
301 frontend tests, production build, static verification and 261 browser tests passed. Desktop Chinese and mobile English screenshots inspected.
Fresh independent review found no blocking issues. Integration follows the user's standing authorization after remote checks pass.
