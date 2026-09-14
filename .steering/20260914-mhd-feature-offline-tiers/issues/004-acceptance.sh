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

# ★ pause / net は issue 001 の共有ヘルパを使うこと（⚠️ 局所定義を作らない）
#   ⚠️ Codex TASK-PRE 指摘 5: 局所定義は issue 005 (stall onset) との破壊的な食い違いを生む。
SRCF="src/analysis/feat_offline/revision.rs"
if grep -nE '^[[:space:]]*(pub )?fn [a-z_]*(extract_pauses|compute_net|pause_list)' "$SRCF" >/dev/null 2>&1; then
  fail "$SRCF が pause / net を独自に定義している（★ mod.rs の共有ヘルパを使うこと）"
fi
grep -qE 'super::|crate::analysis::feat_offline::' "$SRCF"   || fail "$SRCF が mod.rs の共有ヘルパを参照していない"

echo "[acceptance 004] OK"
