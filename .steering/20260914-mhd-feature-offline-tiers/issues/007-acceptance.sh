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
# ⚠️★★★ 2026-09-20（封筒・起票 2）: `--features` の出力は
#   **`{ provenance, config, rows }` の封筒**になった（判断 25 #14）。
#   ★ 本検査は `capture` で封筒ごと (`ENV_JSON`) と行だけ (`ROWS_JSON`) の両方を取り、
#     以降の `.[]` / `all(.[]; ...)` は封筒を剥がした後の配列を指す。
#   ⚠️★★★ **この検査が封筒に対して見るのは AC3b（被験者由来語）と AC6 / AC7
#     （capabilities）だけ**である。★ 封筒の形・`config` の値・byte-equal 性は
#     `.steering/20260920-envelope-issues/envelope-acceptance.sh` が持つ。
#   ★ 封筒が無い（配列のままの）出力では `jq '.rows'` が失敗し、
#     `set -o pipefail` によりその場で赤になる（fail-closed）。
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

# ⚠️★★★ 2026-09-20（封筒・起票 2）: `--features` の出力は
#   **`{ provenance, config, rows }`** になった。★ 本検査は封筒ごと (`ENV_JSON`) と
#   行だけ (`ROWS_JSON`) の両方を持ち、**封筒も毎回走査する**。
#
# ⚠️ 走査から除くのは 2 つだけ（判断 4 / 判断 11）:
#   (1) `provenance.capabilities` —— 「加工せずそのまま載せる」フィールドで、
#       instrument_rich の宣言には**行種名** `recording_pause` が含まれる（判断 21 と同じ事情）。
#   (2) `provenance.source_basename` —— **入力ファイルの名前**で、実運用では `..._P003.ndjson`
#       のように参加者 ID を含みうる。★ 研究者の手元のファイル名であり新しい漏洩先を作らない、
#       と裁定した（判断 4）。→ ⚠️ **この検査は意図してこの 2 つを見ていない。**
scan_envelope() { # scan_envelope <ラベル> <封筒 JSON>
  if printf '%s' "$2" \
     | jq -c 'del(.provenance.capabilities) | del(.provenance.source_basename) | del(.rows)' \
     | grep -nEi "$PARTICIPANT_RE" >/dev/null 2>&1; then
    fail "AC3b: 封筒に被験者由来の語が現れている（${1}・★ capabilities / source_basename は除外済み）"
  fi
}

# capture <ラベル> <入力パス> —— `ENV_JSON` / `ROWS_JSON` を立て、封筒を走査する。
#   ⚠️★★★ 2026-09-20（security-checker M2 (a)）: 旧版は `instrument_rich` の封筒 1 本しか
#     走査しておらず、★ `minimal` / `stall_onset_observed` / 削除版 / hook 入り / legacy の
#     封筒は **1 度も見ていなかった**。→ 取得を 1 か所に集めて、全部に掛ける。
capture() {
  local label="$1" path="$2"
  ENV_JSON="$(replay "$path" --features 2>/dev/null)" \
    || fail "gse-replay --features が非 0 で終了した（${label}）"
  [ -n "$ENV_JSON" ] || fail "--features の出力が空（${label}）"
  ROWS_JSON="$(printf '%s' "$ENV_JSON" | jq -e '.rows | arrays')" \
    || fail "出力から封筒の .rows を取り出せない（${label}・★ { provenance, config, rows } の形か確認）"
  scan_envelope "$label" "$ENV_JSON"
}

[ -f "$RICH" ] || fail "$RICH が無い（★ 裁定セッションが用意した fixture。自分で作らない）"
[ -f "$OBS" ] || fail "$OBS が無い（★ 裁定セッションが用意した fixture。自分で作らない）"
if [ "${ACC_SKIP_SRC:-0}" != "1" ]; then [ -f "$SRCF" ] || fail "$SRCF が無い"; fi
tmpd="$(mktemp -d)"; trap 'rm -rf "$tmpd"' EXIT

ALLOWED='["capability_undeclared","dropped_events","hook_dead"]'
PARTICIPANT_RE='(recording_pause|redaction|redact|participant|subject_|一時停止|区間削除|削除要求)'

# ---------- instrument_rich（AC1 / AC3 / AC6 / AC8） ----------
capture "instrument_rich" "$RICH"
env_out="$ENV_JSON"
out="$ROWS_JSON"

# AC1
printf '%s' "$out" | jq -e '
  all(.[];
    (.quality | type == "object")
    and (.quality | has("hook_health")
         and has("missing_reasons") and has("observability_mask")))' >/dev/null 2>&1 \
  || fail "AC1: 全行に quality の必須フィールドが揃っていない"

# ⚠️★★★ 出力キー集合の**完全一致**（★ privacy の門）。フィールドが 1 つ増えたら**必ず落とす**。
#   ⚠️ 2026-09-20（判断 3）: `capabilities` を規範の集合から外した。★ 行に戻ってきたら落とす。
printf '%s' "$out" | jq -e '
  ([.[].quality | keys_unsorted[]] | unique
     == ["hook_health","missing_reasons","observability_mask"])
  and ([.[].quality.observability_mask | keys_unsorted[]] | unique == ["feat","hook"])
  and ([.[].quality.hook_health | select(. != null) | keys_unsorted[]] | unique
     == ["alive","dropped_delta","rehook","starved_ms"])' >/dev/null 2>&1 \
  || fail "quality / observability_mask / hook_health のキー集合が規範と完全一致しない（★ 増えても減っても落とす。⚠️ capabilities は封筒へ移した）"

# AC6 ＋ capabilities は meta の値を**加工せずそのまま**封筒に 1 回だけ載せる（判断 3）
meta_cap="$(jq -c 'select(.type=="meta" and has("capabilities")) | .capabilities' "$RICH" | head -1)"
[ -n "$meta_cap" ] || fail "前提: $RICH の meta に capabilities が無い"
printf '%s' "$env_out" | jq -e --argjson cap "$meta_cap" '.provenance.capabilities == $cap' >/dev/null 2>&1 \
  || fail "AC6: 封筒の provenance.capabilities が meta の値と JSON 値として等価でない（★ 加工・欠落をしない。⚠️ キー順は辞書順に正規化されうるので jq の == で比べる）"

# AC3: ⚠️★★★ 被験者由来の欠測理由が 1 つも出ていないこと
#   ★ ここが見るのは **`rows` 全体**である（⚠️ ここは狭めない）。
#   ★ 封筒側は `capture` の中の `scan_envelope`（AC3b）が、
#     `provenance.capabilities` と `provenance.source_basename` の 2 つだけを除いて走査する。
if printf '%s' "$out" | jq -c '.' | grep -nEi "$PARTICIPANT_RE" >/dev/null 2>&1; then
  fail "AC3: 行に被験者由来の欠測理由が現れている（★ ADR-030 D10 / docs/o1-deletion-ledger.md）"
fi

# ★ AC3b（封筒の走査）は `capture` の中で全入力に対して掛かる（★ 冒頭の定義を参照）。

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
capture "minimal（★ 古い形式で落ちてはならない）" "$OLD"
old_env="$ENV_JSON"
old_out="$ROWS_JSON"
# ⚠️★★★ 2026-09-20（判断 3）: 「宣言が無いことを `null` で表し、空配列・空オブジェクトで
#   埋めない」という規律は**封筒へ移った**。行に残るのは `capability_undeclared` の理由だけ。
printf '%s' "$old_env" | jq -e '.provenance.capabilities == null' >/dev/null 2>&1 \
  || fail "AC7: 宣言の無い入力で封筒の provenance.capabilities が null でない（★ 空配列・空オブジェクトで埋めない）"
printf '%s' "$old_out" | jq -e '
  all(.[]; (.quality | has("capabilities") | not) and .quality.hook_health == null
           and .quality.missing_reasons == ["capability_undeclared"]
           and .quality.observability_mask == {"feat":false,"hook":null})' >/dev/null 2>&1 \
  || fail "AC7/AC8: minimal.ndjson の quality が正解表と一致しない（★ 行に capabilities は無い・理由は capability_undeclared だけ）"
if printf '%s' "$old_out" | grep -nEi "$PARTICIPANT_RE" >/dev/null 2>&1; then
  fail "AC3: 古い形式の出力に被験者由来の理由が現れている"
fi

# ---------- stall_onset_observed とその削除版（AC8 / AC9） ----------
capture "stall_onset_observed" "$OBS"
obs_out="$ROWS_JSON"
printf '%s' "$obs_out" | jq -e 'length == 220 and all(.[]; .quality.observability_mask.feat == true)' >/dev/null 2>&1 \
  || fail "AC8: stall_onset_observed で mask.feat が全行 true でない（★ feat 行は途切れていない）"

T=1700000000000
jq -c --argjson lo "$((T + 100000))" --argjson hi "$((T + 140000))" '
  select(((.t // .ts // 0) < $lo) or ((.t // .ts // 0) > $hi))' "$OBS" > "$tmpd/redacted.ndjson" \
  || fail "削除版の生成に失敗"
capture "stall_onset_observed の削除版" "$tmpd/redacted.ndjson"
red_out="$ROWS_JSON"
printf '%s' "$red_out" | jq -e '
  [to_entries[] | select(.value.quality.observability_mask.feat == false) | .key] == [range(99; 140)]' >/dev/null 2>&1 \
  || fail "AC9: 削除版で mask.feat = false が tick 99〜139 だけに立っていない。実際: $(printf '%s' "$red_out" | jq -c '[to_entries[] | select(.value.quality.observability_mask.feat == false) | .key] | [first, last, length]' 2>/dev/null)"
printf '%s' "$red_out" | jq -e 'all(.[]; .quality.missing_reasons == ["capability_undeclared"])' >/dev/null 2>&1 \
  || fail "AC9: ⚠️★★★ 削除版で穴に理由が付いている（★ 穴は mask.feat=false とだけ書く。理由を付けない）"
# ⚠️ 2026-09-20（判断 3）: `capabilities` は行に無いので `del` は要らなくなった。
if printf '%s' "$red_out" | jq -c '.' | grep -nEi "$PARTICIPANT_RE" >/dev/null 2>&1; then
  fail "AC3: 削除版の行に被験者由来の語が現れている"
fi

# ---------- 判断 24 の改訂（AC13 / AC14 / AC15） ----------
#   ★ 正解値は参照実装（ジョブ一時領域の ref_q_emit.py）と手計算で確定した。
# AC13: hook の持ち越しを観測区間で切る（★ security-checker MEDIUM）
{ cat "$OBS"
  echo "{\"type\":\"hook_health\",\"t\":$((T + 50500)),\"alive\":true,\"starved_ms\":0,\"rehook\":false,\"dropped\":0,\"dropped_delta\":0}"
  echo "{\"type\":\"hook_health\",\"t\":$((T + 120500)),\"alive\":false,\"starved_ms\":0,\"rehook\":false,\"dropped\":0,\"dropped_delta\":0}"
} > "$tmpd/obs_hook.ndjson"
jq -c --argjson lo "$((T + 100000))" --argjson hi "$((T + 140000))" '
  select(((.t // .ts // 0) < $lo) or ((.t // .ts // 0) > $hi))' "$tmpd/obs_hook.ndjson" > "$tmpd/obs_hook_red.ndjson"
capture "hook 入り" "$tmpd/obs_hook.ndjson"
hk_out="$ROWS_JSON"
printf '%s' "$hk_out" | jq -e '
  ([.[].quality.observability_mask.hook]
     == ([range(50)] | map(null)) + ([range(70)] | map(true)) + ([range(100)] | map(false)))
  and ([to_entries[] | select(.value.quality.missing_reasons | index("hook_dead")) | .key] == [range(120; 220)])' >/dev/null 2>&1 \
  || fail "AC13: 穴の無い入力で hook の持ち越し（null×50 / true×70 / false×100）と hook_dead（tick 120〜219）が正解と一致しない"
capture "hook 入りの削除版" "$tmpd/obs_hook_red.ndjson"
hkr_out="$ROWS_JSON"
printf '%s' "$hkr_out" | jq -e '
  ([.[].quality.observability_mask.hook]
     == ([range(50)] | map(null)) + ([range(49)] | map(true)) + ([range(121)] | map(null)))
  and ([.[] | select(.quality.missing_reasons | index("hook_dead"))] | length == 0)' >/dev/null 2>&1 \
  || fail "AC13: ⚠️★★★ 穴をまたいで hook の古い状態を持ち越している（★ 期待: null×50 / true×49 / null×121・hook_dead 無し）。実際: $(printf '%s' "$hkr_out" | jq -c '[.[].quality.observability_mask.hook] | reduce .[] as $x ([]; if length>0 and .[-1][0]==$x then .[:-1]+[[.[-1][0], .[-1][1]+1]] else .+[[$x,1]] end)' 2>/dev/null)"

# AC14: dropped_delta の欠けた行を 0 で埋めない（★ code-reviewer M1）
TR=1700000100000
{ cat "$RICH"
  echo "{\"type\":\"hook_health\",\"t\":$((TR + 8000)),\"alive\":true,\"starved_ms\":0,\"rehook\":false,\"dropped\":0}"
} > "$tmpd/rich_legacy.ndjson"
capture "旧形式の hook_health 入り" "$tmpd/rich_legacy.ndjson"
lg_out="$ROWS_JSON"
printf '%s' "$lg_out" | jq -e '
  (.[7].quality.hook_health == {"alive":true,"starved_ms":0,"rehook":false,"dropped_delta":null})
  and (.[7].quality.missing_reasons == [])
  and (.[13].quality.hook_health.dropped_delta == 2)' >/dev/null 2>&1 \
  || fail "AC14: dropped_delta の欠けた行（tick 7）が null にならない、または理由が立っている（★ 0 で埋めない）。実際: $(printf '%s' "$lg_out" | jq -c '.[7].quality' 2>/dev/null)"

# AC15: capabilities が JSON オブジェクトでない / 4096 バイト超 → Err（★ security-checker LOW-3。null に倒さない）
jq -c 'if .type == "meta" and has("capabilities") then .capabilities = "x" else . end' "$RICH" > "$tmpd/cap_str.ndjson"
if replay "$tmpd/cap_str.ndjson" --features >/dev/null 2>&1; then
  fail "AC15: capabilities が文字列の入力で --features が exit 0（★ 形の合わない宣言を黙って受けない）"
fi
jq -c --arg pad "$(head -c 5000 /dev/zero | tr '\0' 'a')" \
  'if .type == "meta" and has("capabilities") then .capabilities.padding = $pad else . end' "$RICH" > "$tmpd/cap_big.ndjson"
if replay "$tmpd/cap_big.ndjson" --features >/dev/null 2>&1; then
  fail "AC15: 4096 バイトを超える capabilities で --features が exit 0（★ 行ごとに複製されるので上限を置く）"
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
  # ⚠️★★★ 2026-09-18 修正（判断 23）: 本体（最初の #[cfg(test)] より前）だけを見る。
  #   ★ 旧版はファイル全体を見ていたので、AC9 が要求する test 名 `feat_hole_is_masked_without_a_reason`
  #     （★ 裁定セッション自身が命名した）に必ず一致し、**AC9 と AC11 が両立しなかった**（worker が実測で指摘）。
  first_test_line="$(grep -nE '^#\[cfg\(test\)\]' "$SRCF" | head -1 | cut -d: -f1)"
  first_test_line="${first_test_line:-999999}"
  if grep -nE 'fn [a-z_]*(hole|gap|interval)[a-z_]*\(' "$SRCF" | grep -vE '^[0-9]+:[[:space:]]*//' \
       | awk -F: -v L="$first_test_line" '$1 < L' | grep -q .; then
    fail "AC11: $SRCF の本体が穴 / 区間の判定関数を独自に定義している（★ observed_intervals を使う）"
  fi
  # ★ AC の test が実在すること
  # ⚠️ 2026-09-20（判断 3）: `absent_capabilities_is_null_not_empty` は
  #   `absent_capabilities_is_reported_as_missing_reason` へ改名した（★ 行に `capabilities` が
  #   無くなり、`null` を見る側が封筒へ移ったため）。★ 値が行へ漏れないことは
  #   `declared_capabilities_do_not_appear_in_rows` が張る。
  for t in missing_reasons_are_instrument_side_only participant_originated_reasons_are_never_emitted \
           missing_is_null_not_zero absent_capabilities_is_reported_as_missing_reason \
           declared_capabilities_do_not_appear_in_rows \
           feat_hole_is_masked_without_a_reason hook_state_carries_forward_until_next_row \
           hook_carry_is_cut_at_observed_interval_boundaries missing_dropped_delta_is_null_not_zero \
           aggregation_of_multiple_rows_in_one_tick in_tick_dead_row_sets_hook_dead_even_if_state_ends_alive \
           tick_boundary_rows_are_attributed_correctly; do
    grep -qE "fn ${t}\b" "$SRCF" || fail "AC の test \`$t\` が $SRCF に無い"
  done
  for t in malformed_hook_health_line_does_not_break_run_replay non_object_or_oversized_capabilities_is_an_error \
           quality_inputs_reach_feature_rows_through_the_collectors \
           envelope_carries_meta_facts_and_sharing_marker; do
    grep -qE "fn ${t}\b" src/bin/replay.rs || fail "AC の test \`$t\` が bin/replay.rs に無い"
  done

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
