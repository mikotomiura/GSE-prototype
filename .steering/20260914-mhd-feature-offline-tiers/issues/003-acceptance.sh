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

echo "[acceptance 003] OK"
