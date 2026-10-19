# Overseas signals: forward archive protocol v1

[Chinese version](overseas-forward-v1.zh-CN.md)

Evidence starts with an actual receipt. Existing historical data remain research inputs; downloading them today cannot establish historical availability or create an untouched holdout. The October 18 installation probe is ineligible. The first scheduled archive completed on October 19, 2026 at 08:44 Shanghai time; one eligible observation is now retained.

## First scheduled acceptance: October 19, 2026

The timer started the service at 08:44:00 Shanghai time and it exited successfully at 08:44:02, without a manual trigger or rerun. Collection ran from `2026-10-19T00:44:00.373965Z` to `00:44:02.093013Z`; the prediction was sealed at `00:44:02.236136Z`. The dated manifest records `eligible=true` with no exclusion reasons. All eight archived CSV hashes, the receipt hash and the prediction hash were independently checked.

One eligible observation verifies this collection and sealing chain only. It does not establish predictive accuracy or returns. The first evaluation still requires at least 60 eligible target days; no outcome was automatically scored, no message was sent and no trade was placed.

Stable acceptance hashes: qualification manifest SHA256 `7e2a388e925d0b46d846793781e055c1338a73afbf3d87958d07c6c163cef139`; raw receipt SHA256 `6827020df51f990fb8fce1c74454c5a349fa5574f3b677c4c54ec337251ff3a4`. These identify the retained evidence without publishing source rows, signal direction or machine-local paths.

## Fixed signal and timing

Signal `spx-last-session-direction-csi300-open-next-open-v1` uses the sign of the return between the last two completed SPX closes to predict the CSI 300 direction from today's open to the next SSE session's open. Positive, negative and zero returns produce +1, −1 and 0. There is no fitting. This baseline checks the live information chain; it is separate from the historical expanding-window models and does not establish an executable strategy.

New requests start at 08:44 on Shanghai weekdays, within the permitted 08:43–08:45 window. Collection and prediction sealing must finish by 08:45. The calendar in the same receipt must confirm that today is an SSE session. The latest SPX source date must equal the cutoff's New York date rolled back to a weekday. A US holiday without that date's data causes exclusion. The two bars must be at most seven calendar days apart, have unique dates and finite positive prices, and satisfy assumed close plus one hour before cutoff. Assumed exchange close is not proof of the provider's historical publication time. Actual receipt clocks provide the new evidence. Asian indices and FX are archived but are not v1 predictors.

## Immutable records

```sh
python -m market_research.studies.overseas_leadlag.forward --receipt-directory <MDP-run> --output <QMR-owner-data>/forward/overseas-v1
```

The consumer verifies raw CSV hashes, exclusively writes and fsyncs a `.prediction.json` payload, then reads the actual completion clock. It exclusively writes a `.json` qualification manifest containing the payload hash, actual `sealed_utc` and `eligible` decision. Crossing the deadline excludes the observation. A payload without a manifest indicates interrupted sealing.

Derived records retain receipt and code hashes, signal identity, selected bars, prediction and exclusion reasons. Scheduled mode exclusively creates one record per target day, including failed or late exclusions. It cannot overwrite or select a later rerun. Probes are stored separately and are always ineligible. Failures retain existing evidence; missing observations are investigated rather than backfilled as eligible. A started record without a receipt indicates interrupted collection; a receipt without a forecast indicates failed sealing.

## Evaluation and operation

V1 consumes no domestic prices after the target date. It does not automatically score outcomes, send messages or place orders. Future evaluation needs separate append-only outcome records with subsequently received opening prices and receipt times; predictions remain unchanged. The first direction-accuracy evaluation requires at least 60 eligible SSE target days, uncertainty estimates and a list of all missing, late and US-holiday exclusions. Changing the signal, cutoff or dependencies starts a new protocol version.

After both owners are installed, `scripts/overseas_forward.sh [scheduled|capture_probe]` chains collection and sealing. Required environment names are `MARKETDATA_BIN`, `DATA_PLATFORM_CONFIG`, `MDP_CAPTURE_PYTHON`, `RESEARCH_PYTHON`, `OVERSEAS_RAW_ROOT` and `OVERSEAS_DERIVED_ROOT`. Both Python environments and the wrapper point to merged immutable releases. The dedicated timer uses `OnCalendar=Mon..Fri *-*-* 08:44:00 Asia/Shanghai`, `AccuracySec=1s`, `RandomizedDelaySec=0` and `Persistent=false`. There is no automatic retry. Logs retain service status and artifact paths.
