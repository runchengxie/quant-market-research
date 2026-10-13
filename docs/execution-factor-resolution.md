# Factor alarms and full-year execution exploration

[中文](execution-factor-resolution.zh-CN.md)

Historical factor changes can alert us to missing corporate actions. They are not themselves cash/share entitlements. The optional `--factor-evidence` path tests source-bound explanations specifically for raw-price execution accounting; default preparation still rejects every unexplained change. Neither path establishes complete historical revision-vintage PIT or supplier internals.

The full-2024 canonical sample has 109 securities across three target variants and 183 otherwise unexplained keys. Actual reobservations support stability for 162 keys; independent raw and adjusted bars, reference prices and full-year event queries support no observed economic adjustment for the remaining 21 keys. The screen also retains 25 changes associated with modeled events. Factors are kept unchanged. An 11-key rounding reproduction is supporting evidence, not a substitute for these checks.

Mixing four freshly observed dates into an older full-year factor sequence introduces new boundary alarms, including June 24. The validator therefore retains the canonical sequence and checks evidence per original key. All applicable original keys must still match their factor, prior factor and prior trading day, even when a modification would make the current alarm disappear. Nonfinite factors, missing original rows, changed study coverage, changed hashes and uncovered new alarms reject the evidence.

The packet schema is `execution-factor-evidence.v1`, scoped to `raw_price_execution_event_screen`. It binds the study start/end and symbols, daily-clean manifest and dividend source hashes, original diagnostic Parquet, actual native factor reobservations and independent query receipt. Residual alarms require exact constant ratios of independent adjusted/raw close strings, matching raw OHLC and reference prices, correct query modes, complete daily coverage and full-window dated adjustment/dividend query coverage. Available independent economic events cannot be ignored just because a reobservation is stable. Unknown event dates remain blocking.

Known distributions still pass through the ordinary corporate-action normalization and actual record-date ownership accounting. Market ex-reference deductions are not necessarily the cash amount credited to a shareholder, especially for differential dividends excluding repurchased shares. The evidence packet neither alters nor creates entitlements.

## Run in stages

Create a new external output directory. Prepare using the ordinary data, dividend-coverage, primary-action-override and suspension arguments, adding:

```bash
uv run --locked --extra formal --extra duckdb python scripts/run_execution_cost_minute.py \
  --data-root "$DATA_OWNER_ROOT" \
  --dividends "$SOURCE_ROOT/dividend.parquet" \
  --dividend-coverage "$SOURCE_ROOT/coverage.json" \
  --action-overrides "$SOURCE_ROOT/corporate-action-overrides.json" \
  --factor-evidence "$FACTOR_EVIDENCE" --suspensions "$SUSPENSION_SOURCE" \
  --start 20240102 --end 20241231 --count 40 \
  --output "$FULL_YEAR_OUTPUT" --prepare-only

uv run --locked --extra formal --extra duckdb python scripts/run_execution_cost_minute.py \
  --output "$FULL_YEAR_OUTPUT" --run-prepared \
  --scenario fees_1m --scenario fees_10m
```

The two pilots remain `complete=false`, `expected_scenarios=9`, `published=false`. Validate cash, shares, receivables, fees, marks, order/fill quantities and execution constraints independently. Only after both pass, rerun with `--run-prepared` without `--scenario` to complete the nine-scenario matrix. Existing scenarios resume only when source/configuration/output hashes match. The factor validator source hash is part of the implementation receipt; DuckDB temporary spills remain under the external output directory.

The supplied packet is retrospective source evidence, not proof that all historical reference versions were available to a trader. A passed screen permits an exploratory raw-account simulation; it does not prove live capacity, causal own-order impact or a resolved supplier formula. Keep derived results private until the complete evidence and ledgers have been reviewed.

## Pilot outcome

Prepared inputs cover 242 sessions, 109 securities and 6,216,836 observed minute bars, with 25 modeled corporate actions. Both CNY 1m and CNY 10m pilots failed held-position valuation checks: 127 sessions cannot produce complete NAV. Annual returns are withheld and the other seven scenarios were not started.

Three held securities were subsequently delisted: 600321.SH on June 27, 002621.SZ on August 5 and 000982.SZ on August 12. Full-window daily and minute partitions contain no observations after their final trading sessions. Termination notices confirm there was no delisting-arrangement trading period. Transfer of share registration and trading to the delisting board does not establish cash recovery.

Sources: [600321 termination notice](https://big5.sse.com.cn/site/cht/www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2024-06-21/600321_20240621_6WSY.pdf), [002621 termination notice](https://disc.static.szse.cn/disc/disk03/finalpage/2024-08-02/3bfda236-6bb2-4350-b232-b1e99494fd8b.PDF), [000982 termination notice](https://disc.static.szse.cn/download/disc/disk03/finalpage/2024-08-12/c552bbd6-8940-49ef-bbd0-c2c83a3ece6d.PDF).

Available assets contain no verified subsequent valuation, executed disposal or cash settlement. Dropping holdings, assigning an undocumented zero value or indefinitely carrying the last quote would not resolve this gap. Further work requires disposal/valuation evidence or a separately declared conservative impairment scenario. Such a policy must operate inside the account simulation and trigger a fresh run, because later funded targets depend on valuation; a post-hoc NAV patch is insufficient. External records retain input, implementation, configuration and failed-ledger hashes. The published 18 scenarios remain unchanged.

Subsequent work adds [explicit nontrading valuation scenarios](execution-delist-valuation.md) for assumption-based sensitivity studies. The original strict gate and failed runs remain retained.
