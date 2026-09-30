#!/usr/bin/env bash
# issue 006 acceptance — 1 セルの段取り
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
RC="${K}/run/run_cell.py"; EX="${K}/run/cell.example.json"

echo "[006] 1 セルの段取り"
need_file "${RC}"; need_file "${EX}"; need_file "${K}/run/README.md"

# AC1 / AC2
selftest_ok "${RC}"
need_grep "${RC}" "a dead child process marks the run aborted" "AC2 selftest ケース: 子プロセスが死んだら aborted（陰性対照）"

# 最小の計画
printf '%s\n' '{"kind":"header","format":"plan/1","os":"macos","seed":1,"generator_version":"0","config_sha256":"0000000000000000000000000000000000000000000000000000000000000000"}' \
  '{"kind":"block","block_id":0,"reset_ime":false,"marker":[]}' \
  '{"kind":"trial","trial_id":"t0","block_id":0,"scenario":"S3","speed":"mid","think_ms":200,"phrase_id":"w1-0-0","reading_len":1,"steps":[{"key":"a","at_ms":0,"down":true},{"key":"a","at_ms":60,"down":false}],"intent":{"commit":"enter","cand_index":0,"nav_count":0,"abandon":false,"predictive":false,"ime_toggle_mid":false,"focus_switch_mid":false,"expect_session":true}}' > "${TMP}/plan.jsonl"
STUB="import sys,time; open(sys.argv[1],'w').write('x'); time.sleep(30)"
cat > "${TMP}/cell_real.json" <<EOF
{"os":"macos","ime":"stub","ime_settings":{},"refinput_cmd":["${PY}","-c","${STUB}","{out}"],
 "logger_cmd":["${PY}","-c","${STUB}","{out}"],"reset_cmd":[],"focus_cmd":[],"ready_wait_ms":100,
 "backend":"macos","clock_sync_disabled":true,"auto_update_disabled":true}
EOF

# AC3: 既存の run ディレクトリを上書きしない
mkdir -p "${TMP}/run_exists"; echo keep > "${TMP}/run_exists/keep.txt"
sed 's/"backend":"macos"/"backend":"dryrun"/' "${TMP}/cell_real.json" > "${TMP}/cell_dry.json"
run_fail "AC3 既存の run ディレクトリを渡すと止まる" "${PY}" "${RC}" --cell "${TMP}/cell_dry.json" --plan "${TMP}/plan.jsonl" --run-dir "${TMP}/run_exists"
if [ "$(cat "${TMP}/run_exists/keep.txt")" = "keep" ] && [ "$(ls "${TMP}/run_exists" | wc -l | tr -d ' ')" = "1" ]; then ok "AC3 中のファイルが変わらない"; else ng "AC3 既存の run ディレクトリが書き換えられた"; fi

# AC4: ⚠️ フラグなしでは送らない
run_exit 2 "AC4 フラグなしの実バックエンドは exit 2" "${PY}" "${RC}" --cell "${TMP}/cell_real.json" --plan "${TMP}/plan.jsonl" --run-dir "${TMP}/run_real"

# AC5
run_ok "AC5 cell.example.json が JSON として読める" "${PY}" -c "import json,sys; json.load(open(sys.argv[1],encoding='utf-8'))" "${EX}"

# AC6
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/run/(run_cell\.py|cell\.example\.json|README\.md)$'
style_ok
finish
