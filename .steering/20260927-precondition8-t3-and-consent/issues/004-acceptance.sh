#!/usr/bin/env bash
# issue 004 acceptance — 人単位ライフサイクル台帳の構築仕様書（T3 / B）
# ⚠️ cwd は worktree のルート。相対パスで書く。
set -u

DOC="docs/person-lifecycle-ledger-template.md"
FAILS=0
ok () { printf '  ✅ %s\n' "$1"; }
ng () { printf '  ❌ %s\n' "$1"; FAILS=$((FAILS + 1)); }
need () {
  if [ ! -f "$1" ]; then ng "$3: ファイルが無い ($1)"; return; fi
  if grep -qF -- "$2" "$1"; then ok "$3"; else ng "$3 (見つからない: $2)"; fi
}

echo "[004] 人単位ライフサイクル台帳の構築仕様書"

# AC 1
if [ -f "$DOC" ]; then ok "AC1 ${DOC} が存在する"; else ng "AC1 ${DOC} が無い"; exit 1; fi

# AC 2: 3 タブ
for t in "状態ログ" "現在の状態" "数える"; do
  need "$DOC" "$t" "AC2 タブ: ${t}"
done

# AC 3: 出来事の限定リスト 11 種（⚠️ 1 つ欠けたら赤）
for e in "案内" "登録" "配布" "開始" "中断" "やめた" "取り消し" "削除の求め" "完了" "未実施のまま据え置き" "名簿から外した"; do
  need "$DOC" "$e" "AC3 出来事: ${e}"
done

# AC 4: 矛盾検知 4 件（条件式つき）
need "$DOC" "D4-2b" "AC4 矛盾検知: D4-2b 違反（O1 が先）"
need "$DOC" "D4-2c" "AC4 矛盾検知: D4-2c（文言が空）"
need "$DOC" "赤"    "AC4 赤の条件がある"
need "$DOC" "黄"    "AC4 黄の条件がある"
# ★ 数式が逐語で書かれていること（= で始まる行が 1 行以上）
if grep -qE '^[[:space:]]*(\||`)?[[:space:]]*=' "$DOC"; then
  ok "AC4 数式が逐語で書かれている（= で始まる行がある）"
else
  ng "AC4 数式の逐語が無い（= で始まる行が 1 行も無い）"
fi

# AC 5: ⚠️ 禁止事項の明記
for w in "氏名" "メール" "理由は聞かない" "repo に置かない" "結合しない"; do
  need "$DOC" "$w" "AC5 禁止事項: ${w}"
done

# AC 6: ダミー P-ID の確認手順と「未実施」の明記
for w in "赤" "黄" "緑" "未実施"; do
  need "$DOC" "$w" "AC6 確認手順: ${w}"
done

# AC 7: ⚠️ 実 P-ID / ID / URL が入っていない
if grep -qE 'P0[0-9][0-9]' "$DOC"; then
  ng "AC7 ⚠️ 実 P-ID の形（P0xx）が混入している"
else
  ok "AC7 実 P-ID の混入なし"
fi
if grep -qE 'https?://' "$DOC"; then
  ng "AC7 ⚠️ URL が混入している（シートの ID / URL は repo に書かない）"
else
  ok "AC7 URL の混入なし"
fi
if grep -qE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' "$DOC"; then
  ng "AC7 ⚠️ メールアドレスが混入している"
else
  ok "AC7 メールアドレスの混入なし"
fi

echo "  ---- 失敗 ${FAILS} 件 ----"
[ "$FAILS" -eq 0 ] || exit 1
exit 0
