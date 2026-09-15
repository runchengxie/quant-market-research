# Quant Market Research

本项目维护市场研究代码、公开研究页面和方法说明，覆盖指数与 ETF、流动性、微盘股、现金流和风格因子。报告读取本机已有数据，原始行情和完整运行结果保存在仓库外。

## 快速开始

需要 Python 3.11 或更新版本，以及 [uv](https://docs.astral.sh/uv/)。

```bash
uv sync --locked --extra dev --extra duckdb
uv run market-research --help
```

要运行本地报告，先创建并编辑数据配置：

```bash
cp configs/local.example.toml configs/local.toml
```

把配置中的示例路径改成本机数据目录，再检查配置并运行报告：

```bash
uv run market-research validate --config configs/local.toml
uv run market-research report microcap --config configs/local.toml
```

配置文件包含本机路径，已被 Git 忽略。请勿在其中保存凭证。可运行的报告、所需数据和输出位置见[本地运行手册](docs/runbook-local.md)。

## 浏览研究内容

- [研究网页](https://runchengxie.github.io/quant-market-research/)
- [研究说明站](https://runchengxie.github.io/quant-market-research/docs/)
- [低换手研究](docs/research/factors/low-turnover.md)
- [微盘股研究](docs/research/factors/microcap.md)

## 项目目录

| 目录 | 内容 |
| --- | --- |
| `src/` | 可复用的研究代码和命令行入口 |
| `scripts/` | 独立的研究、数据整理和本地维护脚本 |
| `studies/` | 研究配置、方法说明和结果记录 |
| `web/` | 研究网页及经过审核的公开数据快照 |
| `docs/` | 运行手册、数据约定和研究说明 |

更完整的报告清单和项目职责见[兼容与职责说明](docs/compatibility.md)。原始数据由 `quant-market-data-platform` 管理，通用回测与执行模拟由 `quant-platform` 提供。`quant-research` 是独立维护的相邻仓库，本项目没有 Git 子模块。

## 开发检查

```bash
uv run --locked --extra duckdb --extra dev python -m pytest -q
uv run --locked --extra dev ruff check src tests scripts
uv run --locked --extra docs mkdocs build --strict
```

网页测试和构建方式见[本地运行手册](docs/runbook-local.md)。GitHub Actions 会在拉取请求中运行检查，合并到 `main` 后发布网页和经过筛选的说明文档。
