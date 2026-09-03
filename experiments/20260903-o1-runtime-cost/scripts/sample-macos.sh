#!/usr/bin/env bash
# macOS: GSE のプロセスを INTERVAL 秒ごとにサンプルする。
# ⚠️★★★ プロセス名以外は 1 つも記録しない (★ 他プロセスの列挙・ウィンドウ名は取らない)。
set -euo pipefail
DURATION_S="$1"; INTERVAL_S="$2"
end=$(( $(date +%s) + DURATION_S ))
while [ "$(date +%s)" -lt "$end" ]; do
  now=$(date +%s)
  # ★ GSE 本体の pid。⚠️ 無ければ (対照 = without-gse) 空行を 0 で埋める。
  pid=$(pgrep -x 'gse-next' 2>/dev/null | head -1 || true)
  if [ -n "$pid" ]; then
    # ⚠️ `ps` の %cpu は「起動以降の平均」なので使わない。★ top の 1 サンプルを採る。
    line=$(top -l 2 -pid "$pid" -stats cpu,mem,th -n 1 2>/dev/null | tail -1 || true)
    cpu=$(printf '%s' "$line" | awk '{print $1}')
    mem=$(printf '%s' "$line" | awk '{print $2}')
    th=$(printf '%s'  "$line" | awk '{print $3}')
    # ★ top の mem は "123M" 等。⚠️ KB に揃える。
    rss_kb=$(printf '%s' "$mem" | awk '/G$/{printf "%d", $0*1024*1024} /M$/{printf "%d", $0*1024} /K$/{printf "%d", $0} !/[GMK]$/{printf "%d", $0/1024}')
  else
    cpu=0; rss_kb=0; th=0
  fi
  batt=$(pmset -g batt 2>/dev/null | grep -oE '[0-9]+%' | head -1 | tr -d '%' || true)
  printf '%s\t%s\t%s\t%s\t%s\n' "$now" "${cpu:-0}" "${rss_kb:-0}" "${th:-0}" "${batt:-}"
  sleep "$INTERVAL_S"
done
