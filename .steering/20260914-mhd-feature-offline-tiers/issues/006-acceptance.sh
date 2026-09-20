#!/usr/bin/env bash
# issue 006 (T1d restart) の AC 検査
# ⚠️★★★ 2026-09-20（封筒・起票 2）: `--features` の出力は
#   **`{ provenance, config, rows }` の封筒**になった（判断 25 #14）。
#   ★ 本検査は取得時に `jq '.rows'` で**行だけを取り出して**おり、
#     以降の `.[]` / `all(.[]; ...)` は封筒を剥がした後の配列を指す。
#   ⚠️★★★ **この検査は `provenance` と `config` を 1 つも見ていない。**
#     ★ 封筒自体の検査は `.steering/20260920-envelope-issues/envelope-acceptance.sh` が持つ。
#   ★ 封筒が無い（配列のままの）出力では `jq '.rows'` が失敗し、
#     `set -o pipefail` によりその場で赤になる（fail-closed）。
set -uo pipefail
fail() { echo "[acceptance 006] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"
cd src-tauri || fail "src-tauri が無い"
SRC="src/analysis/feat_offline/restart.rs"

# ⚠️★★★ 2026-09-20（`.steering/20260920-issues-004-006/decisions.md` 判断 2・**V3 の裁定**）:
#   fixture を deep_silence.ndjson → stall_onset_observed.ndjson へ差し替えた。
#   ★ 理由: deep_silence.ndjson は **feat 行を持たない**ので観測区間が無く、issue 008 以後
#     onset が 1 つも立たない（blockers.md 起票 17）。→ AC6 が原理的に通らなかった。
#   ★ stall_onset_observed.ndjson は実測で onset が 2 本立つ（t0 = +40160 / +187600）。
out="$(cargo run --quiet --bin gse-replay -- tests/fixtures/stall_onset_observed.ndjson --features 2>/dev/null | jq -e '.rows | arrays')" \
  || fail "gse-replay --features が非 0 で終了した、または封筒の .rows を取り出せない（★ { provenance, config, rows } の形か確認）"
[ -n "$out" ] || fail "--features の出力が空"

printf '%s' "$out" | jq -e '
  all(.[];
    (.restart | type == "object")
    and (.restart | has("post_t0_inserts") and has("post_t0_deletes") and has("post_t0_navigations")
         and has("restop_ms") and has("stable_generation_ms")
         and has("stable_generation_net_presses") and has("resumption_count")))' >/dev/null 2>&1 \
  || fail "全行に restart の必須フィールドが揃っていない"

# AC3: ⚠️ onset が立っていない行は null（★ 0 で埋めない）
printf '%s' "$out" | jq -e '
  all(.[] | select(.stall_onset.t0_ms == null) | .restart;
    (.post_t0_inserts == null and .post_t0_deletes == null
     and .post_t0_navigations == null and .restop_ms == null
     and .stable_generation_ms == null
     and .stable_generation_net_presses == null and .resumption_count == null))' >/dev/null 2>&1 \
  || fail "t0 が無い行で restart が 0 埋めされている（★ null にすること）"

# AC6: ⚠️ 退化していないこと
#   ★ 2026-09-20（判断 2 の V3 / 判断 3 の V6）: fixture の差し替えで**この検査は通るようになった**。
#   ⚠️★★★ V6（原点 o で条件 A が既に false なら生成区間は o で開いている）を採らないと、
#     このデータでは 2 本の onset の**どちらも restop_ms が null** になり AC6 は通らない。
#     → ★ この行は V6 の裁定そのものを守っている（⚠️ 「辺だけ」の読みへ戻すと赤くなる）。
printf '%s' "$out" | jq -e '[.[].restart.restop_ms | select(. != null)] | length > 0' >/dev/null 2>&1 \
  || fail "restop_ms が全行 null（★ onset 後の再停止が 1 つも測れていない。⚠️ V6 の裁定＝原点で条件 A が既に false なら r_1 を o にクリップする、を外していないか確認）"

# AC4: buffer B を stall_onset 側から引いていること
grep -qE 'buffer|_b_ms|StallOnsetConfig|stall_onset::' "$SRC" \
  || fail "$SRC が stall_onset 側の設定 (buffer B) を参照していない"

# AC5: ⚠️ 禁止用語（★ glossary: 限定資源モデルの語彙）
if grep -nEi '(recovery|recover|回復)' "$SRC" >/dev/null 2>&1; then
  fail "$SRC に recovery / 回復 がある（★ docs/glossary.md の禁止用語。stable_generation_ms で表す）"
fi

# ★ pause / net は issue 001 の共有ヘルパを使うこと（⚠️ 局所定義を作らない）
#   ⚠️ Codex TASK-PRE 指摘 5: 局所定義は issue 005 (stall onset) との破壊的な食い違いを生む。
SRCF="src/analysis/feat_offline/restart.rs"
if grep -nE '^[[:space:]]*(pub )?fn [a-z_]*(extract_pauses|compute_net|pause_list)' "$SRCF" >/dev/null 2>&1; then
  fail "$SRCF が pause / net を独自に定義している（★ mod.rs の共有ヘルパを使うこと）"
fi
grep -qE 'super::|crate::analysis::feat_offline::' "$SRCF"   || fail "$SRCF が mod.rs の共有ヘルパを参照していない"

# AC7: ⚠️★★★ restart は retrospective であり、detection 側へ渡らないこと
MODRS="src/analysis/feat_offline/mod.rs"
# ⚠️★★★ 2026-09-20 修正（判断 5）: 旧版はパターンの中に**リテラル改行**を含んでいた
#   （`restart[^<改行>]*retrospective|...`）。★ grep は PATTERN 引数を改行で分割して
#   **複数パターンとして扱う**ので、`restart[^` 等の未閉じブラケットになり
#   `grep: Invalid regular expression` で**必ず失敗していた**（⚠️ 実測。判断 26 の
#   「受け入れスクリプトは未検証」がここで顕在化した）。
#   ★ grep は行単位で走るので `.` で十分である（`.` は改行に一致しない）。
grep -qEi 'restart.*retrospective|retrospective.*restart' "$MODRS" \
  || fail "$MODRS に restart が retrospective である旨の明記が無い"
if grep -nE '(activity|stall_onset)::[a-z_]+\([^)]*restart' "$MODRS" >/dev/null 2>&1; then
  fail "$MODRS が restart を detection 側へ渡している（★ 転帰側を検出側に混ぜない）"
fi

# ⚠️★★★ 2026-09-15 追加（★ 引き継ぎ §4 の型 / decisions.md 判断 8）
# ⚠️★★★ 2026-09-19 改訂（decisions.md 判断 26 / theory-critical-review 判断 2 #7 / #8）——
#   ★ stable_generation_net_presses（速度との交絡の手当て）と resumption_count（E1 の過剰結合を見せる）を追加した。
printf '%s' "$out" | jq -e '
  [.[].restart | keys_unsorted[]] | unique
  == ["post_t0_deletes","post_t0_inserts","post_t0_navigations",
      "restop_ms","resumption_count","stable_generation_ms","stable_generation_net_presses"]' >/dev/null 2>&1 \
  || fail "restart のキー集合が AC1 の 7 個と完全一致しない（★ 増えても減っても落とす）"

if grep -nE '^[[:space:]]*(pub )?const +[A-Z_]+ *: *(u8|u16|u32|u64|usize|i8|i16|i32|i64|isize|f32|f64) *=' \
     "$SRC" | grep -vE '^[0-9]+:[[:space:]]*//' | grep -vE 'const +TEST_' >/dev/null 2>&1; then
  fail "$SRC が数値定数を宣言している（★ buffer B は stall_onset 側の設定から引く。テスト専用は TEST_ 接頭辞）"
fi
if grep -nE '[<>=!]=?[[:space:]]*(2000|2_000|1000|1_000)\b' "$SRC" \
     | grep -vE '^[0-9]+:[[:space:]]*//' >/dev/null 2>&1; then
  fail "$SRC が pause / tick の閾値をリテラルで直書き比較している（★ PAUSE_THRESHOLD_MS / ENGINE_TICK_MS を使う）"
fi

echo "[acceptance 006] OK"
