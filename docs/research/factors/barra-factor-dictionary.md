# Barra factor dictionary

[Chinese version](barra-factor-dictionary.zh-CN.md)

This dictionary separates raw research metrics, style factors, and report-level factor families. It documents the public research implementation and is not a complete reproduction of a commercial Barra model.

## Quick guide

A **descriptor** is a measured feature, such as company size or recent return. A **factor** turns one or more descriptors into a score used to compare stocks. A **factor family** groups related scores for reporting. “High minus low” means the average result for the highest-scoring stock group minus that for the lowest-scoring group; it is a historical comparison, not an investor's account return. **Point-in-time (PIT)** means the information was available on the historical date being studied. The tables retain the exact calculation and source limits below.

The machine-readable descriptors are maintained in `studies/style_factors_18y/factor-descriptors.yml`. The public pages show only reviewed derived results; implementation details and source ownership remain linked to the relevant research and platform repositories.

## Reading formulas and source fields

In the current formulas, `ln` is the natural logarithm, `clip(x, a, b)` caps a value to the inclusive range from `a` to `b`, and `1 / PB` or `1 / PE_TTM` reverses the multiple so a lower positive valuation multiple receives a higher score. `PE_TTM` means price-to-earnings using trailing twelve-month earnings. A 21-day or 252-day window counts trading observations as defined by the source, not calendar days. `Cov` is covariance (whether two return series move together); `Var` is variance (how much one series varies); `rᵢ` is a stock return and `rₘ` is the sample's equal-weight market return in the current beta proxy. Percentile clipping limits extreme observations before standardization. A z-score expresses a value relative to the cross-sectional mean and standard deviation.

Source identifiers such as `total_mv`, `turnover_rate`, `pct_chg`, `PE_TTM`, `netprofit_yoy`, and `debt_to_assets` remain unchanged so a reader can find them in the data contract. Their units, missing-value rules, and point-in-time availability follow the source table and the formula-specific notes below; a familiar field name alone does not establish those details. ROE means return on equity, ROA return on assets, and OCF operating cash flow. They are separate financial measures and are not interchangeable.

## Historical 19-factor snapshot

The historical snapshot contains 19 factor identifiers. These are reviewed historical results, not 19 fully reconstructable commercial Barra factors. The current core dictionary and the historical source package have different provenance boundaries.

| Factor ID | Evidence boundary |
| --- | --- |
| `liquidity` | Historical Barra-style snapshot; source definition remains bounded |
| `growth` | Historical Barra-style snapshot; source definition remains bounded |
| `value` | Historical Barra-style snapshot; source definition remains bounded |
| `ps_value` | Historical Barra-style snapshot; source definition remains bounded |
| `lowvol` | Historical Barra-style snapshot; source definition remains bounded |
| `dividend_yield` | Historical Barra-style snapshot; source definition remains bounded |
| `institution_holding` | Historical Barra-style snapshot; source definition remains bounded |
| `earnings_yield` | Historical Barra-style snapshot; source definition remains bounded |
| `quality` | Historical Barra-style snapshot; source definition remains bounded |
| `leverage` | Historical Barra-style snapshot; source definition remains bounded |
| `chip_concentration` | Historical Barra-style snapshot; source definition remains bounded |
| `fund_breadth_change` | Historical Barra-style snapshot; source definition remains bounded |
| `fund_ownership_change` | Historical Barra-style snapshot; source definition remains bounded |
| `fund_ownership` | Historical Barra-style snapshot; source definition remains bounded |
| `beta` | Historical Barra-style snapshot; source definition remains bounded |
| `fund_breadth` | Historical Barra-style snapshot; source definition remains bounded |
| `momentum` | Historical Barra-style snapshot; source definition remains bounded |
| `size` | Historical Barra-style snapshot; source definition remains bounded |
| `liquidity_flow` | Historical Barra-style snapshot; source definition remains bounded |

The repository does not include the original historical factor panel or a complete descriptor and formula for every row. Do not describe this snapshot as a fully reproducible commercial Barra model.
