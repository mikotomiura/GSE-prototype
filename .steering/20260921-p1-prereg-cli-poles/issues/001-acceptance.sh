#!/usr/bin/env bash
# issue 001 (凍結値の CLI 注入 ＋ θ の標本数) の AC 検査
#
# ⚠️ 実行は **repo 直下**から。内部で src-tauri へ cd する
#   (★ Cargo.toml は repo 直下に無い)。
# ⚠️ `--features` の出力は封筒 `{ provenance, config, rows }` である (起票 2・判断 25 #14)。
set -uo pipefail
fail() { echo "[acceptance 001] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"

# ⚠️★★★ loop-run.sh は `( cd "$wt" && bash "$acc" )` で **worktree を cwd にして**呼ぶ
#   (scripts/loop-run.sh:369)。★ よって repo root は **cwd** であって、
#   ${BASH_SOURCE[0]} の位置 (= main checkout) ではない。
#   ⚠️ BASH_SOURCE から導くと **worktree ではなく main checkout を検査**してしまう。
REPO_ROOT="$(pwd)"
[ -f "$REPO_ROOT/src-tauri/Cargo.toml" ] || fail "cwd が repo root ではない（src-tauri/Cargo.toml が無い）: $REPO_ROOT"
PREREG="$REPO_ROOT/src-tauri/prereg/p1-episode.json"
[ -f "$PREREG" ] || fail "凍結 JSON が無い: $PREREG"

# ── AC8: 事前宣言の一致検査と、その陽性対照 ──────────────────────────────
command -v python >/dev/null 2>&1 || command -v python3 >/dev/null 2>&1 || fail "python が無い"
PY="$(command -v python || command -v python3)"
"$PY" "$REPO_ROOT/scripts/check_prereg_parity.py" >/dev/null 2>&1 \
  || fail "AC8: check_prereg_parity.py が非 0 (文書と凍結 JSON が食い違っている)"
"$PY" "$REPO_ROOT/scripts/check_prereg_parity.py" --self-test >/dev/null 2>&1 \
  || fail "AC8: check_prereg_parity.py --self-test が非 0 (★ 検査が赤にならない = 検査が壊れている)"

status="$(jq -r '.status' "$PREREG")" || fail "AC8: 凍結 JSON を読めない"
[ "$status" = "frozen" ] || fail "AC8: status が 'frozen' でない (実測: '$status')"

cd "$REPO_ROOT/src-tauri" || fail "src-tauri が無い"
FIX="tests/fixtures/stall_onset_observed.ndjson"
[ -f "$FIX" ] || fail "fixture が無い: $FIX"

run_features() { cargo run --quiet --bin gse-replay -- "$FIX" --features "$@" 2>/dev/null; }

# ── AC1: 封筒 config の 8 値が凍結 JSON の operational と一致する ────────
env_out="$(run_features)" || fail "AC1: --features が非 0 で終了した"
[ -n "$env_out" ] || fail "AC1: --features の出力が空"

for k in w_ms q b_ms hole_gap_ms warmup_count theta_estimator t1a_window_ms net_diff_min; do
  want="$(jq -c --arg k "$k" '.operational[$k]' "$PREREG")" || fail "AC1: 凍結 JSON に $k が無い"
  got="$(printf '%s' "$env_out" | jq -c --arg k "$k" '.config[$k]')" \
    || fail "AC1: 封筒 config を読めない"
  [ "$want" = "$got" ] || fail "AC1: config.$k が凍結値と違う (凍結=$want 出力=$got)"
done

# ── AC2: 由来フィールドと overrides の既定 ───────────────────────────────
printf '%s' "$env_out" | jq -e '
  (.config | has("prereg_id") and has("prereg_version") and has("prereg_sha256_prefix")
            and has("config_source") and has("overrides"))
  and (.config.config_source == "frozen")
  and (.config.overrides | type == "array")
  and (.config.overrides | length == 0)' >/dev/null 2>&1 \
  || fail "AC2: prereg_* / config_source / overrides の既定が期待と違う"

# ── AC3: --set が効き、overrides に 1 件だけ載る ─────────────────────────
set_out="$(run_features --set q=0.995)" || fail "AC3: --set q=0.995 が非 0 で終了した"
printf '%s' "$set_out" | jq -e '
  (.config.q == 0.995)
  and (.config.config_source == "frozen")
  and (.config.overrides | length == 1)
  and (.config.overrides[0] | tostring | test("q"))' >/dev/null 2>&1 \
  || fail "AC3: --set q=0.995 が config.q / overrides に反映されていない"

# ── AC4: fail-closed (未知キー / 型不一致 / 範囲外) ──────────────────────
#   ⚠️★★★ exit code と stdout の **両方** を見る。
#     「エラーを出しつつ出力もする」を通さないため。
assert_fail_closed() {
  local label="$1"; shift
  local out rc
  out="$(cargo run --quiet --bin gse-replay -- "$FIX" --features "$@" 2>/dev/null)"
  rc=$?
  [ "$rc" -ne 0 ] || fail "AC4($label): exit 0 で通ってしまった (fail-closed でない)"
  [ -z "$out" ] || fail "AC4($label): 非 0 で終了したが stdout に $(printf '%s' "$out" | wc -c) バイト出ている"
}
assert_fail_closed "未知キー"   --set bogus=1
assert_fail_closed "型不一致"   --set q=abc
assert_fail_closed "範囲外"     --set w_ms=0

# ⚠️ 陰性対照: 正常な --set は通ること (★ AC4 の ok 枝が実際に取られることの確認)
run_features --set hole_gap_ms=3000 >/dev/null 2>&1 \
  || fail "AC4(陰性対照): 正常な --set hole_gap_ms=3000 まで落ちている (過剰拒否)"

# ── AC5: --feature-config が効き、config_source が file になる ───────────
tmp_cfg="$(mktemp)" || fail "AC5: 一時ファイルを作れない"
trap 'rm -f "$tmp_cfg"' EXIT
jq '.operational.hole_gap_ms = 5000' "$PREREG" > "$tmp_cfg" || fail "AC5: 一時 config を作れない"
file_out="$(run_features --feature-config "$tmp_cfg")" || fail "AC5: --feature-config が非 0 で終了した"
printf '%s' "$file_out" | jq -e '
  (.config.hole_gap_ms == 5000) and (.config.config_source == "file")' >/dev/null 2>&1 \
  || fail "AC5: --feature-config の値 / config_source が反映されていない"

# ── AC6: theta_sample_n が theta_person_ms と同時にだけ立つ ──────────────
printf '%s' "$env_out" | jq -e '
  (.rows | arrays)
  and (.rows | all(.stall_onset;
        (.theta_person_ms == null) == (.theta_sample_n == null)))' >/dev/null 2>&1 \
  || fail "AC6: theta_sample_n が theta_person_ms と同時に立っていない行がある"

# ── AC7: warmup_count = 100 が効いて第 1 onset が消える ─────────────────
#   ⚠️★★★ これは「検査が本当に何かを見ている」ことの中核である。
#     実測 (2026-09-21): stall_onset_observed.ndjson は第 1 onset (s = T+37,560) の
#     時点で press が 12 本 (= 隣接対 11) しかなく、warmup_count=100 を下回る。
#     → 残るのは第 2 onset (t0 = T+187,600) の 1 本だけになる。
#   ★ T は 008-acceptance.sh と同じ約束 (1700000000000) を使う。
T=1700000000000
onsets="$(printf '%s' "$env_out" | jq -c --argjson T "$T" \
  '[.rows[] | select(.stall_onset.is_onset) | (.stall_onset.t0_ms - $T)]')" \
  || fail "AC7: onset を取り出せない"
[ "$onsets" = "[187600]" ] \
  || fail "AC7: onset が [187600] (T 相対) の 1 本でない。実測: $onsets（★ 2 本のままなら warmup_count が配線されていない＝ AC が空振り）"

printf '%s' "$env_out" | jq -e '
  [.rows[] | select(.stall_onset.is_onset) | .stall_onset.theta_sample_n]
  | (length == 1) and (.[0] != null) and (.[0] >= 100)' >/dev/null 2>&1 \
  || fail "AC7: 残った onset の theta_sample_n が null か 100 未満（★ 実測の見込みは 352）"

# ⚠️ 陽性対照: warmup_count を 1 に緩めると第 1 onset が戻ること。
#   ★ これが無いと「そもそも onset が 1 本しか立たない fixture だった」と区別できない
#     (検査の検査 ルール 3: 「置換した」と「そもそも無かった」を分ける)。
relaxed="$(run_features --set warmup_count=1)" || fail "AC7(陽性対照): --set warmup_count=1 が非 0"
relaxed_onsets="$(printf '%s' "$relaxed" | jq -c --argjson T "$T" \
  '[.rows[] | select(.stall_onset.is_onset) | (.stall_onset.t0_ms - $T)]')" \
  || fail "AC7(陽性対照): onset を取り出せない"
[ "$relaxed_onsets" = "[40160,187600]" ] \
  || fail "AC7(陽性対照): warmup_count=1 で onset が [40160,187600] に戻らない。実測: $relaxed_onsets"

# ── AC9: 既存 acceptance 3 本が緑であること ─────────────────────────────
#   ⚠️ 期待値を更新したうえで緑であることを見る。検査を外して緑にしていないかは
#     レビューが見る（★ ここでは exit code だけを回収する）。
PREV="$REPO_ROOT/.steering/20260914-mhd-feature-offline-tiers/issues"
for prev in 005 006 008; do
  ( cd "$REPO_ROOT" && bash "$PREV/$prev-acceptance.sh" ) >/dev/null 2>&1 \
    || fail "AC9: 前タスクの $prev-acceptance.sh が非 0（★ 期待値の更新が漏れている）"
done

echo "[acceptance 001] OK"
