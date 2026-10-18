# Overseas lead-lag robustness and publication plan

**Goal:** Extend the exploratory index forecast into a documented, reproducible chronological comparison and publish reviewed aggregate findings.

**Architecture:** General research methods live in this public repository. Provider inputs, retrieval receipts, joined timing rows, daily forecasts and simulation results stay in external task directories. The website consumes an explicit aggregate allowlist.

**Scope authorized by the user:** Historical signal availability, FX/common-market controls, multiple time splits, ETF or futures proxies, cost sensitivity, and publication. Execute within the current session.

## Constraints and decisions

- Historical retrieval vintages are unavailable. Preserve this limitation; calendar-derived availability is an assumption, never proof of historical API availability.
- Freeze 08:45 Shanghai decisions. Convert overseas session closes with local time zones and DST; defer GMT-labelled FX bars until their day has ended plus one hour. Also delay all external inputs by one A-share session as a sensitivity.
- Compare domestic-plus-FX, plus-SPX, and plus-Asian-market models on identical rows. Use expanding annual fits with training-only normalization and purge labels unavailable at the test cutoff. Historical periods already inspected are retrospective, not fresh holdouts.
- Use 510300 and 512480 with adjustment factors. The semiconductor ETF tracks a different benchmark from the SW industry index. Ordinary domestic equity ETFs require T+1: evaluate next-open exits, not same-day round trips.
- Costs apply to changes in position, including terminal liquidation. Show round-trip 0/5/10/20/40 bp and budget/minimum-commission/slippage sensitivities with prior ADV admission and conservative limit-price guards. This is a daily-bar proxy, not a certified fill replay.
- Publish methods and aggregate fold/cost results in English and Chinese with source links and a public research topic. Keep raw histories, local paths, daily predictions and credentials out of public projections.

## Tasks

- [x] Implement availability joins, annual model comparisons and T+1 ETF sensitivity accounting; cover DST, FX date boundaries, label purging, adjustment and turnover with regression tests.
- [x] Run against authorized provider pulls; independently check key arithmetic, temporal bounds and source joins. Save external run receipts and hashes.
- [x] Write reviewed research notes, add a bilingual topic and aggregate-only snapshot, and validate links, locale rendering and public data boundaries.
- [ ] Run affected Python and web checks, create a PR, satisfy required checks, merge and verify the deployed Pages route before cleanup.
