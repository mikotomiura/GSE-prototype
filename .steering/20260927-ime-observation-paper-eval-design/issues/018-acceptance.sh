#!/usr/bin/env bash
# issue 018 acceptance — L1 の連続量・分類の指標
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
F="${K}/analysis/l1.py"

echo "[018] L1 の指標"
selftest_ok "${F}"
for c in "dwell の偏りを回復" "abandon の反転を回復" "dwell_ms 0 を除外" "シャッフルで一致限界が広がる"; do
  need_grep "${F}" "${c}" "selftest ケース: ${c}"
done
forbid_grep "${F}" '^def (wilson|cluster_bootstrap|bland_altman|cohen_kappa)' "AC5 統計を再実装していない"
need_grep "${F}" "stats" "AC5 stats を使う"
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/analysis/l1\.py$'
finish
