#!/usr/bin/env bash
# issue 007 (Q evidence quality) の AC 検査
# ⚠️★★★ ここは data-privacy に触れる。★ 「被験者由来の欠測理由が出ていないこと」を機械で見る。
#
# ⚠️★★★ 2026-09-15 改訂 (decisions.md 判断 11 / 12):
#   ★ verify_level を recheck → parse に落としたぶん、**機械検査をここで厚くする**。
#   ★ fixture を minimal.ndjson → instrument_rich.ndjson へ差し替えた。
#     理由: **minimal.ndjson の meta 行には capabilities が無く**、hook_health 行を持つ
#     fixture も存在しなかったので、旧 AC6 は原理的に充たせなかった。
#   ★ minimal.ndjson は「**古い形式でも落ちない**」ことの検査 (AC7) に回した。
set -uo pipefail
fail() { echo "[acceptance 007] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"
cd src-tauri || fail "src-tauri が無い"
MODRS="src/analysis/feat_offline/mod.rs"
SRCF="src/analysis/feat_offline/quality.rs"
RICH="tests/fixtures/instrument_rich.ndjson"
OLD="tests/fixtures/minimal.ndjson"

[ -f "$RICH" ] || fail "$RICH が無い（★ 裁定セッションが用意した fixture。自分で作らない）"
[ -f "$SRCF" ] || fail "$SRCF が無い"

out="$(cargo run --quiet --bin gse-replay -- "$RICH" --features 2>/dev/null)" \
  || fail "gse-replay --features が非 0 で終了した ($RICH)"
[ -n "$out" ] || fail "--features の出力が空"

# AC1
printf '%s' "$out" | jq -e '
  all(.[];
    (.quality | type == "object")
    and (.quality | has("capabilities") and has("hook_health")
         and has("missing_reasons") and has("observability_mask")))' >/dev/null 2>&1 \
  || fail "全行に quality の必須フィールドが揃っていない"

# ⚠️★★★ 出力キー集合の**完全一致**。
#   ★ ここが privacy の門である。フィールドが 1 つ増えたら**必ず落とす**。
#   ⚠️ 増やしたくなったら、この検査を先に直し、security-checker を通してからにすること。
printf '%s' "$out" | jq -e '
  [.[].quality | keys_unsorted[]] | unique
  == ["capabilities","hook_health","missing_reasons","observability_mask"]' >/dev/null 2>&1 \
  || fail "quality のキー集合が AC1 の 4 個と完全一致しない（★ 増えても減っても落とす）"

# AC2 / AC3: ⚠️★★★ 被験者由来の欠測理由が 1 つも出ていないこと（★ 出力全体を見る）
if printf '%s' "$out" | grep -nEi '(recording_pause|redaction|redact|participant|subject_|一時停止|区間削除|削除要求)' >/dev/null 2>&1; then
  fail "出力に被験者由来の欠測理由が現れている（★ ADR-030 D10 / docs/o1-deletion-ledger.md）"
fi
# ★ 許可リスト方式であること (AC2): missing_reasons の値が計器側の語彙に閉じている。
printf '%s' "$out" | jq -e --argjson ok '
  ["capability_undeclared","capability_not_declared","hook_starved","hook_dead",
   "dropped_events","no_instrument","unknown_capabilities","instrument_absent",
   "threshold_not_reached","not_logged"]' '
  ([.[].quality.missing_reasons // [] | .[]] | unique) - $ok | length == 0' >/dev/null 2>&1 \
  || fail "missing_reasons に計器側の許可リスト外の値がある（★ 値を足すなら本検査と AC2 を先に直す）"

# AC6: ⚠️ 退化していないこと（★ instrument_rich は capabilities 入り meta ＋ hook_health 2 行を持つ）
printf '%s' "$out" | jq -e '[.[].quality.capabilities | select(. != null)] | length > 0' >/dev/null 2>&1 \
  || fail "capabilities が全行 null（★ instrument_rich.ndjson の meta は capabilities を持つ）"
printf '%s' "$out" | jq -e '[.[].quality.hook_health | select(. != null)] | length > 0' >/dev/null 2>&1 \
  || fail "hook_health が全行 null（★ instrument_rich.ndjson は hook_health を 2 行持つ）"

# AC4: ⚠️ 欠測が 0 で埋められていないこと。
#   ★ hook_health は 2 行しか無いので、**非 null の行と null の行が両方ある**のが正しい形。
printf '%s' "$out" | jq -e '[.[].quality.hook_health | select(. == null)] | length > 0' >/dev/null 2>&1 \
  || fail "hook_health が全行で非 null（★ 行が無い tick は null。0 や既定値で埋めない）"

# AC7: ⚠️★★★ capabilities を持たない**古い形式のログ**でも落ちないこと。
#   ★ minimal.ndjson の meta は session_start / hmm_version だけ（ADR-013 D1 より前）。
old_out="$(cargo run --quiet --bin gse-replay -- "$OLD" --features 2>/dev/null)" \
  || fail "gse-replay --features が非 0 で終了した ($OLD・★ 古い形式で落ちてはならない)"
[ -n "$old_out" ] || fail "--features の出力が空 ($OLD)"
printf '%s' "$old_out" | jq -e 'all(.[]; .quality.capabilities == null)' >/dev/null 2>&1 \
  || fail "capabilities を持たないログで capabilities が null でない（★ 空配列で埋めない。『宣言が無い』と『何も宣言していない』は別）"
if printf '%s' "$old_out" | grep -nEi '(recording_pause|redaction|participant|一時停止|区間削除)' >/dev/null 2>&1; then
  fail "古い形式の出力に被験者由来の理由が現れている"
fi

# AC5: ⚠️ quality を他 Tier の入力に渡していないこと（★ 状態特徴にしない）
if grep -nE '(activity|boundary|dispersion|revision|restart|stall_onset)::[a-z_]+\([^)]*quality' \
     "$MODRS" >/dev/null 2>&1; then
  fail "$MODRS が quality を他 Tier の計算へ渡している（★ Q は状態特徴ではない・survey:194）"
fi

# ★ 計器変更をしていないこと（⚠️ Scope Out）
#   ⚠️★★★ `git diff HEAD` で見ない —— worker は commit するので、**コミット済みの計器変更を見逃す**。
#   ★ base ブランチとの差分を見る。⚠️ ref が解決できないときは **fail-closed**（沈黙して通さない）。
BASE_REF="docs/adr-030-stall-onset-definition"
git rev-parse --verify --quiet "$BASE_REF" >/dev/null 2>&1 \
  || fail "base ref $BASE_REF が解決できず、計器変更の有無を検査できない（★ 検査できないものを緑にしない）"
if ! git diff --quiet "$BASE_REF" -- src/capabilities.rs src/schema_dto.rs src/logger.rs; then
  fail "capabilities.rs / schema_dto.rs / logger.rs を変更している（★ 計器変更は Scope Out）"
fi

echo "[acceptance 007] OK"
