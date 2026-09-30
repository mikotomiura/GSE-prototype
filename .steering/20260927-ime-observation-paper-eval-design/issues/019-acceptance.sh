#!/usr/bin/env bash
# issue 019 acceptance — L2 測度の一致
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
F="${K}/analysis/l2.py"

echo "[019] L2 測度の一致"
selftest_ok "${F}"
for c in "a dwell bias appears in the mean conversion time" "shuffling lowers the ICC" "the bias moves with the mixture ratio"; do
  need_grep "${F}" "${c}" "selftest ケース: ${c}"
done
forbid_grep "${F}" '^def (icc|bland_altman|cluster_bootstrap)' "AC5 統計を再実装していない"
need_grep "${F}" "stats" "AC5 stats を使う"
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/analysis/l2\.py$'
style_ok
finish
