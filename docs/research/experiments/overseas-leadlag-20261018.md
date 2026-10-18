# Overseas signals and the A-share open: timing, controls and ETF costs

[Chinese version](overseas-leadlag-20261018.zh-CN.md)

**Decision:** retain this as exploratory forecasting research. Much of the opening-gap information overlaps with SPX. Adding HSI, N225 and KS11 after domestic, FX and SPX controls does not show a stable incremental benefit. Neither historical source availability nor actual ETF fills are certified.

**Evidence stage:** retrospective, annually refitted daily-bar diagnostics, reviewed 2026-10-18; source histories end 2026-10-16. The prior experiment inspected some of these years, so the following folds are not a fresh untouched holdout. Methods and reviewed aggregates are public; supplier histories and daily prediction rows remain external.

## What changed from the first exploration

The first pass compared index opening gaps and open-to-close returns. Its same-day index long/cash calculation was hypothetical. Domestic equity ETFs normally use T+1, so that calculation cannot establish an executable ETF result. This extension uses two different questions:

1. Can completed overseas daily bars improve an A-share index forecast at 08:45 Shanghai?
2. Does that information help a long/cash ETF exposure entered at an opening auction and retained until at least the next tradable open?

The second outcome includes another overnight interval. It does not isolate the first day's open-to-close return. Ordinary cash equity ETFs cannot generally monetize an opening-gap forecast by buying before the already established opening price.

## Availability and data audit

Decisions are fixed at 08:45 Asia/Shanghai. Source session dates are converted into UTC availability assumptions before an as-of join. US closes use America/New_York and its daylight-saving offset. HK uses 16:10 local; Tokyo uses its dated 15:00/15:30 close; Korea uses a conservative 15:30 close for all years. A one-hour publication allowance is added. Regular full-day closes conservatively bound earlier half-days; supplied bar dates do not independently prove calendar completeness. [NYSE trading hours](https://www.nyse.com/trade/trading-information), [HKEX hours](https://www.hkex.com.hk/Services/Trading-hours-and-Severe-Weather-Arrangements/Trading-Hours/Securities-Market?sc_lang=en), [JPX November 2024 change](https://www.jpx.co.jp/english/corporate/news/news-releases/1030/20241103-01.html).

TuShare FXCM daily dates are GMT dates. CNH, USD/JPY and EUR/USD mid-prices are eligible only after the GMT day ends plus one hour. Thus the previous GMT date's complete FX bar is **not** eligible at 08:45 Shanghai the next morning: its assumed availability is 09:00. That lag is intentional. [TuShare FX daily definition](https://tushare.pro/document/2?doc_id=179).

External signals measure the change between the latest eligible closes at consecutive A-share decisions. Moves during A-share holidays accumulate; foreign holidays do not repeat the same old daily return as new information. Selections older than ten calendar days are unavailable. A second scenario delays all external inputs, including FX, by one A-share observation.

| Audit | Finding |
| --- | --- |
| Source selections across targets and lag scenarios | 148,568 |
| Selected inputs later than the assumed decision cutoff | 0 |
| Historically verified retrieval vintages | **0** |
| Source selections older than ten days | 377; excluded from usable features |
| FX quote defect | One crossed USD/JPY bid/ask on 2019-07-07 excluded |
| ETF adjustment joins | No bar lacks an adjustment factor |
| 512480 extra adjustment date | 2021-03-26, a confirmed split suspension |

**These checks establish temporal consistency under stated assumptions, not historical API timeliness.** All raw pulls are current historical downloads. A provider could have published a bar later, revised it or omitted it at the original decision time. No historical retrieval timestamps have been fabricated. A strict historically available or newly forward-observed result remains unverified.

## Controls and chronological fits

All models use training-only centering/scaling and ordinary least squares, with a zero forecast threshold for the ETF exposure rule. There is no tuning against test-year returns.

- **Domestic + FX:** previous own-index/ETF return, five-session momentum, 20-session volatility; previous CSI 300 return and five-session momentum; CNH, USD/JPY and EUR/USD changes.
- **Global:** domestic + FX plus SPX.
- **All overseas:** global plus HSI, N225 and KS11.

Expanding fits are made separately for each year from 2020 through 2026, with at least 252 usable earlier training observations. Every training label must end before the first decision of that test year. The last prior-year ETF target can end after that decision and is purged. Index evaluation has seven annual folds; 512480 begins evaluation in 2021 after adequate post-listing training data, giving six folds. 2026 is partial.

## Forecast results

The table shows the **reduction in mean squared error**, `1 − MSE(augmented) / MSE(baseline)`, on common rows. Positive means lower prediction error; this differs from the first pass's R² against a training mean. The intervals resample paired errors in ten-observation circular blocks, with 1,000 fixed-seed draws. They are descriptive and not adjusted for the family of comparisons.

| Outcome, scheduled availability | N | All overseas vs domestic + FX | Asian addition after SPX, 95% interval | Years with positive Asian increment |
| --- | ---: | ---: | ---: | ---: |
| CSI 300 opening gap | 1,643 | +13.86% | +0.75% [−5.22%, +4.64%] | 2 / 7 |
| SW semiconductor opening gap | 1,643 | +11.92% | +1.16% [−1.67%, +3.34%] | 3 / 7 |
| CSI 300 open-to-close | 1,643 | +0.88% | −0.02% [−0.34%, +0.28%] | 2 / 7 |
| SW semiconductor open-to-close | 1,643 | +0.84% | +0.01% [−0.37%, +0.35%] | 3 / 7 |
| 510300 next tradable open | 1,642 | −1.36% | −1.40% [−2.66%, −0.22%] | 1 / 7 |
| 512480 next tradable open | 1,398 | +0.99% | −0.41% [−1.07%, +0.31%] | 2 / 6 |

Delaying external data by one A-share observation reduces the opening-gap Asian increments to −1.63% for CSI 300 and −1.42% for semiconductors, again with intervals crossing zero. The ETF Asian increments are −0.46% and −0.65%. The aggregate JSON includes all 36 comparisons and 246 annual rows, including negative findings. This is evidence of timing sensitivity, not proof of a particular provider's arrival delay.

## ETF proxy and cost results

510300 supplies broad-market exposure; 512480 supplies semiconductor exposure. The latter tracks a different benchmark from the SW semiconductor research index, so it is a proxy rather than an exact replication. Both were selected retrospectively from surviving products; there is no full historical ETF-universe selection test.

Open-to-next-tradable-open outcomes use `raw_open × fund_adj`. Known splits therefore do not become artificial 50% losses, and auction-limit guards use a split-adjusted reference. 512480's 2021-03-26 missing market bar is a documented suspension, with resumption on March 29. One holding interval spans more than one A-share session; annualized Sharpe uses an approximate 252 observed intervals. [SSE split and suspension announcement](https://www.sse.com.cn/disclosure/fund/announcement/c/2021-03-17/512480_20210317_1.pdf), [ETF trading-rule FAQ](https://www.sse.com.cn/assortment/fund/etf/question/), [ETF daily units](https://tushare.pro/document/2?doc_id=127).

Positions are long or cash. Consecutive long forecasts retain the existing holding. Costs apply to entries, exits and terminal liquidation, not to imaginary daily round trips. Entry admission uses only prior 20-observation average turnover, converting TuShare's thousand-yuan amounts to yuan, capped at 1% for a fixed reference notional. An auction open near the relevant 10% limit conservatively blocks the corresponding trade; blocked sales retain the holding. This approximates trading restrictions and does not establish an actual auction fill.

| Scheduled inputs, 10 bp round-trip assumption | Domestic + FX + SPX | Plus Asian indices | Always long |
| --- | ---: | ---: | ---: |
| 510300 mean net return per observed interval | +0.70 bp | −2.58 bp | +1.67 bp |
| 510300 approximate annualized Sharpe | 0.13 | −0.45 | 0.21 |
| 512480 mean net return per observed interval | +8.41 bp | +7.17 bp | +6.42 bp |
| 512480 approximate annualized Sharpe | 0.63 | 0.54 | 0.41 |

The semiconductor global model is positive in this retrospective sample, but the Asian addition lowers its mean return. That does not establish a deployable global model: source vintages, ETF selection, estimated opening fills and cash-distribution assumptions remain unverified. The two ETFs cover different windows; their numbers should not be ranked as a same-period competition.

All 224 cost scenarios are available in the reviewed snapshot. They cover 0/5/10/20/40 bp round-trip assumptions, both input-delay cases, four exposure rules, and CNY 10,000/100,000/1,000,000 reference budgets with a 3 bp commission assumption subject to a CNY 5 minimum plus 1/5/10 bp one-way slippage. These are sensitivity inputs rather than actual broker quotes. The fixed reference budget is used for fees and prior-turnover admission while returns compound: it does **not** measure the capacity of a growing account. Lot rounding, order-book impact, distributions in a cash ledger, futures rolls and historical fee schedules are not replayed.

![ETF cost sensitivity for the scheduled-input models](https://runchengxie.github.io/quant-market-research/charts/overseas-leadlag-cost.svg)

## Reproduction and publication boundary

Run from the repository with its locked research environment:

```bash
PYTHONPATH=src python -m market_research.studies.overseas_leadlag.run \
  --index-inputs /external/index-histories \
  --extra-inputs /external/fx-and-etf-histories \
  --output /external/new-task-output
python scripts/export_overseas_leadlag_public.py \
  --input /external/new-task-output/reviewed_summary.json \
  --output /external/reviewed-public-summary.json
```

The index directory supplies the four `{hsi,n225,ks11,spx}_tushare_daily.csv` files plus `000300_sh_tushare_daily.csv` and `801081_si_sw_daily.csv`. The extra directory supplies `{usdcnh,usdjpy,eurusd}_fxcm_fx_daily.csv` plus `{510300,512480}_sh_{fund_daily,fund_adj}.csv`. Each CSV has `trade_date`; other fields follow the named TuShare endpoint. `fund_daily.amount` is in thousands of yuan. Output must be a new directory outside this repository. The run records input SHA-256 values, joins, annual training bounds, daily predictions, cost results and the assumed availability audit.

The public exporter permits only aggregate comparisons, annual statistics, cost scenarios, training bounds and audit metadata. Supplier bars, daily private predictions, provider credentials and local filesystem paths are excluded. The optional plotter `scripts/plot_overseas_leadlag.py` uses Matplotlib with the aggregate JSON; it does not load raw bars.

The next evidentiary step is a genuinely forward period with retained pre-cutoff retrieval receipts, followed by execution-proxy checks against auction or minute data. This release publishes the current retrospective result and its limitations; it does not qualify a production strategy.
