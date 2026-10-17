# Rotation evidence workbench publication

The unified style/theme rotation topic now consumes an explicitly reviewed versioned research asset rather than treating manually transcribed weekly notes as current comparable results. The original 24 observations and the separate 66 ETF/six hotspot aggregate metrics remain retrievable. Both old topic routes preserve query strings and anchors.

## Evidence and controls

The release registers 24 configurations: 21 reproduced, three unavailable for missing required price columns. Readers can select compatible groups/allocation methods and full-common/252/756-session windows, sort numeric metrics, inspect risk/bond/cost contributions and replay 972 historical events across two representative baselines. Dates, eligibility filters, no-trade/blocked/executed states, listing uncertainty and aggregate allocations are explicit. The theme runner has no admitted real historical inputs, so the page publishes no theme-performance claim.

Input panel coverage differs from evaluation periods. Common risk/pool windows contain 2,182 sessions starting 2017-08-28; holdover/score windows contain 2,429 sessions starting 2016-08-22; all end 2026-08-24. Legacy event averages and rounded note observations remain separate from new daily-average measurements. Detailed reader-facing methods and findings are in `web/public/research-notes/rotation-evidence-review.md` and its Chinese companion.

## Contract and import

The single envelope is `web/public/data/rotation-evidence-release.json`, containing exactly `asset` and `review`. Schema: `research.rotation_evidence_public.v1`; evidence: `rotation-evidence-20261017-native-v2`. Source/content/exact-asset digests bind the review. Typed field allowlists, execution-state keys, exact named-window lengths, strictly later execution dates and comparison-bound contribution totals are checked at import/build time. Unknown private fields, local locators, nonfinite values or stale review pairs fail without overwriting a valid release.

```bash
cd web
npm run import:rotation -- "$ROTATION_PUBLIC_ASSET" "$ROTATION_PUBLIC_REVIEW" public/data
npm test
npm run build:pages
PORT=4398 npm run e2e -- --workers=4 --output="$ROTATION_BROWSER_OUTPUT"
```

Resolve these operator paths explicitly outside the source checkout; never pass a private source bundle to the consumer importer. The producer integration preceded consumer integration; its merge identity is `9b1736f3484234746212d5f2c2f347efed4c9f54`.

React receives a summary subset. Replay is downloaded on demand and checked with browser SHA-256 against the exact release hash bound into HTML. Stale HTML/data pairs show retry/reload rather than unverified replay. Static HTML provides comparison/contribution tables, representative replay samples and theme/source boundaries. English is default; explicit Chinese selection and query controls persist. Storage-denied sessions preserve URL locale and system theme. Mobile tables scroll horizontally instead of stacking digits; the standard compact research layout keeps the topic readable.

## Validation and review

The combined result includes target main `8ced680` and its earlier microcap/provider changes. Local environment: Node 24.21.0/npm 11.19, locked npm dependencies, installed Chromium. `npm test`: **185 passed**. `npm run build:pages`: type check, production build and static/public-boundary admission passed. Full Playwright suite: **170 passed**. Desktop and Chinese dark mobile screenshots were inspected. `git diff --check` passed. GitHub PR checks additionally validate the supported Node 22 environment and the shared Python execution provider.

An independent whole-branch review found five Important admission gaps; all received failing-then-passing regressions. A contradictory archive sentence was treated as Important and corrected in both languages with a regression. Storage-denied failures and the screenshot-discovered narrow-column issue also received browser checks. No Critical findings remain.

Deferred Minor: the current theme panel is intentionally written for the sole published `blocked` release. Before importing a future real `diagnostic` theme release, extend it and the static fallback to render that status, reasons and period-labelled metrics. No current real theme result is hidden by this limitation.

Execution decisions: public replay covers representative baselines (cost: detailed private variant traces are not public); canonical numbers use at most 12 decimals (cost: rounding up to 0.5e-12 per public value, with private full precision retained). Consumer code and then its immutable reviewed asset were staged locally before producer integration to permit independent validation; production integration remained producer-first (cost: reimport/revalidation if the producer contract changed). Website review relied on the separate producer review/run evidence for private calculations and reproduction scope; source availability remains unverified rather than certified (cost: any undetected producer error can propagate to public metrics).
