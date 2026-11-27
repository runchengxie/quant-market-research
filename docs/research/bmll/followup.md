# Follow-up experiments

[简体中文](followup.zh-CN.md) · [Pilot](README.md)

The next pass separates quote diagnostics from portfolio construction. Run the retained-input analysis before requesting a larger event sample.

```sh
PYTHONPATH=src uv run python scripts/run_smallcap_followup.py --pilot "$BMLL_RUN_ROOT" --features "$BMLL_FEATURES" --output "$BMLL_FOLLOWUP_ROOT"
```

Use a new output directory outside Git. The script retains input hashes. Its output includes daily quote diagnostics, per-security unknown-aggressor fractions, a provisional stratified candidate list and target-membership comparisons. Security-level results stay private.

## Quote and exit diagnostics

Compare full valid-time spreads with spreads restricted to quote ages below 60 seconds. Keep valid-time and fresh-time coverage visible. Fully covered windows may still contain crossed or invalid quotes. Compare displayed bid notional and the fraction of valid, size-covered time exceeding each order-size threshold. Those quantities do not imply fill probability. The three half-hour windows do not form a continuous intraday tape.

Check corporate announcements between baseline and comparison dates before attributing any change to a market-wide event. Next acquisition should use five-minute windows with preceding-quote carry, an explicit missing-window record and price/quantity decomposition. Exclude no adverse observation merely because it weakens the case.

## Provisional expansion

At the fixed 2025-03-18 feature date, take up to four candidates per capitalization and ADV cell below one billion dollars, ordered by a documented stable hash. Eligibility comes from the retained snapshot. Validate historical listing identity and instrument type against reference data before event queries. Preserve nonmatches, duplicate mappings and subsequent exits. This is retrospective stratification, not a certified point-in-time equity universe or probability sample. Add independent periods only after the coverage and query-cost pilot.

## Lower-turnover experiment

Select the smallest 100 positive-cap, positive-ADV eligible feature rows. Compare monthly target replacement with a buffer retaining existing names up to rank 150, then filling vacancies by ascending cap. Quarterly formation dates provide a separate, very short comparison. Initial funding is excluded from replacement averages. Delisted or otherwise ineligible names are removed from targets, but the model does not pretend they could be sold.

This measures membership replacement only. Equal target weights do not capture price drift, actual turnover, returns or execution. A lower replacement fraction is a useful engineering result; profitability requires adjusted prices, dividend and delisting cash flows, delayed eligibility information and a reconciled holdings ledger. Do not combine a selected pilot spread with this universe as an estimated portfolio cost.

## Fundamentals and cross-market evidence

Use SEC company facts together with original filings and accession identities. Preserve period start/end, units, form, filing date and amendments. Join availability from filing acceptance timestamps; a conservative daily prototype can use only filings strictly before the formation day. Latest restated historical facts cannot replace values available at that time. Custom tags and changing accounting concepts need explicit mappings. Source: [SEC API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces). A failed download is a missing input, not a zero financial value.

For the 2024 China A-share drawdown, retain the frozen NAV chronology and its missing constituent/flow fields. Cross-market comparisons should first align group definitions and measurement denominators. US NBBO and China A-share depth snapshots support different execution questions. A causal explanation needs dated exposures, flows and trade records beyond the NAV series.
