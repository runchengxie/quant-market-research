# Reproducible liquidity review

The [review notebook](review.ipynb) inspects the reviewed four-market aggregate release, common dates, the difference between mean and median rolling turnover, source-panel exclusions and sampled execution gaps. Outputs and vendor data stay outside the repository.

Read the [methods and audit findings](../../docs/research/experiments/liquidity-rebuild-20261016.md) before using the comparisons. The public page is `/research/liquidity/`.

## Reproduction

Use Python with DuckDB, pandas, PyArrow, NumPy, nbformat, nbclient, ipykernel and Matplotlib. Configure a private JSON input specification; never commit vendor paths or security rows. Its `sources` object maps `us`, `a_clean`, `hk_daily`, `hk_value`, `hk_master`, `jp_daily`, `jp_master`, `jp_shares` and `fx` to local file/glob paths. Set `cutoff` to an ISO date. FX input is the ECB historical ZIP.

From the repository root, with `PYTHONPATH=src`:

```sh
python scripts/rebuild_liquidity_evidence.py --config "$INPUT_SPEC" --output "$RUN_DIR"
python scripts/review_liquidity_evidence.py --run "$RUN_DIR" --output "$REVIEW_DIR/aggregate-review.json"
python scripts/audit_liquidity_source_windows.py --help
python scripts/audit_execution_minute_gaps.py --help
python scripts/publish_liquidity_evidence.py --help
```

The `--help` commands describe the extra private source selections and input-receipt arguments. Review scripts fail on disagreement; the publication gate requires the exact proposal checksum and a successful independent receipt. It writes the exact reviewed bytes, without private receipts or feature rows.

Set `LIQUIDITY_REVIEW_RUN` and `LIQUIDITY_REVIEW_OUTPUT` to the external run and review directories before executing the notebook with a Python kernel. The review directory must contain `aggregate-review.json` and `minute-gap-audit.proposed.json`. Save the executed notebook and PNGs there, leaving the repository template without outputs.

The current numerical run predates formatting of the runner/feature module. Their exact executed sources and hashes are retained with the private run; formatting did not alter calculations. The [public AST/hash mapping](../../web/public/data/liquidity/code-format-review.json) confirms equivalence to the current code. The two independent review scripts remain byte-identical to their published code receipts.
