# Financial statement template coverage repair

[Chinese version](financial-template-coverage-20261019.zh-CN.md)

The 87 financial-template companies in the original 2026-10-16 valuation panel recover PE coverage from 0 to 87 and parent-equity PB coverage from 12 to 87 after correcting the owner's statement normalization. Their five-metric common sample increases from 0 to 49. This is a single-date coverage diagnosis using retained raw data, with conflicting observation keys quarantined. It is not a published replacement asset, a historical PIT certification, or a return backtest.

| Sample / measure | Before | Diagnostic after |
| --- | ---: | ---: |
| All valid market-value quotes | 5,567 | 5,567 |
| All quotes: PE TTM | 3,839 | 3,931 |
| All quotes: deducted-profit PE | 3,703 | 3,703 |
| All quotes: parent-equity PB | 5,447 | 5,522 |
| All quotes: PB excluding goodwill proxy | 2,650 | 2,693 |
| All quotes: PB excluding goodwill and intangibles proxy | 2,601 | 2,644 |
| All quotes: common five | 1,743 | 1,794 |
| Original 87 financial templates: PE / deducted PE / PB | 0 / 87 / 12 | 87 / 87 / 87 |
| Original 87: both adjusted PB measures | 6 | 49 |
| Original 87: common five | 0 | 49 |
| Original general template: PE / common five | 3,839 / 1,743 | 3,844 / 1,745 |

The cohorts are fixed using the original panel's reporting-template classification. They are not industry classifications. No metric loses availability in the all-quote comparison. The original general-template cohort gains five PE observations and two common observations, so the effect extends beyond the original financial cohort. Its other four coverage counts do not change. Thirty-eight original financial-template names still lack the asset balances required by the adjusted PB measures; no missing amount is filled with zero.

The raw 2026-10-18 vintage already contains the required profit and balance-sheet legs. The standardizer treated `comp_type=1` as a consolidated statement and preferred it over financial templates. In addition, its merge created a new row index, then aligned the resulting mask with the filtered frame's original index. This deleted unrelated financial-template rows. [TuShare income](https://tushare.pro/document/2?doc_id=33), [balance sheet](https://tushare.pro/document/2?doc_id=36), and [cash flow](https://tushare.pro/document/2?doc_id=44) define `comp_type` as the company reporting template, including `7` for diversified financial companies. Consolidation scope is selected by `report_type`.

The provider correction accepts templates 1, 2, 3, 4, and 7 and removes template priority. Existing update-flag and announcement-date selection remain in place. The strict builder then rejects conflicting rows for the same observation rather than choosing a template. Complete strict rebuilding therefore fails on this retained raw bundle. The diagnostic excludes every ambiguous observation key after those ordinary revision filters: income 31 keys / 62 rows / 6 issuers; balance sheet 25 / 50 / 4; cash flow 13 / 26 / 6. Counts are per table and cannot be added as distinct issuers. Cash flow is audited for the owner but is not used in this valuation comparison.

For example, 603093.SH has `report_type=1`, the same final announcement date and exact retrieval timestamp, but templates 2 and 7 for its 2026-03-31 income report. The rows also differ in `n_oth_income` and `rd_exp`. Its 2026-06-30 balance-sheet rows have templates 1 and 7 and differences in several financial fields. Existing observation and update metadata cannot establish which template to use. Other conflicts sometimes differ only in the template label; all are quarantined under the same rule. Full keys, differing column names and the actual conflicting rows remain in the owner's diagnostic evidence.

No new API requests were made. Both baseline and diagnostic use the same raw observations and 2026-10-16 daily-basic partition. The diagnostic preserves exact raw retrieval timestamps from 2026-10-17/18 and separately records its actual generation time. It neither changes sealed inputs nor makes information available earlier. The consumer retains independent latest reports, positive finite denominators, the 550-day freshness guard, and equal report periods for the five-way sample. Parent/minority, preferred-equity and multiclass ownership limitations from the [original study](valuation-panel-20261018.md) still apply. No historical formation dates were added or recalculated.

The dedicated [aggregate evidence](https://runchengxie.github.io/quant-market-research/data/financial_template_coverage_reviewed.json) records source hashes, metric counts and quarantine totals. This diagnosis is published as a separate reviewed aggregate. The original published valuation panel JSON remains unchanged.

Provider source: [repair PR 105](https://github.com/runchengxie/quant-market-data-platform/pull/105), diagnostic code commit `616f789`. Reproduce after checking out the provider repair and this consumer revision. Resolve `MDP_CODE`, `QMR_CODE`, `MDP_DATA`, and `QMR_DATA` from the workspace configuration. Use new output directories for each run:

```bash
cd "$MDP_CODE"
python scripts/operations/audit_fundamentals_templates.py \
  --vintage "$MDP_DATA/assets/tushare/a_share/fundamentals_vintages/vintage=20261018" \
  --output "$MDP_DATA/task_outputs/financial-template-coverage-20261019/diagnostic01"
cd "$QMR_CODE"
python scripts/analyze_financial_template_coverage.py \
  --vintage "$MDP_DATA/assets/tushare/a_share/fundamentals_vintages/vintage=20261018" \
  --diagnostic "$MDP_DATA/task_outputs/financial-template-coverage-20261019/diagnostic01" \
  --prices "$MDP_DATA/assets/tushare/a_share/daily_basic/a_share_all_daily_basic_latest/data/trade_date=20261016/part.parquet" \
  --output "$QMR_DATA/task_outputs/financial-template-coverage-20261019/run01"
```

The price alias is a locator; the evidence records the exact partition hash. Source amounts remain outside both repositories. The provider repair was merged before this consumer diagnosis; reproduce with the merged revisions above.
