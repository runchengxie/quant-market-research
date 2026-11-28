# Three low-turnover target arms now share an explicit support contract

[Chinese (Simplified)](smallcap-target-support-20261128.zh-CN.md)

The next account experiment now has three reproducible target sets: a common-support benchmark, exclusion of the highest-turnover fifth and selection of the lowest-turnover fifth. This completes target construction and arithmetic checks, not the shared account, executable returns or a successful strategy.

The retained panel has 566,283 security/formation rows and 138 monthly dates. The diagnostic forms the full archive and its smallest 20% by size before looking at the low-turnover score. Each arm uses the same finite raw-score support. Missing scores stay counted in the original cohort; no forward return or financial descriptor determines support. The first source date, 27 February 2015, has no usable raw scores and is explicitly unsupported. The 137 supported dates run from 31 March 2015 through 31 July 2026. Across supported dates the mean score coverage is 96.28% in the smallest fifth and 96.81% in the full archive. This conditional benchmark is not the entire unconditional eligible universe.

## What the new diagnostic shows

Within the smallest fifth, using equal target weights:

| Arm | Mean target names | Low-volatility exposure versus common benchmark | Trading-activity exposure versus common benchmark | Mean target-weight change |
| --- | ---: | ---: | ---: | ---: |
| Common-support benchmark | 799.6 | 0 | 0 | 10.55% |
| Exclude highest-turnover fifth | 639.3 | +0.164 | −0.165 | 13.69% |
| Select lowest-turnover fifth | 160.3 | +0.546 | −0.667 | 25.84% |

Exposures use the full archived date's descriptor population standard deviation; no new clipping is added. A missing selected descriptor makes the exposure unknown, with coverage reported separately. Industry unknown weight is also retained (about 7.68% for the small-cohort low-turnover arm). Historical eligibility and industry vintages remain uncertified.

Target-weight change is half the sum of absolute differences between consecutive source-date target weights, including entrants and exits. Its first value is unknown; a known unsupported date resets the comparison. The table averages 136 transitions per arm. It excludes price drift, actual orders, fills, fees, cash, suspension and settlement. It is not realized portfolio turnover, trading cost or a forecast of either. Calendar completeness must still be verified under the account timing contract.

Selecting stocks with low stock-level turnover can still produce a target list that changes substantially at each formation. Here the selected low-turnover arm changes more than the wider benchmark. The arms have different breadth as designed; this is not a matched-K attribution of the mechanism. The result motivates holding buffers and a matched ledger comparison, rather than proving the arm is inferior after costs.

## Selection and checks

For n common-score names, take ceil(0.2n) at each tail, with deterministic symbol tie-breaking. The exclusion arm removes the lowest raw low-turnover scores; the selection arm keeps the highest. Require at least five common names. Each target arm is fully invested and equal-weighted in this diagnostic; these conventions are not executable share quantities or a cash policy.

The run produced 822 normalized formation/scope/arm groups. An independent reconstruction checked every group's positive weights and sum, duplicate identities and all 816 adjacent transitions across six scope/arm combinations. It used retained security-level target files outside Git; no such rows are published here. Five regression tests cover support, missing exposures, no future-return filter, target transitions/gaps, unknown industries and invalid keys.

Input SHA-256: `8dc7c10c3483163703dd1c0bf5cf03b82249d2ce471f676095ca7f2101efa3e5`.
Summary SHA-256: `779180d26cb70153f3e87a162d2f04edd69d1f69266d45b92907ebd3a7d5ef90`.
Support SHA-256: `75ab28f7f3481d9f08fbd4b6cdb2c1e2d9745d3a51572eb0165634038ffe5f31`.

Run `PYTHONPATH=src python scripts/explore_smallcap_target_support.py --panel <retained-panel> --output <new-external-directory>`. The manifest fingerprints runner, implementation, input and outputs. The three arms use 137 dates; they must not be confused with the prior 134-date raw/residual exposure comparison or the distinct 86/136-period historical-return studies. All history is development evidence, not untouched out-of-sample evidence.

## What remains

The [30-task register](../../../studies/smallcap_investability/README.md) records owners, dependencies, acceptance and next actions. The immediate path is a common timing contract, admitted historical membership/valuation and extension of the shared share/cash ledger. Cost calibration, stress exits, net factor comparisons and risk forecasts retain their own gates. The published 120-session window discrepancy remains unresolved: reviewing the existing 45/90-observation receipts does not recover the original generating run.
