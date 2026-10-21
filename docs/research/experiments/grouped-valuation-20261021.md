# Low-valuation research: annual comparisons, definitions and return evidence

[Chinese version](grouped-valuation-20261021.zh-CN.md)

**Unpublished draft, prepared for local review.** The first layer is complete. The frozen 130-date, 556,948-record baseline was reproduced with every stored value equal, then extended into 6,500 date/group/metric/sample-basis distribution rows. The second layer contains 720 conditional factor-period diagnostics. It does not establish a complete or executable return history.

Financial histories and reconstructed ST histories both have **revision_safe=false**. These historical observations are not untouched out-of-sample evidence. Existing results, source assets and published aliases were preserved.

## Reading the topic

The existing `/research/valuation-groups/` URL is the low-valuation topic. It combines annual comparisons, five accounting definitions, historical status groups, the older ordinary valuation portfolio archive, conditional factor diagnostics and interpretation. Detailed distribution and factor controls remain below the narrative.

Annual comparisons default to non-ST parent-equity PB. Each main row is the last sampled date in that year, with minimum, P1, P5, valid/quoted counts and exclusions. P1 and P5 give every valid stock one observation with linear interpolation, without market-cap weighting. A separate foldout reports the minimum across that year's sampled cross-sections, including every tied date and its valid sample count. It does not mix extreme dates with last-sampled-date percentiles. The chart uses a logarithmic vertical scale and breaks at unavailable values or missing years. The latest row is 2026-10-16, not a full-year endpoint. There are 12 samples per year in 2016–2025 and ten in 2026; none claim daily historical lows.

Coverage changes are visible. Ordinary PE on 2016-01-29 has just 10 valid observations out of 2,558 quotes. The financial-template gap remains. Latest *ST deducted PE covers only 4/88 quotes, describing an available positive-profit subset. A dated historical normal name and listing interval are required for non-ST; absence from the reconstructed positive ST file is insufficient.

The 2026-10-16 common positive, same-period sample contains 1,743/5,567 quotes. PE versus PB rank correlation is 0.5066, with cheapest-quintile Jaccard 28.07%; ordinary versus deducted PE is 0.9466 and 75.38%; PB versus PB excluding goodwill and intangibles is 0.9343 and 75.82%. Jaccard is intersection/union, not the fraction of one selected list retained. These compare same-date valuation ranks, not forward-return IC or which definition earns more.

## Separate return experiments and interpretation

The topic retains the existing published `style-factors/weekly-20260904` ordinary valuation archive: 2008-02-01 to 2026-09-04, with 4,518 daily observations each for PB value, PE earnings yield and PS value. Their geometric annualized idealized long-short spreads are 10.64%, 5.24% and 6.04%. Monthly quintiles use equal initial endpoint weights and fixed shares between rebalances. The retained historical implementation uses `missing_holding_return=zero`, materially different from the new complete-original-basket rule below. Of 32 receipts, 31 match, with a `meta.json` difference and unrecovered exact generating revision. Source/formula and PIT limitations in the [factor dictionary](../factors/barra-factor-dictionary.md) and [source inventory](../factors/barra-source-inventory.md) remain. A newer Linux package is not substituted here.

The new study uses 36 monthly forward-return periods and conditions IC on resolvable endpoints. A positive conditional correlation does not establish an unconditional all-stock result, a full executable quintile history or a live account. Gap bars show first-failing-check counts from the retained member audit, not returns; missing returns are never plotted as zero. Exact counts and definitions remain below.

One-off earnings, cyclical profit peaks, expected impairment, weak asset realization and distress are mechanisms to investigate, not causal findings here. Positive parent profit can coexist with a deducted loss, so very low ordinary PE need not mean a sustainable short payback period. Deducting goodwill and intangibles does not prove liquidation proceeds. An IC relationship can coexist with an untradeable basket. Discussion is aggregate or anonymous; private security identities and supplier amounts are not published.

Topic evidence is prepared without rerunning research from the existing public valuation panel, historical factor summary, public source manifest and retained endpoint-gap audit. Its public projection includes only aggregate counts, correlations, old factor summaries and source hashes; the external receipt retains exact input paths. To reproduce into new destinations:

```sh
cd web
node --import tsx scripts/prepare-low-valuation-topic.mjs \
  --gap-audit "$FROZEN_ENDPOINT_GAP_AUDIT" \
  --output "$NEW_PUBLIC_AGGREGATE" \
  --receipt "$NEW_EXTERNAL_RECEIPT"
```

Both destinations must not exist. Annual views derive directly from the original grouped public distributions; all annual rows covered by the private annual summary are checked against it at acceptance. No raw vendor data or security list is copied to the topic.

## Scope and first findings

Formations run from 2016-01-29 through 2026-10-16. October is partial. Four status groups and an unknown category are retained. “All quoted” includes unknown status; it is not independently certified complete exchange membership.

The latest 5,567 quoted names comprise 5,333 non-ST, 108 ST, 88 *ST and 38 unknown. Unknown reasons are 28 unknown/ambiguous names, eight unavailable instrument intervals, one name/positive-state conflict and one delisting-period record. A missing positive ST row alone never establishes normal status.

The following are metric-specific positive-denominator samples on 2026-10-16. They are not the same stocks across definitions. Equal-weight arithmetic mean and ratio of totals use the identical valid sample within each row.

| Group / definition | Valid names | Equal-weight mean | Total M / total D | Median | Minimum positive |
| --- | ---: | ---: | ---: | ---: | ---: |
| All quoted / deducted PE TTM proxy | 3,703 | 210.8240 | 16.6107 | 41.3059 | 3.8897 |
| Non-ST / deducted PE TTM proxy | 3,646 | 210.6871 | 16.5596 | 41.3554 | 3.8897 |
| ST / deducted PE TTM proxy | 23 | 447.1766 | 36.0351 | 76.3380 | 16.0515 |
| *ST / deducted PE TTM proxy | 4 | 121.7066 | 83.3040 | 106.4400 | 56.9525 |
| All quoted / parent-equity PB | 5,447 | 5.3773 | 2.0431 | 2.5310 | 0.0496 |
| Non-ST / parent-equity PB | 5,252 | 5.0042 | 2.0593 | 2.5261 | 0.2253 |
| ST / parent-equity PB | 101 | 22.1442 | 2.1080 | 2.8792 | 0.3435 |
| *ST / parent-equity PB | 56 | 10.1351 | 1.9441 | 3.2765 | 0.0863 |
| All quoted / PB excluding goodwill and intangibles proxy | 2,601 | 47.8525 | 2.1790 | 2.7675 | 0.1091 |
| Non-ST / adjusted PB proxy | 2,524 | 48.9953 | 2.2064 | 2.7690 | 0.2445 |
| ST / adjusted PB proxy | 43 | 11.9691 | 2.2681 | 2.9448 | 0.3538 |
| *ST / adjusted PB proxy | 14 | 13.9775 | 1.2915 | 2.6231 | 0.1091 |

Only four of 88 *ST names have positive available deducted earnings. Its PE distribution therefore describes a highly selected positive-profit subset. Extreme ratios and small denominators make arithmetic means particularly sensitive. The all-quoted minimum ordinary PB belongs to unknown status, illustrating why a minimum cannot establish a cheap normal stock.

The private audit retains every minimum tie, its security identifier, actual denominator and market value, report periods, valid sample count and risk flags. Each date/group/metric/basis also has a ten-name low-valuation tail, extended for boundary ties. The draft public file contains aggregate statistics only, not supplier amounts or security-level lists.

## Five definitions and two sample bases

M is `daily_basic.total_mv × 10,000` in yuan. PE uses `M / TTM(n_income_attr_p)`; deducted PE uses `M / TTM(profit_dedt)` as a supplier-defined proxy. TTM is current YTD plus prior full year minus matching prior YTD; annual reports use their annual amount. Missing legs are unavailable.

Parent-equity PB divides M by `total_hldr_eqy_exc_min_int`. Adjusted variants deduct `goodwill`, then `goodwill + intan_assets`. These assets have consolidated group scope while equity excludes minority interests. Attribution, preferred equity and multi-class market value are not certified. Capitalized development costs and tax adjustments are not additionally deducted. Proxy labels are retained.

`metric_available` uses each metric's positive finite denominator and corresponding latest admissible report. `common_five` additionally requires all five metrics and matching report periods. Both bases are available at every formation, including empty groups. Quantiles P01/P05/P10/P25/P50/P75/P90/P95/P99 use pandas linear interpolation. Zero/negative denominators are counted but never become low valuations. Missing assets are not zero, negative asset balances are unavailable, and no positive multiple is clipped for this distribution study.

The arithmetic mean averages security-level multiples equally. Ratio of totals is `sum(M) / sum(D)` over the identical positive valid set. It is not an arithmetic or market-cap-weighted mean; it can be interpreted as denominator-weighted multiples on that set. Median and minimum remain separate fields.

## Historical status and provenance

Names must be active in their start/end interval, have announcement dates strictly before formation, and have no ambiguous latest-start names. Instruments must have a known listing date no later than formation and no prior delisting. A special-treatment name must match the reconstructed positive state's type and modeled availability. *ST is matched before ST. Disagreement, missing dates, unavailable positive states and delisting periods remain unknown. Non-ST requires a positively observed dated normal name plus absence of a conflicting positive state; positive-file absence by itself is insufficient.

Inputs are the original `valuation-panel-20261018/run03` panel and published summary, the sealed `vintage=20261018` financial tables, each original hashed daily-basic formation partition, namechange/instruments version 20260928 and reconstructed ST version 20261020. ST file SHA256 is `d5ad218d558e31452e28d0d0f184ec31069b7213f4a60b63b3dd67f84c72dbee`. The 130 baseline values are checked exactly; only whole-panel integer-to-float dtype widening is tolerated.

Financial admission retains strict prior-date disclosure, consolidated `report_type=1`, per-table 550-day freshness and the original retained-version reconstruction. It does not certify original historic report revisions. The financial-template diagnosis is not silently incorporated; this first version deliberately preserves the existing baseline and its coverage gap.

Daily price endpoints come from the immutable retained clean asset referenced by the earlier ST paired study, through 2026-10-16, rather than a moving clean alias. Its path and manifest hash, the calendar, all formation partitions, all financial input hashes, code hashes and output hashes are recorded in the external run receipt. Top-level input files are checked again before run completion. This is not an independent revalidation of every price file's vendor history.

## Conditional factor results and the return blocker

The fixed diagnostic window has 36 monthly formations from 2022-12-30 through 2025-11-28, entries 2023-01-03 through 2025-12-01 and final endpoint 2026-01-05. Signals are positive multiples, with lower values receiving higher scores. Five groups are formed using average ranks so exact ties stay together. At least 25 signal names are required; Rank IC additionally requires at least ten resolved returns and nonconstant ranks. Factor diagnostics always use `metric_available`, independently of the distribution sample selector.

Entry is the next SSE session's adjusted close; endpoint is the session after the next formation. Positive finite prices, positive amount and non-suspended flags are required at both endpoints. A long entry at an up limit, an exit at a down limit, missing flags or a delisting before endpoint leave the return unresolved. There is no future-availability filter before quintile construction. A quintile requires every original member; missing members do not receive zero or trigger renormalization.

The stock forward return is `adj_close(endpoint) / adj_close(entry) - 1`, with equal initial weights within each basket. This adjusted-price proxy does not establish a raw-share and corporate-action cash ledger.

Rank IC is Spearman correlation between `−multiple` and the available endpoint return, **conditional on resolved outcomes**. It is not an unconditional all-stock result. The monthly IC mean is equal-weighted across admitted months; ICIR uses sample standard deviation times sqrt(12), only with at least six months, and is not a significance claim.

| Group | Deducted PE IC / months | Parent PB IC / months | Adjusted PB IC / months |
| --- | ---: | ---: | ---: |
| All quoted, listing interval required | 0.03374 / 36 | 0.07157 / 36 | 0.06339 / 36 |
| Non-ST | 0.03381 / 36 | 0.07207 / 36 | 0.06352 / 36 |
| ST | unavailable / 0 | 0.03590 / 36 | 0.02405 / 35 |
| *ST | unavailable / 0 | 0.02793 / 35 | −0.02858 / 6 |

**Complete quintile return support is much weaker than IC support.** All-quoted parent-PB and deducted-PE quintiles have zero complete months under these strict original-basket rules. All-quoted adjusted PB has one complete cheapest-quintile month and no paired cheap/expensive month. Thus there is no complete all-market quintile history, spread or cost result to report.

A post-run audit of the existing member records explains the zero support; it does not rerun returns. Parent PB has 189,797 stock-months, with 185,237 resolved and 4,560 unresolved. Deducted PE has 133,275, with 131,115 resolved and 2,160 unresolved. The mutually exclusive counts below assign the first failing check in this order: entry price, entry amount, entry suspension, entry limit, terminal event, endpoint price, endpoint amount, endpoint suspension, endpoint limit. Zero-count checks are omitted. They are not overlapping raw flag totals.

| First failing check | Parent PB | Deducted PE TTM proxy |
| --- | ---: | ---: |
| Entry price missing or invalid | 125 | 37 |
| Entry up limit after preceding checks pass | 3,373 | 1,785 |
| Delisting by endpoint after entry checks pass | 25 | 2 |
| Endpoint price missing or invalid after preceding checks pass | 351 | 140 |
| Endpoint down limit after preceding checks pass | 686 | 196 |
| Total unresolved | 4,560 | 2,160 |

Every one of the five original baskets has unresolved members in every one of the 36 months. The minimum monthly unresolved counts for quintiles 1–5 are 3/4/4/6/10 for parent PB and 1/1/1/1/4 for deducted PE. A missing endpoint quote does not establish suspension, and this draft does not invent an intramonth fill. The private endpoint-gap receipt preserves the source member and run-receipt hashes. Complete-basket absence is a limitation of the current evidence and execution model, not evidence that prices do not exist anywhere or that the factor has zero return.

ST parent PB has eight complete cheapest-quintile months and three paired-tail months; adjusted PB has 15 and eight respectively. *ST parent PB has eight and three; adjusted PB has two and one. These sparse and different conditional samples cannot establish which definition is better. ST and *ST deducted-PE samples never pass the fixed 25-name signal threshold in this window; results remain unavailable rather than lowering the threshold after seeing data.

Turnover compares equal initial target weights with the previous fully resolved basket's drifted endpoint weights, using L1 traded notional. Initial cash entry and the final liquidation are included. Missing preceding basket marks make turnover and net scenarios unavailable; the method never resets missing history to cash. Costs are additive 0/10/30 bp per traded notional. These are hypothetical conditional-basket sensitivity calculations, not fee-accurate reinvested wealth or executed orders. Gross and cost summaries show their own month counts; 0/10/30 comparisons use identical support. There is no CAGR compounded across gaps.

For example, the cheapest ST parent-PB basket has eight gross-return months but only two traded-notional/cost months. The page displays each count and the 0 bp comparison on the same support as 10/30 bp, so the broader gross mean is not mistaken for the cost scenarios' baseline.

The practical next step is to investigate the retained unresolved member audit, reconstruct raw shares, cash entitlements and corporate actions, and use a specified execution/marking policy with dated availability and terminal settlements. Endpoint flags alone do not support intramonth fills, market impact, actual capacity, borrowing or a continuous account ledger. Missing marks must not be replaced with zero or the last price just to obtain a full-market performance line.

## Reproduction and output contract

Resolve machine-local owner paths externally. Use the existing locked project environment, set `PYTHONPATH=src`, `OPENBLAS_NUM_THREADS=1` and `OMP_NUM_THREADS=1`, and run with lower CPU priority if sharing the host. No download or API request is made. DuckDB is fixed at two threads and 512MB; pandas works on the selected 130 formations and 37 price endpoint dates, not a daily whole-market backtest. This budget does not impose a 512MB cap on the entire Python process.

```sh
python scripts/analyze_grouped_valuation.py \
  --baseline-panel "$QMR_DATA/task_outputs/valuation-panel-20261018/run03/reconstructed_panel.parquet" \
  --baseline-summary web/public/data/valuation_panel_reviewed.json \
  --vintage "$MDP_DATA/assets/tushare/a_share/fundamentals_vintages/vintage=20261018" \
  --daily-basic "$FROZEN_DAILY_BASIC_LOCATOR" \
  --namechange "$FROZEN_NAMECHANGE_20260928" \
  --instruments "$FROZEN_INSTRUMENTS_20260928" \
  --st-history "$FROZEN_ST_HISTORY_20261020" \
  --daily-clean "$FROZEN_CLEAN_20261016" --calendar "$EXCHANGE_CALENDAR" \
  --factor-start 20230101 --factor-end 20251231 \
  --output "$NEW_RESEARCH_OUTPUT"
```

Output must not exist and must be outside the repository. `private_panel.parquet`, `private_minimum_audit.csv`, `private_low_valuation_tail.csv` and `private_factor_members.parquet` stay in external research storage. `distribution_statistics.csv`, `factor_periods.json`, `distribution_aggregate_draft.json` and `public_aggregate_draft.json` contain derived aggregates; `phase1_receipt.json` preserves the completed first layer even if later return inputs fail, and `receipt.json` records complete run lineage. Only the aggregate draft is prepared in the worktree's public-data directory. Nothing is deployed or promoted.
