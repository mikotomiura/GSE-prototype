#!/bin/bash
# 残りの CPU の出どころを探す: main.tsx の一時的な TIMER-PROBE を環境変数で切り替えて、O1 の形の開発版を順に起動して測る。
# 使い方: timer-rounds.sh <作業フォルダ> <差し替え>...（差し替えは none / all / 1000 などの間隔の並び）
set -u
W="$1"; shift
P=/Users/johnd/GSE-prototype-pause-resume/.steering/20261031-trim-ui-polling/probe
stop_dev() {
  local m; m=$(pgrep -f "target/debug/gse-next"); [ -n "$m" ] && kill $m; sleep 2
  local ps; ps=$(ps -axo pid,command | grep -E "gse-next-trim-polling|20261031-trim-ui-polling/probe/run-dev|pause-resume/node_modules/(\.bin/vite|@esbuild)" | grep -v grep | awk '{print $1}')
  [ -n "$ps" ] && kill $ps 2>/dev/null; sleep 2
}
for r in "$@"; do
  ps -axo pid= | sort -n > "$W/pre-$r.txt"
  if [ "$r" = none ]; then unset VITE_PROBE_BLOCK_DELAYS; else export VITE_PROBE_BLOCK_DELAYS="$r"; fi
  L="$W/round-$r.log"
  "$P/run-dev-o1.sh" "$L" &
  for i in $(seq 1 150); do grep -qE "SessionLogger: writing" "$L" 2>/dev/null && break; sleep 2; done
  sleep 45
  if python3 "$P/procs.py" target/debug/gse-next "$W/pre-$r.txt" 4 > "$W/pids-$r.txt"; then
    echo "## round=$r"
    for k in 1 2; do date -u +%T; "$P/cpu-window.sh" 60 $(awk '{print $1}' "$W/pids-$r.txt"); done
    m=$(head -1 "$W/pids-$r.txt" | cut -d' ' -f1)
    echo "session: $("$W/axdump" "$m" | grep -A1 'v=SESSION' | tail -1) / 3s later: $(sleep 3; "$W/axdump" "$m" | grep -A1 'v=SESSION' | tail -1)"
  else
    echo "## round=$r procs.py failed rc=$?"
  fi
  T=$(head -1 "$L" | cut -d= -f2)
  stop_dev
  case "$T" in /var/folders/*/tmp.*) rm -rf "$T";; esac
done
ps -axo pid,command | grep -E "gse-next-trim|target/debug/gse-next|pause-resume/node_modules" | grep -v grep
echo done
