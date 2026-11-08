# China commodity futures and equity returns

[中文](README.zh-CN.md)

[Third exploration](next-20261108.md) adds cash/risk controls, soymeal contract accounting and the first prospective macro capture. [Open interactive reader](https://runchengxie.github.io/quant-market-research/research/commodity-equity/).

First-round index diagnostics are available in the [findings](findings-20261107.md). Read the [validation record](validation-20261107.md) before interpretation. The [research protocol](../../docs/research/asset-returns/china-commodity-equity.md) defines the fixed analysis rules and remaining evidence gates.

- `benchmark-config.json`: candidate series and fixed comparison rules.
- `data-contract.json`: ownership and required input receipts.
- `conclusion-register.json`: unresolved questions and publication status.
- [Related frozen study](../asset_returns/README.md): existing evidence remains unchanged.

The frozen-input runner is `python -m market_research.studies.commodity_equity.run`; acquisition stays with the data owner. Full runs and raw data remain outside Git. The protocol contains the validation and publication gates.

[Four-part follow-up](exploration-20261108.md): robustness, implementation, source evidence and macro admission.
