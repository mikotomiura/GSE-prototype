#!/usr/bin/env bash
# issue 003 acceptance — G1 削除保証台帳とゲート検査 [9]（前提条件 8 / A-3）
# ⚠️ cwd は worktree のルート。相対パスで書く。
set -u

LED="docs/g1-deletion-ledger.md"
O1LED="docs/o1-deletion-ledger.md"
HUB="docs/agent-shared.md"
GATE="scripts/check-g1-collection-readiness.sh"
FAILS=0
ok () { printf '  ✅ %s\n' "$1"; }
ng () { printf '  ❌ %s\n' "$1"; FAILS=$((FAILS + 1)); }
need () {
  if [ ! -f "$1" ]; then ng "$3: ファイルが無い ($1)"; return; fi
  if grep -qF -- "$2" "$1"; then ok "$3"; else ng "$3 (見つからない: $2)"; fi
}
forbid () {
  if [ ! -f "$1" ]; then ng "$3: ファイルが無い ($1)"; return; fi
  if grep -qF -- "$2" "$1"; then ng "$3 (⚠️ 在ってはいけない: $2)"; else ok "$3"; fi
}

echo "[003] G1 削除保証台帳とゲート検査 [9]"

# AC 1: 台帳が存在し必須節を持つ
if [ -f "$LED" ]; then ok "AC1 ${LED} が存在する"; else ng "AC1 ${LED} が無い"; fi
for s in "削除要求の経路" "削除チェックリスト" "保管上限" "実施記録" "この台帳自身の検査"; do
  need "$LED" "$s" "AC1 必須節: ${s}"
done

# AC 2: consent.md §5 の対象を網羅（★ G1 固有の 5 種）
for t in "blocks/" ".age" "results/" "記録用紙" "回答シート"; do
  need "$LED" "$t" "AC2 削除対象: ${t}"
done

# AC 3: ⚠️ O1 の 48 時間の猶予を流用していない
forbid "$LED" "48 時間" "AC3 O1 の 48 時間の猶予を流用していない"
if grep -qF "猶予" "$LED"; then
  if grep -qF "無い" "$LED" || grep -qF "存在しない" "$LED"; then
    ok "AC3 猶予が無いことを明記している"
  else
    ng "AC3 「猶予」に触れているが「無い/存在しない」と書いていない"
  fi
else
  ng "AC3 G1 に猶予が無いことへの言及が無い"
fi

# AC 4: 保管上限の機械可読マーカ（⚠️ unset でも緑・行ごと消えたら赤）
need "$LED" "g1-retention:" "AC4 保管上限の機械可読マーカがある"

# AC 5: ⚠️ 実名・メールアドレスを書いていない
if [ -f "$LED" ] && grep -qE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' "$LED"; then
  ng "AC5 ⚠️ メールアドレスらしい文字列が混入している"
else
  ok "AC5 メールアドレスの混入なし"
fi
forbid "$LED" "三浦尊統" "AC5 実名の混入なし"

# AC 6: ゲートに検査 [9] があり、未達が記録票 A/B/C の 3 件だけ
gout="$(bash "$GATE" 2>&1)"
if printf '%s' "$gout" | grep -qF "前提条件 8"; then ok "AC6 ゲートに検査 [9] 前提条件 8 がある"; else ng "AC6 ゲートに検査 [9] 前提条件 8 が無い"; fi
# ⚠️ `printf | grep -q` の SIGPIPE を避けるため一時ファイルに落として数える。
#    ⚠️ ❌ の行数を数えてはいけない —— ゲートは末尾に総括の ❌ を 1 行足すので 3 件でも 4 になる
#    （★ 2026-09-27 に実測）。→ ★ **「未達 N 件」の行から N を取る。**
tmp="$(mktemp)"; printf '%s\n' "$gout" > "$tmp"
nng="$(sed -n 's/.*未達 \([0-9]\{1,\}\) 件.*/\1/p' "$tmp" | tail -1)"
nrec=$(grep -c '記録票 [ABC] ' "$tmp")
if [ "${nng:-none}" = "3" ] && [ "$nrec" -ge 3 ]; then
  ok "AC6 未達が 3 件で、その 3 件が記録票 A/B/C"
else
  ng "AC6 未達が ${nng:-読めない} 件（記録票 A/B/C の 3 件だけであること。記録票の行 ${nrec} 件）"
fi
rm -f "$tmp"

# AC 7: ゲート自身の空回り検査
if bash "$GATE" --selftest >/dev/null 2>&1; then
  ok "AC7 ゲートの --selftest が exit 0"
else
  ng "AC7 ゲートの --selftest が赤"
fi

# AC 8: 検査 [7] の古い注記が直っている
forbid "$GATE" "計器は未対応" "AC8 検査 [7] の古い注記が消えている"

# AC 9: リンクハブに 2 文書
n=0
grep -qF "g1-deletion-ledger" "$HUB" && n=$((n + 1))
grep -qF "person-lifecycle-ledger-template" "$HUB" && n=$((n + 1))
if [ "$n" -eq 2 ]; then ok "AC9 リンクハブに 2 文書が載っている"; else ng "AC9 リンクハブに載っているのは ${n} 件"; fi

# AC 10: O1 版からの相互参照
need "$O1LED" "g1-deletion-ledger" "AC10 O1 版から G1 版への相互参照がある"

# ★ 参照先の実体（issue 004 の成果物）が在ること
if [ -f "docs/person-lifecycle-ledger-template.md" ]; then
  ok "AC-dep 参照先 docs/person-lifecycle-ledger-template.md が実在する"
else
  ng "AC-dep 参照先 docs/person-lifecycle-ledger-template.md が無い（issue 004 が未マージ）"
fi

echo "  ---- 失敗 ${FAILS} 件 ----"
[ "$FAILS" -eq 0 ] || exit 1
exit 0
