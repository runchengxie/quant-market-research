# Topic reading migration evidence

The three asset pages retain the original long-return, robustness and decision evidence. Cash-flow performance, recovery and replication remain in their original topic. Ten interactive charts belong to one asset topic each. The existing research datasets and archived download files are unchanged.

## Content preservation

The published pre-migration cash-flow page was retained outside source against revision `52cfc4ee0e2213b8273f62f240eeccdda348c7fb`. Its asset sections contain 804 evidence-table rows. Comparing the combined new pages as a multiset gives the same 804 rows, with no original row missing or replaced. Former subsection and chart identifiers remain present. New scenario-label cells are excluded from this original-column comparison; their presence and values are checked separately.

All scenario rows render in the static document. JavaScript applies the chosen cost/demand/shock filters only after initialization. Tables and methods start expanded, and chart loading leaves them expanded. With browser storage blocked, explicit locale destinations preserve language across topics. New prose explains holding windows and annualized returns near the graph, with rebalancing and spending units on the allocation page.

## Verification record

The first complete local website suite passed 330 tests. Python passed 923 tests with 22 optional dependency skips, and Ruff passed. The first migrated-asset browser suite passed 23 checks. The first source prose audit covered 279 source files and 38 registered documents without flagged prose. The rendered audit covers 64 generated routes in both locales. Detailed logs, visual captures and exact row comparisons are retained under the external project task identifier `topic-reading-20261102`.

One independent whole-branch review identified two important cases, non-default scenarios without scripts and Chinese navigation with blocked storage. Both were reproduced with failing browser assertions and enter the final verification pass. All required checks must pass for the final source revision before merge.

Two minor observations are retained for later editorial work. The directory primarily indexes charts, while constituent, closure and conclusion-register tables remain visible in full text. The discovery evidence-version date remains unspecified; acquisition dates are kept separate in the prose.
