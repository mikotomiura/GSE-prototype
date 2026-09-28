#!/usr/bin/env bash
# issue 021 acceptance — E2 閉集合のシミュレーション攻撃
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
E="${K}/e2"

echo "[021] E2 閉集合"
selftest_ok "${E}/simulate_obs.py"
selftest_ok "${E}/closed_set.py"
need_file "${E}/README.md"
need_grep "${E}/closed_set.py" "all features exceed chance" "AC2 selftest ケース: all features exceed chance"
need_grep "${E}/closed_set.py" "uninformative observation stays at chance level" "AC3 selftest ケース: uninformative observation stays at chance level（陰性対照）"
for f in closed_set simulate_obs; do forbid_grep "${E}/${f}.py" '^def (romaji|generate_plan)\(' "AC4 ${f}.py が生成器を再実装していない"; done
if grep -Eq 'generate_plan|romaji' "${E}/closed_set.py" "${E}/simulate_obs.py"; then ok "AC4 生成器のモジュールを使う"; else ng "AC4 生成器のモジュールを使っていない"; fi
forbid_grep "${E}/closed_set.py" 'gt/1|oracle/1' "AC5 攻撃が gt / oracle を読まない"
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/e2/(simulate_obs\.py|closed_set\.py|README\.md)$'
finish
