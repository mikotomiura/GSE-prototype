#!/bin/bash
# 指定のプロセス番号それぞれの累積 CPU 時間（ps の TIME）を、$1 秒の前後で読んで、1 コアに対する割合を出す。
# 使い方: cpu-window.sh <秒> <pid>...
set -u
SECS="$1"; shift
case "$SECS" in ""|*[!0-9]*|0) echo "秒は正の整数で渡す: $SECS" >&2; exit 2;; esac
readtime() { local t; t=$(ps -o time= -p "$1" | tr -d ' '); [ -n "$t" ] || { echo "pid=$1 が無い（消えた）" >&2; exit 3; }; echo "$t"; }
tosec() { awk -F'[:.]' '{ if (NF==3) print $1*60+$2+$3/100; else print $1*3600+$2*60+$3+$4/100 }' <<<"$1"; }
declare -a A
i=0; for p in "$@"; do t=$(readtime "$p") || exit 3; A[$i]=$(tosec "$t"); i=$((i+1)); done
sleep "$SECS"
i=0; tot=0
for p in "$@"; do
  t=$(readtime "$p") || exit 3; b=$(tosec "$t")
  pct=$(awk -v a="${A[$i]}" -v b="$b" -v s="$SECS" 'BEGIN{printf "%.2f", (b-a)/s*100}')
  echo "pid=$p cpu_pct=$pct"
  tot=$(awk -v t="$tot" -v x="$pct" 'BEGIN{print t+x}')
  i=$((i+1))
done
echo "total_pct=$tot"
