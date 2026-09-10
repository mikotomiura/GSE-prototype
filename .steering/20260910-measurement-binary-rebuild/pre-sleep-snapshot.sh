#!/usr/bin/env bash
# ★ スリープ跨ぎ検証の**基線**を採る（⚠️ これを採らずに寝かせると post-wake-check.sh は exit 2 で止まる）
#
# ⚠️★★★ 副作用: **8h 計測サンプラを止める**。
#   ★ スリープ中は cputime が伸びず実時間だけ進むので、★ レート系の CPU% が下振れする。
#   → ★ 計測は復帰後に**採り直す**（このスクリプトは止めるだけ・結果は消さない）。
set -uo pipefail
OUT=".steering/20260910-intake-windows-and-cpu-convention/pre-sleep-snapshot.txt"  # ★ post-wake-check.sh が読む場所
L=~/Documents/GSE-sessions/gse-app.log

echo "=== ① 走っている 8h 計測を止める（⚠️ スリープで汚れるため）"
if pgrep -f sample-macos.sh > /dev/null; then
  # ⚠️ 「いま書かれているディレクトリ」を samples.tsv の mtime で選ぶ
  #    （★ ls -td はメタファイルを触っただけの古い run に当たる —— 2026-09-10 に実際に誤表示した）
  RUN=$(ls -t experiments/20260903-o1-runtime-cost/results/*/samples.tsv 2>/dev/null | head -1)
  pkill -f sample-macos.sh
  echo "  ★ サンプラを停止した（★ 結果 ${RUN:-（不明）} は残す・消していない）"
else
  echo "  ★ 走っていない"
fi

echo "=== ② GSE が走っているか（⚠️ 走っていないと検証にならない）"
if ! pgrep -x gse-next > /dev/null; then
  echo "  ⚠️★★★ gse-next が居ない。★ 先に起動すること:"
  echo "     nohup ~/Desktop/O1_計測用_macOS/gse-next.app/Contents/MacOS/gse-next > /tmp/gse.log 2>&1 &"
  exit 3
fi
PID=$(pgrep -x gse-next)
echo "  ★ 生存 pid=$PID 稼働=$(ps -o etime= -p "$PID" | tr -d ' ')"

echo "=== ③ 版を確かめる（⚠️ v0.1.31 を寝かせても機序は追えない）"
bash scripts/check-measurement-binary.sh > /tmp/gate.$$ 2>&1; GRC=$?
grep -E "app  \(CFBundleShortVersionString\)|診断 tap_enabled|meta.app_version" /tmp/gate.$$ | sed 's/^/  /'
rm -f /tmp/gate.$$
if [ "$GRC" -ne 0 ]; then
  echo "  ⚠️★★★ ゲートが rc=$GRC。★ 版ずれ or 診断欠落のまま寝かせても意味が無い。→ 中止する。"
  exit 4
fi
echo "  ★ ゲート rc=0"

echo "=== ④ 基線を書く"
ND=$(ls -t ~/Documents/GSE-sessions/gse_o1_*.ndjson | head -1)
{
  echo "epoch=$(date +%s)"
  echo "utc=$(date -u '+%FT%TZ')"
  echo "pid=$PID"
  echo "applog_lines=$(grep -c '' "$L")"
  echo "ndjson=$ND $(grep -c '' "$ND")"
  echo "hwm=$(cat ~/Documents/GSE-sessions/.o1_clock_hwm 2>/dev/null || echo MISSING)"
} > "$OUT"
cat "$OUT" | sed 's/^/  /'

echo
echo "=== ⚠️★★★ 次にやること（★ 人が叩く）"
echo "  1. ★ Safari のメディア再生を止める / 音声を止める"
echo "  2. ★ **蓋を閉じて 5 分ほど待つ**（⚠️ pmset sleepnow は Claude の assertion で拒否されうる）"
echo "     ★ どうしても sleepnow を使うなら、先に:  pkill -x caffeinate"
echo "  3. ★ 起こしたら **何か打鍵してから**（⚠️ 項目 6 は打鍵しないと判定できない）:"
echo "     bash .steering/20260910-intake-windows-and-cpu-convention/post-wake-check.sh"
echo "  4. ★ そのあと 8h 計測を採り直す:"
echo "     cd experiments/20260903-o1-runtime-cost && \\"
echo "       GSE_COST_LABEL=with-gse-\$(date +%Y%m%d-%H%M)-macos-8h-v0133 nohup bash run.sh with-gse >/dev/null 2>&1 & disown"
