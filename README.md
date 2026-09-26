# Quant Market Research

本项目维护可复现的公开市场研究代码、方法说明和研究网页，主题包括指数与 ETF、流动性、微盘股、现金流和风格因子。原始行情和完整运行结果保存在仓库之外。

本项目属于 Quant Research 项目系列，与同系列的数据、研究框架和交付项目各自独立维护、按接口协作。私有策略和模型由 `quant-research` 管理，市场原始数据由 `quant-market-data-platform` 管理，通用回测能力由 `quant-platform` 提供。

## 浏览研究

- [研究网页](https://runchengxie.github.io/quant-market-research/)
- [研究说明站](https://runchengxie.github.io/quant-market-research/docs/)
- [低换手研究](docs/research/factors/low-turnover.md)
- [微盘股研究](docs/research/factors/microcap.md)

## 本地运行

需要 Python 3.11 或更新版本，以及 [uv](https://docs.astral.sh/uv/)：

```bash
uv sync --locked --extra dev --extra duckdb
uv run market-research --help
```

运行报告前，先按[本地运行手册](docs/runbook-local.md)配置数据目录，并查看每份报告需要的数据。示例配置在 `configs/local.example.toml`，本机配置 `configs/local.toml` 已被 Git 忽略。

## 文档

- [文档首页](docs/index.md)：按主题查找研究和数据说明
- [本地运行手册](docs/runbook-local.md)：配置数据、运行报告和网页检查
- [兼容与职责说明](docs/compatibility.md)：查看仓库职责和迁移边界
