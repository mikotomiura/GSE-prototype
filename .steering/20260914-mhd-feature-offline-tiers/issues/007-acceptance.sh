#!/usr/bin/env bash
# issue 007 (Q evidence quality) の AC 検査
# ⚠️★★★ ここは data-privacy に触れる。★ 「被験者由来の欠測理由が出ていないこと」を機械で見る。
#
# ⚠️★★★ 2026-09-15 改訂 (decisions.md 判断 11 / 12):
#   ★ verify_level を recheck → parse に落としたぶん、**機械検査をここで厚くする**。
#   ★ fixture を minimal.ndjson → instrument_rich.ndjson へ差し替えた。
#   ★ minimal.ndjson は「**古い形式でも落ちない**」ことの検査 (AC7) に回した。
#
# ⚠️★★★ 2026-09-18 改訂 (decisions.md 判断 21):
#   ★ **旧 AC3 は原理的に通らなかった** —— instrument_rich の meta.capabilities には
#     `"recording_pause"` という**行種名**が入っており（capabilities.rs::unconditional）、
#     AC6 が要求する「capabilities をそのまま出す」と、出力全体への grep が必ず衝突した。
#     → ★ 被験者由来語の grep は **capabilities を除いた出力**に掛ける。
#       capabilities は別途「meta の値と完全一致（加工していない）」で見る。
#   ★ 許可リストを「規範となる定義」の 3 語に絞り、正解表の値を検査する (AC8 / AC9)。
#
# ★ ACC_REPLAY_CMD を与えると gse-replay の代わりにそのコマンドを使う（★ 検査自体の 3 状態テスト用）。
#   ACC_SKIP_SRC=1 でソース検査を省く（同上）。
set -uo pipefail
fail() { echo "[acceptance 007] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"
cd src-tauri || fail "src-tauri が無い"
MODRS="src/analysis/feat_offline/mod.rs"
SRCF="src/analysis/feat_offline/quality.rs"
RICH="tests/fixtures/instrument_rich.ndjson"
OLD="tests/fixtures/minimal.ndjson"
OBS="tests/fixtures/stall_onset_observed.ndjson"

replay() {
  if [ -n "${ACC_REPLAY_CMD:-}" ]; then $ACC_REPLAY_CMD "$@"
  else cargo run --quiet --bin gse-replay -- "$@"; fi
}

[ -f "$RICH" ] || fail "$RICH が無い（★ 裁定セッションが用意した fixture。自分で作らない）"
[ -f "$OBS" ] || fail "$OBS が無い（★ 裁定セッションが用意した fixture。自分で作らない）"
if [ "${ACC_SKIP_SRC:-0}" != "1" ]; then [ -f "$SRCF" ] || fail "$SRCF が無い"; fi
tmpd="$(mktemp -d)"; trap 'rm -rf "$tmpd"' EXIT

ALLOWED='["capability_undeclared","dropped_events","hook_dead"]'
PARTICIPANT_RE='(recording_pause|redaction|redact|participant|subject_|一時停止|区間削除|削除要求)'

# ---------- instrument_rich（AC1 / AC3 / AC6 / AC8） ----------
out="$(replay "$RICH" --features 2>/dev/null)" || fail "gse-replay --features が非 0 で終了した ($RICH)"
[ -n "$out" ] || fail "--features の出力が空"

# AC1
printf '%s' "$out" | jq -e '
  all(.[];
    (.quality | type == "object")
    and (.quality | has("capabilities") and has("hook_health")
         and has("missing_reasons") and has("observability_mask")))' >/dev/null 2>&1 \
  || fail "AC1: 全行に quality の必須フィールドが揃っていない"

# ⚠️★★★ 出力キー集合の**完全一致**（★ privacy の門）。フィールドが 1 つ増えたら**必ず落とす**。
printf '%s' "$out" | jq -e '
  ([.[].quality | keys_unsorted[]] | unique
     == ["capabilities","hook_health","missing_reasons","observability_mask"])
  and ([.[].quality.observability_mask | keys_unsorted[]] | unique == ["feat","hook"])
  and ([.[].quality.hook_health | select(. != null) | keys_unsorted[]] | unique
     == ["alive","dropped_delta","rehook","starved_ms"])' >/dev/null 2>&1 \
  || fail "quality / observability_mask / hook_health のキー集合が規範と完全一致しない（★ 増えても減っても落とす）"

# AC6 ＋ capabilities は meta の値を**加工せずそのまま**全行に載せる
meta_cap="$(jq -c 'select(.type=="meta" and has("capabilities")) | .capabilities' "$RICH" | head -1)"
[ -n "$meta_cap" ] || fail "前提: $RICH の meta に capabilities が無い"
printf '%s' "$out" | jq -e --argjson cap "$meta_cap" 'all(.[]; .quality.capabilities == $cap)' >/dev/null 2>&1 \
  || fail "AC6: capabilities が meta の値と完全一致しない行がある（★ 加工・並べ替え・欠落をしない）"

# AC3: ⚠️★★★ 被験者由来の欠測理由が 1 つも出ていないこと（★ capabilities を除いた出力全体を見る）
if printf '%s' "$out" | jq -c 'map(.quality |= del(.capabilities))' | grep -nEi "$PARTICIPANT_RE" >/dev/null 2>&1; then
  fail "AC3: 出力に被験者由来の欠測理由が現れている（★ ADR-030 D10 / docs/o1-deletion-ledger.md）"
fi

# AC2: 許可リスト方式
printf '%s' "$out" | jq -e --argjson ok "$ALLOWED" '
  ([.[].quality.missing_reasons[]] | unique) - $ok | length == 0' >/dev/null 2>&1 \
  || fail "AC2: missing_reasons に許可リスト $ALLOWED の外の値がある"

# AC8: 正解表（instrument_rich・原点 T+200・T = 1700000100000）
printf '%s' "$out" | jq -e '
  (length == 15)
  and ([to_entries[] | select(.value.quality.hook_health != null) | .key] == [5, 13])
  and (.[5].quality.hook_health == {"alive":true,"starved_ms":0,"rehook":false,"dropped_delta":0})
  and (.[13].quality.hook_health == {"alive":true,"starved_ms":7200,"rehook":false,"dropped_delta":2})
  and ([to_entries[] | select(.value.quality.missing_reasons != []) | [.key, .value.quality.missing_reasons]]
       == [[13, ["dropped_events"]]])
  and ([.[].quality.observability_mask.hook] == ([range(5)] | map(null)) + ([range(10)] | map(true)))
  and all(.[]; .quality.observability_mask.feat == false)' >/dev/null 2>&1 \
  || fail "AC8: instrument_rich の quality が正解表と一致しない（★ issues/007.md の規範となる定義を参照）。実際: $(printf '%s' "$out" | jq -c '[.[] | .quality | [.hook_health, .missing_reasons, .observability_mask]]' 2>/dev/null | head -c 1500)"

# ---------- minimal（AC7 / AC8） ----------
old_out="$(replay "$OLD" --features 2>/dev/null)" \
  || fail "AC7: gse-replay --features が非 0 で終了した ($OLD・★ 古い形式で落ちてはならない)"
[ -n "$old_out" ] || fail "--features の出力が空 ($OLD)"
printf '%s' "$old_out" | jq -e '
  all(.[]; .quality.capabilities == null and .quality.hook_health == null
           and .quality.missing_reasons == ["capability_undeclared"]
           and .quality.observability_mask == {"feat":false,"hook":null})' >/dev/null 2>&1 \
  || fail "AC7/AC8: minimal.ndjson の quality が正解表と一致しない（★ capabilities は null・理由は capability_undeclared だけ）"
if printf '%s' "$old_out" | grep -nEi "$PARTICIPANT_RE" >/dev/null 2>&1; then
  fail "AC3: 古い形式の出力に被験者由来の理由が現れている"
fi

# ---------- stall_onset_observed とその削除版（AC8 / AC9） ----------
obs_out="$(replay "$OBS" --features 2>/dev/null)" || fail "gse-replay --features が非 0 で終了した ($OBS)"
printf '%s' "$obs_out" | jq -e 'length == 220 and all(.[]; .quality.observability_mask.feat == true)' >/dev/null 2>&1 \
  || fail "AC8: stall_onset_observed で mask.feat が全行 true でない（★ feat 行は途切れていない）"

T=1700000000000
jq -c --argjson lo "$((T + 100000))" --argjson hi "$((T + 140000))" '
  select(((.t // .ts // 0) < $lo) or ((.t // .ts // 0) > $hi))' "$OBS" > "$tmpd/redacted.ndjson" \
  || fail "削除版の生成に失敗"
red_out="$(replay "$tmpd/redacted.ndjson" --features 2>/dev/null)" || fail "削除版で --features が非 0 で終了した"
printf '%s' "$red_out" | jq -e '
  [to_entries[] | select(.value.quality.observability_mask.feat == false) | .key] == [range(99; 140)]' >/dev/null 2>&1 \
  || fail "AC9: 削除版で mask.feat = false が tick 99〜139 だけに立っていない。実際: $(printf '%s' "$red_out" | jq -c '[to_entries[] | select(.value.quality.observability_mask.feat == false) | .key] | [first, last, length]' 2>/dev/null)"
printf '%s' "$red_out" | jq -e 'all(.[]; .quality.missing_reasons == ["capability_undeclared"])' >/dev/null 2>&1 \
  || fail "AC9: ⚠️★★★ 削除版で穴に理由が付いている（★ 穴は mask.feat=false とだけ書く。理由を付けない）"
if printf '%s' "$red_out" | jq -c 'map(.quality |= del(.capabilities))' | grep -nEi "$PARTICIPANT_RE" >/dev/null 2>&1; then
  fail "AC3: 削除版の出力に被験者由来の語が現れている"
fi

# ---------- ソース検査（AC5 / AC11 / 計器変更の禁止 / test の実在） ----------
if [ "${ACC_SKIP_SRC:-0}" != "1" ]; then
  # AC5: ⚠️ quality を他 Tier の入力に渡していないこと（★ 状態特徴にしない）
  if grep -nE '(activity|boundary|dispersion|revision|restart|stall_onset)::[a-z_]+\([^)]*quality' \
       "$MODRS" >/dev/null 2>&1; then
    fail "AC5: $MODRS が quality を他 Tier の計算へ渡している（★ Q は状態特徴ではない・survey:194）"
  fi
  # AC11: mask.feat は 008 の observed_intervals を使う（★ 独自の穴判定を作らない）
  grep -qE 'observed_intervals' "$SRCF" "$MODRS" \
    || fail "AC11: quality が stall_onset::observed_intervals を使っていない（★ 独自に穴を判定しない）"
  if grep -nE 'fn [a-z_]*(hole|gap|interval)[a-z_]*\(' "$SRCF" | grep -vE '^[0-9]+:[[:space:]]*//' | grep -q .; then
    fail "AC11: $SRCF が穴 / 区間の判定関数を独自に定義している（★ observed_intervals を使う）"
  fi
  # ★ AC の test が実在すること
  for t in missing_reasons_are_instrument_side_only participant_originated_reasons_are_never_emitted \
           missing_is_null_not_zero absent_capabilities_is_null_not_empty \
           feat_hole_is_masked_without_a_reason hook_state_carries_forward_until_next_row; do
    grep -qE "fn ${t}\b" "$SRCF" || fail "AC の test \`$t\` が $SRCF に無い"
  done
  grep -qE 'fn malformed_hook_health_line_does_not_break_run_replay\b' src/bin/replay.rs \
    || fail "AC12 の test \`malformed_hook_health_line_does_not_break_run_replay\` が bin/replay.rs に無い"

  # ★ 計器変更をしていないこと（⚠️ Scope Out）
  #   ⚠️★★★ `git diff HEAD` で見ない —— worker は commit するので、**コミット済みの計器変更を見逃す**。
  #   ★ base ブランチとの差分を見る。⚠️ ref が解決できないときは **fail-closed**（沈黙して通さない）。
  BASE_REF="docs/adr-030-stall-onset-definition"
  git rev-parse --verify --quiet "$BASE_REF" >/dev/null 2>&1 \
    || fail "base ref $BASE_REF が解決できず、計器変更の有無を検査できない（★ 検査できないものを緑にしない）"
  if ! git diff --quiet "$BASE_REF" -- src/capabilities.rs src/schema_dto.rs src/logger.rs; then
    fail "capabilities.rs / schema_dto.rs / logger.rs を変更している（★ 計器変更は Scope Out）"
  fi
  # ★ stall_onset.rs は observed_intervals の可視性 1 語だけ（★ 本体を変えない）
  sdiff="$(git diff "$BASE_REF" -- src/analysis/feat_offline/stall_onset.rs | grep -E '^[+-][^+-]' || true)"
  if [ -n "$sdiff" ] && [ "$(printf '%s\n' "$sdiff" | grep -cvE 'fn observed_intervals\(')" != "0" ]; then
    fail "stall_onset.rs を observed_intervals の可視性以外で変更している（★ 1 語だけ）"
  fi
fi

echo "[acceptance 007] OK"
