# Small- and micro-cap research: evidence, methods and open questions

Public evidence review: 2026-10-16. This editorial date is not a data cutoff. The portfolio snapshot was generated on 2026-09-16, covering 2015-01-01 to 2026-07-31; each appendix retains its own dates. No research was rerun for this report.

This report assembles the reviewed public record. It is not an inventory of every private experiment or a statement of strategy readiness. Missing comparisons remain open questions. All figures are historical, modeled or source-reported within their stated scope.

## Current conclusion

The clearest micro-cap finding is substantial downside risk and potentially long recovery waits. Returns remain sensitive to eligibility, missing quotes, execution clocks and portfolio construction. Low turnover has historical conditional associations, but an independent causal premium and practical capacity have not been established.

The fixed monthly low-turnover simulation reports net annual returns of 3.52%, 5.33% and 7.60% for 20-, 60- and 120-session windows; corresponding drawdowns are -65.01%, -52.39% and -45.61%. These are repeatedly inspected historical sensitivities, not a prospective ranking of investable strategies.

## Contents

1. Research map and evidence status
2. Comparable portfolio definitions
3. Turnover-window comparison
4. Definition × rebalance matrix
5. Research history and coverage register
6. All published snapshot table families
7. Revisions and limits
8. Open questions and resumption criteria
9. Public methodology appendices and sources

## Research map

### What did the smallest-stock baskets return and lose?

**Historical reconstruction · data audit**

Drawdowns and time below prior highs are central findings. Some early returns and missing-price treatments remain under review.

**Sample and construction：** N = 50 / 100 / 200 / 400 / 800; early 2008–2014 history is separate from the cleaned 2015+ sample.

**Open question：** How much do delistings, missing quotes and company actions change the result?

[Explore historical charts](https://runchengxie.github.io/quant-market-research/research/microcap/#microcap-history-evidence)

### Is the return primarily a size exposure?

**Historical factor evidence**

Style-factor tests help describe size exposure. Long-short factor returns and long-only micro-cap portfolios answer different questions.

**Sample and construction：** 18-year style research; see each factor’s source, sign convention and construction.

**Open question：** Does the result survive removing the smallest market-cap tail under the same ledger?

[Explore size-factor evidence](https://runchengxie.github.io/quant-market-research/research/style-factors-18y/?factor=size)

### What does low turnover add?

**Conditional association · exploratory**

The historical return spread changes with controls. Neither an independent premium nor stable synergy has been established.

**Sample and construction：** Latest common cross-sectional sample: 86 months, 2019-05 to 2026-06. One completed forward month in the published record.

**Open question：** Is avoiding the high-turnover tail enough, and does the relation persist prospectively?

[Read controls, intervals and execution](https://runchengxie.github.io/quant-market-research/research/factors/low-turnover/)

### How sensitive is the result to portfolio rules?

**Historical sensitivity comparison**

Turnover-window length changes return, drawdown and turnover in a fixed portfolio setup. It is not a fresh out-of-sample selection.

**Sample and construction：** 20 / 60 / 120 prior trading sessions; monthly, 40 target names and a 60-name buffer.

**Open question：** Can the ordering repeat under a frozen prospective rule and consistent share accounting?

[Compare the three windows](https://runchengxie.github.io/quant-market-research/research/microcap/#microcap-window-evidence)

### Could the portfolio actually trade?

**Simulation diagnostic · costs uncalibrated**

A public execution ledger tests participation limits, blocked trades and cash. Its short sample cannot establish profitable capacity.

**Sample and construction：** Separate short-sample diagnostic: 5% participation, T+1, daily price limits and 5 bp assumed cost.

**Open question：** Can fills, cash, corporate actions and calibrated impact reconcile in one ledger?

[Read the execution diagnostic](https://runchengxie.github.io/quant-market-research/docs/research/experiments/microcap-execution-diagnostic-20260928/)

### Are small stocks equally liquid across markets?

**Exploratory cross-market comparison**

Market-cap groups reveal differences in traded value and coverage. Aggregate trading activity is not a capacity estimate.

**Sample and construction：** Latest available observations by market; currencies, dates and eligibility vary.

**Open question：** Can currencies, trading calendars and eligibility be aligned before cost comparisons?

[Compare market coverage and liquidity](https://runchengxie.github.io/quant-market-research/research/liquidity/#market-profiles)

## Keep portfolio definitions separate

| Object | Formation and return basis | Purpose and limit |
| --- | --- | --- |
| Vendor reference index | Provider points and available membership; dividend conventions need review | Reference comparison, not an executable account |
| Smallest-N reconstruction | Post-close ranking, next-session close execution, following close valuation; early and cleaned sources kept separate | Historical return and risk with explicit missing-price policies |
| Low-turnover candidate | Monthly; 40 target names, 60-name buffer, 10 bp fee in the window comparison | Portfolio sensitivity; not the cross-sectional low-minus-high spread |
| Small-cap plus low-turnover composite | Definition × cadence grid from a historical weight-level screening engine | Requires consistent share-ledger confirmation before selection |
| Public execution diagnostic | Separate continuous holdings and cash; 5% participation, T+1, price limits, assumed 5 bp cost | Short-sample mechanism check; not full historical performance or certified capacity |

## Does smoothing turnover change the result?

In this historical simulation, longer turnover windows coincide with higher net return, smaller drawdown and lower trading turnover. This is definition sensitivity, not an independently confirmed optimum.

2015–2026 daily-data study; monthly formation, 40 target names, 60-name holding buffer and 10 bp trading fee. Values come directly from window_sensitivity in the public exploratory snapshot dated 2026-09-16. The snapshot coverage ends on 2026-07-31. This panel does not reuse the separate small-cap-plus-low-turnover composite results.

![Does smoothing turnover change the result?](https://runchengxie.github.io/quant-market-research/downloads/microcap-windows.en-US.svg)

| Trading-day lookback | Net annual return | Maximum drawdown | Sharpe | Annual trading turnover |
| --- | --- | --- | --- | --- |
| 20 | 3.52% | -65.01% | 0.264 | 11.59× |
| 60 | 5.33% | -52.39% | 0.331 | 6.79× |
| 120 | 7.60% | -45.61% | 0.411 | 4.47× |

Historical, repeatedly inspected evidence; no independent final holdout or broker-calibrated impact estimate. The daily traded-value proxy and simulator assumptions limit implementation claims. Do not interpret these bars as an executable return forecast.

## Turnover definition × rebalance cadence

Sixteen historical screening configurations are preserved here to show how much was explored. These small-cap-plus-low-turnover composite results use a weight-level screening engine. They are a different portfolio from the three-window low-turnover chart above.

Net annual return, percent, from the 2026-09-16 exploratory snapshot. Shading encodes historical return, not confidence. All cells need consistent share-ledger confirmation before cadence or parameter selection. The previously inspected 2024–2026 segment is descriptive only.

| Definition | Weekly | Biweekly | Monthly | Quarterly |
| --- | --- | --- | --- | --- |
| 20-day mean | 8.68% | 17.07% | 7.81% | 7.35% |
| 60-day mean | 9.56% | 19.00% | 7.73% | 8.33% |
| 60-day median | 9.52% | 18.60% | 7.91% | 9.16% |
| 120-day mean | 13.20% | 21.18% | 13.88% | 10.53% |

## Research history and coverage register

This is an editorial register of 35 reviewed research families, not 35 independent experiments. The review covers the known quantitative research repositories and selected adjacent infrastructure as of 2026-10-16. Language companions, migration copies and synthesis notes are deduplicated. A follow-up inventory below records which notebooks and migrated result bundles were located; unresolved items have named evidence requirements.

The web report and downloadable Markdown use this same register. Restricted studies are represented only by reviewed high-level findings and limitations; private parameters, raw inputs and reproduction locations are excluded. Their source identities remain in the restricted provenance ledger. Public evidence links below support the public subset, not every restricted historical claim.

### H01 · Size across market regimes

**Historical association · 2008–2026 · 223 month ends**

Industry-demeaned factor spreads vary across regimes. Size is defined in the large-cap direction; a negative spread cannot be described as small-cap underperformance.

The claim that 2026 was the first positive large-cap year conflicts with positive years listed in the same record. Early fundamentals are reconstructed; 2026 is incomplete.

### H02 · Early multi-factor spread stability

**Exploratory comparison · Overlapping starts in 2019–2022, ending in 2026**

Selected long-short combinations appeared stable across several starts. These are overlapping histories rather than independent tests.

A factor that helped a long-short spread need not help a long-only account. Keep selected model weights restricted and require a frozen future comparison.

### H03 · Minimum-cap threshold and endpoint reversal

**Endpoint-sensitive · Historical windows ending in 2026**

An attractive minimum-cap filter depended on the ending period. Changing the endpoint weakened the original interpretation.

Neither a permanent size floor nor unrestricted micro-cap exposure is established as the long-run optimum.

### H04 · Long-only translation and universe choice

**Historical simulation · 2008–2026; separate post-2015 universe**

Long-short findings did not transfer mechanically to long-only portfolios. Results changed materially with the universe and starting date.

Early unadjusted returns and incomplete eligibility require repair. A broad-universe result cannot certify a more restricted investable universe.

### H05 · Broad factor-combination search

**Selection-sensitive search · 455 combinations of 14 factors**

The historical search found attractive selected combinations, with substantial drawdowns and weaker later-period results.

The selected winner is not independent proof of optimal synergy. Conflicting annualizations and an inconsistent yearly win count remain unresolved.

### H06 · Combined scores versus independent sleeves

**Construction sensitivity · 2016–August 2026**

A combined-score screen exceeded separate sleeves in the inspected history; much of the advantage appeared after 2021.

Full-sample selection prevents a strict out-of-sample claim. Match the eligibility, cash, costs and execution clock before selecting a construction.

### H07 · Capital and traded-amount unit corrections

**Corrected assumptions · Separate 2019–2026 execution checks**

Capital assumptions and a 1,000-fold traded-amount unit error changed earlier liquidity interpretations. A high simulated fill ratio followed the correction.

A high fill ratio under an assumed model does not establish unconstrained liquidity or calibrated market impact.

### H08 · Model attribution and equal-weight benchmark

**Diagnostic, incomplete evidence · 2025–2026 attribution; 2016–2026 benchmark**

Style covariance explained part of a model return series. A separate equal-weight benchmark diagnosis exposed universe, new-listing and return-clipping defects.

Covariance is not causal skill attribution. Revised benchmarks still zero-filled missing stock-days and omitted costs; they cannot establish model promotion.

### H09 · Small-cap × low-turnover screening

**Historical exploration · 2015–July 2026; development through 2023**

Raw, residualized and combined screens gave different results and large drawdowns. Public candidate and cadence tables are retained below.

The repeatedly inspected 2024+ segment is descriptive. Narrative and snapshot versions differ; do not splice them into a single final backtest.

### H10 · Turnover definition sensitivity

**Historical cross-section · 2008–July 2026; 223 formations**

Point-in-time turnover and prior-window means or medians answer different questions. Quintile diagnostics are separate from later decile controls.

Alternative definitions require their own executable comparison. Definition sensitivity alone does not identify a unique premium.

### H11 · Deconfounding: early and corrected controls

**Conditional association · Early 133 formations; later 86 common-support months**

Later matched-stock controls retained a low-turnover association after size, risk, liquidity and return controls. A regression check also remained positive.

Earlier anatomy tables use a different sample and ranking basis. Neither double sorts nor regressions identify a causal or executable premium.

### H12 · Frozen prospective observation

**One-month observation · One completed month: August 2026**

The frozen July-end signal produced opposite raw and controlled spreads in August. Only one completed month is reported by the reviewed source.

Do not mark later pending months complete merely because time has passed. Require actual receipts and multiple new observations.

### H13 · Daily investability and intraday coverage

**Simulation; partial coverage · Separate daily portfolio and intraday samples**

An explicit suspension correction lowered the daily simulation’s annual return from 7.04% to 5.33%. Minute coverage was about 80.8%; quote-level coverage was lower.

Missing quotes are not proven suspensions or zero returns. Incomplete minute and order-book records cannot support a full-history fill-cost replay.

### H14 · Window × cadence comparisons

**Historical sensitivity · Public snapshot: 3 windows and 16 grid cells**

The complete published grid is available, alongside three fixed monthly low-turnover windows. Definitions and engine scope differ between the tables.

A source caveat says the grid was pending while the same snapshot contains 16 rows. Preserve the inconsistency and inspect actual rows; do not infer independent confirmation.

### H15 · Weight targets, shares and cash reconciliation

**Unreconciled comparison · Monthly and biweekly ledgers**

Weight-level, ideal-share and continuous-ledger results differ. Formation counts, target counts and owner replay periods also differ.

Do not splice return series or declare one canonical result. Zero modeled impact is an assumption, not evidence of zero realized cost.

### H16 · Capital, lots and delayed fills

**Path-dependent simulation · Seven public capital scenarios; separate lot checks**

Cash, lot rounding and delayed orders changed outcomes. The published capital sweep has rising returns at larger capital.

This is not an economic capacity curve: deferred orders can skip later losers, and impact is uncalibrated. Opportunity-cost figures are diagnostic.

### H17 · Monthly micro-cap exclusion scorecard

**Source-reported historical results · 2015–July 2026; selected monthly 40-name results**

Removing different bottom-cap fractions did not produce a monotonic improvement; large drawdowns remained.

A selected scorecard is not completion of the full weighting, buffer, cost and capacity protocol. Restricted configurations are not republished.

### H18 · Monthly 100-name and weekly 200-name proxies

**Historical bundles recovered; partial provenance · Different 2015+ and 2023+ samples**

The dated monthly 100-name bundle was recovered through a documented storage migration; its stored full-sample summary agrees with the rounded source-note figures. The weekly 200-name proxy remains a separate comparison.

No performance was rerun. The recent-window comparison receipt and immutable code/input/output binding remain missing. A separate weekly proxy cumulative-excess label still fails percentage-point subtraction; do not pool or reinterpret these returns.

### H19 · Complete exclusion robustness protocol

**Outputs recovered; structural checks passed · Bottom 0/10/20/30%; weighting and buffer controls**

The migrated bundle contains 112 factor rows, 56 weighting comparisons, 80 buffer rows and 24 capacity rows. The factor, buffer and capacity grids have unique keys, no blank cells and complete declared axes; four checkpoint files match final outputs byte-for-byte.

The recorded owner-code commit fields are unknown. This artifact audit does not rerun performance, authenticate every historical input, establish an untouched holdout or promote a strategy. The separate characteristic-decomposition protocol still has no located result bundle.

### H20 · Characteristic decomposition protocol

**Protocol only · Size, illiquidity, extreme returns, volatility and quality**

Double sorts and regression designs would test which characteristics accompany the apparent micro-cap effect.

No verified outputs were found for this protocol. Mechanism claims remain open, including delisting and shell-value effects.

### H21 · Future-quote and current-membership repair

**Replay blocked · 2015–September 2026 validity audit**

Earlier targets used future quote availability and current membership. Removing these filters changes the sample and invalidates direct reuse of old results.

A current membership snapshot cannot reconstruct historical membership. Missing held-security marks block a complete validated NAV.

### H22 · Historical names, ST status and date parsing

**Data repair, not return evidence · Historical-status supplement, September 2026**

Historical names replace current-name ST inference. Strict date parsing exposed nullable export strings and previously admitted delisted securities.

A documented nullable adapter repairs representation only. Suspension-event matches do not prove a tradable price or settlement value.

### H23 · Frozen target re-formation

**Targets rebuilt; NAV unverified · Protocol frozen before new performance inspection**

Historical eligibility is reconstructed without future-price filters; unknown status stays unknown. Old-target audits and new targets remain separate.

Targets are not a validated account. Do not drop missing-price names and renormalize; engine installation and run verification need separate receipts.

### H24 · 400-name missing-quote audit

**Incomplete valuation · Multiple audits with different windows**

Public audits found 189 missing marks on 117 dates in one window; an older broader replay found 3,708 marks on 1,407 dates.

Counts are neither distinct delistings nor comparable rates without denominators. Remaining-name averaging silently renormalizes exposure; the return bias is not quantified.

### H25 · Early history, cleaned sources and recovery

**Historical return and risk · 2008–2014 extension; later overlapping sources**

The longer history adds earlier drawdowns and prolonged underwater intervals. Cleaned and earlier source series are shown separately.

Do not stitch sources without an overlap audit. An unfinished recovery is censored at the sample endpoint rather than assigned a completed waiting time.

### H26 · Vendor points versus membership replication

**Reference comparison · Vendor series, available membership and proxy indices**

Published index points support return comparisons, while current membership snapshots lack historical effective dates and weights.

Dividend conventions, pool differences and incomplete daily data prevent a certified index replication. A proxy index is a separate benchmark.

### H27 · Continuous-account execution diagnostic

**Short-sample mechanism check · Public diagnostic dated 2026-09-28**

Continuous holdings and cash expose effects of participation, T+1, price limits and assumed fees. The public bilingual source is included in the appendices.

This diagnostic does not certify full-history performance or actual capacity. A later method does not retroactively validate earlier ledgers.

### H28 · Cross-market small-cap liquidity

**Descriptive, quality-gated · A-share, Hong Kong, Japan and US; unmatched dates**

Market-cap quantiles and USD ADV20 provide context, but dates, security types, units and eligibility differ. Some A-share totals do not reconcile.

Exclude inconsistent slices from rankings. Missing P90 cannot be replaced by a median; mean-versus-median lineage remains unresolved.

### H29 · Order-book and impact calibration readiness

**Partial coverage · Ten-date book audit plus separate historical trades**

Published valid and excluded order-book counts reconcile, but missing minutes cluster on one date; a trades-only sample has no orders.

Book counts are not actual-order capacity calibration. Require aligned orders, trades, timestamps and observed fills before estimating implementation cost.

### H30 · Constrained full-history factor follow-up

**Promotion held · 2008–2026 matched raw, constrained and net comparisons**

Data checks passed, but only half of the core factor gates passed. Constraints and costs reduced apparent factor returns.

Theoretical shorts, terminal proxies and reconstructed point-in-time fundamentals remain limits. This does not rerun or validate every earlier long-only strategy.

### H31 · Small-cap sensitivity artifact contract

**Infrastructure only · Adjacent factor-framework infrastructure**

A small-cap sensitivity CSV is part of an output contract, with synthetic pipeline checks.

A file contract and synthetic test are not empirical small-cap evidence. No performance conclusion is added for this infrastructure.

### H32 · Hong Kong provider, PIT and size-control probes

**Diagnostic, source-reported · Archived monthly comparisons, March 2026**

Provider and point-in-time fundamental portfolios differed substantially. The provider result accompanied small-cap and short-horizon price exposures; size-neutral and softer controls changed that exposure.

Style correlation does not establish causality. Better-controlled size exposure did not establish stronger structural alpha, and this Hong Kong sample cannot validate A-share micro-caps.

### H33 · Four-stock micro-cap feasibility and cost stress

**Reconstructed proxy; substantial limits · September 2023–July 2026; 150 weekly formations**

The strict historical-status window produced four selections at every formation. The standalone concentrated sleeve was highly sensitive to trading costs and experienced severe drawdowns; common-week index comparisons showed only partial agreement.

This is a reconstructed proxy, with revision safety false, current master-data inputs and incomplete limit-price execution modeling. Historical ST coverage ends in July; do not extend the strict sample through August or call it index replication.

### H34 · Cash-flow plus micro-cap allocation studies

**Source-reported; share with caveats · Three-year studies; broad proxy and separate four-stock sleeve**

The broad proxy comparison and later unified four-stock sleeve replay are distinct studies. A shared weekly calendar, next-session open execution and portfolio-level costs permitted a combined-account comparison.

The combined outcome does not isolate a micro-cap premium. Reconstructed fundamentals may contain later revisions; large drawdowns, concentration and incomplete execution constraints prevent live-capacity or formal point-in-time claims.

### H35 · Weekly size and beta neutrality feasibility

**Cached exploratory evidence; not rerun · Cached notebook comparisons: 2025 and partial 2026**

A concentrated candidate pool could not consistently satisfy portfolio size and beta constraints. Widening the candidate pool improved feasibility, while hard exposure controls reduced historical selected-sample excess returns.

The notebook reads existing comparison files and retains cached outputs; execution counters do not authenticate a fresh run. Samples were reused, lineage was incomplete and missing-outcome weights were flagged. Neither independent micro-cap alpha nor untouched out-of-sample performance is established.

### Public evidence anchors

- [Micro-cap history and method](https://runchengxie.github.io/quant-market-research/docs/research/factors/microcap/)
- [Low-turnover history and corrections](https://runchengxie.github.io/quant-market-research/docs/research/factors/low-turnover/)
- [Published numerical snapshot](https://runchengxie.github.io/quant-market-research/data/low_turnover_exploration.json)
- [Index reconstruction findings](https://github.com/runchengxie/quant-market-research/blob/main/studies/index_replication/findings-20260909.md)
- [Liquidity evidence and quality gates](https://runchengxie.github.io/quant-market-research/research/liquidity/)

Resumption requires source receipts for missing outputs, frozen future observations for selected rules, matched accounting for engine comparisons, and complete held-security valuation for returns. No research is promoted by this editorial consolidation.

## Evidence recovery follow-up · 2026-10-16

This follow-up searched beyond source notes: tracked notebooks, retained derived reports, migration receipts and identified cold archives. Artifact recovery, structural checks and research reproduction are separate evidence stages.

The private ledger retains exact source identities, hashes, search roots and exclusions. The public build reads only this reviewed summary. No backtest or notebook was rerun and no shared data or latest pointer was changed.

### R01 · Notebook inventory

**Inspected; one family added**

Seven source notebooks were found, all tracked in the two research repositories. Eight retained notebook files were also inspected: three are byte-identical copies, five are separate executed reviews. No additional untracked notebook was found in these two repositories.

Cached size/beta feasibility evidence is now H35. Empty launcher notebooks, duplicate copies and synthetic calibration outputs do not count as independent empirical confirmations. No notebook was executed by this audit.

### R02 · Published snapshot lineage

**53 rows matched; three still open**

All 53 published rows in six table families match retained CSV fields at numerical tolerance 1e-10. This covers candidates, anatomy, capital, cadence, ledgers and the joint grid.

The three low-turnover window rows are traceable to a public Git insertion, but a matching three-window runtime bundle was not located in the inspected roots. One coincidentally matching number elsewhere is insufficient. The published values are retained with this limitation.

### R03 · Historical 100-name bundle

**Recovered through migration**

The dated bundle and its self-referencing metadata were located after following a documented directory rename. All full-sample summary figures agree with the rounded source note; this closes the earlier blanket “bundle unavailable” gap.

The recent-window comparison receipt and immutable execution binding remain missing. Recovery of stored results does not reproduce performance, verify index membership or certify implementation.

### R04 · Micro-cap exclusion robustness

**Bundle recovered; provenance incomplete**

The full named artifact set and declared factor, weighting, buffer and capacity grids were recovered. Unique-key and completeness checks pass for 112 factor, 80 buffer and 24 capacity rows. Four checkpoint CSVs match final files.

The owner-code commit fields are unknown. Input-vintage authentication, matching historical code and an independent rerun remain requirements before stronger reproducibility or strategy claims.

### R05 · Frozen-target rebuild receipts

**Hashes agree; valuation remains blocked**

The stored readiness receipt and both target files match the hashes in the final verification receipt. Missing-mark table counts also agree with the stored audit.

The receipts explicitly say no NAV was published. Suspension matches do not supply settlement prices or prove fills, and this audit did not verify a new engine installation or replay.

### R06 · Attribution and characteristic decomposition

**Exact bundles still missing**

The exact historical Top800 attribution JSON and yearly CSV, its run-linked factor matrix, and the characteristic-decomposition output set were not found in the inventoried warm roots, migrated research subtree and identified cold archives.

Similarly named later matrices cannot substitute. These are bounded negative findings, not proof of deletion. Resolution needs an exact artifact or a documented historical run/code/input binding; a new run must be labeled separately.

### R07 · Later liquidity and execution reviews

**Executed reviews located**

Later executed notebooks preserve descriptive liquidity alignment and conditional execution-cost reviews. Synthetic calibration notebooks are separately identified as infrastructure evidence. The inspected cold-storage volume was available.

Later aligned samples do not erase older source discrepancies. Numeric notebook outputs with unresolved redistribution permission remain local; cached execution and synthetic tests do not establish actual-order capacity.

## Full published snapshot tables

The snapshot contains seven numerical families and 56 source rows: 9 candidates, 15 anatomy rows, 7 capital scenarios, 4 cadences, 2 ledgers, 16 joint cells and 3 windows. All rows are represented in this report; the three windows appear above. The JSON retains every machine field. Percentage return fields are already in percent; anatomy leg returns, fill ratios and cash weights are fractions and are converted for display. Rank IC and turnover multiples are not percentages.

### Nine candidates

![Nine historical candidates](https://runchengxie.github.io/quant-market-research/downloads/microcap-candidates.en-US.svg)

| Candidate | Annual net | Max drawdown | Sharpe | Annual turnover (×) | Blocked entry days | Blocked exit days |
| --- | --- | --- | --- | --- | --- | --- |
| Small cap | 2.05% | -73.78% | 0.218 | 2.97 | 605 | 1231 |
| Low turnover | 5.33% | -52.39% | 0.331 | 6.79 | 327 | 2383 |
| Residual turnover | -9.96% | -88.25% | -0.176 | 19.22 | 869 | 2735 |
| Industry-residual turnover | -7.62% | -84.49% | -0.086 | 19.95 | 724 | 1402 |
| Composite | 7.73% | -68.59% | 0.399 | 6.77 | 661 | 916 |
| Residual composite | 4.84% | -74.30% | 0.309 | 15.42 | 824 | 1502 |
| Industry-residual composite | 1.91% | -81.33% | 0.219 | 13.02 | 765 | 1305 |
| Large-cap control | 6.82% | -44.39% | 0.411 | 1.40 | 200 | 775 |
| Low-volatility control | 0.41% | -67.52% | 0.131 | 16.96 | 372 | 970 |

### Historical deconfounding anatomy

This earlier 133-formation panel is retained as history, not substituted for the later 86-month corrected common-support controls. Mean period returns are not annualized. The later inspected segment remains descriptive.

| Sample | Control stage | Formations | Stock observations | Mean rank IC | Low-turnover leg | High-turnover leg | Low − high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Development | Raw | 103 | 369066 | 0.0730 | 0.38% | -1.23% | 1.60% |
| Development | Size | 103 | 369066 | 0.0790 | 0.72% | -1.35% | 2.06% |
| Development | Size + low volatility | 103 | 369066 | 0.0262 | 0.01% | -0.95% | 0.96% |
| Development | + liquidity | 103 | 369066 | 0.0078 | -0.09% | -0.81% | 0.72% |
| Development | + past returns | 103 | 369066 | 0.0210 | 0.13% | -0.98% | 1.11% |
| Later descriptive | Raw | 30 | 160324 | 0.0600 | 2.54% | 0.82% | 1.72% |
| Later descriptive | Size | 30 | 160324 | 0.0727 | 2.76% | 0.93% | 1.83% |
| Later descriptive | Size + low volatility | 30 | 160324 | 0.0278 | 1.92% | 1.05% | 0.87% |
| Later descriptive | + liquidity | 30 | 160324 | 0.0180 | 2.22% | 0.94% | 1.28% |
| Later descriptive | + past returns | 30 | 160324 | 0.0179 | 2.16% | 1.04% | 1.12% |
| Full descriptive | Raw | 133 | 529390 | 0.0701 | 0.87% | -0.76% | 1.63% |
| Full descriptive | Size | 133 | 529390 | 0.0776 | 1.18% | -0.83% | 2.01% |
| Full descriptive | Size + low volatility | 133 | 529390 | 0.0265 | 0.44% | -0.50% | 0.94% |
| Full descriptive | + liquidity | 133 | 529390 | 0.0101 | 0.43% | -0.42% | 0.85% |
| Full descriptive | + past returns | 133 | 529390 | 0.0203 | 0.59% | -0.52% | 1.11% |

### Seven capital scenarios

All use the composite candidate and assumed 5% participation. Rising simulated returns do not certify scalable capacity. Cash, delayed fills and uncalibrated impact can change the path.

| Capital (CNY) | Annual net | Max drawdown | Sharpe | Fill ratio | Average cash | Delayed orders |
| --- | --- | --- | --- | --- | --- | --- |
| 100000 | 5.28% | -25.61% | 0.530 | 13.82% | 38.25% | 28 |
| 500000 | 11.46% | -48.69% | 0.587 | 40.94% | 5.11% | 37 |
| 1000000 | 11.85% | -49.94% | 0.585 | 43.89% | 2.54% | 38 |
| 5000000 | 12.48% | -51.59% | 0.596 | 44.48% | 0.71% | 40 |
| 10000000 | 13.00% | -51.67% | 0.608 | 45.74% | 0.66% | 44 |
| 30000000 | 14.47% | -51.40% | 0.645 | 47.71% | 2.04% | 41 |
| 50000000 | 15.07% | -51.70% | 0.664 | 48.29% | 6.18% | 40 |

### Four rebalance cadences

| Cadence | Annual net | Max drawdown | Sharpe | Annual turnover (×) | Development annual | Later descriptive annual |
| --- | --- | --- | --- | --- | --- | --- |
| Weekly | 9.56% | -61.56% | 0.452 | 5.18 | 6.44% | 21.07% |
| Biweekly | 19.00% | -59.37% | 0.703 | 3.25 | 17.86% | 23.04% |
| Monthly | 7.73% | -68.59% | 0.399 | 6.77 | 4.55% | 19.48% |
| Quarterly | 8.33% | -64.99% | 0.419 | 4.24 | 3.23% | 27.76% |

### Two continuous-share ledgers

These are comparison-only replays. Formations (139/296), weight targets (138/295) and owner replay periods (137/37) do not establish a matched sample. Cumulative-return machine fields have not been reinterpreted here. Modeled impact is zero; reported delay opportunity costs are uncalibrated and their currency basis needs confirmation.

| Cadence | Formations | Annual net | Max drawdown | Sharpe | Fill ratio | Average cash | Cumulative turnover (×) | Delayed orders | Reported delay cost |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Monthly | 139 | 15.06% | -51.07% | 0.658 | 50.56% | 12.63% | 147.43 | 40 | 291602.59 |
| Biweekly | 296 | 14.13% | -59.51% | 0.632 | 75.37% | 21.12% | 69.35 | 13 | -40144.76 |

### All 16 definition × cadence records

| Definition | Cadence | Formations | Annual net | Max drawdown | Sharpe | Annual turnover (×) | Development annual | Later descriptive annual |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20-day mean | Weekly | 592 | 8.68% | -58.55% | 0.428 | 6.13 | 6.75% | 15.59% |
| 60-day mean | Weekly | 592 | 9.56% | -61.56% | 0.452 | 5.18 | 6.44% | 21.07% |
| 60-day median | Weekly | 592 | 9.52% | -62.63% | 0.450 | 5.14 | 6.48% | 20.71% |
| 120-day mean | Weekly | 592 | 13.20% | -65.31% | 0.553 | 4.71 | 10.16% | 24.35% |
| 20-day mean | Biweekly | 296 | 17.07% | -60.16% | 0.649 | 3.68 | 16.53% | 18.95% |
| 60-day mean | Biweekly | 296 | 19.00% | -59.37% | 0.703 | 3.25 | 17.86% | 23.04% |
| 60-day median | Biweekly | 296 | 18.60% | -59.75% | 0.689 | 3.24 | 17.37% | 22.93% |
| 120-day mean | Biweekly | 296 | 21.18% | -60.48% | 0.746 | 3.11 | 20.72% | 22.76% |
| 20-day mean | Monthly | 139 | 7.81% | -68.42% | 0.402 | 8.60 | 3.11% | 25.75% |
| 60-day mean | Monthly | 139 | 7.73% | -68.59% | 0.399 | 6.77 | 4.55% | 19.48% |
| 60-day median | Monthly | 139 | 7.91% | -66.28% | 0.406 | 6.63 | 4.54% | 20.39% |
| 120-day mean | Monthly | 139 | 13.88% | -65.15% | 0.574 | 5.57 | 10.83% | 25.08% |
| 20-day mean | Quarterly | 47 | 7.35% | -58.34% | 0.387 | 4.69 | 3.13% | 23.12% |
| 60-day mean | Quarterly | 47 | 8.33% | -64.99% | 0.419 | 4.24 | 3.23% | 27.76% |
| 60-day median | Quarterly | 47 | 9.16% | -65.05% | 0.443 | 4.16 | 4.37% | 27.24% |
| 120-day mean | Quarterly | 47 | 10.53% | -65.07% | 0.479 | 4.21 | 6.18% | 26.77% |

Version warning: candidate, cadence and ledger numbers differ from earlier narrative reports. Apart from explicitly documented corrections, this compilation does not attribute every difference to a single cause. The snapshot also retains a stale caveat saying the joint grid is pending despite containing 16 cells. These conflicts remain visible rather than being silently reconciled.

## How the interpretation changed

Read revisions with the study they affect. A change in one return window or simulator does not automatically invalidate every related experiment.

### Next-session execution

Early reconstructions used post-close information with same-close execution. Those versions were superseded. Historical reconstruction now separates the decision close from the execution close.

### Data-source transitions

An old holding interval divided prices from different sources across the 2014–2015 boundary. That interval was removed; separate historical coverage must not be silently stitched together.

### Return-window correction

Later low-turnover validation uses next-session open to period-end close with both endpoints present. Earlier attribution tables use a different basis and must remain historical.

### Execution paths and accounting

Delayed fills, cash and held shares can change both performance and cadence rankings. Report simulator-specific results separately; a participation constraint improving simulated return is not proof of alpha.

### A repeatedly inspected holdout

2024–2026 has been examined across several historical sensitivity checks. It remains descriptive evidence; further parameter choices need genuinely prospective observations.

## Open research and publication gaps

### Micro-cap exclusion and weighting

Publish a matched 0% / 10% / 20% / 30% exclusion matrix with equal- and market-value weights. Recompute signals on each formation universe and retain the same costs, buffer and evaluation period.

### Size, liquidity and other characteristics

Separate size from illiquidity, extreme daily returns, idiosyncratic volatility, turnover and quality on common support. Conditional association would still not identify a causal mechanism.

### A comparable execution and capacity ladder

Use identical targets and dates to compare ideal held shares with a constrained cash ledger. Attribute differences to lot size, participation, delayed fills, costs and idle cash before publishing capacity claims.

### What would justify stronger conclusions?

Resume a return comparison only after the same universe, formation clock, source versions, benchmark, missing-price policy and held-share accounting reconcile. Capacity claims require fills, cash, costs and delayed-order opportunity costs under calibrated impact. Mechanism claims need common-support controls and prospective evidence; stage differences alone do not establish causal effects. Preserve failed and inconclusive tests.

## Sources and version boundaries

- [Interactive research page](https://runchengxie.github.io/quant-market-research/research/microcap/)
- [Published exploratory snapshot](https://runchengxie.github.io/quant-market-research/data/low_turnover_exploration.json)

The appendices below preserve the selected public language records in full. English and Chinese companions are not always equally detailed: the Chinese execution note contains additional historical receipts. Language selection does not certify equivalence of samples or authorize reusing superseded figures. Read correction notices beside their source results.

## Appendix 1 · Micro-cap Method

[Canonical web source](https://runchengxie.github.io/quant-market-research/docs/research/factors/microcap/)

## Microcaps: return evidence and underwater periods

[Chinese version](https://runchengxie.github.io/quant-market-research/docs/research/factors/microcap.zh-CN/?lang=zh-CN)

This page describes reconstructed historical rules and risk characteristics. It is not a Wind index replication and does not represent a directly tradable strategy.

### Plain-language takeaway

The clearest result here is about risk: portfolios rebuilt from small stocks had deep losses and sometimes took years to recover their previous highs. Some early returns are still being checked, and delisted stocks, historical membership, and actual trading have not been fully reconstructed. Treat the return series as a research record, not as an index or an account result.

An **underwater period** is the time a portfolio stays below its previous high until it passes that high again. **Maximum drawdown** is the largest fall from a high to a later low. **NAV** (net asset value) is the portfolio-value series scaled to a starting level. For each measure, missing-price rules also matter.

The current source coverage extends through 2026-09-17. The next-day return audit for the minimum-market-cap proxy is computable through 2026-09-16. Portfolio sizes are N = 50, 100, 200, 400, and 800.

The [microcap execution diagnostic](https://runchengxie.github.io/quant-market-research/docs/research/experiments/microcap-execution-diagnostic-20260928/) uses a separate public execution-simulation ledger and must not be joined directly to historical paper returns. Differences in data cleaning, decision clocks, fills, and cost assumptions remain part of the evidence boundary.

### Research map: history, factors and execution

Public evidence synthesis reviewed on 2026-10-16. This review did not rerun the studies or extend their sample dates. The [micro-cap topic page](https://runchengxie.github.io/quant-market-research/research/microcap/) connects the following questions without treating them as one strategy.

| Question | Available public evidence | Important boundary | Next useful evidence |
| --- | --- | --- | --- |
| What did the smallest stocks return and lose? | Reconstructed N = 50, 100, 200, 400 and 800 baskets, drawdown and underwater statistics, missing-price sensitivities | Historical eligibility, company actions and delisting prices remain incomplete; strict and partial treatments have different valid sessions | Reconcile holding-level missing quotes and settlement events |
| Is the result a size exposure? | Historical style-factor research, including size and market regimes | Factor sign and long-short construction differ from a long-only micro-cap basket | Matched tail-exclusion tests with recomputed formation signals |
| What does low turnover add? | [Low-turnover evidence](https://runchengxie.github.io/quant-market-research/docs/research/factors/low-turnover/): common-sample controls, confidence intervals and a short forward record | Conditional association is not a causal premium; theoretical stock-group returns are not executable portfolios | Freeze prospective rules and accumulate additional observations |
| Do portfolio rules change the result? | Published 20-, 60- and 120-session window sensitivity | Repeatedly inspected historical sample; cannot select an independently confirmed optimum | Repeat frozen comparisons under consistent share accounting |
| Could the portfolio trade? | [Public execution diagnostic](https://runchengxie.github.io/quant-market-research/docs/research/experiments/microcap-execution-diagnostic-20260928/), cash and blocked-trade accounting | Separate short sample, adjusted-price proxy and assumed cost; not a capacity certification | Identical targets and dates, reconciled accounting and calibrated impact |
| Are small stocks equally liquid across markets? | Market-cap group traded-value and coverage comparisons; [early A-share turnover context](https://runchengxie.github.io/quant-market-research/docs/research/factors/smallcap-turnover-history/) | Currencies, dates and eligibility differ; turnover rate and traded value are distinct measures | Align samples, currency conversion and execution constraints |

#### Keep portfolio identities separate

A vendor reference index, a daily smallest-N reconstruction, a monthly low-turnover candidate and the short execution diagnostic have different identities. Neither a shared label such as “micro-cap” nor equal portfolio size makes their results comparable. Record the sample, formation and execution clock, weighting, buffer, missing-price treatment, costs and simulator before comparing any two figures. Do not join their NAVs.

The new window-comparison chart reads `window_sensitivity` directly from the existing public `low_turnover_exploration.json` snapshot, generated on 2026-09-16 with overall coverage through 2026-07-31. Its public method describes 2015–2026 daily data, monthly formation, 40 target holdings, a 60-name buffer and a 10 bp fee. These are low-turnover window results, not the small-cap-plus-low-turnover composite. Returns and drawdowns in this snapshot are percentage values; annual turnover is a multiple. A later note with different source figures must not silently replace these values while keeping the old provenance.

#### Revisions that affect interpretation

- Early reconstructions that used post-close market capitalization with same-close execution were superseded. The reconstruction now separates the decision close and next-session execution close.
- An old 2014–2015 holding interval used execution and valuation prices from different sources. That interval was removed. Early-period eligibility remains incomplete.
- Later low-turnover validation changed to next-session open through period-end close, requiring both endpoints. Its revised 86-month common sample must not be merged with older attribution tables. See the latest-validation section in the [Chinese source record](https://runchengxie.github.io/quant-market-research/docs/research/factors/low-turnover.zh-CN/).
- Share accounting, idle cash and delayed fills can change return and cadence rankings. Results from a weight-level screening simulator and a share ledger must retain their engine identity. An apparent gain from tighter participation limits is execution-path sensitivity, not evidence of additional signal alpha.
- The 2024–2026 sample has already been examined across several historical comparisons. It is descriptive evidence rather than an untouched final holdout.

The public revision history is preserved in the existing [follow-up research source record](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/experiments/turnover-microcap-followup-20260915.md), which explicitly marks superseded low-turnover results. Those old figures are not reused as current headline returns.

#### Open comparisons and publication requirements

Three comparisons still need a matched, reproducible public synthesis: removing the smallest 0%, 10%, 20% and 30% under equal and value weighting; separating size from liquidity, extreme daily returns, idiosyncratic volatility, turnover and quality on common support; and comparing ideal held shares with a constrained cash ledger across capital levels. This list records open questions, not completed results.

For each addition, preserve a stable experiment identity, source version, sample dates, formation-time availability, universe, benchmark, metric units, costs, missingness policy, simulator and limitations. Publish reviewed aggregate outputs only. Raw vendor data, private strategy configurations and private reproduction locators remain outside this public site. A source-reported historical number without recoverable provenance should remain labeled as such until reproduced; no return series should be invented from summary metrics.


## Appendix 2 · Low-turnover Method

[Canonical web source](https://runchengxie.github.io/quant-market-research/docs/research/factors/low-turnover/)

## Low turnover: what might it represent?

[Chinese version](https://runchengxie.github.io/quant-market-research/docs/research/factors/low-turnover.zh-CN/?lang=zh-CN)

Current evidence is exploratory. An independent premium and practical tradability have not been established.

### Plain-language takeaway

In some historical samples, lower-turnover stocks did better. Low turnover also tends to appear alongside lower volatility and less active trading. The return gap changes when those features are included, so the evidence does not yet show that low turnover itself adds returns or that the pattern can be traded reliably.

In the tables, **low minus high** means the average return of the low-turnover group minus that of the high-turnover group. It is a historical group difference, not the return an investor would have earned. **Rank IC** measures whether the signal's stock rankings line up with later return rankings; a value near zero means the ranking added little information. **Point-in-time data** means information that was actually available on the date being studied. **ADV20** is the average trading value over the prior 20 sessions, used as a rough measure of how much a stock normally trades. One **basis point (bp)** is 0.01%; the slippage values below are assumptions, not broker-calibrated costs.

The candidate study covers 2015-02 through 2026-07. The development sample is 2015–2023; 2024–2026 is descriptive only. Historical style diagnostics cover 2008–2026.

The study separates turnover proxies from the economic interpretation of the signal, reports group ranking and implementation limits, and keeps unresolved data and execution questions explicit. See the Chinese companion for the historical tables and detailed experiment record.


## Appendix 3 · Micro-cap Execution Simulation Diagnostic

[Canonical web source](https://runchengxie.github.io/quant-market-research/docs/research/experiments/microcap-execution-diagnostic-20260928/)

## Microcap portfolio execution diagnostic

[Chinese version](https://runchengxie.github.io/quant-market-research/docs/research/experiments/microcap-execution-diagnostic-20260928.zh-CN/?lang=zh-CN)

### Plain-language takeaway

A short historical list of target stocks was sent through a public trading simulator to see what could be bought or sold under basic trading limits. This checks whether the simulation process runs; it does not show that a strategy makes money. The sample is short, and both prices and costs are simplified.

A **5% participation rate** limits simulated trading in a stock to 5% of its daily trading value. **T+1** means a stock bought today cannot be sold until the next trading day. **Five basis points** equals a 0.05% assumed cost per trade. Any unfilled amount stays in cash.

The `microcap-execution-diagnostic` experiment selects the smallest N eligible stocks from cleaned daily data using post-close market capitalization, ST status, suspension, and listing-state rules. Each decision date has an independent research clock. The input is submitted by content hash to `quant-backtest-runtime`, whose worker calls the public execution simulator in `quant-platform`.

The diagnostic uses a 5% participation rate, T+1, daily limit-up and limit-down blocking, unfilled cash, and a simplified 5-basis-point per-trade cost. Prices use the cleaned daily `adj_close` proxy. Targets, orders, fills, daily cash, and NAV ledgers remain outside the repository. Only runtime-validated ledgers are copied into the diagnostic directory, and `summary.json` records the job ID.

This diagnostic ledger is separate from historical paper returns. It is an execution feasibility check, not a live-trading result or strategy promotion.


## Appendix 4 · Small-cap Turnover History

[Canonical web source](https://runchengxie.github.io/quant-market-research/docs/research/factors/smallcap-turnover-history/)

## Small-cap turnover history, 2008–2014

[Chinese version](https://runchengxie.github.io/quant-market-research/docs/research/factors/smallcap-turnover-history.zh-CN/?lang=zh-CN)

### Plain-language takeaway

This note checks how actively smaller A-share stocks traded from 2008 to 2014. It adds background for later low-turnover and microcap studies; it does not test a strategy or show how much money could have been invested. **Turnover rate** here is the share of tradable stock that changed hands during the period. Missing historical eligibility and trading-status data limit what the sample can tell us.

This supplement uses published A-share `daily` and `daily_basic` assets from `quant-market-data-platform` to observe turnover among the N smallest stocks ranked by total market capitalization.

It supplies early-period liquidity context for the low-turnover and microcap studies. It is not a low-turnover strategy backtest. The data source, date range, ranking rule, and missing-data treatment remain part of the published research boundary.

