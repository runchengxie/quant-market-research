# Public term and formula inventory

This inventory covers the registered public pages and documents in `web/src/content/public-registry.ts`. It records the plain-language explanation needed beside specialist terms while preserving the original names, formulas, field identifiers, dates, and evidence limits. It is a review aid; it does not change the underlying data or research method.

## Route coverage

| Public page or page group | Reader-facing terms and likely confusion | Explanation and boundary to show |
| --- | --- | --- |
| `/`, `/research/`, `/docs/`, `/data-sources/` | evidence stage, coverage, snapshot, source version | Say what the page concludes, which dates/data it covers, and what remains unknown. A snapshot is a saved data extract, not a live feed. Keep source IDs and build/version details available. |
| `/research/cashflow/`, `/research/cashflow/recovery/` | cash flow, dividend, recovery, previous high, benchmark | Explain recovery as the elapsed time until the measured portfolio/index regains its prior peak, if that is the metric shown. It does not mean every constituent stock recovered. Define return basis and whether dividends are included from the cited study; do not infer missing treatment. |
| `/research/microcap/`, `/research/microcap/cross-market-liquidity/`, microcap method and execution diagnostic | microcap, market value, ADV, fill ratio, slippage, limit-up/down, settlement | Microcap means the lower end of listed-company market value under the page’s stated selection rule. ADV is average traded value over the stated window, a rough capacity guide. Fill ratio is simulated filled quantity divided by requested quantity when that is the source definition. Distinguish simulated execution from actual fills. Explain market-specific trading and settlement rules without implying identical cross-market data. |
| `/research/indices/` | total return, price return, ETF, annualized return, drawdown | State whether dividends are reinvested and the exact start/end dates. Annualized return converts a multi-year cumulative result to a yearly compound rate; drawdown is the decline from a previous peak. Do not compare periods or instruments with different return bases as if like-for-like. |
| `/research/style-factors-18y/`, Barra dictionary/source inventory | factor, descriptor, family, long-short, high-minus-low, percentile, z-score, winsorization, industry neutral | A factor is a rule for ranking stocks on one characteristic; a descriptor is the underlying measured characteristic. High-minus-low is the return of the high-score group minus the low-score group, using the stated group and weighting rules. Percentile is relative rank in that date’s stock set. A z-score expresses distance from the cross-sectional mean in standard deviations. Winsorization caps extremes; industry demeaning subtracts an industry average. These steps do not guarantee industry-neutral portfolio weights. Historical factor return series are distinct from current formula proxies. |
| `/research/factors/pb-roe/` and PB/ROE method | PB, ROE, matched universe, candidate pool, PIT, annual/quarterly | PB is price divided by book value per share (or the source’s stated equivalent); ROE is profit relative to shareholder equity. Explain the exact comparison universe and date alignment. A matched universe means both variants use the same eligible stocks on each date. PIT (point-in-time) means using only information publicly available by that date. Preserve the source’s annual/quarterly matching rules. |
| `/research/factors/low-turnover/` and low-turnover method | turnover, 20/60-day measure, IC, RankIC, Sharpe, excess return | Turnover rate measures traded shares/value relative to the source’s stated base; the factor uses its stated 20- or 60-observation window. IC is the correlation between a factor score and later returns; RankIC correlates their ranks. Sharpe scales average excess return by return volatility under the stated frequency/annualization. Preserve whether the page reports a factor spread or a tradable strategy. |
| `/docs/research/factors/microcap/`, `/docs/research/factors/smallcap-turnover-history/` | size bucket, turnover, rebalance, survivorship, execution | Explain the actual market-cap cutoffs, rebalance dates, and sample dates where available. Survivorship bias occurs when the sample omits stocks that later disappeared. Historical portfolio returns do not include execution costs unless the source explicitly says so. |
| English and Chinese research documents | formulas, abbreviations, raw fields, provenance | Put short explanations next to first meaningful use in each language. Keep formulas and source identifiers intact. If the public source does not define the historical field or algorithm, label it “not documented in the available source” and link the source record instead of guessing. |

## Current factor formulas and raw fields

Keep the exact formulas in `web/src/lib/factor-implementations.ts` and explain their moving parts in the UI/documentation:

| Term or identifier | Plain-language explanation | Boundary |
| --- | --- | --- |
| `total_mv`, `ln(total_mv + 1)` | `total_mv` is the source total-market-value field; the natural logarithm compresses the scale so very large companies do not dominate the numeric range as much. | Do not translate the source field into a different currency/unit without its data contract. |
| `PB`, `PE_TTM`, `ps_ttm` and reciprocals | PB is price-to-book; PE_TTM is trailing-twelve-month price-to-earnings; PS is price-to-sales. Taking the reciprocal makes lower valuation multiples produce higher value/yield scores. | Preserve the stated positive-value filters and clipping bounds. PE-based earnings yield is a valuation measure, not operating quality. |
| `pct_chg`, `rᵢ`, `rₘ`, `Cov`, `Var`, beta | `pct_chg / 100` converts percentage points to a decimal return. `Cov` measures how two return series move together; `Var` measures a series’ own variation. Here market return is the equal-weight average of the sample stocks, not automatically an index. | Preserve 252 observations, 126 minimum, and formation-date inclusion. |
| `turnover_rate`, `clip`, `−clip(...)` | `turnover_rate` is the source’s daily turnover field; clipping bounds extreme values, and the minus sign makes lower turnover score higher. | This current snapshot uses one formation-day value, not the separate 20/60-day research measure. |
| `netprofit_yoy`, revenue growth, `debt_to_assets` | Year-over-year changes in net profit/revenue compare with the corresponding prior-year period. Debt-to-assets measures liabilities relative to assets. | Keep source units and clipping bounds. PIT availability still needs its stated verification. |
| ROE, ROA, OCF | ROE = return on equity (净资产收益率); ROA = return on assets (总资产收益率); OCF = operating cash flow (经营活动现金流). | State whether each is a source field, component, or sensitivity check. Do not treat the terms as interchangeable. |
| z-score, 1%/99% clipping, equal-weight composite | A z-score shows how far a value is from the group average in standard-deviation units. Clipping limits extreme values at the stated percentiles. Equal weighting gives each available component the same weight after the documented direction/standardization steps. | Current quality implementation has component-specific missing-value behavior; retain it verbatim and distinguish from the legacy 18-year returns. |
| `buy_lg_amount_rate`, `net_amount` | These are separate source fields: the former is a large-order buy-rate field; the latter is a net traded amount field. | Do not describe both as a buy ratio or assume row-by-row fallback. The implementation only chooses `net_amount` when the first column is absent. |
| `top10_float_concentration`, `top10_inst_float_hold_ratio` | The first describes concentration among the top ten tradable-share holders; the second is the top ten institutional holders’ tradable-share ratio. | Their exact source visibility dates require the source-table contract; do not imply complete holdings coverage. |
| `fund_top10_stk_float_ratio_sum` | Sum of the listed fund holdings’ proportions of a stock’s tradable shares within the stated disclosure scope. | This is based on top-ten holdings records, not all fund positions. |
| `daily_basic.dv_ttm` | Source field for trailing dividend yield. | Do not imply dividends are reinvested in portfolio returns unless separately documented. |
| winsorization, industry demeaning, market-wide z-score | Cap cross-sectional extremes, subtract the available industry mean, then standardize across the full market. | The code states this does not guarantee sector-neutral long/short portfolio weights. |

## Metrics and historical-record cautions

- CAGR is the constant yearly compound rate that links starting and ending values; annual volatility scales return variation to a year under the source’s sampling convention; Sharpe divides average excess return by that volatility. Keep the risk-free-rate and annualization convention beside the result when available.
- Maximum drawdown is the largest peak-to-trough percentage fall in the measured series. Hit rate is the share of measured periods/positions with positive outcomes; state the unit being counted.
- Deciles are ten groups formed by sorting the eligible stocks; state whether group 1 is the highest or lowest score and how ties/weights are handled.
- “Residual” means what remains after the named controls/model are applied; list those controls. “Industry control” is not proof the portfolio’s industry weights are neutral.
- Historical source inventories sometimes preserve factor labels and return summaries without the original feature inputs or complete formula. In those cases retain the original label and result, explain that the historical definition was not recoverable from the available source, and avoid substituting the current proxy formula.
- Any terms whose exact calculation depends on a report-specific source (for example, recovery horizon, one-way turnover, execution fill, or information ratio) must state that source’s numerator, denominator, timing, and annualization. If those are absent, mark them undocumented.

## Review checklist

1. Cover every registered route and all 18 documents in both languages.
2. Explain each visible specialist term at first use or in an immediately available note; preserve exact formula, field name, and value.
3. Distinguish current proxy calculations from historical results and observed data from simulated results.
4. State dates, universe, denominator, units, weighting, annualization, and missing-data treatment where the source defines them.
5. Mark source gaps explicitly; do not fill them by intuition.

## Implementation map

| Page group | Final reader-facing location |
| --- | --- |
| Style factor explorer and performance measures | `web/src/components/react/style-page.tsx`: expandable bilingual note defines annualized return, annualized volatility, Sharpe, drawdown, positive-day share, `ln`, `clip`, `Cov`, `Var`, return symbols, and preserved source field identifiers. |
| Barra factor dictionary | `docs/research/factors/barra-factor-dictionary.md` and `.zh-CN.md`: bilingual formula/source-field note defines formula operators, trading-observation windows, beta symbols, percentile clipping, z-scores, ROE/ROA/OCF, and source-contract limits. |
| Low-turnover execution evidence | Existing `web/src/components/LowTurnoverExecutionEvidence.tsx` note defines net annualized return, Sharpe, drawdown, annualized turnover, fill ratio, cash weight, and keeps the simulated-execution limitation adjacent. |
| Other public pages and registered method records | Existing summaries/method sections were checked against registered routes; they already provide date, sample, return-basis, and evidence-boundary context. The inventory retains historical fields whose exact formula, unit, or denominator remains undocumented rather than inventing a definition. |
