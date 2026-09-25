#!/usr/bin/env bash
# issue 009 (ADR-030 補訂 2 ＋ 起票の是正記録) の AC 検査
# ⚠️ 実行は repo 直下から。文書だけを見る (コードは触らない issue)。
set -uo pipefail
fail() { echo "[acceptance 009] NG: $*" >&2; exit 1; }

# ⚠️★★★ loop-run.sh は `( cd "$wt" && bash "$acc" )` で **worktree を cwd にして**呼ぶ
#   (scripts/loop-run.sh:369)。★ よって repo root は **cwd** であって、
#   ${BASH_SOURCE[0]} の位置 (= main checkout) ではない。
#   ⚠️ BASH_SOURCE から導くと **worktree ではなく main checkout を検査**してしまう。
REPO_ROOT="$(pwd)"
[ -f "$REPO_ROOT/src-tauri/Cargo.toml" ] || fail "cwd が repo root ではない（src-tauri/Cargo.toml が無い）: $REPO_ROOT"
cd "$REPO_ROOT" || fail "repo root へ移動できない"

ADR="docs/adr/ADR-030-stall-onset-and-decision-episode.md"
BLK=".steering/20260914-mhd-feature-offline-tiers/blockers.md"
TL=".steering/20260914-mhd-feature-offline-tiers/tasklist.md"
for f in "$ADR" "$BLK" "$TL"; do [ -f "$f" ] || fail "$f が無い"; done

# ── AC1: 補訂 2 の節と冒頭の表 ──────────────────────────────────────────
grep -qE '^## 補訂 2' "$ADR" || fail "AC1: ADR-030 に「## 補訂 2」の節が無い"
amend2_line="$(grep -nE '^## 補訂 2' "$ADR" | head -1 | cut -d: -f1)" \
  || fail "AC1: 補訂 2 の行番号を取れない"
# ★ 補訂 2 の直後 30 行以内に表（| … | … |）があること
sed -n "${amend2_line},$((amend2_line + 30))p" "$ADR" | grep -qE '^\|.*\|.*\|' \
  || fail "AC1: 補訂 2 の冒頭に「何を上書きし何を規範へ上げるか」の表が無い"

# ── AC3: 6 点が規範になっている ─────────────────────────────────────────
amend2_body="$(sed -n "${amend2_line},\$p" "$ADR")" || fail "AC3: 補訂 2 の本文を取れない"
check_in_amend2() {
  printf '%s' "$amend2_body" | grep -qE "$1" || fail "AC3: 補訂 2 に「$2」が無い（正規表現: $1）"
}
check_in_amend2 '事前宣言文書'                    '運用値は事前宣言文書が持つ'
check_in_amend2 '(凍結 JSON|--feature-config|--set)' 'CLI 注入の形'
check_in_amend2 '(1 実行 1 極|--pole)'            '極は 1 実行 1 極'
check_in_amend2 '(Cartesian|直積)'                'Cartesian を作らない'
check_in_amend2 '観測区間'                        '極 B の抑制は観測区間と同じ構造'
check_in_amend2 '(no_modifier_rows|modifier. 行が 0 本|修飾キーの行が 0 本)' '極 M+ の not_applicable の判定式'
check_in_amend2 '(30 秒|t1a_window_ms|30,000)'    'T1a の 30 秒窓'

# ── AC4: D9 を裁いていない ──────────────────────────────────────────────
#   ⚠️ 「壁時計」が出るのは構わないが、「未決のまま」であることが書かれていること。
if printf '%s' "$amend2_body" | grep -qE '壁時計'; then
  printf '%s' "$amend2_body" | grep -E '壁時計' | grep -qE '(未決|決めない|範囲外|P1 の実データ)' \
    || fail "AC4: 補訂 2 が壁時計 (D9) を裁いている疑い（★ 研究者判断は「P1 の実データの後」）"
fi

# ── AC5: 起票 8 件に「✅ 是正済み」がある ───────────────────────────────
for n in 7 11 12 13 14 15 16 21; do
  # ★ 起票 n の見出しから、次の「## 起票」までの範囲に ✅ 是正済み があること
  awk -v n="$n" '
    $0 ~ "^## 起票 " n "[:：]" { inblk=1; found=0; next }
    inblk && /^## 起票 /       { exit found ? 0 : 1 }
    inblk && /✅ *是正済み/    { found=1 }
    END { exit (inblk && found) ? 0 : 1 }
  ' "$BLK" || fail "AC5: 起票 $n に「✅ 是正済み」の節が無い"
done

# ── AC2 / AC6: 削除行が 0 であること ────────────────────────────────────
#   ⚠️★★★ 「本文を書き換えていない」は **削除行の不在** でしか確かめられない。
#     ★ base は _loop-config.json の base_branch。取れなければ origin/main へ退く。
BASE="$(sed -nE 's/.*"base_branch" *: *"([^"]+)".*/\1/p' \
        .steering/20260921-p1-prereg-cli-poles/_loop-config.json 2>/dev/null | head -1)"
[ -n "${BASE:-}" ] || BASE="origin/main"
git rev-parse --verify "$BASE" >/dev/null 2>&1 || BASE="origin/main"
git rev-parse --verify "$BASE" >/dev/null 2>&1 \
  || fail "AC2/AC6: 比較対象のブランチを解決できない（$BASE）"

for f in "$ADR" "$BLK"; do
  del="$(git diff "$BASE" -- "$f" | grep -cE '^-[^-]' || true)"
  [ "${del:-0}" -eq 0 ] \
    || fail "AC2/AC6: $f に削除行が $del 行ある（★ 本文・起票本文は追記のみの規約）"
done

# ── AC7: tasklist の 004 / 006 が [x] になっている ──────────────────────
grep -qE '^- \[x\] *004' "$TL" || fail "AC7: tasklist の 004 が [x] になっていない"
grep -qE '^- \[x\] *006' "$TL" || fail "AC7: tasklist の 006 が [x] になっていない"
grep -qE '6f5bb9f|9eb539d' "$TL" \
  || fail "AC7: tasklist に 004/006 の merge コミットが書かれていない"

echo "[acceptance 009] OK"
