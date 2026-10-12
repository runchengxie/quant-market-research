# Earlier book and order-flow inventory (2026-10-12)

Paired standardized books, orders and trades exist from 2021. This extends coverage beyond the initial three-day pilot, but does not establish more complete event streams or validated replay. Checks were limited to files, Parquet metadata, schema and trading-day values in the first row group.

The January 2021 book file contains 301,715,217 rows and ten levels of prices, volumes and order counts. Continuous-session orders for 2021-01-04 contain 65,228,573 rows; the checked standardized schema includes order IDs but lacks `Channel` and `BizIndex`. Corresponding trades contain 63,292,159 rows with buy/sell order references. A separate pre-opening order file contains 1,145,476 rows; check overlap and session definitions before combining it with continuous orders. These are not counts of validated transactions.

Located native archives begin on 2026-03-02 and preserve channel and business-sequence fields in orders/trades. The initial pilot already used native April 2026 books. Longer history does not establish richer sequencing.

The next candidate is 2021-01-04. Compare matched securities and sessions with a native 2026 day, auditing missing minutes, duplicates, one-sided books, units, time precision, identifier scope, trade/order linkage, cancellations, special events and sequence. Keep auctions separate. Earlier data may support static historical stability even if replay gates fail. Actual-order calibration remains absent. Sources were inspected read-only; private paths remain outside this record.

[Chinese inventory and next gates](historical_data_audit.zh-CN.md) · [Initial pilot](pilot_findings.md)
