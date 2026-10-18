# Including ST stocks: a paired short-window measurement

[Chinese version](microcap-st-paired-short-window-20261018.zh-CN.md)

Reviewed on 2026-10-18. **This run produces an actual matched descriptive comparison, but does not establish a reliable return benefit from including ST stocks.** Status coverage is much better documented in this recent window. Missing endpoint prices still remove most monthly pairs, and the sign depends on which complete months are compared. These are adjusted-price basket labels, with zero assumed costs; they are not trades, a cash ledger or an investable performance series.

The [preceding ST comparability audit](microcap-st-comparability-audit-20261018.md) left this measurement open. This follow-up adds executable methods, same-sample comparisons and explicit member-level failure records. It does not revise the earlier frozen studies or certify their historical inputs.

## Window and state evidence

The primary measurement uses 36 monthly formations from 2022-12-30 through 2025-11-28. Entry closes run from 2023-01-03 through 2025-12-01; the last endpoint is 2026-01-05. The period was chosen for recent historical status coverage, before inspecting these basket differences. A same-provider `stock_st` positive-state source has completed annual retrieval receipts and no missing SSE open dates for 2015–2025. Its retained 2024 and 2025 audits exactly matched reconstructed positive states; the retained 2023 audit had four missing positive records. These checks cover positive states, not the entire universe or original publication history.

At the 36 formation dates, the new run observes:

| Coverage measure | Count |
| --- | ---: |
| Clean daily security/date rows | 191,112 |
| Known non-ST state after all status gates | 185,243 |
| Known ST state after all status gates | 4,836 |
| Unknown state, excluded identically in both arms | 1,033 (0.541%) |
| Daily positive-state disagreement with the separate endpoint | 0 |
| Positive state lacking modeled availability by formation | 0 |
| Reconstructed active-master rows without a daily row | 551 |
| Daily rows absent from the dated instrument master | 25 |
| Missing observed market sessions versus the SSE calendar | 0 |

These are summed security/date observations, not counts of different firms. Unknown states here coincide with missing or ambiguous dated names; they are not silently classified as non-ST. A daily row without a master record cannot pass the listing gate. Missing master or daily observations prevent any claim that this is a complete historical market census.

Each usable state requires an active historical name, `ann_date < formation_date`, and agreement between that name's ST marker and cleaned `is_st`. Positive states also require `st_available_from <= formation_date`. The separate positive-state endpoint must agree; absence there alone never establishes non-ST. Delisting-period names are excluded from new targets identically in both arms.

**Effective dates and modeled announcement availability do not establish vintage safety.** The sources were retrieved retrospectively in 2026. The positive-state source was observed on 2026-10-02, with an actual availability policy of the following Shanghai day (2026-10-03); it was not available to these historical decisions. The cleaned `st_available_from` field instead models announcement-date availability. The positive-state manifest explicitly says `historical_pit_eligible=false`; the reconstructed history says `revision_safe=false`. Same-provider agreement is not independent truth. No source supplies original release vintages or complete announcement receipt times. This measurement therefore remains retrospective and cannot certify a strictly historical trading decision.

## What changes between the two arms

Both arms start with the same reconstructed active instrument universe, historical status gates, formation prices, listing and delisting dates, positive capitalization and traded amount, and non-suspended formation rows. Firms that delist later remain eligible before their actual delisting boundary. Unknown states are excluded from both arms.

At each monthly last market session, rank by total market capitalization, breaking ties by stable security code. The include-ST arm selects the smallest N known-state names. The exclude-ST arm removes ST and selects the smallest N remaining names. N = 50, 100 and 200 are separate size sensitivities. Every selected member receives initial weight 1/N. There is no buffer or other signal.

Measure each basket from the next market session's adjusted close to the market session after the next monthly formation. Thus formation information never receives a same-close return. Hold the initial basket weights through that interval and average its member price changes. Both arms assume zero cost. The code models no fills, price-limit access, borrow, shares, cash, capacity or settlement; even a positive-volume endpoint need not have been executable.

Selection happens **before** inspecting entry or endpoint availability. An endpoint must have a positive adjusted price and traded amount and must not be suspended. A selected member delisted on or before the endpoint has an unresolved terminal value even if a price row exists. Any unresolved member invalidates the entire paired period. There is no replacement based on future prices, weight renormalization, stale-flat mark or assumed total loss. Both arm returns are then missing. Counts and member records remain available for those failed periods.

## Monthly result and common support

The differences below are **include-ST minus exclude-ST, in percentage points per measured interval**, averaged only over periods complete in both arms. They are not annualized. No cumulative NAV is constructed across missing months.

| N | Complete / attempted monthly pairs | Mean ST members in include arm, all months | Mean common weight between arms, all months | Mean difference on this N's complete months |
| --- | ---: | ---: | ---: | ---: |
| 50 | 15 / 36 | 9.14 | 81.72% | +0.202 pp |
| 100 | 13 / 36 | 16.08 | 83.92% | −0.514 pp |
| 200 | 9 / 36 | 34.31 | 82.85% | −1.028 pp |

For those separate complete subsets, the include/exclude arm mean price changes are 9.110% / 8.907% (N=50), 10.157% / 10.671% (N=100), and 14.558% / 15.586% (N=200). These high conditional means leave out unresolved months and are not a full-window return.

Common weight is the number of identical selected names divided by N; the remaining weight is replaced when ST eligibility changes. This measures actual membership change, unlike the earlier 0–30% size-tail matrix.

The complete-month sets differ across N. Restricting every N to the **same nine complete months** changes the mean differences to **−0.752 pp, −0.927 pp and −1.028 pp** for N = 50, 100 and 200. The N = 50 sign reverses from its own 15-month subset. This is sensitivity to observed support, not evidence that the nine months are representative.

The annual breakdown uses the year of the entry close:

| Entry year | N=50 complete / 12; difference | N=100 complete / 12; difference | N=200 complete / 12; difference |
| --- | ---: | ---: | ---: |
| 2023 | 7; −0.007 pp | 6; −0.107 pp | 5; −0.550 pp |
| 2024 | 6; +0.721 pp | 5; −0.916 pp | 2; −2.232 pp |
| 2025 | 2; −0.619 pp | 2; −0.733 pp | 2; −1.018 pp |

Only two monthly pairs survive in 2025 at every N. The very large observed basket means in some complete subsets cannot be extrapolated into a year: missing periods can contain precisely the risks being studied.

## Terminal and missing-price boundary

| N | Unresolved selected arm/member records | Different unresolved formation/member records | Different eventually delisted firms retained in selections | Terminal events before endpoint |
| --- | ---: | ---: | ---: | ---: |
| 50 | 50 | 48 | 51 | 5 |
| 100 | 68 | 64 | 66 | 5 |
| 200 | 117 | 107 | 94 | 5 |

Arm/member records count a shared member twice when it appears in both arms. Different formation/member counts remove that duplication. Eventually delisted firm counts cover the entire dated master, including delistings after the label endpoint; these firms were not removed retrospectively. All five distinct formation/member terminal events occur in the include-ST arm at every N. Counts across N repeat those events and must not be added together.

Most unresolved records fail a price/positive-amount/non-suspension endpoint gate; some fail the entry gate too. They cannot be assigned zero returns. The monthly complete-pair means condition away these observations and therefore cannot settle the economic effect of including ST.

## Exploratory shorter horizon

After observing the monthly missing-price problem, a daily-formation, one-session forward-label diagnostic was added for 2024 and 2025. This was an **exploratory coverage sensitivity chosen after seeing monthly incompleteness**, not a prespecified confirmation test. It keeps the same classification, ranks, N, equal initial weights, next-close lag, zero assumed cost and paired missing-mark rule; it changes the holding interval and formation frequency. Its magnitude cannot be compared directly with a monthly mean.

| Entry year | N | Complete / attempted one-session pairs | Mean difference on complete pairs |
| --- | ---: | ---: | ---: |
| 2024 | 50 | 211 / 242 | −0.122 pp |
| 2024 | 100 | 199 / 242 | −0.078 pp |
| 2024 | 200 | 183 / 242 | −0.067 pp |
| 2025 | 50 | 193 / 243 | −0.050 pp |
| 2025 | 100 | 180 / 243 | +0.014 pp |
| 2025 | 200 | 168 / 243 | +0.016 pp |

Coverage improves at this shorter horizon, but 31–75 paired days per year/N remain unresolved. No in-label terminal delisting event appears in these one-session selections; this does not validate settlement for the five monthly terminal events. Known-state coverage remains retrospective: the 2024/2025 runs exclude 6,883 / 6,719 unknown formation records, with zero positive-state cross-check disagreements. The sign still varies across year and N.

Even with more complete endpoints, this shorter label cannot recover a liquidation value for a position carried through suspension or delisting. Conditional mean differences remain descriptive; no significance, annualized premium or deployable trading claim is made.

## Reproduction and next useful evidence

The implementation is [the runner](https://github.com/runchengxie/quant-market-research/blob/e2dcfface24e83648dbe62a512c2c3e2fe2deba9/scripts/analyze_st_paired_short_window.py), [status and pairing methods](https://github.com/runchengxie/quant-market-research/blob/e2dcfface24e83648dbe62a512c2c3e2fe2deba9/src/market_research/st_paired.py), and [regression fixtures](https://github.com/runchengxie/quant-market-research/blob/e2dcfface24e83648dbe62a512c2c3e2fe2deba9/tests/test_st_paired.py). Raw and security-level audit records remain outside this public repository. The public report includes aggregate derived counts and means only.

With owner-published assets under an explicitly supplied `MARKET_DATA_ROOT` and a task-specific external `RESEARCH_OUTPUT` directory:

```bash
uv run --locked --extra duckdb --extra dev python scripts/analyze_st_paired_short_window.py \
  --data-root "$MARKET_DATA_ROOT" --output "$RESEARCH_OUTPUT/monthly-v1"
uv run --locked --extra duckdb --extra dev python scripts/analyze_st_paired_short_window.py \
  --data-root "$MARKET_DATA_ROOT" --output "$RESEARCH_OUTPUT/daily2024-v1" \
  --frequency daily --start 20231229 --end 20250103 --execution-year 2024
uv run --locked --extra duckdb --extra dev python scripts/analyze_st_paired_short_window.py \
  --data-root "$MARKET_DATA_ROOT" --output "$RESEARCH_OUTPUT/daily2025-v1" \
  --frequency daily --start 20241230 --end 20260105 --execution-year 2025
```

Each output contains `coverage.csv`, `periods.csv`, `summary.csv`, a private `selection_audit.parquet`, and `receipt.json`. The receipt pins the resolved clean version, manifest, dated instrument and name files, ST version and receipt, positive-source content, calendar, script and method hashes. A latest pointer is resolved for convenience, so future reproduction must use the retained receipt and confirm identical version hashes; silently consuming a newer alias is a new experiment. The receipt hashes the clean manifest, not every daily price file, so byte-for-byte price reproduction also depends on retaining the owner asset version intact. The output directory must not already exist. No shared `latest` pointer is updated.

Validation: seven focused regression cases pass with locked dependencies; they cover identical non-ST support, unknown exclusion, same-day announcements, positive availability, ambiguous names, missing endpoints, insufficient N and later delisting. The full Python suite reports 634 passed and 14 skipped (optional formal provider/runtime integrations unavailable); repository Python Ruff checks pass. No website files were changed by this task. These tests validate the measurement rules, not historical source completeness.

The useful next step is to resolve the retained monthly failed member records with dated trading, corporate-action and terminal-settlement evidence, then recompute the **same** monthly paired protocol. A revision-safe original-vintage status/universe archive remains a separate missing requirement. More complete price labels or shorter holding periods cannot supply that archive.
