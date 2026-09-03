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
    # ★ top の mem は "123M" / "546M+" 等。
    # ⚠️★★★ **`+` / `-` の接尾辞が付く**（前回サンプルからの増減の印）。
    #   ★ 2026-09-03 に実測: `pid,command` を stats に入れると `546M+` が出た。
    #   ⚠️ これを剥がさないと `/M$/` に当たらず **最後の分岐で 1024 で割られて 0 になる**
    #   （＝ 8 時間ぶんのメモリが黙って全部ゼロ）。→ ★ 先に落とす。
    mem=$(printf '%s' "$mem" | tr -d '+-')
    rss_kb=$(printf '%s' "$mem" | awk '/G$/{printf "%d", $0*1024*1024} /M$/{printf "%d", $0*1024} /K$/{printf "%d", $0} !/[GMK]$/{printf "%d", $0/1024}')
    # ★ 対照: `ps rss`（⚠️ top の MEM とは別物。env.md 参照）
    rss_alt=$(ps -o rss= -p "$pid" 2>/dev/null | tr -d ' ')
  else
    cpu=0; rss_kb=0; th=0; rss_alt=0
  fi
  batt=$(pmset -g batt 2>/dev/null | grep -oE '[0-9]+%' | head -1 | tr -d '%' || true)
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$now" "${cpu:-0}" "${rss_kb:-0}" "${th:-0}" "${batt:-}" "${rss_alt:-0}"
  sleep "$INTERVAL_S"
done
