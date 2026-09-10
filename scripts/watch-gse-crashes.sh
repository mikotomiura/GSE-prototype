#!/usr/bin/env bash
# ★ `gse-next` の**クラッシュと無言停止**を見張り、起きたら台帳へ 1 行書く。
#
# ⚠️★★★ なぜ要るか: 2026-09-10 に **10〜40 分ごとに SIGSEGV** で落ちていたのに、
#   ★ 気づいたのは**たまたま `pgrep` を見たから**だった（★ 通知も画面変化も無い）。
#   ★ v0.1.34 の修正が効いたかを言うには、⚠️ **「落ちなかった」を機械で記録する**しかない。
#
# 使い方:  nohup bash scripts/watch-gse-crashes.sh > /dev/null 2>&1 & disown
#          （★ 既定で 8 時間見張る。第 1 引数で秒数を変えられる）
set -uo pipefail
DUR="${1:-28800}"
LEDGER="${GSE_CRASH_LEDGER:-$HOME/Documents/GSE-sessions/crash-watch.tsv}"
# ⚠️★ 監視対象は**差し替えられる**ようにする —— ★ さもないと**陽性対照が取れない**
#   （★ 本物のクラッシュを起こさないと「検出できる」ことを確かめられなくなる）。
DR="${GSE_CRASH_DR:-$HOME/Library/Logs/DiagnosticReports}"
PROC="${GSE_CRASH_PROC:-gse-next}"
APP_PLIST="$HOME/Desktop/O1_計測用_macOS/gse-next.app/Contents/Info.plist"

# ⚠️ 陽性対照: 監視対象のディレクトリが無ければ **判定しない**（★「0 件＝健全」を出さない）
[ -d "$DR" ] || { echo "⚠️ $DR が無い → 判定しない"; exit 2; }

[ -s "$LEDGER" ] || printf 'utc\tevent\tdetail\n' > "$LEDGER"
note() { printf '%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$1" "$2" >> "$LEDGER"; }

count_ips() { ls -1 "$DR" 2>/dev/null | grep -c "^${PROC}-"; }

SEEN=$(count_ips)
START_PID=$(pgrep -x "$PROC" | head -1)
VER=$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "$APP_PLIST" 2>/dev/null || echo unknown)
note start "seen_ips=$SEEN pid=${START_PID:-none} version=$VER dur=${DUR}s"

END=$(( $(date +%s) + DUR ))
LAST_PID="$START_PID"
while [ "$(date +%s)" -lt "$END" ]; do
  NOW=$(count_ips)
  if [ "$NOW" -gt "$SEEN" ]; then
    NEW=$(ls -1t "$DR" | grep "^${PROC}-" | head -1)
    note crash "$NEW"
    SEEN="$NOW"
  fi
  PID=$(pgrep -x "$PROC" | head -1)
  if [ -z "$PID" ]; then
    if [ -n "$LAST_PID" ]; then note gone "last_pid=$LAST_PID"; fi
    LAST_PID=""
  elif [ "$PID" != "$LAST_PID" ]; then
    # ⚠️ pid が変わった ＝ 落ちて上がり直した（★ クラッシュ報告が無くても捕まえる）
    note restarted "old=${LAST_PID:-none} new=$PID"
    LAST_PID="$PID"
  fi
  sleep "${GSE_CRASH_INTERVAL:-30}"
done
note end "seen_ips=$SEEN pid=${LAST_PID:-none}"
