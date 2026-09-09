#!/usr/bin/env bash
# macOS: GSE のプロセスを INTERVAL 秒ごとにサンプルする。
# ⚠️★★★ プロセス名以外は 1 つも記録しない (★ 他プロセスの列挙・ウィンドウ名は取らない)。
#
# ⚠️★★★ **2026-09-10 の訂正 —— CPU% の測り方を変えた。**
#   ★ 旧: `top -l 2 ... | tail -1` の 1 列目。
#   ⚠️ **これは 1 コアを飽和させたプロセスを 47.6 % と報告する**（★ 地上真実 99.7 %）。
#     原因は 2 フレーム目の分母に **top 自身の起動時間 ≈ 1.1 s** が混ざること
#     （★ `-s` を 2/5/10 s と伸ばすと 62.5 → 79.1 → 88.3 % と 100 % に漸近することで確認）。
#     → ★ **約 0.48 倍**の系統的な過小報告。⚠️ 8 h × 2 本の macOS 実測はこの影響下にある。
#   ★ 新: **CPU 時間 (`ps -o cputime`) の増分 / 実時間の増分**。
#     ⚠️ これは累積カウンタなので、★ **サンプル間隔より短い山も取りこぼさない**
#     （★ 山の CPU 時間は次のサンプルにそのまま乗る）。
#     ★ 校正は `scripts/calibrate-cpu.sh`（陽性対照＝ 1 コア飽和・陰性対照＝不在）。
#   ★ `top` は **mem / th / power のためだけ**に残し、⚠️ `-l 3` に直した
#     （★ 3 フレーム目は分母が正しく、校正で地上真実と一致した）。
#
# ★ 基準: **1 コア = 100 %**（⚠️ 全コア合計基準ではない。10 コア機なら最大 1000 %）。
#   → ★ `meta.json` の `cpu_pct_basis` に機械可読な形で記録される（run.sh）。
set -euo pipefail
DURATION_S="$1"; INTERVAL_S="$2"

# ★ 間隔が短いときは参照プロセス (Finder) の power を採らない
#   （⚠️ `top -l 3` は 1 回あたり約 3.1 s かかる。2 回呼ぶと細かい間隔が成立しない）。
REF_POWER=1
[ "$INTERVAL_S" -ge 10 ] || REF_POWER=0

# ★ CPU 時間 (秒) を返す。⚠️ 取れなければ空を返す（★ 0 と混ぜない）。
cputime_s() {
  local raw
  raw=$(ps -o cputime= -p "$1" 2>/dev/null | tr -d ' ') || return 0
  [ -n "$raw" ] || return 0
  printf '%s' "$raw" | awk -F: '{ if (NF==3) print $1*3600+$2*60+$3; else if (NF==2) print $1*60+$2; else print $1 }'
}

prev_pid=""; prev_cpu=""; prev_t=""
end=$(( $(date +%s) + DURATION_S ))
while [ "$(date +%s)" -lt "$end" ]; do
  now=$(date +%s)
  # ★ GSE 本体の pid。⚠️ 無ければ (対照 = without-gse) 空行を 0 で埋める。
  pid=$(pgrep -x 'gse-next' 2>/dev/null | head -1 || true)
  if [ -n "$pid" ]; then
    # ⚠️★★★ `power` = Activity Monitor の「**エネルギー影響**」。★ sudo 不要。
    #   ⚠️ **ワットではない**（CPU・wakeup・GPU・ディスクの Apple 内部の合成指標）ので、
    #   ★ 「何時間バッテリーが減るか」には**換算できない**。→ 参照プロセスと**比べて**読む。
    line=$(top -l 3 -pid "$pid" -stats cpu,mem,th,power -n 1 2>/dev/null | tail -1 || true)
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
    ref_pw=""
    if [ "$REF_POWER" = 1 ]; then
      ref_pid=$(pgrep -x Finder 2>/dev/null | head -1)
      if [ -n "$ref_pid" ]; then
        ref_pw=$(top -l 3 -pid "$ref_pid" -stats power -n 1 2>/dev/null | tail -1 | awk '{print $1}' | tr -d '+-')
      fi
    fi
    # ★ CPU: 累積 CPU 時間の増分 / 実時間の増分（⚠️ top の cpu 列は使わない）。
    cur_cpu=$(cputime_s "$pid"); cur_t=$(date +%s)
    cpu=""
    if [ -n "$cur_cpu" ] && [ "$pid" = "$prev_pid" ] && [ -n "$prev_cpu" ]; then
      cpu=$(awk -v a="$prev_cpu" -v b="$cur_cpu" -v t0="$prev_t" -v t1="$cur_t" \
            'BEGIN{ d=t1-t0; if (d>0 && b>=a) printf "%.2f", 100*(b-a)/d }')
    fi
    prev_pid="$pid"; prev_cpu="$cur_cpu"; prev_t="$cur_t"
    # ⚠️ 最初の 1 行は前値が無いので CPU が空になる（★ 0 とは書かない）。
    #   ★ 集計側は空を「測れていない」として扱う。
  else
    # ⚠️ プロセス不在 = 対照条件。★ 全列 0（計測器の陰性対照になる）。
    cpu=0; rss_kb=0; th=0; rss_alt=0; pw=0; ref_pw=""
    prev_pid=""; prev_cpu=""; prev_t=""
  fi
  batt=$(pmset -g batt 2>/dev/null | grep -oE '[0-9]+%' | head -1 | tr -d '%' || true)
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$now" "${cpu:-}" "${rss_kb:-0}" "${th:-0}" "${batt:-}" "${rss_alt:-0}" "${pw:-0}" "${ref_pw:-}"
  sleep "$INTERVAL_S"
done
