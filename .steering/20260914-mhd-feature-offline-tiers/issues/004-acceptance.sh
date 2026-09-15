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

# ⚠️★★★ 2026-09-15 追加（★ 引き継ぎ §4 の型 / decisions.md 判断 8）——
#   ★ 「否定形だけでは抜ける」ことを issue 001 で実測した（`TICK_MS` の再宣言が緑のまま通った）。
printf '%s' "$out" | jq -e '
  [.[].revision | keys_unsorted[]] | unique
  == ["delete_run_max","delete_runs","local_recurrence","loop_depth_max",
      "redelete_count","rewrite_count"]' >/dev/null 2>&1 \
  || fail "revision のキー集合が AC1 の 6 個と完全一致しない（★ 増えても減っても落とす）"

if grep -nE '^[[:space:]]*(pub )?const +[A-Z_]+ *: *(u8|u16|u32|u64|usize|i8|i16|i32|i64|isize|f32|f64) *=' \
     "$SRCF" | grep -vE 'const +TEST_' >/dev/null 2>&1; then
  fail "$SRCF が数値定数を宣言している（★ 既存 SSOT を use する。テスト専用は TEST_ 接頭辞）"
fi
if grep -nE '[<>=!]=?[[:space:]]*(2000|2_000|1000|1_000)\b' "$SRCF" >/dev/null 2>&1; then
  fail "$SRCF が pause / tick の閾値をリテラルで直書き比較している（★ PAUSE_THRESHOLD_MS / ENGINE_TICK_MS を使う）"
fi

echo "[acceptance 004] OK"
