# Quant Market Research

Reproducible public market research methods, reviewed derived results, and a research website covering indices and ETFs, liquidity, microcaps, cash flow, and style factors. Raw market data and complete run outputs remain outside the repository.

Private strategies and models are maintained by `quant-research`. Market data is owned by `quant-market-data-platform`. Shared backtesting and execution simulation come from `quant-platform`.

[中文 README](README.zh-CN.md)

## Browse the research

- [Research website](https://runchengxie.github.io/quant-market-research/)
- [Documentation site](https://runchengxie.github.io/quant-market-research/docs/)
- [Low-turnover research](docs/research/factors/low-turnover.md)
- [Microcap research](docs/research/factors/microcap.md)

## Local development

Requirements: Python 3.11 or newer and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --locked --extra dev --extra duckdb
uv run market-research --help
```

Before running a report, follow the [local runbook](docs/runbook-local.md), configure the data directories, and check each report's data requirements. Use `configs/local.example.toml` as the configuration template. The local `configs/local.toml` file is ignored by Git.

## Documentation and layout

- [Documentation index](docs/index.md): research and data topics.
- [Local runbook](docs/runbook-local.md): data setup, reports, and website checks.
- [Compatibility and ownership](docs/compatibility.md): repository responsibilities and migration boundaries.

```text
src/market_research/  reusable Python research code and CLI implementation
scripts/              maintenance and data-preparation scripts
studies/              study configuration, methods, review records, and notebooks
web/                  Astro website with its own source, tests, and dependencies
docs/                 runbooks, data documentation, and research methods
```
