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
#   ⚠️ 「どれか 1 行が合えば通る」では、別の行で D9 を裁いていても素通りする。
#     ★ 壁時計を含む行は **1 行残らず** 未決の語を持つことを要求する（語の無い行を列挙して赤にする）。
bad_d9="$(printf '%s\n' "$amend2_body" | grep -E '壁時計' | grep -vE '(未決|決めない|範囲外|P1 の実データ)' || true)"
[ -z "$bad_d9" ] \
  || fail "AC4: 補訂 2 の次の行が壁時計 (D9) を「未決」と言わずに書いている（★ 研究者判断は「P1 の実データの後」）: $bad_d9"

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
#     ★ base は「補訂 2 の見出しを初めて足したコミットの**親**」（★ 2026-09-25 メイン修正）。
#     ⚠️ 旧式は `_loop-config.json` の base_branch（＝ 作業ブランチ自身）を使っていたので、009 を merge した後は
#       BASE == HEAD となり「追記が 1 バイトも無い」で**必ず赤**になった（★ main へ入った後も同じ）。
#     ★ 見出しで引けない場合（worktree で未コミット等）だけ、従来どおり base_branch → origin/main へ退く。
#     ★ `ACC_009_BASE` で明示指定できる（検査の検査用）。
BASE="${ACC_009_BASE:-}"
if [ -z "$BASE" ]; then
  intro="$(git log --format=%H -S'## 補訂 2（2026-09-25）' -- "$ADR" 2>/dev/null | tail -1)"
  [ -n "$intro" ] && BASE="${intro}^"
fi
if [ -z "$BASE" ]; then
  BASE="$(sed -nE 's/.*"base_branch" *: *"([^"]+)".*/\1/p' \
          .steering/20260921-p1-prereg-cli-poles/_loop-config.json 2>/dev/null | head -1)"
fi
[ -n "${BASE:-}" ] || BASE="origin/main"
git rev-parse --verify "$BASE" >/dev/null 2>&1 || BASE="origin/main"
git rev-parse --verify "$BASE" >/dev/null 2>&1 \
  || fail "AC2/AC6: 比較対象のブランチを解決できない（${BASE}）"

#   ⚠️★★★ 検査の検査（2026-09-25）: 旧式の `git diff | grep -cE '^-[^-]'` は **箇条書きの削除を数え落とす**。
#     markdown の `- foo` を消すと diff では `-- foo`（先頭が `--`）になり、`^-[^-]` に当たらない。
#     ★ 空行の削除（diff では `-` だけの行）も同じく当たらない。→ この 2 本の文書は箇条書きだらけなので、
#       旧式は「本文を書き換えていない」ことを実質的に何も確かめていなかった。
#     ★ `git diff --numstat` の削除行数（2 列目）は行頭の文字に依らないので、これで数える。
for f in "$ADR" "$BLK"; do
  stat="$(git diff --numstat "$BASE" -- "$f")" \
    || fail "AC2/AC6: git diff --numstat が失敗した: $f"
  if [ -n "$stat" ]; then
    del="$(printf '%s\n' "$stat" | awk -F'\t' 'NR == 1 { print $2 }')"
  else
    del=0
  fi
  case "$del" in
    ''|*[!0-9]*) fail "AC2/AC6: $f の削除行数を読めない（numstat: ${stat}）" ;;
  esac
  [ "$del" -eq 0 ] \
    || fail "AC2/AC6: $f に削除行が $del 行ある（★ 本文・起票本文は追記のみの規約）"
done

# ── AC2 (強): ADR は「元の全バイトが接頭辞として残っている」＝ 末尾への追記だけ ─────
#   ⚠️ 削除行が 0 でも、本文の**途中に**行を挿入する変更は通ってしまう（AC2 は「追加行が補訂 2 より後だけ」）。
#     ★ base の blob と、作業ツリーの先頭から同じバイト数を切ったものが一致することで確かめる。
base_size="$(git cat-file -s "$BASE:$ADR")" \
  || fail "AC2: base の ADR のサイズを取れない（${BASE}:${ADR}）"
# ⚠️ `git show` が失敗すると空入力の sha1 が入り `-n` を通ってしまう（security-checker LOW）→ 先に blob を取り出して失敗を拾う。
base_blob="$(mktemp)" || fail "AC2: 一時ファイルを作れない"
git show "$BASE:$ADR" > "$base_blob" || { rm -f "$base_blob"; fail "AC2: base の ADR を取り出せない（${BASE}:${ADR}）"; }
base_sha="$(sha1sum < "$base_blob" | cut -d' ' -f1)"
rm -f "$base_blob"
work_sha="$(head -c "$base_size" "$ADR" | sha1sum | cut -d' ' -f1)"
[ -n "$base_sha" ] && [ "$base_sha" = "$work_sha" ] \
  || fail "AC2: ADR-030 の既存の本文が（追記以外で）変わっている（base=${base_sha} work=${work_sha}・先頭 ${base_size} バイト）"
[ "$(wc -c < "$ADR")" -gt "$base_size" ] \
  || fail "AC2: ADR-030 に追記が 1 バイトも無い（補訂 2 が入っていない）"

# ── AC5 (補): 起票 12 を「閉じた」と書いていない（★ 数える計器だけ・抑制は未決）─────────
awk '
  $0 ~ "^## 起票 12(:|：)" { inblk=1; next }
  inblk && /^## 起票 /    { exit ok ? 0 : 1 }
  inblk && /閉じていない/ { ok=1 }
  END { exit (inblk && ok) ? 0 : 1 }
' "$BLK" || fail "AC5: 起票 12 の是正記録に「閉じていない」が無い（★ 抑制は P1 の頻度を見てから）"

# ── AC7: tasklist の 004 / 006 が [x] になっている ──────────────────────
grep -qE '^- \[x\] *004' "$TL" || fail "AC7: tasklist の 004 が [x] になっていない"
grep -qE '^- \[x\] *006' "$TL" || fail "AC7: tasklist の 006 が [x] になっていない"
grep -qE '6f5bb9f|9eb539d' "$TL" \
  || fail "AC7: tasklist に 004/006 の merge コミットが書かれていない"

echo "[acceptance 009] OK"
