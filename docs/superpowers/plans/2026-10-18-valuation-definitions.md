# Valuation definitions and current-snapshot illustration

**Goal:** Distinguish earnings and equity denominators, publish a small reproducible illustration, and link the separate ST comparability audit.

**Architecture:** Read sealed owner financial snapshots and one daily market-value partition without changing shared inputs. Publish only reviewed derived multiples and ranks. Keep current observed data separate from reconstructed historical availability.

**Scope:** Six deliberately chosen A-only issuers illustrate definitions, not market-wide cheapness or investment performance. Consolidated goodwill/intangibles deducted from parent equity are explicitly labelled proxies; no allocation to minority shareholders is assumed.

- [x] Verify financial field definitions, seals, observation times and report versions.
- [x] Implement a standalone analysis script with finite-value, unit, revision, common-period and missing-data checks.
- [x] Review arithmetic and publish bilingual definitions, six-name comparisons and limitations.
- [x] Register public pages and connect existing PB/ROE and microcap material.
- [ ] Complete applicable checks, PR, merge and verify live publication.
