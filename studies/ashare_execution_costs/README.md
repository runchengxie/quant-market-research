# A-share trading costs, market impact and capacity

[中文](README.zh-CN.md) · [Public topic](https://runchengxie.github.io/quant-market-research/research/execution-costs/)

Current conclusion: arithmetic scenarios establish why high turnover needs precise execution assumptions. They do not establish observed slippage or executable capacity. No local Level-2 files or real orders have been inspected for this study yet.

At 250 sessions, daily buys and sells each equal to 60% of NAV, illustrative inclusive commission of 1 bp per side and sell tax of 5 bp, annual fee expenditure / constant NAV is 10.5%. Additional slippage of 1 bp per side adds 3 percentage points. If 60% denotes buys plus sells, both figures halve. This is a simple expenditure ratio, not a compounded performance deduction. Fees are scenario inputs, not a verified current fee schedule.

- [Methodology](methodology.md): benchmarks, cost ledger and validation.
- [Data requirements](data_requirements.md): local inspection and publication gates.
- [Literature queue](literature_review.md): sources awaiting full-text review.
- [Study declaration](study.yml): stable identity, evidence stage and proposed scenarios.

The market-data platform owns vendor normalization and L2 governance. quant-platform owns general execution simulation and TCA. This study owns empirical methods and reviewed aggregate results. The factor observatory can consume reviewed net-return and capacity summaries after calibration; it does not receive a new L2 engine from this change.
