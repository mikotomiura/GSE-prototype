#!/usr/bin/env bash
# issue 010 acceptance — 正解の組み立て
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
G="${K}/analysis/gt_sessions.py"; R="${K}/analysis/gt_rules.example.json"

echo "[010] 正解の組み立て"
need_file "${G}"; need_file "${R}"

# AC1-3
selftest_ok "${G}"
need_grep "${G}" "five session types" "AC2 selftest ケース: 5 型"
need_grep "${G}" "arrows outside the interval are not counted" "AC2 selftest ケース: 区間外の矢印を数えない"
need_grep "${G}" "changing the rules changes the result" "AC3 selftest ケース: 規則を変えると結果が変わる（陰性対照）"

# AC4: ⚠️ 観測側を読まない
forbid_grep "${G}" 'ime_shadow|obs/1|dwell_ms' "AC4 観測側（ime_shadow / obs/1）を読んでいない"

# AC5: 例の規則で最小の入力を処理する（mac の開始 → 確定 1 回）
printf '%s\n' '{"kind":"header","format":"gt/1","src":"mac_nstic","app_version":"0.1.0","os":"macos"}' \
  '{"kind":"ev","t_wall_ms":1000,"t_mono_ns":1000000000,"ev":"set_marked","len":1,"sel_loc":1,"sel_len":0}' \
  '{"kind":"ev","t_wall_ms":1200,"t_mono_ns":1200000000,"ev":"set_marked","len":3,"sel_loc":3,"sel_len":0}' \
  '{"kind":"ev","t_wall_ms":1500,"t_mono_ns":1500000000,"ev":"insert_text","len":2}' > "${TMP}/gt.jsonl"
printf '%s\n' '{"kind":"header","format":"oracle/1","plan_sha256":"0000000000000000000000000000000000000000000000000000000000000000","os":"macos","emitter_version":"0","backend":"dryrun"}' \
  '{"kind":"block_begin","block_id":0,"t_wall_ms":900,"t_mono_ns":900000000}' \
  '{"kind":"trial_begin","trial_id":"t0","t_wall_ms":950,"t_mono_ns":950000000}' \
  '{"kind":"trial_end","trial_id":"t0","t_wall_ms":1600,"t_mono_ns":1600000000}' \
  '{"kind":"block_end","block_id":0,"t_wall_ms":1700,"t_mono_ns":1700000000}' > "${TMP}/oracle.jsonl"
run_ok "AC5 例の規則で実行できる" "${PY}" "${G}" --gt "${TMP}/gt.jsonl" --oracle "${TMP}/oracle.jsonl" --rules "${R}" --out "${TMP}/s.json"
run_ok "AC5 definitions.all が 1 件" "${PY}" -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); sys.exit(0 if len(d['definitions']['all'])==1 else 1)" "${TMP}/s.json"
run_ok "AC5 mac の windows_def は null" "${PY}" -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); sys.exit(0 if d['definitions']['windows_def'] is None else 1)" "${TMP}/s.json"

# AC6
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/analysis/(gt_sessions\.py|gt_rules\.example\.json)$'
finish
