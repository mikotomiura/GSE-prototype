#!/usr/bin/env bash
# 多世代往復テスト。
# ★ 「exit code / ファイルの存在」で成功と判定しない。
#    toecollapse が実際に新しいファイルを書いたことを、bkp が作られたかで確認する。
set -u

WORK="$1"
SRC="$2"
BASE="$(basename "$SRC")"

TOEEXPAND="/c/Program Files/Derivative/TouchDesigner/bin/toeexpand.exe"
TOECOLLAPSE="/c/Program Files/Derivative/TouchDesigner/bin/toecollapse.exe"

GEN="$WORK/gen2"
mkdir -p "$GEN"
cp "$SRC" "$GEN/g0.$BASE"

cd "$GEN" || exit 1

printf '%-4s %-10s %-18s %-11s %s\n' gen size sha256_16 collapse_ok tree_vs_gen0
printf '%-4s %-10s %-18s %-11s %s\n' 0 "$(stat -c%s "g0.$BASE")" "$(sha256sum "g0.$BASE" | cut -c1-16)" - -

for i in 1 2 3; do
  prev=$((i - 1))
  d="$GEN/w$i"
  mkdir -p "$d"
  cp "$GEN/g${prev}.$BASE" "$d/$BASE"

  # --- expand ---
  ( cd "$d" && "$TOEEXPAND" "$BASE" > expand.log 2>&1 )
  if ! grep -q "expanded into directory" "$d/expand.log"; then
    echo "FAIL: expand gen$prev -> $(cat "$d/expand.log")"; exit 1
  fi
  # 展開ツリーを世代 0 と比較するために保存
  cp -r "$d/$BASE.dir" "$GEN/tree${prev}.dir"

  # --- collapse (.toc を残したまま行う) ---
  ( cd "$d" && "$TOECOLLAPSE" "$BASE.dir" > collapse.log 2>&1 )
  # ★ 成功判定は「bkp へ退避した」というメッセージの実在で行う (exit code ではない)
  if grep -q "moved to" "$d/collapse.log"; then ok=YES; else ok="NO:$(tr -d '\n' < "$d/collapse.log")"; fi
  cp "$d/$BASE" "$GEN/g${i}.$BASE"

  if [ "$prev" -gt 0 ]; then
    if diff -rq "$GEN/tree0.dir" "$GEN/tree${prev}.dir" > /dev/null 2>&1; then t=IDENTICAL; else t=DIFFERS; fi
  else
    t=base
  fi
  printf '%-4s %-10s %-18s %-11s %s\n' "$i" "$(stat -c%s "$GEN/g${i}.$BASE")" \
    "$(sha256sum "$GEN/g${i}.$BASE" | cut -c1-16)" "$ok" "$t"
done

echo "--- 最終世代のツリーを世代0と比較 ---"
d="$GEN/w3"
cp -r "$d/$BASE.dir" "$GEN/tree3.dir" 2>/dev/null
if diff -rq "$GEN/tree0.dir" "$GEN/tree3.dir" > /dev/null 2>&1; then
  echo "tree0 vs tree3: IDENTICAL"
else
  echo "tree0 vs tree3: DIFFERS"
  diff -rq "$GEN/tree0.dir" "$GEN/tree3.dir" | head -20
fi
