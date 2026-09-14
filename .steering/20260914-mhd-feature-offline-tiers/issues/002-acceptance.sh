#!/usr/bin/env bash
# issue 002 (T1b 境界) の AC 検査
set -uo pipefail
fail() { echo "[acceptance 002] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"
cd src-tauri || fail "src-tauri が無い"

out="$(cargo run --quiet --bin gse-replay -- tests/fixtures/argumentative_ime_mixed.ndjson --features 2>/dev/null)" \
  || fail "gse-replay --features が非 0 で終了した"
[ -n "$out" ] || fail "--features の出力が空"

# AC1 / AC2: boundary の必須フィールド（★ sentence_punctuation が分離していること）
printf '%s' "$out" | jq -e '
  all(.[];
    (.boundary | type == "object")
    and (.boundary | has("prev_cat_counts") and has("next_cat_counts")
         and has("space") and has("enter") and has("sentence_punctuation")
         and has("ime_dwell_ms") and has("ime_nav") and has("ime_abandon")))' >/dev/null 2>&1 \
  || fail "全行に boundary の必須フィールドが揃っていない"

# ⚠️ sentence_punctuation が punctuation に畳まれていないこと
printf '%s' "$out" | jq -e '
  [.[].boundary.prev_cat_counts | keys[]] | unique
  | (index("sentence_punctuation") != null) or (index("punctuation") != null)' >/dev/null 2>&1 \
  || fail "prev_cat_counts に句読点系のカテゴリが 1 つも現れない（★ 分離を検査できない）"

# AC5: ⚠️ 退化していないこと（IME を含む fixture なので dwell は立つはず）
printf '%s' "$out" | jq -e '[.[].boundary.ime_dwell_ms] | add > 0' >/dev/null 2>&1 \
  || fail "ime_dwell_ms の総和が 0（★ IME を含む fixture なのに出力が退化している）"

# AC6: ⚠️ abandon を「迷い」と解釈する語を置かない（★ 起票 6: ライブ変換 ON で偽陽性が立つ）
if grep -nEi '(迷い|hesitat|ためらい)' src/analysis/feat_offline/boundary.rs >/dev/null 2>&1; then
  fail "boundary.rs が abandon を迷いと解釈している（★ 起票 6 より、行数は変換回数の代理にならない）"
fi

echo "[acceptance 002] OK"
