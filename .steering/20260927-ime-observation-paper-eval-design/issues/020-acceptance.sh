#!/usr/bin/env bash
# issue 020 acceptance — 実験一式と 1 コマンドの再現
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
X="papers/ime-observation/experiment"; PL="${K}/analysis/pipeline.py"

echo "[020] 実験一式"
for f in "${PL}" "${X}/run.sh" "${X}/config.json" "${X}/SEED" "${X}/env.md" "${X}/data.md" "${X}/notes.md"; do need_file "${f}"; done

# AC1
selftest_ok "${PL}"

# AC2: 2 回でバイト一致（出力先は run.sh が決める。結果の置き場を環境変数で受ける前提にしない —— 出力の一覧を比べる）
hash_results () {
  "${PY}" - "$1" <<'EOF'
import hashlib, os, sys
root = sys.argv[1]; out = []
for d, _, fs in os.walk(root):
    for f in sorted(fs):
        if f.endswith(".json"):
            p = os.path.join(d, f); out.append("%s %s" % (os.path.relpath(p, root), hashlib.sha256(open(p, "rb").read()).hexdigest()))
print("\n".join(sorted(out)))
EOF
}
run_ok "AC2 run.sh --synthetic（1 回目）" env IME_RESULTS_DIR="${TMP}/r1" bash "${X}/run.sh" --synthetic
run_ok "AC2 run.sh --synthetic（2 回目）" env IME_RESULTS_DIR="${TMP}/r2" bash "${X}/run.sh" --synthetic
if [ -d "${TMP}/r1" ] && [ -n "$(hash_results "${TMP}/r1")" ] && [ "$(hash_results "${TMP}/r1")" = "$(hash_results "${TMP}/r2")" ]; then
  ok "AC2 2 回の結果がバイト一致"
else ng "AC2 結果が無い、または 2 回で一致しない（★ run.sh は結果の出力先を環境変数 IME_RESULTS_DIR で受けること）"; fi

# AC3: ⚠️ 凍結前は本番を走らせない
if [ -f "${X}/preregistration.md" ]; then ng "AC3 preregistration.md が既にある（この issue では作らない）"; fi
run_exit 3 "AC3 凍結の印が無ければ本番は exit 3" bash "${X}/run.sh"

# AC4 / AC5
forbid_grep "${PL}" '^def (match|icc|wilson|dwell_error)\(' "AC4 段を再実装していない"
for m in gt_sessions match l1 l2; do need_grep "${PL}" "${m}" "AC4 ${m} を使う"; done
for f in "${X}/run.sh" "${PL}"; do forbid_grep "${f}" 'scripts/|capabilities_gate' "AC5 GSE の scripts/ を参照しない: ${f}"; done
need_grep "${X}/notes.md" "Step 0" "AC5 notes.md に Step 0 を代えた理由"

# AC6
run_ok "AC6 config.json が JSON" "${PY}" -c "import json,sys; json.load(open(sys.argv[1],encoding='utf-8'))" "${X}/config.json"
if grep -Eq '^[0-9]+$' "${X}/SEED" && [ "$(grep -c . "${X}/SEED")" = "1" ]; then ok "AC6 SEED が整数 1 つ"; else ng "AC6 SEED が整数 1 つでない"; fi

# AC7
run_ok "AC7 check-shell-portability が緑" bash scripts/check-shell-portability.sh
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/(kit/analysis/pipeline\.py|experiment/(run\.sh|config\.json|SEED|env\.md|data\.md|notes\.md))$'
style_ok
finish
