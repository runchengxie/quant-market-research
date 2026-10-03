# Barra factor dictionary

[Chinese version](barra-factor-dictionary.zh-CN.md)

This dictionary separates raw research metrics, style factors, and report-level factor families. It documents the public research implementation and is not a complete reproduction of a commercial Barra model.

## Quick guide

A **descriptor** is a measured feature, such as company size or recent return. A **factor** turns one or more descriptors into a score used to compare stocks. A **factor family** groups related scores for reporting. “High minus low” means the average result for the highest-scoring stock group minus that for the lowest-scoring group; it is a historical comparison, not an investor's account return. **Point-in-time (PIT)** means the information was available on the historical date being studied. The tables retain the exact calculation and source limits below.

The machine-readable descriptors are maintained in `studies/style_factors_18y/factor-descriptors.yml`. The public pages show only reviewed derived results; implementation details and source ownership remain linked to the relevant research and platform repositories.

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
