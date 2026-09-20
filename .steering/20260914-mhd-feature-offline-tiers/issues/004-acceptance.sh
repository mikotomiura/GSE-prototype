#!/usr/bin/env bash
# issue 004 (T1c revision topology) の AC 検査
# ⚠️★★★ 2026-09-20（封筒・起票 2）: `--features` の出力は
#   **`{ provenance, config, rows }` の封筒**になった（判断 25 #14）。
#   ★ 本検査は取得時に `jq '.rows'` で**行だけを取り出して**おり、
#     以降の `.[]` / `all(.[]; ...)` は封筒を剥がした後の配列を指す。
#   ⚠️★★★ **この検査は `provenance` と `config` を 1 つも見ていない。**
#     ★ 封筒自体の検査は `.steering/20260920-envelope-issues/envelope-acceptance.sh` が持つ。
#   ★ 封筒が無い（配列のままの）出力では `jq '.rows'` が失敗し、
#     `set -o pipefail` によりその場で赤になる（fail-closed）。
set -uo pipefail
fail() { echo "[acceptance 004] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"
cd src-tauri || fail "src-tauri が無い"

# ⚠️★★★ 2026-09-15: fixture を minimal.ndjson → instrument_rich.ndjson へ差し替えた
#   （★ decisions.md 判断 13）。★ 理由: **minimal.ndjson の backspace press は 1 個しかない**ので、
#   「delete run は連続 2 打以上」と定義した実装では `delete_runs` が 0 になり、
#   ⚠️ **欠陥でないのに acceptance が落ちる**（★ issue 002 で実際に $5.7 を捨てた失敗様式）。
#   ★ instrument_rich は **backspace 3 連**を持つので、どちらの定義でも run が 1 本以上立つ。
out="$(cargo run --quiet --bin gse-replay -- tests/fixtures/instrument_rich.ndjson --features 2>/dev/null | jq -e '.rows | arrays')" \
  || fail "gse-replay --features が非 0 で終了した、または封筒の .rows を取り出せない（★ { provenance, config, rows } の形か確認）"
[ -n "$out" ] || fail "--features の出力が空"

printf '%s' "$out" | jq -e '
  all(.[];
    (.revision | type == "object")
    and (.revision | has("delete_run_max") and has("delete_runs") and has("del_to_ins_transitions")
         and has("delete_runs_after_first_in_burst") and has("di_alternations_max")
         and has("category_bigram_repeat_rate")))' >/dev/null 2>&1 \
  || fail "全行に revision の必須フィールドが揃っていない"

printf '%s' "$out" | jq -e '[.[].revision.delete_runs] | add > 0' >/dev/null 2>&1 \
  || fail "delete_runs の総和が 0（★ instrument_rich は backspace 3 連を持つ。出力が退化している）"
# ★ 3 連の走りが「走り」として見えていること（⚠️ 1 打ずつ数えていたら max は 1 になる）
printf '%s' "$out" | jq -e '[.[].revision.delete_run_max] | max >= 3' >/dev/null 2>&1 \
  || fail "delete_run_max が 3 未満（★ fixture は backspace を 3 連続で持つ。走りの長さを数えていない疑い）"

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
# ⚠️★★★ 2026-09-19 改訂（decisions.md 判断 26 / theory-critical-review 判断 2 #5）——
#   ★ 観測の名前へ改名した。旧名 rewrite_count / redelete_count / loop_depth_max / local_recurrence で
#   実装すると、このキー集合の完全一致で落ちる。
printf '%s' "$out" | jq -e '
  [.[].revision | keys_unsorted[]] | unique
  == ["category_bigram_repeat_rate","del_to_ins_transitions","delete_run_max","delete_runs",
      "delete_runs_after_first_in_burst","di_alternations_max"]' >/dev/null 2>&1 \
  || fail "revision のキー集合が AC1 の 6 個と完全一致しない（★ 増えても減っても落とす）"

if grep -nE '^[[:space:]]*(pub )?const +[A-Z_]+ *: *(u8|u16|u32|u64|usize|i8|i16|i32|i64|isize|f32|f64) *=' \
     "$SRCF" | grep -vE '^[0-9]+:[[:space:]]*//' | grep -vE 'const +TEST_' >/dev/null 2>&1; then
  fail "$SRCF が数値定数を宣言している（★ 既存 SSOT を use する。テスト専用は TEST_ 接頭辞）"
fi
if grep -nE '[<>=!]=?[[:space:]]*(2000|2_000|1000|1_000)\b' "$SRCF" \
     | grep -vE '^[0-9]+:[[:space:]]*//' >/dev/null 2>&1; then
  fail "$SRCF が pause / tick の閾値をリテラルで直書き比較している（★ PAUSE_THRESHOLD_MS / ENGINE_TICK_MS を使う）"
fi

echo "[acceptance 004] OK"
