#!/usr/bin/env bash
# issue 008 (stall onset の観測区間・末尾の沈黙・task_kind・検出力) の AC 検査
#
# ★ 正解値は裁定セッションが「参照実装 (Python) ＋ 手計算」で確定させた（decisions.md 判断 18）。
#   既定値 W=30000 / q=0.99 / hole_gap_ms=2000 のときの値である。
#   ⚠️ 既定値（事前宣言事項）を変えたら、この表を先に書き換えること。
#
# ★ ACC_REPLAY_CMD を与えると gse-replay の代わりにそのコマンドを使う（★ 検査自体の 3 状態テスト用）。
#   ACC_SKIP_005=1 で 005-acceptance の再実行を省く（同上）。
# ⚠️★★★ 2026-09-20（封筒・起票 2）: `--features` の出力は
#   **`{ provenance, config, rows }` の封筒**になった（判断 25 #14）。
#   ★ 本検査は取得時に `jq '.rows'` で**行だけを取り出して**おり、
#     以降の `.[]` / `all(.[]; ...)` は封筒を剥がした後の配列を指す。
#   ⚠️★★★ **この検査は `provenance` と `config` を 1 つも見ていない。**
#     ★ 封筒自体の検査は `.steering/20260920-envelope-issues/envelope-acceptance.sh` が持つ。
#   ★ 封筒が無い（配列のままの）出力では `jq '.rows'` が失敗し、
#     `set -o pipefail` によりその場で赤になる（fail-closed）。
set -uo pipefail
fail() { echo "[acceptance 008] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"
command -v timeout >/dev/null 2>&1 || fail "timeout が無い"
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(pwd)"
cd src-tauri || fail "src-tauri が無い"
SRC="src/analysis/feat_offline/stall_onset.rs"
FIX="tests/fixtures/stall_onset_observed.ndjson"
[ -f "$FIX" ] || fail "$FIX が無い（★ 裁定セッションが作成済みのはず。fixture を作り直さないこと）"

replay() {
  if [ -n "${ACC_REPLAY_CMD:-}" ]; then $ACC_REPLAY_CMD "$@"
  else cargo run --quiet --bin gse-replay -- "$@"; fi
}

T=1700000000000
tmpd="$(mktemp -d)"; trap 'rm -rf "$tmpd"' EXIT

# ---------- 1. そのままの fixture（AC1 / AC7 / AC14） ----------
out1="$(replay "$FIX" --features 2>/dev/null | jq -e '.rows | arrays')" || fail "gse-replay --features が非 0 で終了した、または封筒の .rows を取り出せない ($FIX)"
[ -n "$out1" ] || fail "--features の出力が空 ($FIX)"

printf '%s' "$out1" | jq -e --argjson T "$T" '
  [.[] | select(.stall_onset.is_onset) | .stall_onset | [(.s_ms - $T), (.t0_ms - $T), .theta_person_ms]]
  == [[37560, 40160, 2600], [185000, 187600, 2600]]' >/dev/null 2>&1 \
  || fail "AC1: onset が [s,t0,θ] = [37560,40160,2600] と [185000,187600,2600] (T 相対) の 2 つでない（★ 末尾の沈黙の onset が出力に出ているか）。実際: $(printf '%s' "$out1" | jq -c --argjson T "$T" '[.[] | select(.stall_onset.is_onset) | .stall_onset | [(.s_ms - $T), (.t0_ms - $T), .theta_person_ms]]' 2>/dev/null)"

# AC14: onset は t0 を含む tick に載る（★ tick 幅は隣接行の t_ms 差から取る。リテラルを置かない）
printf '%s' "$out1" | jq -e '
  (.[1].t_ms - .[0].t_ms) as $tick
  | all(.[] | select(.stall_onset.is_onset);
        .t_ms <= .stall_onset.t0_ms and .stall_onset.t0_ms < .t_ms + $tick)' >/dev/null 2>&1 \
  || fail "AC14: onset が t0 を含む tick に載っていない（t_ms <= t0 < t_ms + tick）"

# AC7: onset 行の task_kind は s 時点の宣言、onset でない行は null
printf '%s' "$out1" | jq -e '
  all(.[] | .stall_onset;
      if .is_onset then .task_kind == "argumentative"
      else (.task_kind == null and .s_ms == null and .t0_ms == null and .theta_person_ms == null) end)' >/dev/null 2>&1 \
  || fail "AC7: onset 行の task_kind が \"argumentative\" でない、または onset でない行に値が残っている"

# ---------- 2. 削除版（AC2）: T+100000〜T+140000 の key 行と feat 行を落とす ----------
#   ★ meta / session_meta は残す（redaction.rs の retain_outside_range と同じ形）。
jq -c --argjson lo "$((T + 100000))" --argjson hi "$((T + 140000))" '
  select(((.t // .ts // 0) < $lo) or ((.t // .ts // 0) > $hi))' "$FIX" > "$tmpd/redacted.ndjson" \
  || fail "削除版の生成に失敗"
out2="$(replay "$tmpd/redacted.ndjson" --features 2>/dev/null | jq -e '.rows | arrays')" || fail "削除版で --features が非 0 で終了した、または封筒の .rows を取り出せない"
printf '%s' "$out2" | jq -e --argjson lo "$((T + 100000))" --argjson hi "$((T + 140000))" '
  [.[] | select(.stall_onset.is_onset) | .stall_onset
       | select((.s_ms >= $lo and .s_ms <= $hi) or (.t0_ms >= $lo and .t0_ms <= $hi))] | length == 0' >/dev/null 2>&1 \
  || fail "AC2: ⚠️★★★ 削除区間の内側に onset が立っている（ADR-030 D8 (b-2)）。実際: $(printf '%s' "$out2" | jq -c --argjson T "$T" '[.[] | select(.stall_onset.is_onset) | .stall_onset | [(.s_ms - $T), (.t0_ms - $T)]]' 2>/dev/null)"
printf '%s' "$out2" | jq -e --argjson T "$T" '
  [.[] | select(.stall_onset.is_onset) | .stall_onset.t0_ms - $T] == [40160, 187600]' >/dev/null 2>&1 \
  || fail "AC2: 削除版の onset が t0 = [40160, 187600] (T 相対) でない"

# ---------- 3. feat 行 0 本（AC3） ----------
out3="$(replay tests/fixtures/deep_silence.ndjson --features 2>/dev/null | jq -e '.rows | arrays')" \
  || fail "AC3: deep_silence.ndjson で --features が非 0 で終了した、または封筒の .rows を取り出せない"
printf '%s' "$out3" | jq -e 'length > 0 and all(.[]; .stall_onset.is_onset == false)' >/dev/null 2>&1 \
  || fail "AC3: feat 行の無い deep_silence.ndjson で onset が立った（★ 観測区間が無ければ onset は立たない）"

# ---------- 4. 計算量（AC18）: 15 万打鍵 ＋ 末尾 60 秒の沈黙 ----------
#   ★ 実測 (2026-09-18・debug): 現行 O(N²) 実装 = 56 秒 / 検出器以外の処理 = 2 秒。
#   ★ 末尾の沈黙で onset がちょうど 1 つ立つこと＝ 検出器が実際に走ったことも確かめる。
awk 'BEGIN{T=1700000000000; n=150000;
  print "{\"type\":\"meta\",\"session_start\":" T ",\"hmm_version\":\"0.5.0\"}";
  print "{\"type\":\"session_start\",\"t\":" T "}";
  for(i=0;i<n;i++) printf "{\"type\":\"key\",\"t\":%d,\"vk\":%d,\"press\":true}\n", T+1000+i*250, 65+(i%26);
  end=T+1000+n*250+60000;
  for(f=T+1000; f<=end; f+=1000) printf "{\"type\":\"feat\",\"t\":%d}\n", f }' > "$tmpd/big.ndjson" \
  || fail "大入力の生成に失敗"
if [ -n "${ACC_REPLAY_CMD:-}" ]; then
  BIG_CMD="$ACC_REPLAY_CMD"
else
  # ★ build 時間を計測に含めないよう、先に build してからバイナリを直接叩く
  cargo build --quiet --bin gse-replay 2>/dev/null || fail "gse-replay の build に失敗"
  BIG_CMD="./target/debug/gse-replay"
fi
start=$(date +%s)
# ⚠️★★★ ここだけ封筒を**別の行で**剥がす（2026-09-20・封筒）。
#   ★ `timeout ... | jq` にすると、打ち切られた出力で jq が 5 を返した瞬間に
#     pipefail が「最も右の非 0」= 5 を採り、**rc=124（時間切れ）が消える**。
#     → ★ 時間切れの診断が「非 0 で終了した」に化ける。生の rc を先に確定させる。
#   ★ 併せて出力は**ファイルへ落とす**（2026-09-20・code-reviewer MEDIUM）——
#     15 万打鍵の pretty 出力は数十 MB 規模で、生と剥がし済みを同時にシェル変数へ載せると
#     ⚠️ ピーク使用量が倍になる。`elapsed` は jq の前に確定するので計時 AC は汚れない。
timeout 20 $BIG_CMD "$tmpd/big.ndjson" --features > "$tmpd/big_out.json" 2>/dev/null
rc=$?
elapsed=$(( $(date +%s) - start ))
[ $rc -eq 124 ] && fail "AC18: 15 万打鍵の --features が 20 秒で終わらない（★ 計算量が二乗のまま。現行実装は実測 56 秒）"
[ $rc -eq 0 ] || fail "AC18: 大入力で --features が非 0 で終了した (rc=$rc)"
out4="$(jq -e '.rows | arrays' "$tmpd/big_out.json")" \
  || fail "AC18: 出力から封筒の .rows を取り出せない（★ { provenance, config, rows } の形か確認）"
printf '%s' "$out4" | jq -e '[.[] | select(.stall_onset.is_onset)] | length == 1' >/dev/null 2>&1 \
  || fail "AC18: 大入力の末尾の沈黙で onset がちょうど 1 つ立たない（★ 検出器が走っていない可能性）"
echo "[acceptance 008] AC18: ${elapsed}s" >&2

# ---------- 4b. 計算量（AC18b）: 条件 A の立ち上がりが打鍵数に比例する入力 ----------
#   ⚠️★★★ 2026-09-18 追加（decisions.md 判断 22）: AC18 の入力は立ち上がりが 1 回しか起きないので、
#     「立ち上がりのたびに θ の標本を集め直す」二乗の経路を捉えなかった（★ 2 レビューが独立に実測）。
#   ★ 文字 → 1ms 後に BS の対を 70ms ごとに 75,000 対（15 万打鍵）＝ 立ち上がり 75,000 回。
#   ★ 実測 (debug): e079b21 の実装 = 248 秒（security-checker）。
awk 'BEGIN{T=1700000000000; n=75000;
  print "{\"type\":\"meta\",\"session_start\":" T ",\"hmm_version\":\"0.5.0\"}";
  print "{\"type\":\"session_start\",\"t\":" T "}";
  for(i=0;i<n;i++){ t=T+1000+i*70;
    printf "{\"type\":\"key\",\"t\":%d,\"vk\":65,\"press\":true}\n", t;
    printf "{\"type\":\"key\",\"t\":%d,\"vk\":8,\"press\":true}\n", t+1 };
  end=T+1000+n*70+60000;
  for(f=T+1000; f<=end; f+=1000) printf "{\"type\":\"feat\",\"t\":%d}\n", f }' > "$tmpd/churn.ndjson" \
  || fail "AC18b の入力生成に失敗"
start=$(date +%s)
# ⚠️ AC18 と同じ理由で、封筒は別の行で剥がす（rc=124 を jq の 5 で潰さない）。
timeout 20 $BIG_CMD "$tmpd/churn.ndjson" --features > "$tmpd/churn_out.json" 2>/dev/null
rc=$?
elapsed=$(( $(date +%s) - start ))
[ $rc -eq 124 ] && fail "AC18b: 立ち上がり 75,000 回の入力で --features が 20 秒で終わらない（★ θ の再計算が二乗。e079b21 は実測 248 秒）"
[ $rc -eq 0 ] || fail "AC18b: 立ち上がりの多い入力で --features が非 0 で終了した (rc=$rc)"
out4b="$(jq -e '.rows | arrays' "$tmpd/churn_out.json")" \
  || fail "AC18b: 出力から封筒の .rows を取り出せない（★ { provenance, config, rows } の形か確認）"
printf '%s' "$out4b" | jq -e 'length > 0' >/dev/null 2>&1 || fail "AC18b: 出力が空"
echo "[acceptance 008] AC18b: ${elapsed}s" >&2

# ---------- 5. ソースの検査（AC8 ほか） ----------
grep -qE 'merge_gap_ms' "$SRC" || fail "AC8: $SRC が W / B の既定を OutcomeConfig::merge_gap_ms から引いていない"
# ★ 本体（最初の #[cfg(test)] より前）のコード行に 30000 の直書きが無いこと
#   （⚠️ doc コメントとテストの期待値は許す）
first_test_line="$(grep -nE '^#\[cfg\(test\)\]' "$SRC" | head -1 | cut -d: -f1)"
first_test_line="${first_test_line:-999999}"
if grep -nE '30_?000' "$SRC" | grep -vE '^[0-9]+:[[:space:]]*//' \
     | awk -F: -v L="$first_test_line" '$1 < L' | grep -q .; then
  fail "AC8: $SRC の本体に 30000 の直書きが残っている（★ OutcomeConfig::default().merge_gap_ms を使う）"
fi
grep -qE 'hole_gap_ms' "$SRC" || fail "AC8: StallOnsetConfig に hole_gap_ms が無い"
grep -qE 'warmup_count' "$SRC" || fail "AC9: StallOnsetConfig に warmup_count が無い"
grep -qE 'ENGINE_TICK_MS' "$SRC" || fail "AC8: hole_gap_ms の既定が ENGINE_TICK_MS 由来でない"

# ★ AC の test が実在すること（★ 名前は issue の AC 表と一致させる）
for t in feat_hole_cuts_condition_b no_feat_rows_means_no_onset no_evaluation_within_w_after_hole \
         theta_sample_excludes_gaps_across_holes onset_beyond_last_feat_is_not_confirmed \
         task_kind_is_the_declaration_in_effect_at_s defaults_come_from_existing_params \
         warmup_count_suppresses_small_sample refractory_one_onset_per_rise \
         production_before_t0_cancels_onset quantile_uses_q_not_max prefix_stable_at_every_cut \
         onset_is_attributed_to_the_t0_tick same_tick_collision_keeps_the_first \
         timestamp_near_u64_max_does_not_panic; do
  grep -qE "fn ${t}\b" "$SRC" || fail "AC の test \`$t\` が $SRC に無い"
done
grep -qE 'fn malformed_feat_line_does_not_break_run_replay\b' src/bin/replay.rs \
  || fail "AC17 の test \`malformed_feat_line_does_not_break_run_replay\` が bin/replay.rs に無い"

# ---------- 6. 回帰: 005-acceptance（★ キー集合 6 個・原因語なし・定数なし） ----------
if [ "${ACC_SKIP_005:-0}" != "1" ]; then
  ( cd "$ROOT" && bash "$HERE/005-acceptance.sh" ) >/dev/null 2>&1 \
    || fail "AC19: 005-acceptance.sh が通らない（★ 出力: $( cd "$ROOT" && bash "$HERE/005-acceptance.sh" 2>&1 | tail -1 )）"
fi

echo "[acceptance 008] OK"
