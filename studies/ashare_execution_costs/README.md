# A-share trading costs, market impact and capacity

[中文](README.zh-CN.md) · [Public topic](https://runchengxie.github.io/quant-market-research/research/execution-costs/)

Current conclusion: ten selected dates contain 306,483 valid two-sided minute books. CNY100k static median costs are 9.27/8.87 bp for buys/sells; CNY1m full ten-level coverage is 62.12%/67.68%. Earlier Shenzhen candidate order-reference matches are about 99.7%, while the selected earlier Shanghai sample has no orders. Eighteen constrained strategy sensitivities connect assumed costs to fills and funding. These results do not calibrate real slippage or establish executable capacity.

[Expanded findings](../../docs/research/experiments/execution-cost-expansion-20261012.md) · [Review notebook](expansion_review.ipynb) · [Prior three-day pilot](pilot_findings.md)

At 250 sessions, daily buys and sells each equal to 60% of NAV, illustrative inclusive commission of 1 bp per side and sell tax of 5 bp, annual fee expenditure / constant NAV is 10.5%. Additional slippage of 1 bp per side adds 3 percentage points. If 60% denotes buys plus sells, both figures halve. This is a simple expenditure ratio, not a compounded performance deduction. Fees are scenario inputs, not a verified current fee schedule.

- [Methodology](methodology.md): benchmarks, cost ledger and validation.
- [Data requirements](data_requirements.md): local inspection and publication gates.
- [Literature queue](literature_review.md): sources awaiting full-text review.
- [Study declaration](study.yml): stable identity, evidence stage and proposed scenarios.

The market-data platform owns vendor normalization and L2 governance. quant-platform owns general execution simulation and TCA. This study owns empirical methods and reviewed aggregate results. The factor observatory can consume reviewed net-return and capacity summaries after calibration; it does not receive a new L2 engine from this change.

[Earlier book and order-flow inventory](historical_data_audit.md) · [早期订单簿与订单流核查](historical_data_audit.zh-CN.md)

## Reproduce with private inputs

Copy [the input example](expansion.spec.example.json) outside Git and bind actual source paths after auditing their clocks and units. Set `STUDY_SPEC`, a new external `STUDY_RUN`, `MDP_SOURCE` and `DIAGNOSTIC_SOURCE` from local configuration. Preserve previous outputs.

```bash
PYTHONPATH="$MDP_SOURCE/src:src" uv run --locked --extra duckdb python -m market_research.studies.ashare_execution_costs.expansion --spec "$STUDY_SPEC" --output-root "$STUDY_RUN/l2-run-v1"
PYTHONPATH=src uv run --locked --extra duckdb python -m market_research.studies.ashare_execution_costs.review --source-root "$STUDY_RUN/l2-run-v1" --output-root "$STUDY_RUN/l2-reviewed-v1"
PYTHONPATH=src uv run --locked --python 3.12 --extra formal python scripts/run_execution_cost_strategy.py --source "$DIAGNOSTIC_SOURCE" --pilot web/public/data/execution-costs/pilot.json --output "$STUDY_RUN/strategy/run-v1"
```

Export the reviewed L2 summary with `expansion_publication --l2-summary ... --confirmed-on YYYY-MM-DD --output-root ...` only after aggregate review and permission. Use its exact `expansion.json` with the strategy runner's `--expanded-public` option (keeping the same `--source` and `--pilot`), writing to `strategy/expanded-v1`. Archive those reference bytes. The publication command accepts `--strategy-root` and `--strategy-extra-root` to combine all eighteen scenarios. Use a staging output outside Git for review before copying approved aggregates into the website.

The notebook requires pandas, pyarrow, matplotlib, nbformat, nbclient and ipykernel. Set `EXECUTION_COST_EXPANSION_RUN` to the external run parent; execute all cells with outputs saved outside Git. It independently checks saved measurement aggregates and strategy ledgers, and writes bilingual figures under `analysis-v1`. See [strategy protocol](../../docs/studies/execution-cost-strategy.md) for execution assumptions.

[Interactive charts and real-order entry](../../docs/studies/execution-cost-calibration.md) · [Replay gates and snapshot counterfactuals](../../docs/studies/execution-cost-replay.md) · [Independent order-accounting notebook](calibration_review.ipynb)
