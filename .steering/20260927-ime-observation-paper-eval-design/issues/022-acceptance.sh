#!/usr/bin/env bash
# issue 022 acceptance — E2 開集合の復元
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
E="${K}/e2"

echo "[022] E2 開集合"
selftest_ok "${E}/charlm.py"
selftest_ok "${E}/open_set.py"
for c in "復号がベースラインより良い" "入れ替えると差が消える" "学習と評価が重ならない"; do
  need_grep "${E}/open_set.py" "${c}" "selftest ケース: ${c}"
done
forbid_grep "${E}/open_set.py" '^def romaji' "AC5 ローマ字の表を再実装していない"
need_grep "${E}/open_set.py" "romaji" "AC5 romaji を使う"
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/e2/(charlm|open_set)\.py$'
finish
