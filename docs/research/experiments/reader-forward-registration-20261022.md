# Future-observation registration record

[Chinese version](reader-forward-registration-20261022.zh-CN.md)

Reviewed on 22 October 2026. This update adds a local receipt tool and preserves the existing rules. It collects no market data, installs no scheduler and submits no orders. No new completed future return is reported.

## Low turnover

Keep microcap-prospective-20261017/v1. The primary is the gross spread after beta and valuation controls, paired with the raw signal on identical support. Keep the 60-session feature, 45-observation minimum and ten groups. Evaluate the first 24 eligible completed new months once, with HAC lag 3. Monthly readings remain descriptive.

The retained protocol names the final October session as a candidate. Verify it against an official calendar and archive contemporaneous inputs before entry. The older August window still lacks verified pre-period time evidence and remains a later observation.

## Valuation groups

Keep the [frozen forward protocol](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/experiments/grouped-valuation-forward-protocol-20261021.md). First formation must be no earlier than November 2026 and later than the actual freeze timestamp. Keep all five groups, fixed contrasts and execution rules. Observe 12 planned monthly cohorts followed by the 20-session exit window. This has not started.

## Recording a window

After formation close, prepare the frozen protocol, input manifest and official calendar. The input manifest must bind actual data hashes and first-seen timestamps. Keep source data and receipts outside the repository. Before entry, run `scripts/register_research_window.py` with `--study`, `--protocol`, `--inputs`, `--calendar`, `--formation-at`, `--entry-at` and `--output`. Study IDs are `low-turnover` and `valuation`. Timestamps require explicit timezones; the output directory must already exist.

The tool records current UTC time and the SHA-256 of the three files. It includes neither input contents nor private paths. It exclusively creates a new receipt and refuses to overwrite an existing one. It rejects registration at or after entry and rejects formation inputs recorded before formation. Preserve missed-freeze records instead of changing the clock or backdating a file. Material rule changes require a new cohort and retention of old records.

A local clock is not independent time proof. Every generated receipt remains `pending_external_time_proof`, with admission false and zero completed windows. Before admission, obtain independently verifiable public time evidence that binds the receipt hash before entry. Review the rules, official calendar, first-seen data and ranking implementation separately. Ordinary Git author timestamps can be set by the author and cannot establish this proof alone. Without independent evidence, keep the window pending.

Append later outcome receipts and retain missing prices, absent months and unresolved assets. Missing outcomes are not zero returns, and a registration receipt is not performance evidence.
