#!/usr/bin/env bash
# issue 006 (T1d restart) の AC 検査
set -uo pipefail
fail() { echo "[acceptance 006] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"
cd src-tauri || fail "src-tauri が無い"
SRC="src/analysis/feat_offline/restart.rs"

out="$(cargo run --quiet --bin gse-replay -- tests/fixtures/deep_silence.ndjson --features 2>/dev/null)" \
  || fail "gse-replay --features が非 0 で終了した"
[ -n "$out" ] || fail "--features の出力が空"

printf '%s' "$out" | jq -e '
  all(.[];
    (.restart | type == "object")
    and (.restart | has("post_t0_inserts") and has("post_t0_deletes") and has("post_t0_navigations")
         and has("restop_ms") and has("stable_generation_ms")))' >/dev/null 2>&1 \
  || fail "全行に restart の必須フィールドが揃っていない"

# AC3: ⚠️ onset が立っていない行は null（★ 0 で埋めない）
printf '%s' "$out" | jq -e '
  all(.[] | select(.stall_onset.t0_ms == null) | .restart;
    (.post_t0_inserts == null and .post_t0_deletes == null
     and .post_t0_navigations == null and .restop_ms == null
     and .stable_generation_ms == null))' >/dev/null 2>&1 \
  || fail "t0 が無い行で restart が 0 埋めされている（★ null にすること）"

# AC6: ⚠️ 退化していないこと
printf '%s' "$out" | jq -e '[.[].restart.restop_ms | select(. != null)] | length > 0' >/dev/null 2>&1 \
  || fail "restop_ms が全行 null（★ deep_silence では onset 後の再停止が測れるはず）"

# AC4: buffer B を stall_onset 側から引いていること
grep -qE 'buffer|_b_ms|StallOnsetConfig|stall_onset::' "$SRC" \
  || fail "$SRC が stall_onset 側の設定 (buffer B) を参照していない"

# AC5: ⚠️ 禁止用語（★ glossary: 限定資源モデルの語彙）
if grep -nEi '(recovery|recover|回復)' "$SRC" >/dev/null 2>&1; then
  fail "$SRC に recovery / 回復 がある（★ docs/glossary.md の禁止用語。stable_generation_ms で表す）"
fi

echo "[acceptance 006] OK"
