#!/usr/bin/env bash
# issue 005 (stall onset t0 検出器) の AC 検査
set -uo pipefail
fail() { echo "[acceptance 005] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"
cd src-tauri || fail "src-tauri が無い"
SRC="src/analysis/feat_offline/stall_onset.rs"

out="$(cargo run --quiet --bin gse-replay -- tests/fixtures/deep_silence.ndjson --features 2>/dev/null)" \
  || fail "gse-replay --features が非 0 で終了した"
[ -n "$out" ] || fail "--features の出力が空"

# AC1
printf '%s' "$out" | jq -e '
  all(.[];
    (.stall_onset | type == "object")
    and (.stall_onset | has("is_onset") and has("s_ms") and has("t0_ms")
         and has("theta_person_ms") and has("task_kind") and has("phase")))' >/dev/null 2>&1 \
  || fail "全行に stall_onset の必須フィールドが揃っていない"

# ⚠️ 退化していないこと: deep_silence は長い沈黙を含むので onset が 1 回以上立つはず。
#   ★ 立たないなら「検出器が何も検出しない」= 緑に見えて無意味。
printf '%s' "$out" | jq -e '[.[].stall_onset.is_onset | select(. == true)] | length > 0' >/dev/null 2>&1 \
  || fail "deep_silence.ndjson で onset が 1 度も立たない（★ 検出器が何も検出していない）"

# ⚠️ t0 = s + theta （null でない行について）
printf '%s' "$out" | jq -e '
  all(.[] | .stall_onset;
    (.t0_ms == null or .s_ms == null or .theta_person_ms == null)
    or (.t0_ms == (.s_ms + .theta_person_ms)))' >/dev/null 2>&1 \
  || fail "t0 = s + theta_person が成り立たない行がある（★ ADR-030 D2）"

# AC4: ⚠️★★★ theta に床/天井の clamp が無いこと（ADR-030 D4 逐語「床は置かない。天井も置かない。」）
if grep -nE '(theta|THETA)[A-Za-z_]*[^;]*\.(max|min|clamp)\(' "$SRC" >/dev/null 2>&1; then
  fail "$SRC が theta_person を clamp している（★ ADR-030 D4 は床も天井も置かないと決めている）"
fi

# AC5: ⚠️ net_diff_min を既存の OutcomeConfig から引いていること（★ 新しい定数を作らない）
grep -qE 'net_diff_min' "$SRC" \
  || fail "$SRC が net_diff_min を参照していない（★ ADR-030 D3: 既存 OutcomeConfig の値を使う）"
if grep -nE '^[[:space:]]*(pub )?const [A-Z_]*NET_DIFF[A-Z_]*[[:space:]]*:' "$SRC" >/dev/null 2>&1; then
  fail "$SRC が net_diff_min を新しい定数として宣言している（★ 既存の値を参照すること）"
fi

# ★ pause / net は issue 001 の共有ヘルパを使うこと（⚠️ 局所定義を作らない）
#   ⚠️ Codex TASK-PRE 指摘 5: 局所定義は issue 005 (stall onset) との破壊的な食い違いを生む。
SRCF="src/analysis/feat_offline/stall_onset.rs"
if grep -nE '^[[:space:]]*(pub )?fn [a-z_]*(extract_pauses|compute_net|pause_list)' "$SRCF" >/dev/null 2>&1; then
  fail "$SRCF が pause / net を独自に定義している（★ mod.rs の共有ヘルパを使うこと）"
fi
grep -qE 'super::|crate::analysis::feat_offline::' "$SRCF"   || fail "$SRCF が mod.rs の共有ヘルパを参照していない"

echo "[acceptance 005] OK"
