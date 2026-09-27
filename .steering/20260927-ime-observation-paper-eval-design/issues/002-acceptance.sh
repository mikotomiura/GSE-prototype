#!/usr/bin/env bash
# issue 002 acceptance — 青空文庫の句と読み（辞書は注入可能）
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
B="${K}/corpus/build_corpus.py"

echo "[002] 句と読みの前処理"
need_file "${B}"; need_file "${K}/corpus/README.md"

# AC1-3
selftest_ok "${B}"
need_grep "${B}" "注記とルビを除く" "AC2 selftest ケース: 注記とルビを除く"
need_grep "${B}" "同じ seed でバイト一致" "AC3 selftest ケース: 同じ seed でバイト一致"
need_grep "${B}" "seed を変えると変わる" "AC3 selftest ケース: seed を変えると変わる（陰性対照）"

# AC4: 壊れた corpus を拒否する
printf '%s\n' '{"kind":"header","format":"corpus/1","source":"aozora","tokenizer":"table","dict":"none"}' \
  '{"kind":"phrase","phrase_id":"w1-0-0","work_id":"w1","text":"青空","reading":"青空","reading_len":2}' > "${TMP}/bad.jsonl"
run_fail "AC4 読みに漢字を含む corpus を拒否する" "${PY}" "${B}" --validate "${TMP}/bad.jsonl"
printf '%s\n' '{"kind":"header","format":"corpus/1","source":"aozora","tokenizer":"table","dict":"none"}' \
  '{"kind":"phrase","phrase_id":"w1-0-0","work_id":"w1","text":"青空","reading":"あおぞら","reading_len":4}' \
  '{"kind":"phrase","phrase_id":"w1-0-0","work_id":"w1","text":"青空","reading":"あおぞら","reading_len":4}' > "${TMP}/dup.jsonl"
run_fail "AC4 phrase_id の重複を拒否する" "${PY}" "${B}" --validate "${TMP}/dup.jsonl"
head -n 2 "${TMP}/dup.jsonl" > "${TMP}/good.jsonl"
run_ok "AC4 正しい corpus を通す" "${PY}" "${B}" --validate "${TMP}/good.jsonl"

# AC5: sudachipy を import できない環境でも selftest が緑（先頭 import の禁止）
mkdir -p "${TMP}/fake"
printf 'raise ImportError("sudachipy is not available in this test")\n' > "${TMP}/fake/sudachipy.py"
run_ok "AC5 sudachipy 無しでも --selftest が緑" env PYTHONPATH="${TMP}/fake" "${PY}" "${B}" --selftest
forbid_grep "${B}" '^(import sudachipy|from sudachipy)' "AC5 sudachipy をファイル先頭で import していない"

# AC6
check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/corpus/(build_corpus\.py|README\.md)$'
finish
