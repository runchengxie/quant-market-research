# Data Storage and Publication

> Simplified Chinese reference: [数据保存与公开发布](data-storage-and-publication.md).

This repository stores research code and reviewed derived results. Raw market data is managed by `quant-market-data-platform`. Complete research run outputs stay in stable directories outside the repository.

## Data layers

| Layer | Contents | Common formats | Location |
|---|---|---|---|
| Raw data | Daily security prices, valuation, adjustments, and status fields | Parquet | `quant-market-data-platform` |
| Research intermediates | Large panels, security-level daily results, and reusable computation caches | Parquet, DuckDB | External output directories |
| Public derived results | Annual summaries, quantiles, downsampled series, and reviewed metrics | CSV, JSON | `web/public/data` |
| Research documentation | Methods, sources, coverage, and limitations | Markdown, JSON | Git repository |

Do not commit vendor raw data, credentials, complete market panels, or machine-specific paths.

## File formats

CSV works well for small public outputs that need manual review. It is easy to diff and can be read directly by browsers. Parquet is suitable for larger analyses because it preserves column types, compresses well, and supports filtered column reads with DuckDB.

Store large outputs as `Parquet + manifest + small summary CSV/JSON`. A browser that needs Parquet can use DuckDB-WASM or Apache Arrow. Keep a reviewable summary file in the repository.

## Size guidance

These values guide routine maintenance. Choose the publication format for each study:

- Derived files below about 10 MB can usually use CSV.
- For files around 10–50 MB, consider compression, partitioning, downsampling, or publishing only a summary.
- Files above about 50–100 MB should live outside the repository as Parquet or in object storage.
- When public derived data approaches 50 MB in total, review the published page scope.
- Raw security-level daily data always stays in the external data platform.

Public derived data currently totals only a few megabytes. Prefer stable filenames for new research and avoid accumulating dated duplicate copies.

## Manifest contents

Manifests for large or important research outputs should record at least:

- Data structure version.
- Generation time.
- Data source and coverage.
- Row count and key filters.
- File format, size, and checksum.
- Whether the files are raw data or reviewed derived results.

The small-cap turnover report includes:

- `smallcap_turnover_daily.csv`: complete daily group summaries, stored outside the repository.
- `smallcap_turnover_summary.json`: coverage and research limitations.
- `smallcap_turnover_manifest.json`: structure, file sizes, row counts, and SHA-256 hashes.

The extended series starting in 2008 uses a different historical source and marks `quality_status = incomplete` in its summary and manifest. That source lacks reliable ST and suspension fields. Use it for long-term description, and keep it at a separate quality level from the cleaned series beginning in 2015.

An A-share clean panel can mark its ST source as verified only when `manifest.yml` declares `tushare.a_share.daily_clean.v2`, records `inputs.st_history_file` and a `market-data-platform.reconstructed-st-history.v2` receipt, and declares the `daily_clean.st_available_from.v1` contract. A panel that retains holding quotes is `derived`. Legacy data or data without `st_available_from` is `incomplete`; treat ST eligibility as unknown and do not use it to form new positions. For rows with `is_st=true`, the state is known on a decision date only when `st_available_from` is no later than that date. A missing or later date leaves eligibility unknown. A holding-quote mode can still inspect genuine prices. The ST history is reconstructed by effective date, and `revision_safe=false` on its receipt means historical revision availability has not been fully established.

Pages show only reviewed summaries or downsampled results. They do not read complete security-level daily panels. The small-cap turnover page reads `web/public/data/smallcap_turnover.json`, which contains annual and monthly summaries, coverage quality, an N=1 extreme-case diagnostic, security-count options, and overlap audit summaries. Complete cleaned daily results, historical daily results, and audit details stay outside the repository.

Metric audit results also stay outside the repository. Git stores rerunnable commands, tests, and method documentation, not large audit CSV files.
