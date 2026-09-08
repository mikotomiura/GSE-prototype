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
    # ⚠️★★★ `power` = Activity Monitor の「**エネルギー影響**」。★ sudo 不要。
    #   ★ これがあると **バッテリー% の対照実験が要らなくなる**（プロセス単位で取れるので）。
    #   ⚠️ **ワットではない**（CPU・wakeup・GPU・ディスクの Apple 内部の合成指標）ので、
    #   ★ 「何時間バッテリーが減るか」には**換算できない**。→ 参照プロセスと**比べて**読む。
    line=$(top -l 2 -pid "$pid" -stats cpu,mem,th,power -n 1 2>/dev/null | tail -1 || true)
    cpu=$(printf '%s' "$line" | awk '{print $1}')
    mem=$(printf '%s' "$line" | awk '{print $2}')
    # ⚠️★★★ macOS の `top` は `#TH` を **`31/1`（総数/実行中）**で出すことがある。
    #   ★ 2026-09-04 に実測: 880 サンプル中 **21 行**がこの形だった。
    #   ⚠️ そのまま書くと集計側が数値に変換できず、**その行を丸ごと捨てる**
    #   （★ CPU も RSS も一緒に消える）。→ ★ 先頭の数だけ採る。
    th=$(printf '%s'  "$line" | awk '{print $3}' | cut -d/ -f1)
    # ★ top の mem は "123M" / "546M+" 等。
    # ⚠️★★★ **`+` / `-` の接尾辞が付く**（前回サンプルからの増減の印）。
    #   ★ 2026-09-03 に実測: `pid,command` を stats に入れると `546M+` が出た。
    #   ⚠️ これを剥がさないと `/M$/` に当たらず **最後の分岐で 1024 で割られて 0 になる**
    #   （＝ 8 時間ぶんのメモリが黙って全部ゼロ）。→ ★ 先に落とす。
    mem=$(printf '%s' "$mem" | tr -d '+-')
    rss_kb=$(printf '%s' "$mem" | awk '/G$/{printf "%d", $0*1024*1024} /M$/{printf "%d", $0*1024} /K$/{printf "%d", $0} !/[GMK]$/{printf "%d", $0/1024}')
    pw=$(printf '%s' "$line" | awk '{print $4}' | tr -d '+-')
    # ★ 対照: `ps rss`（⚠️ top の MEM とは別物。env.md 参照）
    rss_alt=$(ps -o rss= -p "$pid" 2>/dev/null | tr -d ' ')
    # ⚠️★★ **参照プロセスの power を同時に採る。** ★ 単独の数値には意味が無い
    #   （エネルギー影響は無次元の合成指標）。→ ★ 「常駐している軽いアプリ」と比べる。
    ref_pid=$(pgrep -x Finder 2>/dev/null | head -1)
    if [ -n "$ref_pid" ]; then
      ref_pw=$(top -l 2 -pid "$ref_pid" -stats power -n 1 2>/dev/null | tail -1 | awk '{print $1}' | tr -d '+-')
    else ref_pw=""; fi
  else
    cpu=0; rss_kb=0; th=0; rss_alt=0; pw=0; ref_pw=""
  fi
  batt=$(pmset -g batt 2>/dev/null | grep -oE '[0-9]+%' | head -1 | tr -d '%' || true)
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$now" "${cpu:-0}" "${rss_kb:-0}" "${th:-0}" "${batt:-}" "${rss_alt:-0}" "${pw:-0}" "${ref_pw:-}"
  sleep "$INTERVAL_S"
done
