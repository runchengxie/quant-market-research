# Synthetic public market research integration

The integration command checks one continuous synthetic path: the DATA owner's
published daily research reader → the public market research replay builder →
the durable runtime CLI and detached worker → verified report Parquet files and
a diagnostic summary. It also changes a copied runtime frame and confirms that
checksum verification rejects it before a second report can be published.

This checks adapter compatibility and integrity for the installed pins. It does
not validate private `quant-research` strategies, vendor data, production services,
Intel report generation/publication, or real investment performance.

## Run without skips

Use Python 3.12 or newer because the formal runtime requires it. The DATA pin is
an optional dependency; the runtime/platform pins remain those of `formal`.
The following commands create an isolated task environment and write results to
a new directory under a temporary parent. Do not use a production data root.

```bash
uv sync --locked --python 3.13 --extra dev --extra duckdb --extra formal --extra integration
smoke_parent=$(mktemp -d /tmp/market-research-chain.XXXXXX)
uv run --locked --extra formal --extra integration \
  market-research-synthetic-chain --output "$smoke_parent/run"
REQUIRE_CROSSREPO_SMOKE=1 uv run --locked --extra dev --extra duckdb --extra formal --extra integration \
  pytest -q tests/test_synthetic_chain.py
```

The CLI does not skip missing dependencies: it fails before generating data when
a required distribution is absent or its `direct_url.json` commit differs from
the expected pin. The normal Python test suite explicitly skips these integration
tests when DATA/runtime are absent; `REQUIRE_CROSSREPO_SMOKE=1` turns missing
dependencies into failures. An existing output directory is refused, and outputs
inside the source repository are refused. Run only against a disposable output
location: the integration intentionally retains an altered copy for diagnosis.

## Fixture and expected result

Three invented sessions (January 2, 5, and 6, 2026) contain one eligible symbol,
with prices 100, 100, and 105. A completed `daily_clean.v2` manifest declares the
ST availability contract. `AShareResearchAssets` directly addresses these fixture
paths; no shared `current` pointer, vendor client or production asset is read.
The DATA APIs read both the daily frame and instrument metadata. The public
`build_replay_inputs` adapter creates two next-session targets and decision clocks.

The daily research API does not supply execution liquidity or adjustment factors.
The adapter therefore adds explicit fixture assumptions: no corporate actions,
adjusted marks equal to close, constant synthetic liquidity, synthetic price
limits from 50 to 200, no suspensions/delistings, and zero transaction costs.
These assumptions are not evidence of real market execution. The runtime starts
with 100,000, buys at 100, and marks the same holding at 105, giving 105,000.

`run_sequenced_job` invokes `python -m backtest_runtime.cli` for submit, status
and result, using a task-local SQLite database and content-addressed artifacts.
It does not run an in-process substitute worker. `publish_report` rechecks the
runtime manifest, request identity and frame checksums through `read_job_result`
before it copies the verified frames and writes `report/summary.json`.

## Evidence and pins

`evidence.json` records interpreter identity, installed distribution versions and
`direct_url.json` metadata, public research source revision and source-file hashes,
the request/result receipt hashes, hashes of fixture/normalized/report/runtime
files, explicit assumptions, the terminal value and negative tamper result.
The runtime request and original/corrupted result copies remain alongside it.
Generated evidence contains local paths and must be reviewed before public sharing;
none is added to the repository or published by this command.

Pinned owners:

| Distribution | Commit |
| --- | --- |
| DATA | `71e40a0da03530fe88d70d4b212701d3af6a8cfa` |
| Runtime | `4fbfe973540e15fb6552068be037229d2f53d540` |
| Platform and research contracts | `15ec62b66e894395d694049eaaace931de4a1265` |

The integration extra also brings DATA's own pinned `research-code-quality`
dependency, recorded in the lockfile. Changing any chain pin requires an explicit
update and a fresh integration run. Fixture/result file hashes are captured for
that run, not promised to match across Parquet library versions.
