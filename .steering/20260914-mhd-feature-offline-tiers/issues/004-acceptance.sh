#!/usr/bin/env bash
# issue 004 (T1c revision topology) の AC 検査
set -uo pipefail
fail() { echo "[acceptance 004] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"
cd src-tauri || fail "src-tauri が無い"

out="$(cargo run --quiet --bin gse-replay -- tests/fixtures/minimal.ndjson --features 2>/dev/null)" \
  || fail "gse-replay --features が非 0 で終了した"
[ -n "$out" ] || fail "--features の出力が空"

printf '%s' "$out" | jq -e '
  all(.[];
    (.revision | type == "object")
    and (.revision | has("delete_run_max") and has("delete_runs") and has("rewrite_count")
         and has("redelete_count") and has("loop_depth_max") and has("local_recurrence")))' >/dev/null 2>&1 \
  || fail "全行に revision の必須フィールドが揃っていない"

printf '%s' "$out" | jq -e '[.[].revision.delete_runs] | add > 0' >/dev/null 2>&1 \
  || fail "delete_runs の総和が 0（★ 出力が退化している）"

# AC4: ⚠️★★★ undo / redo / key.mod を先取りしていないこと
#   ★ ADR-032 は Proposed で、§Migration M4（同意 §3 の改訂）は研究者承認待ちである。
if grep -nEi '\b(undo|redo)\b' src/analysis/feat_offline/revision.rs 2>/dev/null \
     | grep -vE '^[0-9]+:[[:space:]]*//' >/dev/null 2>&1; then
  fail "revision.rs が undo / redo を参照している（★ ADR-032 M4/M5 を先取りしている）"
fi
if grep -nE '\.mod\b|key_mod|"mod"' src/analysis/feat_offline/revision.rs >/dev/null 2>&1; then
  fail "revision.rs が key.mod を参照している（★ ADR-032 D9 は Proposed）"
fi

echo "[acceptance 004] OK"
