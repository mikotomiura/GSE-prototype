#!/usr/bin/env bash
# issue 003 (T1a の 30 秒ローリング窓) の AC 検査
# ⚠️ 実行は repo 直下から。`--features` の出力は封筒 { provenance, config, rows }。
set -uo pipefail
fail() { echo "[acceptance 003w] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"

# ⚠️★★★ loop-run.sh は `( cd "$wt" && bash "$acc" )` で **worktree を cwd にして**呼ぶ
#   (scripts/loop-run.sh:369)。★ よって repo root は **cwd** であって、
#   ${BASH_SOURCE[0]} の位置 (= main checkout) ではない。
#   ⚠️ BASH_SOURCE から導くと **worktree ではなく main checkout を検査**してしまう。
REPO_ROOT="$(pwd)"
[ -f "$REPO_ROOT/src-tauri/Cargo.toml" ] || fail "cwd が repo root ではない（src-tauri/Cargo.toml が無い）: $REPO_ROOT"
cd "$REPO_ROOT/src-tauri" || fail "src-tauri が無い"

FEATURES_RS="src/analysis/features.rs"
FIX="tests/fixtures/t1a_window.ndjson"
[ -f "$FEATURES_RS" ] || fail "$FEATURES_RS が無い"
[ -f "$FIX" ]         || fail "AC3: 新 fixture が無い: $FIX"

# ── AC1: 生リテラルが const に置き換わっている ──────────────────────────
#   ⚠️★★★ 変異ガードは「元の形が消えた」だけでは足りない (検査の検査 ルール 3)。
#     → **const が在ること** と **生リテラルが消えたこと** の両方を見る。
grep -qE 'pub const FEATURE_WINDOW_MS: *u64 *= *30_000;' "$FEATURES_RS" \
  || fail "AC1: pub const FEATURE_WINDOW_MS が $FEATURES_RS に無い"
if grep -nE 'saturating_sub\( *30_000 *\)' "$FEATURES_RS" >/dev/null 2>&1; then
  fail "AC1: 窓の計算に生リテラル 30_000 が残っている（${FEATURES_RS}）"
fi
grep -qE 'saturating_sub\( *FEATURE_WINDOW_MS *\)' "$FEATURES_RS" \
  || fail "AC1: 窓の計算が FEATURE_WINDOW_MS を使っていない（★ 別の綴りに置き換わった疑い）"

# ── AC2: 命名リファクタで振る舞いが変わっていない ───────────────────────
cargo run --quiet --bin gse-replay -- tests/fixtures/minimal.ndjson \
  --snapshot tests/snapshots/minimal.json >/dev/null 2>&1 \
  || fail "AC2: ゴールデン replay が非 0（★ 命名リファクタが振る舞いを変えている）"

rows_of() {
  cargo run --quiet --bin gse-replay -- "$FIX" --features "$@" 2>/dev/null \
    | jq -e '.rows | arrays'
}

# ── AC3: 窓が効いて p50 != max の行が出る ───────────────────────────────
wide="$(rows_of)" || fail "AC3: --features が非 0、または封筒の .rows を取り出せない"
n_diff="$(printf '%s' "$wide" | jq '[.[] | .dispersion
          | select(.pause_p50_ms != null and .pause_max_ms != null)
          | select(.pause_p50_ms != .pause_max_ms)] | length')" \
  || fail "AC3: 行を数えられない"
[ "${n_diff:-0}" -ge 1 ] \
  || fail "AC3: p50 != max の行が 0 件（★ 窓が効いていないか、fixture が窓に 2 本の pause を入れていない）"

# ── AC4: 陽性対照 —— 窓を 1 tick に戻すと同値に戻る ─────────────────────
#   ⚠️★★★ これが AC3 の「別の理由で緑になっていないか」を潰す (検査の検査 ルール 4/5)。
narrow="$(rows_of --set t1a_window_ms=1000)" \
  || fail "AC4: --set t1a_window_ms=1000 が非 0（★ issue 001 の --set が未実装か、キーが未登録）"
n_diff_narrow="$(printf '%s' "$narrow" | jq '[.[] | .dispersion
          | select(.pause_p50_ms != null and .pause_max_ms != null)
          | select(.pause_p50_ms != .pause_max_ms)] | length')" \
  || fail "AC4: 行を数えられない"
[ "${n_diff_narrow:-1}" -eq 0 ] \
  || fail "AC4: 窓を 1 tick に戻しても p50 != max の行が $n_diff_narrow 件ある（★ 窓が原因でない ＝ AC3 が空振り）"

# ⚠️ 不変式は窓の長さに関わらず保たれること
for label in wide narrow; do
  src="$wide"; [ "$label" = narrow ] && src="$narrow"
  printf '%s' "$src" | jq -e '
    all(.[] | .dispersion;
      (.pause_p50_ms == null or .pause_p90_ms == null or .pause_max_ms == null)
      or (.pause_p50_ms <= .pause_p90_ms and .pause_p90_ms <= .pause_max_ms))' >/dev/null 2>&1 \
    || fail "AC8: $label で p50 <= p90 <= max が成り立たない行がある"
done

# ── AC5〜7: 対応する単体テストが実在し、1 件ずつ走って緑であること ───────
for t in \
  window_is_causal_and_never_looks_ahead \
  window_does_not_span_a_feat_hole \
  window_does_not_change_iki_cv_or_surprise
do
  out="$(cargo test --workspace "$t" -- --exact --nocapture 2>&1)" || fail "test $t が赤"
  printf '%s' "$out" | grep -qE '1 passed' \
    || fail "test $t が 1 件も走っていない（★ cargo test は 0 件マッチでも exit 0 になる）"
done

# ── 前タスクの 003-acceptance.sh が緑（★ 期待値の更新を含めて） ──────────
( cd "$REPO_ROOT" && bash "$REPO_ROOT/.steering/20260914-mhd-feature-offline-tiers/issues/003-acceptance.sh" ) >/dev/null 2>&1 \
  || fail "前タスクの 003-acceptance.sh が非 0（★「3 値が同値」の検査を置き換えたか確認）"

echo "[acceptance 003w] OK"
