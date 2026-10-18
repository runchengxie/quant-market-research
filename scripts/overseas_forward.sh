#!/usr/bin/env bash
# Config belongs outside source control. Production interpreters must be immutable releases.
set -euo pipefail
: "${MARKETDATA_BIN:?}" "${DATA_PLATFORM_CONFIG:?}" "${MDP_CAPTURE_PYTHON:?}"
: "${RESEARCH_PYTHON:?}" "${OVERSEAS_RAW_ROOT:?}" "${OVERSEAS_DERIVED_ROOT:?}"
mode="${1:-scheduled}"
receipt_directory="$("${MARKETDATA_BIN}" config run --config "${DATA_PLATFORM_CONFIG}" -- \
  "${MDP_CAPTURE_PYTHON}" -m quant_market_data_platform.overseas_forward \
  --root "${OVERSEAS_RAW_ROOT}" --mode "$mode")"
"${RESEARCH_PYTHON}" -m market_research.studies.overseas_leadlag.forward \
  --receipt-directory "$receipt_directory" --output "${OVERSEAS_DERIVED_ROOT}"
