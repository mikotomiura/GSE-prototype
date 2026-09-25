#!/usr/bin/env bash
# issue 004 (極の器) の AC 検査
# ⚠️ 実行は repo 直下から。
set -uo pipefail
fail() { echo "[acceptance 004] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"

# ⚠️★★★ loop-run.sh は `( cd "$wt" && bash "$acc" )` で **worktree を cwd にして**呼ぶ
#   (scripts/loop-run.sh:369)。★ よって repo root は **cwd** であって、
#   ${BASH_SOURCE[0]} の位置 (= main checkout) ではない。
#   ⚠️ BASH_SOURCE から導くと **worktree ではなく main checkout を検査**してしまう。
REPO_ROOT="$(pwd)"
[ -f "$REPO_ROOT/src-tauri/Cargo.toml" ] || fail "cwd が repo root ではない（src-tauri/Cargo.toml が無い）: $REPO_ROOT"
cd "$REPO_ROOT/src-tauri" || fail "src-tauri が無い"

FIX="tests/fixtures/stall_onset_observed.ndjson"
[ -f "$FIX" ] || fail "fixture が無い: $FIX"

run() { cargo run --quiet --bin gse-replay -- "$FIX" --features "$@" 2>/dev/null; }

# ── AC1 / AC2: 無指定と --pole baseline が同じ出力である ─────────────────
no_flag="$(run)"              || fail "AC1: --features が非 0"
explicit="$(run --pole baseline)" || fail "AC2: --pole baseline が非 0"

rows_no="$(printf '%s' "$no_flag"  | jq -cS '.rows')" || fail "AC1: .rows を取り出せない"
rows_ex="$(printf '%s' "$explicit" | jq -cS '.rows')" || fail "AC2: .rows を取り出せない"
[ "$rows_no" = "$rows_ex" ] || fail "AC2: --pole baseline の rows が無指定と一致しない"

printf '%s' "$no_flag" | jq -e '.config.pole == "baseline"' >/dev/null 2>&1 \
  || fail "AC1: 無指定で config.pole が \"baseline\" でない"

# ── AC6: 封筒の 3 キーが常に出る ────────────────────────────────────────
printf '%s' "$no_flag" | jq -e '
  (.config | has("pole") and has("pole_applicable") and has("pole_not_applicable_reason"))
  and (.config.pole_applicable == true)
  and (.config.pole_not_applicable_reason == null)' >/dev/null 2>&1 \
  || fail "AC6: baseline の pole_applicable / pole_not_applicable_reason が期待と違う"

# ── AC3 / AC4 / AC5: fail-closed ────────────────────────────────────────
#   ⚠️★★★ exit code と stdout の両方を見る。「エラーを出しつつ baseline も返す」を通さない。
assert_exit1_and_silent() {
  local label="$1"; shift
  local out rc
  out="$(cargo run --quiet --bin gse-replay -- "$@" 2>/dev/null)"
  rc=$?
  [ "$rc" -ne 0 ] || fail "$label: exit 0 で通ってしまった"
  [ -z "$out" ]   || fail "$label: 非 0 で終了したが stdout に出力がある（★ 黙って baseline を返している疑い）"
}
# ⚠️ 2026-09-25 (issue 005): 極 M+ を開通させたので「未実装の極は exit 1」の対象から外した。
#   ★ 開通後の振る舞い (exit 0・封筒 `pole == "modifier_m_plus"`) は `005-acceptance.sh` AC1 が持つ。
# ⚠️ 2026-09-25 (issue 006): 極 B も開通させたので `pointer_b` の行を外した（★ 未実装の極が無くなり、AC3 の対象は空になった）。
#   ★ 開通後の振る舞い (exit 0・封筒 `pole == "pointer_b"`) は `006-acceptance.sh` AC1 が持つ。
#   ⚠️ 「未実装の極は Err」という**門そのもの**は `Pole::is_implemented` / `resolve_pole` に残り、単体テストが固定する。
assert_exit1_and_silent "AC4(未知の極名)"       "$FIX" --features --pole bogus
assert_exit1_and_silent "AC5(--features 以外)"  "$FIX" --metrics  --pole baseline

# ── AC7: Pole は enum で、直積を作る語が無い ────────────────────────────
SRC_DIR="src/analysis/feat_offline"
grep -qE '^\s*pub enum Pole\b' "$SRC_DIR/stall_onset.rs" \
  || fail "AC7: pub enum Pole が $SRC_DIR/stall_onset.rs に無い"
if grep -rniE '(cartesian|cross_product|all_pole_pairs|pole_combinations)' "$SRC_DIR" >/dev/null 2>&1; then
  fail "AC7: 極の直積を示唆する識別子が $SRC_DIR にある（★ ADR-030 D3 は Cartesian を禁じる）"
fi

# ── AC8: observed_intervals の doc に「極によって変わる」旨がある ────────
grep -qE '極によって変わる' src/bin/replay.rs \
  || fail "AC8: provenance.observed_intervals の doc に「極によって変わる」旨が無い"

# ── 行が変わっていないことの担保（★ Test Plan 参照） ────────────────────
#   ⚠️ 既存 acceptance は [s, t0, θ] を pin しているので、行が動けば赤になる。
PREV="$REPO_ROOT/.steering/20260914-mhd-feature-offline-tiers/issues"
for prev in 005 008; do
  ( cd "$REPO_ROOT" && bash "$PREV/$prev-acceptance.sh" ) >/dev/null 2>&1 \
    || fail "行の不変性: 前タスクの $prev-acceptance.sh が非 0（★ 極の器が行の値を動かした疑い）"
done

echo "[acceptance 004] OK"
