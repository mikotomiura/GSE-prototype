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
echo "=== ★ 3. 本当に寝たか（⚠️★★★ 検出器を先に校正する）"
# ⚠️★★★ 2026-09-10 **再修正**。★ 前版は `pmset -g log` のイベント種別に錨を下ろしていたが、
#   ⚠️ **この Mac の pmset ログには Sleep/Wake という行が 1 つも無い**（★ 実測: 09-03 以降
#   42,871 行の種別は Assertions / Notification / BatteryHealth のみ）。
#   → ★ 「0 件」は**不在の証拠にならない**。⚠️ 前版は それを「＝ このマシンは寝ていない」と
#   **断定して出力していた**（★ たまたま結論は合っていたが、根拠が無かった）。
#   → ★ **陽性対照を先に置く**: 検出器がそもそも当たりうるかを見て、当たらないなら **判定しない**。
PMHITS=$(pmset -g log 2>/dev/null | grep -cE "^[0-9-]+ [0-9:]+ [+-][0-9]+ (Sleep|Wake|DarkWake) ")
if [ "${PMHITS:-0}" -gt 0 ]; then
  echo "  ★ pmset の Sleep/Wake 行 (直近 6 件):"
  pmset -g log 2>/dev/null | grep -E "^[0-9-]+ [0-9:]+ [+-][0-9]+ (Sleep|Wake|DarkWake) " | tail -6 | sed 's/^/    /'
else
  echo "  ⚠️ pmset にはこの機の Sleep/Wake 行が **1 件も無い** → ★ この経路では **判定しない**"
fi
# ★ 独立した一次資料 ①: カーネルの最終復帰時刻
WT=$(sysctl -n kern.waketime 2>/dev/null)
echo "  ★ kern.waketime: ${WT:-取得できず}"
echo "  ★ kern.boottime: $(sysctl -n kern.boottime 2>/dev/null || echo 取得できず)"
case "$WT" in
  *"sec = 0,"*) echo "     ⚠️ **起動以来 wake の記録が無い** ＝ ★ 寝ていない見込み" ;;
  "")           echo "     ⚠️ 取得できない → ★ この経路でも判定しない" ;;
  *)            echo "     ★ この時刻が**基線より後**なら寝て起きている" ;;
esac
# ★ 独立した一次資料 ②: 統合ログ
# ⚠️★★★ 2 つ踏んだので両方塞ぐ:
#   ① **shell によって結果が変わる** —— ★ zsh 経由では `log show` が 0 行を返し、
#      ⚠️ bash では 736,502 行返した（★ 2026-09-10 実測）。→ ★ この検査は bash 前提。
#   ② ⚠️ 権限が無いと**無フィルタでも 0 行**になる。→ ★ 先に無フィルタで陽性対照を取る。
#   ★ `log show` は遅い（24h だと 2 分超）ので窓は 30 分に限る。
LOGALL=$(log show --last 5m 2>/dev/null | grep -c '')
if [ "${LOGALL:-0}" -lt 10 ]; then
  echo "  ⚠️ log show が 5 分ぶんで ${LOGALL:-0} 行しか返さない（★ 陽性対照が落ちた）→ **判定しない**"
else
  echo "  ★ log show は生きている（★ 5 分で $LOGALL 行）"
  # ⚠️★★★ **自己参照を外す** —— ★ `log show` は**自分のコマンドラインをログに書く**ので、
  #   探している語を引数に含めた瞬間に**自分自身がヒットする**（★ 2026-09-10 に 5 件を誤検出）。
  #   → ★ 送り主が `log` の行を除く。★ 検索語も実行時連結で作る。
  NEEDLE="Wake"" reason"
  WR=$(log show --last 30m --predicate 'process != "log"' 2>/dev/null | grep -c "$NEEDLE")
  echo "  ★ 直近 30 分の wake 理由 (★ 自分の log コマンドを除く): ${WR:-0} 件 ← ★ 寝て起きていれば 1 件以上"
  # ★ 蓋が閉じられたか（★ clamshelled）—— ⚠️ 「寝なかった」のか「閉じていない」のかを分ける
  CS=$(log show --last 30m --predicate 'process != "log"' 2>/dev/null | grep -o "clamshelled: [A-Z]*" | sort | uniq -c | tr '\n' ' ')
  echo "  ★ clamshelled の観測: ${CS:-（観測なし）}  ← ★ YES が 1 件も無ければ **蓋を閉じていない**"
fi
echo "  ⚠️★★★ **いちばん強い証拠は下の 4（NDJSON の穴）である** ——"
echo "     ★ 5 分寝れば 1 Hz の feat に数百秒の穴が開く。★ 穴が 1 秒なら**寝ていない**。"
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
