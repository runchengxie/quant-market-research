# Interactive Reading Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans inline. Obtain one independent whole-branch review before merge.

**Goal:** Make the asset studies explorable through charts and review all public site prose against the owner's plain-language requirements.
**Architecture:** Pure chart selectors over reviewed JSON, a lazy Astro/ECharts controller, existing evidence tables as fallback, source-aware copy audit and scoped editorial revisions.
**Tech Stack:** TypeScript, Astro, ECharts, Node tests, Playwright.
**Spec:** ../specs/2026-11-01-interactive-reading-design.md

## Global Constraints

Research data/calculations and original evidence stages unchanged. English default and bilingual catalogs retained. No fabricated raw observations or uncertainty. Full-table/no-JS evidence preserved. Chinese prose follows the owner's explicit wording/punctuation rules; source identifiers, code and quotations remain intact. Generated audit output belongs outside source.

## Review Focus

- Charts and controls select identical reviewed rows, with correct units and denominators.
- Point ranges keep asymmetric endpoints and crossing zero; no histograms invented from summaries.
- Language/theme/resize, keyboard controls and table fallback work together.
- Prose rewrites preserve uncertainty and historical scope without rhetorical reversals.
- Site-wide coverage is explicit and data/download/provenance contracts remain unchanged.

### Task 1: Whole-site inventory and editorial audit
**Files:** source-aware audit helper/tests, selected locale catalogs, registered public Markdown.
**Interfaces:** consumes project public registry and source strings; produces findings with exact source locations and scoped revisions.
- [ ] Test identifier/code preservation and Chinese prose rules RED, implement GREEN.
- [ ] Inventory public routes/documents and edit actual reader text. Review numeric/source invariants.
Expected: source lookup keys and fenced code unchanged; prohibited rhetorical prose identified and rewritten.

### Task 2: Reviewed chart data and interactive components
**Files:** asset chart selectors/tests, localized copy, lazy chart component/controller.
**Interfaces:** consumes the four reviewed asset datasets; returns consistent chart rows/units/sample metadata and linked accessible summary.
- [ ] Test asymmetric ranges, spending filters, endpoint windows and ETF coverage RED.
- [ ] Implement chart selectors and lazy responsive charts with bilingual controls.
Expected: no new raw data, exact selected results, correct probability/frequency labels.

### Task 3: Reading flow and browser acceptance
**Files:** asset evidence components, affected e2e tests, editorial follow-up.
**Interfaces:** charts and existing controls share selected state; details retain full evidence.
- [ ] Add charts and concise explanations, fold long method/table detail after successful chart load.
- [ ] Verify locale/theme/keyboard, mobile and no-JS fallback; inspect screenshots.
Expected: charts render known values, sources remain available, fallback stays useful.

### Task 4: Full-site verification and release
**Files:** validation/audit record; runtime audit outputs outside source.
- [ ] Scan all published routes and Chinese explanation text, review remaining flags.
- [ ] Run full required checks, independent review, fix important issues, validate current main.
- [ ] PR/CI/merge, live verification, retain closeout and clean current task only.
Expected: final report states exact coverage and real validation, with no unsupported universal readability claim.
