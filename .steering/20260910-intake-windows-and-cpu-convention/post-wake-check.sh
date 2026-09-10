#!/usr/bin/env bash
# ★ スリープ復帰後の点検（⚠️ 5 項目すべて見る。1 つでも欠けたら「確かめた」と書かない）
L=~/Documents/GSE-sessions/gse-app.log
S="$(dirname "$0")"
SNAP="$S/pre-sleep-snapshot.txt"
# ⚠️★★★ **基線が無いなら止まる。** ★ 2026-09-10 に実際に踏んだ:
#   ファイル名がずれて PRE が空になり、`tail -n +1` が **ログを頭から全部**出した。
#   ⚠️ しかも「復帰直後のログ」という見出しの下に出たので、★ **11 日前の行を
#   復帰直後だと読みかけた**。→ ★ 不在は「0」ではなく「測れない」。
if [ ! -s "$SNAP" ]; then
  echo "⚠️★★★ 基線 $SNAP が無い。★ スリープ前のスナップショットを採らずに"
  echo "   復帰後だけ見ても『増えた行』は出せない。→ **判定しない**。"
  exit 2
fi
PRE=$(grep '^applog_lines=' "$SNAP" | cut -d= -f2)
case "$PRE" in ''|*[!0-9]*) echo "⚠️ 基線の applog_lines が数字でない: [$PRE]" >&2; exit 2 ;; esac
echo "=== ★ 復帰時刻: $(date '+%F %T %Z') / $(date -u '+%FT%TZ')"
echo "=== ★ 1. プロセスは生きているか"
if pgrep -x gse-next > /dev/null; then
  echo "  ★ 生存 pid=$(pgrep -x gse-next) 稼働=$(ps -o etime= -p $(pgrep -x gse-next) | tr -d ' ')"
else
  echo "  ⚠️★★★ 落ちている"
fi
echo "=== ★ 2. 基線以降のログ（★ 事前 $PRE 行 → 現在 $(grep -c '' $L) 行）"
tail -n +$((PRE + 1)) "$L" | cut -c1-170 | sed 's/^/  /'
[ "$(grep -c '' $L)" -eq "$PRE" ] && echo "  ⚠️ 新しい行が 1 行も無い（★ 何も記録されていない）"
echo "=== ★ 3. スリープ前後の pmset ログ（★ 本当に寝たかの一次資料）"
# ⚠️★★★ 2026-09-10 修正: 旧版は `grep -E "Sleep|Wake|DarkWake"` だった。
#   ★ これは **`NoIdleSleepAssertion` / `PreventUserIdleSystemSleep` の行に当たる**ので、
#   ⚠️ **1 度も寝ていないのに「スリープのログ」が 6 行出た**（★ 実測）。
#   → ★ `pmset -g log` の**イベント種別の列**に錨を下ろす。
SLEEPLOG=$(pmset -g log 2>/dev/null | grep -E "^[0-9-]+ [0-9:]+ [+-][0-9]+ (Sleep|Wake|DarkWake|Start) " | tail -6)
if [ -n "$SLEEPLOG" ]; then
  printf '%s\n' "$SLEEPLOG" | sed 's/^/  /'
else
  echo "  ⚠️★★★ **スリープ / 復帰のイベントが 1 件も無い** ＝ このマシンは寝ていない。"
  echo "  ★ 誰が止めているか:"
  pmset -g assertions 2>/dev/null | grep -E "NoIdleSleep|PreventUserIdleSystemSleep" | grep "pid " | sed 's/^/    /'
fi
echo "=== ★ 4. NDJSON の連続性（⚠️ 型と時刻だけ・中身は読まない）"
python3 - <<'PY'
import json, collections, glob, sys
fs = sorted(glob.glob('/Users/johnd/Documents/GSE-sessions/gse_o1_*.ndjson'))
if not fs: sys.exit("  ⚠️ O1 の NDJSON が 1 本も無い")
for f in fs:
    c = collections.Counter(); ts = []; bad = 0
    for line in open(f, encoding='utf-8', errors='replace'):
        if not line.strip(): continue
        try: o = json.loads(line)
        except Exception: bad += 1; continue
        c[o.get('type')] += 1
        t = o.get('t') or o.get('timestamp')
        if isinstance(t, (int, float)): ts.append(t)
    print(f"  ★ {f.rsplit('/',1)[-1]}: 行 {sum(c.values())} 型 {dict(c)} 壊れ {bad}")
    ts.sort()
    if len(ts) >= 2:
        g = [(ts[i]-ts[i-1])/1000 for i in range(1, len(ts))]
        print(f"     ★ 最大の穴 {max(g):.0f} 秒 / 30 秒超 {sum(1 for x in g if x>30)} 個"
              " ← ★ スリープ時間とほぼ一致するはず")
PY
echo "=== ★ 5. 時計の高水位マーク（★ 巻き戻りで sweep が止まっていないか）"
echo "  事前: $(grep '^hwm=' "$SNAP" | cut -d= -f2)  現在: $(cat ~/Documents/GSE-sessions/.o1_clock_hwm)"
echo "=== ⚠️ 6. 打鍵が拾えるか —— ★ これは**人が何か打ってから**でないと判定できない"
