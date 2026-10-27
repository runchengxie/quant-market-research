# Local runbook

[简体中文](runbook-local.md)

## Install and configure

Use Python 3.11 or newer. From the repository root:

```bash
uv sync --locked --extra dev --extra duckdb
cp configs/local.example.toml configs/local.toml
uv run market-research --help
uv run market-research validate --config configs/local.toml
```

Edit the ignored `configs/local.toml` to point at existing external data. Under
`[sources]`, use `a_share_root`, `hk_daily_root`, `hk_valuation_root`,
`hk_instruments_path`, `us_shareprices_path` and `jp_root` for the corresponding
markets. Large A-share Parquet inputs can use `use_duckdb = true`.

`validate` lists source keys whose nonempty paths exist. It does not inspect market
data. Missing paths are omitted and even an empty list exits successfully; exit
status alone does not establish data completeness.

Python report output uses configuration `output_root`, then
`MARKET_RESEARCH_OUTPUT_ROOT`, then `$DATA_PLATFORM_ROOT/reports/market-research`.
Missing configuration or an output path inside this checkout is rejected. Keep
raw inputs and complete results outside source repositories.

## Report commands

Run these from the repository root after checking the required inputs:

```bash
uv run market-research report liquidity --config configs/local.toml
uv run market-research report microcap --config configs/local.toml
uv run market-research report smallcap-turnover --config configs/local.toml
uv run market-research report smallcap-turnover-history --config configs/local.toml
uv run market-research report smallcap-turnover-audit --config configs/local.toml
uv run market-research report indices --config configs/local.toml
uv run market-research report etf-pairs --config configs/local.toml
uv run market-research report cashflow --config configs/local.toml
uv run market-research report barra --config configs/local.toml
uv run market-research report barra-risk-inputs --config configs/local.toml
uv run market-research report index-study --study studies/index_replication/study.example.json
uv run market-research report style-factors --study /path/to/local-style-study.yml
uv run market-research report global-six-market --study studies/global_six_market/study.yml
```

Study examples require local input paths. Style studies require an external panel.
The six-market ETF proxy remains exploratory and is not a complete representation
of six national equity markets.

- Liquidity writes `liquidity_report.json`, `liquidity_summary.csv` and
  `coverage_diagnostics.csv`, with capacity diagnostics.
- Microcap reconstruction selects the smallest 400 stocks by total market value.
  It is not the official Wind `8841431.WI` series and does not simulate costs,
  price-limit fills, suspension fills, impact or capacity.
- Small-cap turnover summarizes the smallest 1, 10, 50, 100, 200, 400 and 1000
  stocks. N=1 is an extreme diagnostic, not a tradable portfolio. The history
  extension starts in 2008 and remains `incomplete` because historical ST and
  suspension fields are unreliable. The overlap audit compares common dates and
  group medians at 5%, 10% and 25% error tolerances; it does not validate the older
  source by itself.
- Barra writes `barra_summary.json`, `barra_size_quantiles.csv` and
  `barra_source_manifest.json`. Q1 is the smallest-cap group.
  `monotonicity_score` measures adjacent-group ordering, not statistical
  significance. Costs, capacity, suspensions and survivorship still matter.

Data refreshes use `fetch linked-indices` and `fetch cashflow` with `--config`.
They require provider access and are separate from offline checks.

For extended microcap drawdown and underwater analysis:

```bash
uv run --locked --extra duckdb python scripts/analyze_microcap_history.py \
  --data-root /path/to/quant-market-data-platform \
  --output /path/to/research-outputs/microcap-history
```

This combines 2008–2014 history with the cleaned daily panel from 2015, using
50/100/200/400/800-stock groups and missing-price sensitivities. Signals form
at the close, execute at the next trading close, and earn returns after execution.
The reconstruction excludes costs, fill restrictions and capacity.

The optional Japan shares helper uses Yahoo Finance estimates for local exploration,
not as a replacement for licensed data:

```bash
uv sync --locked --extra yahoo
uv run --locked --extra yahoo python scripts/build_yfinance_shares_sidecar.py \
  --jp-root /path/to/japan-market-data \
  --output /path/to/local-output/shares-sidecar.parquet --start 2020-01-01
```

It supports symbol filtering, pacing, concurrency, checkpoints and failure records.
Coverage and quality are not guaranteed; outputs are not automatically published.

## Website and reviewed snapshots

```bash
cd web
npm ci
npm run dev
```

The website reads reviewed derived snapshots. The legacy `npm run snapshot`
reads a fixed repository-root `outputs/` directory, ignoring the current Python
`output_root` and environment settings. It is not integrated with external report
outputs and is not a direct publication step for current runs. Do not move raw
data into the repository to accommodate it.

The turnover snapshot has a separate builder. From the repository root, explicitly
select the same external output directory as the Python report:

```bash
MARKET_RESEARCH_OUTPUT_ROOT=/path/to/research-outputs \
  node web/scripts/build-smallcap-turnover-public.mjs
```

Public annual and monthly summaries are derived results. Monthly turnover takes
the median of daily medians.

`scripts/sync_public_research_data.py` is a legacy reviewed-index snapshot copier,
not the current publication pipeline. It requires `--source-root`; its optional
`--target-root` defaults to `web/public/data`. It checks the manifest and required
inputs before copying, preserves unrelated counts and updates index file counts.
It is not a multi-file transaction: disk or permission failures may leave partial
updates. Review inputs before running it. See [snapshot migration](snapshot-migration.md).

## Verification

From the repository root:

```bash
uv run --locked --extra duckdb --extra dev pytest -q
uv run --locked --extra dev ruff check src tests scripts
git diff --check
```

From `web/`:

```bash
npm test
npm run build
npm run verify:static
npx playwright install chromium
PORT=54387 npm run e2e -- --workers=2 --output=/tmp/quant-market-research-browser
npm run report:bundle
```

`PORT` defaults to `4321` and controls both preview and browser URLs. The browser
suite starts its own server and fails if that port is occupied. Use a distinct port
for concurrent worktrees. Layout tests cover seven routes at five widths
(320, 390, 768, 1280 and 1440), using 30-second test timeouts. They check the primary
heading, overflow, alignment and page errors. See [browser verification](runbook-browser.md).

The Pages workflow builds Astro and allowlisted documentation, checks routes,
assets and public data boundaries, and runs browser checks. Site output is
`web/dist/`. `report:bundle` measures actual output sizes without a size gate.
Integration acceptance uses separately pinned provider packages and the commands
in [cross-repository smoke checks](validation/crossrepo-smoke.md); the base suite
alone does not establish that integration passed.
