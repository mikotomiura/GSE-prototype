#!/usr/bin/env bash
# issue 018 acceptance — L1 の連続量・分類の指標
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
F="${K}/analysis/l1.py"

echo "[018] L1 の指標"
selftest_ok "${F}"
for c in "recovers a dwell bias" "recovers an abandon flip" "excludes a dwell_ms of zero" "shuffling widens the limits of agreement"; do
  need_grep "${F}" "${c}" "selftest ケース: ${c}"
done
forbid_grep "${F}" '^def (wilson|cluster_bootstrap|bland_altman|cohen_kappa)' "AC5 統計を再実装していない"
need_grep "${F}" "stats" "AC5 stats を使う"
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/analysis/l1\.py$'
style_ok
finish
