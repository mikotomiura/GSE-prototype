#!/usr/bin/env bash
# One-command reproduction (preregistration.md). Synthetic data only until the data are acquired.
set -euo pipefail
cd "$(dirname "$0")"
PY="${PY:-$HOME/.venvs/pkm-main/Scripts/python}"
"$PY" scripts/selftest_synthetic.py
"$PY" scripts/synthetic_check.py --out results/.tmp/synthetic_check.json
cmp results/.tmp/synthetic_check.json results/synthetic_check.json
"$PY" scripts/selftest_main.py
"$PY" scripts/run_main.py --source synthetic --out results/main_synthetic.json --workers "${WORKERS:-16}" --no-timing
