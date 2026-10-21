#!/bin/bash
# 背景の層（自然世界・ポインタ入り）の負荷を外から測る。人の手の入力は使わない（ADR-040 判断 7・判断 4）。
# 使い方: load-run.sh <label> base|off|synth
#   base  = 小面だけ（背景なし）
#   off   = 背景あり・カーソルとクリックを切って始める（GSE_HANDMARK_STAGE_SPIKE_POINTER_OFF=1）
#   synth = 背景あり・合成のポインタ（GSE_HANDMARK_STAGE_SPIKE_SYNTH_POINTER=1・OS を読まない）
# 打鍵は合成（TextEdit へ 300 打・0.2 秒ごと）。CPU は gse-next と責任を持つ WebKit の子の累積秒の差分。
# 判断 8: 他の gse-next（O1）が動いていたら始めない。止めるのは自分が起動したプロセス番号だけ。
# 前の版: .steering/20261016-handmark-stage-spike/load-run.sh（描画の回数の CSV を集めていた）。
set -u
S=$(cd "$(dirname "$0")" && pwd)
OLD=/Users/johnd/GSE-prototype-handmark-stage/.steering/20261016-handmark-stage-spike
W=/Users/johnd/GSE-prototype-handmark-stage
O=${OUT:-$(mktemp -d)}
label=$1
kind=$2
if pgrep -x gse-next >/dev/null; then
  echo "another gse-next is running; not starting (O1?)" >&2
  exit 3
fi
ds=$O/ds-$label
mkdir -p "$ds"
flags="GSE_HANDMARK_SPIKE=1"
case $kind in
  base) ;;
  off) flags="$flags GSE_HANDMARK_STAGE_SPIKE=1 GSE_HANDMARK_STAGE_SPIKE_POINTER_OFF=1" ;;
  synth) flags="$flags GSE_HANDMARK_STAGE_SPIKE=1 GSE_HANDMARK_STAGE_SPIKE_SYNTH_POINTER=1" ;;
  *) echo "kind must be base|off|synth" >&2; exit 2 ;;
esac
(cd $W && env -u GSE_HANDMARK_SPIKE_MEASURE -u GSE_HANDMARK_STAGE_SPIKE -u GSE_HANDMARK_STAGE_SPIKE_PROTECT \
  -u GSE_HANDMARK_STAGE_SPIKE_POINTER_OFF -u GSE_HANDMARK_STAGE_SPIKE_SYNTH_POINTER \
  GSE_DATASET=$ds $flags GSE_DEBUG=1 VITE_GSE_DEBUG=1 npx tauri dev >"$O/log-$label.txt" 2>&1 &)
for _ in $(seq 1 150); do grep -q "surface shown" "$O/log-$label.txt" && break; sleep 2; done
sleep 4
# 開発版は src-tauri から相対の target/debug/gse-next で起動する。起動元のディレクトリで見分ける。
pid=""
for p in $(pgrep -x gse-next); do
  cwd=$(lsof -a -p "$p" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p')
  [ "$cwd" = "$W/src-tauri" ] && pid=$p
done
if [ -z "$pid" ]; then
  echo "dev gse-next not found" >&2
  exit 4
fi
osascript -e 'tell application "System Events" to tell process "gse-next" to set frontmost to true'
sleep 3
for _ in 1 2 3 4 5; do
  r=$(osascript "$OLD/start-session.applescript" click)
  [ "$r" != "not found" ] && break
  sleep 3
done
echo "start: $r"
sleep 10
osascript -e 'tell application "TextEdit" to activate' -e 'tell application "TextEdit" to make new document' >/dev/null
sleep 3
c0=$(python3 -I "$OLD/cpu-sum.py" "$pid"); w0=$(python3 -c 'import time;print(time.time())')
osascript /Users/johnd/GSE-prototype-handmark-stage/.steering/20261016-handmark-a-surface-spike/synthetic-keys.applescript 300 0.2
c1=$(python3 -I "$OLD/cpu-sum.py" "$pid"); w1=$(python3 -c 'import time;print(time.time())')
sleep 60
c2=$(python3 -I "$OLD/cpu-sum.py" "$pid"); w2=$(python3 -c 'import time;print(time.time())')
python3 -c "
c0,c1,c2=[float(x.split()[0]) for x in '''$c0|$c1|$c2'''.split('|')]
w0,w1,w2=$w0,$w1,$w2
print('$label typing %.1f%% (%.0fs) idle %.1f%% (%.0fs) procs=%s' % (100*(c1-c0)/(w1-w0), w1-w0, 100*(c2-c1)/(w2-w1), w2-w1, ' '.join('''$c2'''.split()[1:])))
" | tee -a "$O/load-summary.txt"
osascript -e 'tell application "TextEdit" to close every document saving no' >/dev/null 2>&1
kill "$pid"
sleep 4
grep -E "stage shown|pointer" "$O/log-$label.txt" | tail -2
rm -rf "$ds"
