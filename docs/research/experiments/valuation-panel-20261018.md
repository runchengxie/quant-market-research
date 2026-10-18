# Low valuation: historical denominator coverage and rank comparison

[Chinese version](valuation-panel-20261018.zh-CN.md)

**The five valuation definitions cannot yet support a comparable whole-market cheapest-stock list.** On October 16, 2026, only 1,743 of 5,567 priced names (31.3%) have all five positive, available denominators from the same reporting period. On those names, PE and PB rank correlation is 0.507; the Jaccard overlap of their cheapest fifth is 28.1%. These are descriptive rank results, with no return backtest.

The panel contains 556,948 stock-date records at 130 monthly formations from January 29, 2016 to October 16, 2026. October is partial. [Download the reviewed aggregate](https://runchengxie.github.io/quant-market-research/data/valuation_panel_reviewed.json). The [definition and six-company checks](valuation-denominators-20261018.md) explain the original accounting choices.

## Latest coverage

| Definition | Available names | Share of 5,567 |
| --- | ---: | ---: |
| PE: parent profit TTM | 3,839 | 69.0% |
| PE: deducted parent profit TTM proxy | 3,703 | 66.5% |
| PB: parent equity | 5,447 | 97.8% |
| PB: parent equity less consolidated goodwill proxy | 2,650 | 47.6% |
| PB: parent equity less consolidated goodwill and intangibles proxy | 2,601 | 46.7% |
| All five available, any reporting periods | 1,744 | 31.3% |
| All five available, matching reporting periods | 1,743 | 31.3% |

Missing goodwill or intangibles are not zero. A nonpositive denominator is unavailable, not an exceptionally cheap valuation. Income, indicator and balance-sheet tables each select their latest admissible report independently, so one missing table does not erase another computable metric. Matching periods are additionally required for the five-way rank sample.

**Coverage is particularly incomplete for financial reporting templates:** all 87 names with financial `comp_type` have unavailable PE TTM and none enter the five-way sample. This reflects missing report legs and stale or missing balance sheets in the retained source, not evidence that these companies made losses. Reporting-template groups are not industry classifications; all 1,743 common names use the general-company template. Consequently, this is not a comparison across financial and nonfinancial industries.

## What changes when the denominator changes?

All comparisons below use the same 1,743 names on October 16. Spearman correlation compares ranks. The cheapest fifth includes boundary ties; Jaccard is intersection divided by union, not the share of one portfolio retained.

| Pair | Rank correlation | Cheapest-fifth Jaccard |
| --- | ---: | ---: |
| PE / deducted-profit PE | 0.947 | 75.4% |
| PE / PB | 0.507 | 28.1% |
| PB / PB less goodwill | 0.983 | 89.7% |
| PB / PB less goodwill and intangibles | 0.934 | 75.8% |

Within reporting-template × size-quintile × ROE-quintile strata with at least 20 common names, 19 strata qualify, all from the general-company template. Median within-stratum correlations are 0.903 for PE/deducted PE, 0.778 for PE/PB and 0.930 for PB/PB less goodwill and intangibles. These are rank diagnostics, not industry neutralization, a return regression or a causal explanation. Asset-disclosure selection remains substantial.

## Historical coverage

The following percentages pool records within each year. They do not measure investability or returns.

| Year | Formations | Stock-date records | Five-metric common | PE available | PB available | PB ex G/I available |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2016 | 12 | 31,697 | 33.0% | 65.3% | 99.5% | 53.3% |
| 2017 | 12 | 36,755 | 42.3% | 86.8% | 99.7% | 53.4% |
| 2018 | 12 | 40,514 | 43.8% | 87.4% | 98.9% | 54.4% |
| 2019 | 12 | 43,599 | 41.1% | 82.4% | 98.5% | 55.6% |
| 2020 | 12 | 46,850 | 36.7% | 78.6% | 98.0% | 52.7% |
| 2021 | 12 | 52,614 | 36.0% | 80.8% | 99.1% | 50.2% |
| 2022 | 12 | 58,244 | 34.5% | 78.9% | 99.2% | 48.7% |
| 2023 | 12 | 62,503 | 32.5% | 72.6% | 99.3% | 47.8% |
| 2024 | 12 | 64,128 | 32.3% | 71.8% | 99.3% | 47.6% |
| 2025 | 12 | 64,876 | 31.4% | 69.9% | 99.4% | 47.4% |
| 2026 through October 16 | 10 | 55,168 | 31.2% | 68.9% | 99.0% | 47.0% |

Early 2016 also has a TTM warm-up gap because retained statement coverage starts in 2015 and lacks the preceding annual leg. This must not be interpreted as a loss-making-company count.

## Availability and retained-version checks

Historical rows are reconstructed from the October 18 retained version. The later of `ann_date` and `f_ann_date` must be strictly before the formation day; only standard consolidated `report_type=1` is admitted. TTM uses current YTD plus previous full year minus matching prior YTD. Missing legs remain unavailable. Reports older than 550 calendar days are rejected separately for each table. Observed timestamps must exist and not lie in the future.

This reconstruction can retain subsequently revised historical reports. It is **not certified historical point-in-time data**. A second variant additionally requires the actual source observation timestamp no later than 18:00 Shanghai on the formation day, using retained snapshots where admissible.

| Formation / retained version | Result at the same quoted prices |
| --- | --- |
| August 31 / August 29 | Rejected: on-disk manifest chain fails; no reconstructed replacement counted as observed |
| September 28 / September 26 | 84 balance-report-period differences; PB differs numerically for 25 mutually valid names, adjusted PB for 15; availability also differs |
| October 16 / October 16 | 11 balance-report-period differences; no numeric differences among mutually valid values, but availability differs |

September's observed five-way sample contains 1,738 names; October's contains 1,743. Same-metric rank correlations on the mutually common sample are 1.0. That does not validate excluded names or establish an untouched out-of-sample test.

Of 29 retained date directories, four lack complete top-level seals and eight fail the on-disk metadata chain. A separate read-only forensic check reproduced all 32 original child-manifest hashes by reversing only the historical path migration; all 32 underlying file hashes and parent content aggregates match. This supports unchanged file content, while the original stored chain still fails. No manifests, seals or timestamps were rewritten, and the strict loader still rejects those versions. Metadata inventory alone does not certify all archive data files; the admitted input files used here were hash-verified.

## Accounting checks and remaining limits

Independent checks against the official unaudited 2026 first-half reports for [Focus Media](https://disc.static.szse.cn/disc/disk03/finalpage/2026-08-19/3cb7d235-3a06-4c58-a180-3e1f3a9364c6.PDF) and [China Yangtze Power](https://static.cninfo.com.cn/finalpage/2026-08-31/1225534923.PDF) matched all six checked fields to the cent: parent profit, deducted parent profit, parent equity, minority equity, goodwill and intangibles. The announcement dates also match. This is a two-company, one-period check, not market-wide or historical certification.

The deductions subtract consolidated goodwill/intangibles from parent equity without a complete parent/minority allocation. They remain proxies. Positive minority equity appears in 3,854 latest names; preferred-equity information is positive for 21 and unknown for 5,401. Numerators use A-price-implied total market capitalization, not a certified economic value for multiple share classes. No historical ST, liquidity or execution filter is imposed, and the universe comes from each date's quote records rather than today's instrument list. None of these ranks is a trading recommendation.

Next useful work is to repair financial-template statement coverage and obtain historically retained report versions, then verify parent/minority and preferred-share scope before specifying a return experiment. The analysis source is `src/market_research/valuation_panel.py`; the reproducible entry point is `scripts/analyze_valuation_panel.py`. Public output contains reviewed aggregates only; supplier rows remain in owner storage.

## Reproduction

Supply owner asset paths explicitly as `FINANCIAL_VINTAGES` and `DAILY_BASIC_ASSET`, and an external `RESEARCH_OUTPUT` root. The output directory must not exist. Match the published input hashes before reproducing; a changed daily asset alias constitutes a new experiment.

```sh
uv run --locked --extra duckdb --extra dev python scripts/analyze_valuation_panel.py \
  --vintages "$FINANCIAL_VINTAGES" \
  --daily-basic "$DAILY_BASIC_ASSET" \
  --reference-vintage vintage=20261018 --start 20160101 --end 20261016 \
  --output "$RESEARCH_OUTPUT/valuation-panel-20261018"
```
