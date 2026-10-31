# Follow-up reproduction protocol

This protocol extends the [first-round study](README.md). Read the [English findings](followup-20261031.md) or [中文结果](followup-20261031.zh-CN.md) before interpreting its outputs.

## Frozen inputs and output

```bash
uv run --locked --extra dev python scripts/run_asset_robustness_study.py \
  --previous "$RESEARCH_DATA/tasks/asset-returns-20261031" \
  --previous-owner "$DATA_OWNER/tasks/asset-returns-20261031" \
  --owner "$DATA_OWNER/tasks/asset-robustness-20261031" \
  --output "$RESEARCH_DATA/tasks/asset-robustness-20261031/run-NEW"

uv run --locked --extra dev python scripts/audit_asset_profit_coverage.py \
  --normalized-root "$FROZEN_NORMALIZED_FUNDAMENTALS" \
  --owner-task "$DATA_OWNER/tasks/asset-robustness-20261031" \
  --output "$RESEARCH_DATA/tasks/asset-robustness-20261031/financial-audit-NEW.json"

uv run --locked --extra dev python scripts/project_asset_robustness_summary.py \
  --run "$RESEARCH_DATA/tasks/asset-robustness-20261031/run-NEW" \
  --financial "$RESEARCH_DATA/tasks/asset-robustness-20261031/financial-audit-NEW.json" \
  --output "$RESEARCH_DATA/tasks/asset-robustness-20261031/public-projection-NEW.json"
```

Resolve the variables from project configuration. Every output must be new; full results stay outside source. The public projection is reviewed separately before being copied to the existing website. `coverage_verified` assertions from the first-round input remain their original evidence, not new vendor authentication.

The follow-up raw directory holds 55 API responses and `receipt.json`: three ETFs × (three windows each for `fund_daily`, `fund_adj`, `fund_nav`, plus `fund_div` and `fund_basic`), and two indices × eleven December `index_weight` queries. Windows are 2017–2019, 2020–2022 and 2023–2025. Constituent years are 2015–2025. The acquisition recipe is retained privately with data-owner responses; it contains configuration references, not credential values. Re-querying later produces a new observation vintage, not the same frozen input.

The runner checks response hashes, verifies old CSV hashes against first-round runs, checks exact final-session ETF marks, verifies reported fund-benchmark names, and audits complete annual member counts and rounding-aware weight closure. A month-end endpoint check is not a complete daily-history check. For ETFs the first mark is January 2017; the December 2016 base is not invented.

## Fixed calculation rules

- **Endpoint grid:** initial mark and December marks; minimum 60 elapsed months. CAGRs use actual monthly interval counts. No samples are relabeled independent, and no removed-year histories are spliced.
- **Year contributions:** sum monthly log growth within calendar year. Negative shares or contributions exceeding total growth are valid. If total log growth is essentially zero, percentage contributions are unavailable.
- **Relative waiting:** asset/benchmark level ratios feed the existing recovery algorithm. Episodes include observed ends and censored flags; durations are exact month differences. Entry-level recovery and relative-high-water episodes are different populations. Zero-follow-up entries are reported separately.
- **Allocation:** finite predeclared stock-only, 60/40 stock/bond and equal stock/bond/gold comparisons. Multi-asset policies are buy-and-hold, every twelve elapsed months, or 5pp absolute target deviation. Current-month returns occur before trades. Costs of 0/10/50 bp apply per unit of both buy and sell notional. Solve `fee = rate × sum(abs(target × (wealth-fee) - holdings))` before assigning funded holdings. Initial purchases/final liquidations are excluded. Fractional simultaneous trading and index/spot proxies omit implementation constraints. This study-specific diagnostic is not a replacement for the platform's order or execution engine.
- **ETF reconciliation:** market proxy growth = raw close growth × market adjustment-factor growth. Market/reference relative growth = NAV/reference × price/unit-NAV premium growth × distribution-basis residual. NAV already embeds internal expenses. NAV is matched by valuation date, not announcement availability for trading. Dividend proposals/implementations are not summed as separate cash receipts.
- **Constituents:** one verified December snapshot per consecutive year; exact 300/1,000 counts. Fractional quantum `0.00001` corresponds to 0.001 percentage point. Verify grid precision and a maximum half-quantum rounding error per member before normalizing. Report original sums and error. Annual weight distance includes drift and is not realized turnover.
- **Profits:** independent aggregate-profit accounting keeps negative earnings and all opening members. Missing closing profits of exited firms block fixed-cohort comparisons. The coverage script counts at least one finite retained consolidated-profit field, not a certified original version, correct share scope or known-then input.

## Evidence boundaries and review

Raw prices/NAVs, per-security constituents and financial amounts are not projected. Public output contains derived CAGRs, annual log contributions, waiting episodes, scenario summaries, ETF relative ratios, aggregate member retention, coverage counts and hashes. The 512100 issuer check independently compares only disclosed 2025 and five-year NAV returns, not the complete history or causal tracking explanation. Its contract price benchmark differs from this study's total-return reference.

Reproduction pins exact raw/normalized hashes, not a moving `latest` name. The retained normalized income manifest identifies pre-first-observation history as reconstructed PIT. No missing firm is dropped to produce a complete earnings result. No shared aliases or production data are changed.
