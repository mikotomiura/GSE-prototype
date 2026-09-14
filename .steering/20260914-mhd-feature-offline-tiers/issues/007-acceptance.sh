#!/usr/bin/env bash
# issue 007 (Q evidence quality) の AC 検査
# ⚠️★★★ ここは data-privacy に触れる。★ 「被験者由来の欠測理由が出ていないこと」を機械で見る。
set -uo pipefail
fail() { echo "[acceptance 007] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"
cd src-tauri || fail "src-tauri が無い"
MODRS="src/analysis/feat_offline/mod.rs"

out="$(cargo run --quiet --bin gse-replay -- tests/fixtures/minimal.ndjson --features 2>/dev/null)" \
  || fail "gse-replay --features が非 0 で終了した"
[ -n "$out" ] || fail "--features の出力が空"

printf '%s' "$out" | jq -e '
  all(.[];
    (.quality | type == "object")
    and (.quality | has("capabilities") and has("hook_health")
         and has("missing_reasons") and has("observability_mask")))' >/dev/null 2>&1 \
  || fail "全行に quality の必須フィールドが揃っていない"

# AC3: ⚠️★★★ 被験者由来の欠測理由が 1 つも出ていないこと（★ 出力全体を見る）
if printf '%s' "$out" | grep -nEi '(recording_pause|redaction|participant_(pause|delete)|一時停止|区間削除)' >/dev/null 2>&1; then
  fail "出力に被験者由来の欠測理由が現れている（★ ADR-030 D10 / docs/o1-deletion-ledger.md）"
fi

# AC6: ⚠️ 退化していないこと
printf '%s' "$out" | jq -e '[.[].quality.capabilities | select(. != null)] | length > 0' >/dev/null 2>&1 \
  || fail "capabilities が全行 null（★ minimal.ndjson は meta 行を持つ）"

# AC5: ⚠️ quality を他 Tier の入力に渡していないこと（★ 状態特徴にしない）
if grep -nE '(activity|boundary|dispersion|revision|restart|stall_onset)::[a-z_]+\([^)]*quality' \
     "$MODRS" >/dev/null 2>&1; then
  fail "$MODRS が quality を他 Tier の計算へ渡している（★ Q は状態特徴ではない・survey:194）"
fi

echo "[acceptance 007] OK"
