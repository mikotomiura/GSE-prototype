#!/usr/bin/env bash
# issue 003 (T1a 分布・個人相対) の AC 検査
set -uo pipefail
fail() { echo "[acceptance 003] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"
cd src-tauri || fail "src-tauri が無い"

out="$(cargo run --quiet --bin gse-replay -- tests/fixtures/deep_silence.ndjson --features 2>/dev/null)" \
  || fail "gse-replay --features が非 0 で終了した"
[ -n "$out" ] || fail "--features の出力が空"

# AC1
printf '%s' "$out" | jq -e '
  all(.[];
    (.dispersion | type == "object")
    and (.dispersion | has("pause_p50_ms") and has("pause_p90_ms") and has("pause_max_ms")
         and has("iki_cv") and has("surprise")))' >/dev/null 2>&1 \
  || fail "全行に dispersion の必須フィールドが揃っていない"

# AC3: 不変式 p50 <= p90 <= max（⚠️ null は検査対象外 = 0 埋めしていない行）
printf '%s' "$out" | jq -e '
  all(.[] | .dispersion;
    (.pause_p50_ms == null or .pause_p90_ms == null or .pause_max_ms == null)
    or (.pause_p50_ms <= .pause_p90_ms and .pause_p90_ms <= .pause_max_ms))' >/dev/null 2>&1 \
  || fail "p50 <= p90 <= max が成り立たない行がある"

# AC7: ⚠️ 退化していないこと（deep_silence は長い沈黙を含む fixture）
printf '%s' "$out" | jq -e '[.[].dispersion.pause_max_ms | select(. != null)] | (length > 0) and (max > 0)' >/dev/null 2>&1 \
  || fail "pause_max_ms が全行 null か 0（★ 沈黙を含む fixture なのに出力が退化している）"

# AC6: ⚠️ 帯域分割を入れていないこと（★ [P121] が否定した形）
if grep -nEi '(band|bucket|short_pause|medium_pause|long_pause|帯域)' \
     src/analysis/feat_offline/dispersion.rs >/dev/null 2>&1; then
  fail "dispersion.rs に帯域分割がある（★ [P121] は 4 帯域すべてが成績と負相関と示した）"
fi

# ★ pause / net は issue 001 の共有ヘルパを使うこと（⚠️ 局所定義を作らない）
#   ⚠️ Codex TASK-PRE 指摘 5: 局所定義は issue 005 (stall onset) との破壊的な食い違いを生む。
SRCF="src/analysis/feat_offline/dispersion.rs"
if grep -nE '^[[:space:]]*(pub )?fn [a-z_]*(extract_pauses|compute_net|pause_list)' "$SRCF" >/dev/null 2>&1; then
  fail "$SRCF が pause / net を独自に定義している（★ mod.rs の共有ヘルパを使うこと）"
fi
grep -qE 'super::|crate::analysis::feat_offline::' "$SRCF"   || fail "$SRCF が mod.rs の共有ヘルパを参照していない"

# ⚠️★★★ 2026-09-15 追加（★ 引き継ぎ §4 の型 / decisions.md 判断 8）——
#   ★ 「否定形だけでは抜ける」ことを issue 001 で実測した（`TICK_MS` の再宣言が緑のまま通った）。
#   ⚠️ 出力キー集合の**完全一致**。フィールドを足したくなったら AC1 と本検査を先に直すこと。
printf '%s' "$out" | jq -e '
  [.[].dispersion | keys_unsorted[]] | unique
  == ["iki_cv","pause_max_ms","pause_p50_ms","pause_p90_ms","surprise"]' >/dev/null 2>&1 \
  || fail "dispersion のキー集合が AC1 の 5 個と完全一致しない（★ 増えても減っても落とす）"

# ⚠️ 新しい数値定数を宣言しない（ADR-030 D3 逐語「新しい定数を作らず、既存パラメータを対称に再利用する」）
if grep -nE '^[[:space:]]*(pub )?const +[A-Z_]+ *: *(u8|u16|u32|u64|usize|i8|i16|i32|i64|isize|f32|f64) *=' \
     "$SRCF" | grep -vE 'const +TEST_' >/dev/null 2>&1; then
  fail "$SRCF が数値定数を宣言している（★ 既存 SSOT を use する。テスト専用は TEST_ 接頭辞）"
fi
# ⚠️ 直書き禁止: pause / tick の閾値をリテラルで比較しない
if grep -nE '[<>=!]=?[[:space:]]*(2000|2_000|1000|1_000)\b' "$SRCF" >/dev/null 2>&1; then
  fail "$SRCF が pause / tick の閾値をリテラルで直書き比較している（★ PAUSE_THRESHOLD_MS / ENGINE_TICK_MS を使う）"
fi

echo "[acceptance 003] OK"
