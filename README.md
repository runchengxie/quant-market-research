# Quant Market Research

[中文 README](README.zh-CN.md)

Reproducible public market research methods, reviewed derived results, and a research website covering indices and ETFs, liquidity, microcaps, cash flow, and style factors. Raw market data and complete run outputs remain outside the repository.

Private strategies and models are maintained by `quant-research`. Market data is owned by `quant-market-data-platform`. Shared backtesting and execution simulation come from `quant-platform`.

This repository owns independent public market research projects, their reproducible methods, and project-specific evidence. The [Quant Factor Observatory](https://runchengxie.github.io/quant-factor-observatory/) owns factor catalog organization, standardized factor studies, publication status, and reviewed projections under its publication contract. When a topic appears in both places, each site links to the authoritative source recorded in the study or publication manifest instead of copying the full material.

## Browse the research

- [Research website](https://runchengxie.github.io/quant-market-research/)
- [Methods and research documentation](https://runchengxie.github.io/quant-market-research/docs/)
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
- The public Markdown allowlist is rendered directly by Astro. MkDocs is no longer part of the site build or runtime dependencies.
- [Local runbook](docs/runbook-local.md): data setup, reports, and website checks.
- [Compatibility and ownership](docs/compatibility.md): repository responsibilities and migration boundaries.
- [Snapshot migration](docs/snapshot-migration.md): explicit inputs and safeguards for the legacy reviewed snapshot copier.

```text
src/market_research/  reusable Python research code and CLI implementation
scripts/              maintenance and data-preparation scripts
studies/              study configuration, methods, review records, and notebooks
web/                  Astro website with its own source, tests, and dependencies
docs/                 runbooks, data documentation, and research methods
```
