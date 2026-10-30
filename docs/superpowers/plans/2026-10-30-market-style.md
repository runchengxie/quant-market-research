# Market Style Analysis implementation plan

Approved scope: use 市场风格分析 / Market Style Analysis, with 18 年 A 股市场风格分析 for the long history. Preserve archived evidence, all numerical assets, their hashes, legacy routes, config and import aliases. No research calculations change.

- [x] Inspect and isolate the fetched source revision.
- [x] Add canonical Python style_factors module and CLI names while retaining aliases and historical output filenames.
- [x] Rename current components and current public prose; preserve source citations and historical identifiers.
- [x] Build /data/style-factors/reader.json directly from committed summary and yearly assets, validate IDs/dates/duplicates, preserve percent period_return and source hashes.
- [x] Validate Python, web, static output and browser smoke on port 4347; commit and open PR, hold merge for coordinated publication.

Reader schema remains exactly as approved: schemaVersion 1; historical_archive; percent; row-derived coverage; SHA-256 summary/yearly; 19 original factor IDs with ascending annual observations, actual date ranges, positive days, partial flag and period return. Missing years are absent.

Direction caveat: the archived report describes high-score minus low-score portfolios, but original descriptor definitions and scripts were not fully retained. Current factor-descriptors.yml explicitly mixes high_minus_low and low_minus_high by factor. The independently recomputed size diagnostic is small_minus_large. The archive is not proof of a uniform raw-descriptor direction, a standardized commercial model, or account returns.

Root review confirmed compatibility, data integrity and reader contract; revised ambiguous commercial-model wording. Local full Python: 868 passed, 22 optional-provider skips; newly added study alias regression: affected suite 16 passed. Ruff and diff checks passed. Web and browser results are recorded in the PR. Merge is explicitly held for coordinated provider-first publication.
