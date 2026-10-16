# Execution research follow-up: data gaps and prospective validation

[简体中文](execution-validation-next-stage.zh-CN.md)

Protocol v1 was merged by [PR #171](https://github.com/runchengxie/quant-market-research/pull/171) at 17:43 Shanghai time on 2026-10-14, after that day's session. Under the [SSE 2026 trading and closure schedule](https://www.sse.com.cn/disclosure/announcement/general/c/c_20260915_10832273.shtml), its first eligible trading session was 2026-10-15. A project `DATA_ROOT` inventory on 2026-10-16 found no prospective daily receipt or immutable holdout archive for that start. The registered start was missed. Do not reconstruct October 15 later and label it unseen. Keep v1 and its hashes intact. A valid holdout now requires a new protocol version registered before its first eligible session, with the daily archive process ready. No holdout performance was inspected during this status check.

## What the local data shows

The 2025 original selections contain 106 names and 9,680 symbol-decision-date rows. None of those rows is marked ST in the prepared daily panel. A separate daily positive-ST history contains 5,608 2025 symbol-days across 35 of the 106 names, but none coincides with a date on which that name was selected. This explains why the ST-availability guard did not change 2025 fills.

This is not strict historical PIT evidence. The daily status table was reconstructed and retrieved in October 2026; its manifest explicitly says `revision_safe=false` and `historical_pit_eligible=false`. It records when a security carried ST status, not when a particular vendor knew the event or which revision it served. Do not backfill announcement availability from this table.

TuShare has a separate `st` endpoint with `pub_date` and `imp_date`, documented at 6,000 points. The [endpoint](https://tushare.pro/document/2?doc_id=423) can cross-check event and effective dates, but it does not provide the complete original notice with exact intraday publication time or guarantee a complete vendor revision chain. When intraday time is absent, use the first exchange session after the announcement date; verify important cases against the issuer or exchange notice.

The data platform also has a research-only announcement-time PIT path for financial statements. It preserves report period, availability date and revision flags, while explicitly disclaiming complete revision history. It can support prospective capture and as-of selection. It does not supply termination decisions or prove that 2025 snapshots were unrevised. See the [data-platform documentation](https://github.com/runchengxie/quant-market-data-platform/blob/main/docs/a-share-fundamentals.md).

## Data that can be added and what it still cannot prove

| Question | Existing evidence and feasible addition | Still unproven |
| --- | --- | --- |
| 2025 ST state | Positive-state history and daily selected targets already exist; TuShare `st` publication/effective dates can provide an independent event check | Reconstructed history is not revision-safe PIT; `pub_date` is not an intraday timestamp |
| 2025 delisting notices | None of the 106 ever-selected names has a 2025 delisting date, so that year has no delisting event on which to estimate the guard's effect | The delisting guard has no effective test in that year; an empty event sample does not prove source completeness |
| Full announcement feed | TuShare `anns_d` supplies announcement titles, PDF URLs and an optional publication timestamp, with up to 2,000 rows per request | “Announcement data” is a separately enabled permission and is not included with 15,000 points; the personal pricing table lists CNY1,000/year. See the [endpoint](https://tushare.pro/document/2?doc_id=176) and [permissions table](https://tushare.pro/document/2?doc_id=290). |
| Unseen sample | Freeze the rules and observation window now, then collect 252 future exchange sessions | 2024, 2025 and 2026 history already examined cannot be relabeled unseen |
| Post-delisting valuation and sale | Three samples have candidate post-delisting board daily quotes for source-labelled valuation studies | Independent price, units, ownership transfer, executable quotes and cash settlement remain unverified; these are not sale prices or liquidation capacity |
| Own impact and queueing | Minute data and participation/release sensitivity experiments exist | The local inventory contains no historical order-by-order queue or strategy fills; minute bars cannot identify priority, cancellations or the strategy's effect on prices |

There is no reason to buy the broad announcement permission just to explain the 2025 ST guard's zero incremental effect: no selected decision-date row was ST, and no 2025 delisting event is present for the rule to compare. A claim about termination filtering across the whole candidate universe does require candidate-wide event coverage. Before any purchase, verify whether the account already has access; then run a scoped sample to measure title recall, timestamp availability, PDF retrieval and missing documents. A point balance alone does not establish that the endpoint is enabled.

## Frozen prospective evaluation

**Status as of 2026-10-16:** v1's registered start was missed before a daily archive was created. The rules below describe the frozen v1 design and do not establish that its holdout began.

The holdout starts on the first SSE or SZSE open session after this protocol is merged, rolling forward automatically if the exchange is closed. It ends after 252 complete trading sessions. During the window, inspect data completeness only; do not inspect or publish strategy NAV, return differences, drawdowns or capacity results.

The primary comparison is the original baseline versus the combined 2024 rule: exclude names whose unadjusted prior-session close is below CNY1, while preserving existing strategy eligibility rules. CNY10m is primary capital and CNY1m is secondary. Use 5% participation, a 330-minute single release, one-minute latency and the current research fee settings. ST-availability and termination-announcement guards are separately preregistered secondary comparisons and count only after their event sources, publication times and full-candidate coverage pass audit. Otherwise report them as “not evaluable”; an empty event table is not zero risk.

Before each session, archive the full candidate universe, selection targets, input manifest and SHA-256 hashes, announcement/status sources, minute-data version and execution-engine version. Store these outside the repository in project data storage. Do not commit security lists, raw prices, notice packets or ledgers to the public repository. Corrections create new source versions and preserve prior files and diffs; they never overwrite an input already used.

The single primary result is the CNY10m after-fee account return difference over 252 sessions (combined rule minus baseline). Also report maximum drawdown, target-notional completion, fees, zero-fill sell orders and remaining legal inventory. Give a 95% interval from calendar-month block resampling. The preregistered support criterion is a positive return difference with a lower interval bound above zero. Otherwise classify the finding as unsupported or inconclusive; do not retune using this window. The CNY1m result and individual guards are secondary descriptions.

A termination notice blocks new buys only after its available time. It cannot erase existing shares or create sale proceeds. Preserve legal inventory. If sourced marks or disposal cash are unavailable, final account NAV remains incomplete and no full-year performance is published. Even a positive prospective comparison would validate only this frozen strategy period, not live capacity.

## Work sequence

1. Use the existing positive-state table to publish a source-consistency check for 2025 ST candidates and selected dates. Fetch the separate `st` event endpoint only if a signal-relevant discrepancy remains.
2. Before the first session under a replacement protocol, register hashes of the window, parameters, primary metrics and missing-data policy; then archive daily inputs and receipts.
3. Only if candidate-wide termination filtering is a required hypothesis and the account's access is confirmed, sample TuShare announcements or issuer-specific notices. Manually audit title recall, `rec_time`, original PDFs and source coverage.
4. To measure queueing and own impact, obtain timestamped historical trades, changes in at least ten book levels and actual parent/child order and fill records. TuShare points, daily bars and minute bars do not replace these records.

This remains backtest research. The original 18 public scenarios are unchanged; 2025 is not an unseen sample; current data does not establish live capacity.

The [cross-check record](execution-validation-st-crosscheck.json) binds the local ST comparison to its SHA-256 inputs and PIT limitation.
