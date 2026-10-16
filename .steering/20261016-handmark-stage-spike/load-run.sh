#!/bin/bash
# 使い方: loadrun.sh <label> stage|surface
# 結果・ログ・CSV は $OUT（無ければ mktemp -d）へ。本体の記録は $O/ds-<label> に書かせて最後に消す。results.md §12 で使った。
S=$(dirname "$0"); O=${OUT:-$(mktemp -d)}; label=$1; kind=$2; W=/Users/johnd/GSE-prototype-handmark-stage
ds=$O/ds-$label; mkdir -p $ds; rm -rf "${TMPDIR}gse-handmark-spike"
stageflag=""; [ "$kind" = stage ] && stageflag="GSE_HANDMARK_STAGE_SPIKE=1"
(cd $W && env -u GSE_HANDMARK_STAGE_SPIKE -u GSE_HANDMARK_STAGE_SPIKE_PROTECT GSE_DATASET=$ds GSE_HANDMARK_SPIKE=1 $stageflag GSE_HANDMARK_SPIKE_MEASURE=1 GSE_DEBUG=1 VITE_GSE_DEBUG=1 npx tauri dev > $O/log-$label.txt 2>&1 &)
for i in $(seq 1 100); do grep -q "surface shown" $O/log-$label.txt && break; sleep 2; done
sleep 4; pid=$(pgrep -x gse-next)
osascript -e 'tell application "System Events" to tell process "gse-next" to set frontmost to true'; sleep 3
for i in 1 2 3 4 5; do r=$(osascript $S/start-session.applescript click); [ "$r" != "not found" ] && break; sleep 3; done
echo "start: $r"; sleep 10
osascript -e 'tell application "TextEdit" to activate' -e 'tell application "TextEdit" to make new document' >/dev/null; sleep 3
c0=$(python3 -I $S/cpu-sum.py $pid); w0=$(python3 -c 'import time;print(time.time())')
osascript /Users/johnd/GSE-prototype-handmark-stage/.steering/20261016-handmark-a-surface-spike/synthetic-keys.applescript 300 0.2
c1=$(python3 -I $S/cpu-sum.py $pid); w1=$(python3 -c 'import time;print(time.time())')
sleep 60
c2=$(python3 -I $S/cpu-sum.py $pid); w2=$(python3 -c 'import time;print(time.time())')
python3 -c "
c0,c1,c2=[float(x.split()[0]) for x in '''$c0|$c1|$c2'''.split('|')]
w0,w1,w2=$w0,$w1,$w2
print('$label typing %.1f%% (%.0fs) idle %.1f%% (%.0fs) procs=%s' % (100*(c1-c0)/(w1-w0), w1-w0, 100*(c2-c1)/(w2-w1), w2-w1, ' '.join('''$c2'''.split()[1:])))
" | tee -a $O/load-summary.txt
osascript -e 'tell application "TextEdit" to close every document saving no' >/dev/null 2>&1
pkill -x gse-next; sleep 4
cp "${TMPDIR}"gse-handmark-spike/stage-pid*.csv $O/stage-$label.csv 2>/dev/null
rm -rf "${TMPDIR}gse-handmark-spike" $ds
