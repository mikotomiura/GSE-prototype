#!/usr/bin/env bash
# issue 002 (削除の最小幅) の AC 検査
#
# ⚠️ AC1〜6 は Rust の単体テストが持つ。ここで見るのは
#   (a) その test が実在して緑であること と (b) AC7 の文言だけである。
# ⚠️ 実行は repo 直下から。
set -uo pipefail
fail() { echo "[acceptance 002] NG: $*" >&2; exit 1; }

# ⚠️★★★ loop-run.sh は `( cd "$wt" && bash "$acc" )` で **worktree を cwd にして**呼ぶ
#   (scripts/loop-run.sh:369)。★ よって repo root は **cwd** であって、
#   ${BASH_SOURCE[0]} の位置 (= main checkout) ではない。
#   ⚠️ BASH_SOURCE から導くと **worktree ではなく main checkout を検査**してしまう。
REPO_ROOT="$(pwd)"
[ -f "$REPO_ROOT/src-tauri/Cargo.toml" ] || fail "cwd が repo root ではない（src-tauri/Cargo.toml が無い）: $REPO_ROOT"

# ── AC1〜6: 対応する test が実在し、名前指定で緑であること ───────────────
#   ⚠️★★★ `cargo test <name>` は **0 件マッチでも exit 0** である。
#     → 「マッチ件数」を必ず見る (検査の検査 ルール 4: 判定式が常に真にならないように)。
cd "$REPO_ROOT/src-tauri" || fail "src-tauri が無い"

for t in \
  min_redaction_width_matches_the_ui_granularity \
  min_redaction_width_exceeds_hole_gap \
  min_redaction_width_check_rejects_a_violating_pair \
  narrow_range_is_widened_to_the_minimum \
  wide_enough_range_is_not_widened \
  reversed_range_is_still_rejected
do
  out="$(cargo test --workspace "$t" -- --exact --nocapture 2>&1)" || fail "test $t が赤"
  # ⚠️ 「1 件走った」ことを確かめる。0 件だと cargo は緑で返す。
  printf '%s' "$out" | grep -qE '1 passed' \
    || fail "test $t が 1 件も走っていない（★ 名前が違う / 未実装のまま緑に見えている）"
done

# ── AC7: UI 文言と削除台帳の両方に「広げて消す」旨がある ────────────────
UI="$REPO_ROOT/src/components/RecordingControls.tsx"
LEDGER="$REPO_ROOT/docs/o1-deletion-ledger.md"
[ -f "$UI" ]     || fail "AC7: $UI が無い"
[ -f "$LEDGER" ] || fail "AC7: $LEDGER が無い"

grep -qE '(広げ|最小.*1 ?分|最小幅)' "$UI" \
  || fail "AC7: UI 文言に「広げて消す」旨が無い（${UI}）"
grep -qE '(広げ|最小幅)' "$LEDGER" \
  || fail "AC7: 削除台帳に「広げて消す」旨が無い（${LEDGER}）"

# ⚠️ 片側だけ直して緑になるのを防ぐ: 両方に `MIN_REDACTION_WIDTH_MS` か 60,000 の
#   具体値が現れることまで見る (★ 語が別の理由で出る可能性を潰す・検査の検査 ルール 5)。
grep -qE '(MIN_REDACTION_WIDTH_MS|60,?000|1 ?分)' "$UI" \
  || fail "AC7: UI 文言に具体的な最小幅が書かれていない"
grep -qE '(MIN_REDACTION_WIDTH_MS|60,?000|1 ?分)' "$LEDGER" \
  || fail "AC7: 削除台帳に具体的な最小幅が書かれていない"

echo "[acceptance 002] OK"
