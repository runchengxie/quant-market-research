# 中国商品期货与股票收益研究

[English](README.md)

[第三轮探索](next-20261108.zh-CN.md)补充现金与相近风险对照、豆粕合约记账和首批宏观前瞻归档。[打开交互专题](https://runchengxie.github.io/quant-market-research/research/commodity-equity/?lang=zh-CN)。

首轮指数观察见[研究结果](findings-20261107.zh-CN.md)，复现与限制见[验证记录](validation-20261107.md)。继续研究前阅读[研究协议](../../docs/research/asset-returns/china-commodity-equity.zh-CN.md)，审计覆盖和收益口径，再开展比较。

- `benchmark-config.json`：候选序列和预先固定的比较规则。
- `data-contract.json`：数据职责和输入收据要求。
- `conclusion-register.json`：待回答问题及发布状态。
- [相关冻结研究](../asset_returns/README.zh-CN.md)：保留现有证据。

冻结输入运行器为 `python -m market_research.studies.commodity_equity.run`，供应商接入仍由数据所有者负责。完整结果和原始数据保存在Git之外，验证与发布条件见研究协议。

[四条线后续探索](exploration-20261108.zh-CN.md)涵盖稳健性、投资实施、来源证据与宏观准入。
