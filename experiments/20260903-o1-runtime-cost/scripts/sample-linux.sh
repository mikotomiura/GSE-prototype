#!/usr/bin/env bash
# ★ Linux は対象 OS ではない (Windows / macOS のみ)。⚠️ 開発機での動作確認用。
set -euo pipefail
DURATION_S="$1"; INTERVAL_S="$2"
end=$(( $(date +%s) + DURATION_S ))
while [ "$(date +%s)" -lt "$end" ]; do
  now=$(date +%s)
  pid=$(pgrep -x 'gse-next' 2>/dev/null | head -1 || true)
  if [ -n "$pid" ]; then
    read -r cpu rss th < <(ps -o %cpu=,rss=,nlwp= -p "$pid" | awk '{print $1, $2, $3}')
  else
    cpu=0; rss=0; th=0
  fi
  printf '%s\t%s\t%s\t%s\t%s\n' "$now" "${cpu:-0}" "${rss:-0}" "${th:-0}" ""
  sleep "$INTERVAL_S"
done
