#!/usr/bin/env bash
# issue 025 acceptance — 〔任意〕実アプリへの転移確認の比較
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
F="${K}/analysis/transfer.py"

echo "[025] 転移確認の比較（任意）"
selftest_ok "${F}"
need_grep "${F}" "shifting dwell produces a difference" "AC2 selftest ケース: dwell をずらすと差が出る（陽性対照）"
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/analysis/transfer\.py$'
style_ok
finish
