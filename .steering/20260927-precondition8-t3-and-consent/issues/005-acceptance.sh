#!/usr/bin/env bash
# issue 005 acceptance — consent.md ほか 3 文書の差分案（C）
# ⚠️ cwd は worktree のルート。相対パスで書く。
# ⚠️★★★ 本 issue の核心は「**実ファイルを 1 文字も変えていない**」ことなので、AC2 を最初に見る。
set -u

DOC=".steering/20260927-precondition8-t3-and-consent/consent-diff-proposal.md"
G1DIR="experiments/20260801-controlled-friction-task"
FAILS=0
ok () { printf '  ✅ %s\n' "$1"; }
ng () { printf '  ❌ %s\n' "$1"; FAILS=$((FAILS + 1)); }
need () {
  if [ ! -f "$1" ]; then ng "$3: ファイルが無い ($1)"; return; fi
  if grep -qF -- "$2" "$1"; then ok "$3"; else ng "$3 (見つからない: $2)"; fi
}

echo "[005] consent.md ほか 3 文書の差分案（適用しない）"

# AC 2（最優先）: ⚠️ 被験者向け文書・フォームのコードが 1 文字も変わっていない
#   ★ HEAD と比べる（worker はコミットしてから終わるので、HEAD が worker の成果物である）。
UNTOUCHED="${G1DIR}/consent.md ${G1DIR}/protocol.md Form_G1/README.md Form_G1/GSE_G1_Form_Builder.gs"
# ★ 基準は本タスクの作業ブランチ（worktree は共有 .git を見るので ref は引ける）。
BASE="feature/precondition8-t3-and-consent"
git rev-parse --verify --quiet "$BASE" >/dev/null || BASE=""
if [ -n "$BASE" ]; then
  # ⚠️★★★ 2026-09-27 修正 1 回目（Codex P2 1 巡目・実測で確認）: 旧版は
  #   `git diff --quiet -- $UNTOUCHED`（引数無し＝作業ツリー対 index）で「作業ツリーの
  #   未コミット変更」しか見ておらず、禁止ファイルを編集して `git add`（staged だが
  #   コミットしていない）した場合は index も作業ツリーも一致するため**すり抜けた**。
  #   → `git diff --quiet HEAD -- ...`（作業ツリー対 HEAD）に変更。
  # ⚠️★★★ 2026-09-27 修正 2 回目（Codex / code-reviewer 2 巡目・実測で再現確認）:
  #   `git diff <ref>`（`--cached` 無し）は **index を経由せず** HEAD のツリーと**作業ツリーの
  #   ディスク内容**を直接比べる。禁止ファイルを編集して `git add`（staged）した後、
  #   **作業ツリーだけ元の内容に手で戻す**と、index には禁止変更が残ったまま
  #   `git diff HEAD -- ...` は「差分無し」を返す（実機で再現済み）。その状態で
  #   `git commit`（`git add` し直さない）すると index の禁止変更がそのまま commit される。
  #   → `git diff --quiet --cached -- ...`（index 対 HEAD）を**併せて**検査し、
  #   index 側の差分も取りこぼさない。
  # shellcheck disable=SC2086
  if git diff --quiet "$BASE" HEAD -- $UNTOUCHED \
     && git diff --quiet HEAD -- $UNTOUCHED \
     && git diff --quiet --cached -- $UNTOUCHED; then
    ok "AC2 被験者向け文書とフォームのコードに差分が無い（対 ${BASE} ＋ HEAD 対 作業ツリー ＋ HEAD 対 index）"
  else
    ng "AC2 ⚠️★★★ 被験者向け文書またはフォームのコードが変更されている（本 issue は提案のみ）"
  fi
else
  # ⚠️ 基準が引けないときは緑にしない（fail-closed）。
  ng "AC2 基準ブランチ ${BASE:-feature/precondition8-t3-and-consent} を引けないので不変を確かめられない"
fi

# AC 1
if [ -f "$DOC" ]; then ok "AC1 ${DOC} が存在する"; else ng "AC1 ${DOC} が無い"; echo "  ---- 失敗 ${FAILS} 件 ----"; exit 1; fi

# AC 3: C-1 / C-2 / C-3 と 3 つのファイル名
for w in "C-1" "C-2" "C-3" "consent.md" "protocol.md" "Form_G1/README.md"; do
  need "$DOC" "$w" "AC3 扱っている: ${w}"
done

# AC 4: 現在の行と案が逐語である
need "$DOC" "中断が 0 回の分は記録しません" "AC4 C-1 の逐語（consent.md 側）"
need "$DOC" "計測中のみ"                     "AC4 C-1 の逐語（フォーム側）"
need "$DOC" "打鍵の記録（本文を除く）"       "AC4 C-2 の逐語（フォーム側）"
need "$DOC" "migrateConsentForm"             "AC4 C-3 の対象"

# AC 5: ⚠️ 根拠の限界
need "$DOC" "checkConsentFormParity" "AC5 根拠（parity 関数）を書いている"
need "$DOC" "目視"                   "AC5 実フォームを目視していない旨を書いている"

# AC 6: 反映手順の実行禁止
need "$DOC" "setupG1Forms" "AC6 実行禁止の関数名がある"
need "$DOC" "実行しない"   "AC6 実行しない旨が書かれている"

# AC 7: 3 文書同時改訂の規約
need "$DOC" "同時" "AC7 3 文書同時改訂の規約に触れている"

echo "  ---- 失敗 ${FAILS} 件 ----"
[ "$FAILS" -eq 0 ] || exit 1
exit 0
