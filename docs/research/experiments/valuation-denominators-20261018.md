# Low valuation: define the denominator before ranking

[Chinese version](valuation-denominators-20261018.zh-CN.md)

**There is no single “lowest valuation” ranking.** PE compares price with earnings; PB compares it with recorded equity. Excluding nonrecurring earnings or recorded intangible assets changes the question and can change the order. The six-name illustration below demonstrates the definitions, not future returns or a market-wide stock screen.

Evidence stage: reviewed current-snapshot arithmetic, observed on 2026-10-18. Prices are from 2026-10-16. Financial records were retrieved on October 17 UTC (October 18 in China), including an October 17 disclosure for 002415.SZ. **These inputs cannot be represented as available at the October 16 close.** No historical strategy return has been calculated.

## Definition table

Let M be total common-equity market value in yuan; P the parent-attributable profit over the last twelve months; D the parent-attributable profit excluding nonrecurring items; E the equity attributable to common shareholders; G and I the corresponding attributable goodwill and other recorded intangible assets.

| Measure | Intended definition | What must be fixed before comparison |
| --- | --- | --- |
| PE TTM | M / P | Consolidated parent-attributable earnings, not total group profit; trailing year, not annualized half-year |
| PE excluding nonrecurring items | M / D | Same parent scope and trailing periods; removing nonrecurring items is not the same as removing all investment income |
| PB | M / E | Parent equity, excluding minority and any senior equity claims where applicable; a single balance-sheet date, not four-quarter sum |
| PB excluding goodwill | M / (E − G) | Ownership scope, goodwill definition and impairment version |
| PB excluding goodwill and intangibles | M / (E − G − I) | Recorded intangible scope, ownership allocation, and whether capitalized development costs are additionally excluded |

TTM at an interim date is current cumulative YTD + previous full year − matching previous YTD. An annual report uses its full-year value directly. Missing legs leave the result unavailable. Earnings, equity and deductions must use the same consolidated reporting scope; do not mix parent-company-only statements with consolidated parent-attributable data.

M must cover the same equity claim as the denominator. This illustration deliberately chooses six A-only issuers, without inferring a general treatment for A/H, B shares, preference shares or convertible instruments. An A-share price multiplied by all classes' shares is not automatically the economic value of every class. Circulating market value is also unsuitable against full-company earnings/equity.

## Data mapping and important qualifications

The script maps `daily_basic.total_mv × 10,000` to yuan, `income.n_income_attr_p` to P, `fina_indicator.profit_dedt` to a **supplier-defined nonrecurring-profit proxy**, and `balancesheet.total_hldr_eqy_exc_min_int` to parent equity. The supplier's `profit_dedt` label does not independently certify its parent/common-share scope for every issuer. Source reports and preference-share allocations have not been independently checked; therefore the sample's PB is labelled parent-equity PB and its nonrecurring PE remains provisional.

`goodwill` and `intan_assets` are group-consolidated asset balances, while the equity field excludes minority interests. Their full deduction from parent equity is an **unallocated asset-deduction proxy**, not certified parent tangible equity. There is no assumed pro-rata minority allocation. The two source fields are treated separately; capitalized development costs, deferred tax consequences, off-balance-sheet intangibles and future liquidation recoveries are not included. A recorded asset's book value is not its liquidation value. The sample does not claim intangible-intensive firms are economically worse.

Missing goodwill or intangible values remain missing; they are never silently replaced by zero. A nonpositive denominator is unavailable for positive-multiple cheapness rankings, with loss/negative-equity cases requiring separate analysis. This convention does not mean such companies have no economic value. In this sample Moutai has an unavailable goodwill field and is excluded from the common ranking rather than assigned zero goodwill.

## Six-name illustration

Purposively chosen issuers span several business models and are not a representative cross-section. Multiples below share each issuer's latest period available across income, indicator and balance-sheet sources. Report periods may differ between issuers. Figures are rounded only for display.

| Code | Issuer | Report period | PE TTM | Nonrecurring PE proxy | Parent PB | Ex-goodwill PB proxy | Ex-goodwill/intangibles PB proxy |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 000651.SZ | Gree | 20260630 | 7.94 | 8.36 | 1.49 | 1.50 | 1.61 |
| 002027.SZ | Focus Media | 20260630 | 21.86 | 29.28 | 5.33 | 5.39 | 5.43 |
| 002415.SZ | Hikvision | 20260930 | 17.34 | 17.70 | 3.66 | 3.67 | 3.75 |
| 300059.SZ | East Money | 20260630 | 19.65 | 20.28 | 2.91 | 3.00 | 3.00 |
| 600519.SH | Kweichow Moutai | 20260630 | 20.40 | 20.42 | 6.61 | — | — |
| 600900.SH | China Yangtze Power | 20260630 | 19.86 | 20.81 | 3.33 | 3.34 | 3.77 |

For Focus Media, removing the supplier-defined nonrecurring component changes PE from 21.86 to 29.28. In the five-name common sample, Hikvision and Yangtze Power reverse their relative PB order after goodwill and recorded intangibles are deducted. Neither observation establishes better subsequent returns.

### Same-sample ranks

All five columns below use exactly the same five issuers with positive finite denominators in every measure. Rank 1 is the lowest multiple in this small sample; ties use the minimum rank. The sixth issuer's available PE and PB values are still shown above, but it receives no rank in any common-sample column. Cross-industry ranks here illustrate arithmetic only.

| Code | PE | Nonrecurring PE proxy | Parent PB | Ex-goodwill proxy | Ex-goodwill/intangibles proxy |
| --- | ---: | ---: | ---: | ---: | ---: |
| 000651.SZ | 1 | 1 | 1 | 1 | 1 |
| 002027.SZ | 5 | 5 | 5 | 5 | 5 |
| 002415.SZ | 2 | 2 | 4 | 4 | 3 |
| 300059.SZ | 3 | 3 | 2 | 2 | 2 |
| 600519.SH | — | — | — | — | — |
| 600900.SH | 4 | 4 | 3 | 3 | 4 |

## Availability, revisions and reproduction

The analysis checks the owner archive seal, normalized child-manifest hashes and data hashes before reading selected issuers. It admits only report type 1 cumulative consolidated statements, selects the latest disclosed/observed version for each issuer-period, and requires date-only disclosures to precede the current local calendar day. Ambiguous same-version duplicates fail. The dated input archive was obtained through the owner's configured TuShare route; no new supplier request or production alias change was needed.

Those integrity checks prove the retained files match their recorded hashes. They do not prove that older report values were available in their original historical form, that supplier restatements are complete, or that the supplier's economic definitions are correct. Old legs in a current TTM calculation may reflect subsequently revised comparatives. The result is a weekend observed snapshot using the previous session's prices; it is not a Friday-close historical signal.

Reproduction uses `scripts/analyze_valuation_definitions.py` with `--vintage` pointing to an owner sealed vintage, `--daily-basic` to one retained daily partition, and `--output` to a new directory outside the repository. The reviewed [derived JSON](https://runchengxie.github.io/quant-market-research/data/valuation_denominators_reviewed.json) includes hashes, calculation dates, report periods and source observation/disclosure dates, without raw supplier financial amounts or price bars. The script checks the six fixed sample names and leaves missing deductions unavailable. Reproduction on another vintage is a new observation, not the same snapshot.

## What was already published, and what remains

The [PB/ROE study](https://runchengxie.github.io/quant-factor-observatory/studies/pb-roe) already compares profitability added to PB; the [market-research companion](../factors/pb-roe.md) retains its historical results and qualification. It does not compare all five denominators defined here. This definitions note and current arithmetic illustration belong to market-research; a standardized factor study may later be admitted to the observatory through its existing publication contract.

Next, freeze a historical observation ledger and full-universe eligibility rules, compare measures on common and measure-specific samples, and report missingness by sector and year. Separate financial and nonfinancial sectors, control size/industry/profitability, and retain later-delisted issuers. Only after fixing formation, execution, benchmark, revisions and costs should a paired return study estimate whether any denominator adds value. There is no all-market “cheapest stock” list or performance claim in this release.

## Primary field references

- [TuShare daily indicators](https://tushare.pro/document/2?doc_id=32): market-value unit and field mapping.
- [TuShare income statements](https://tushare.pro/document/2?doc_id=33): parent-attributable earnings and report types.
- [TuShare balance sheets](https://tushare.pro/document/2?doc_id=36): equity, goodwill and recorded intangible fields.
- [TuShare financial indicators](https://tushare.pro/document/2?doc_id=79): supplier nonrecurring-profit field.
