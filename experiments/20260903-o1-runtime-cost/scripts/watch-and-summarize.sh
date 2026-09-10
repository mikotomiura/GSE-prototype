#!/usr/bin/env bash
# ★ run.sh の完了を待って summarize.py を回し、結果をファイルに残す。
#
# ⚠️★★★ **なぜ要るか**: 8 時間の run は「終わったときに誰も見ていない」。
#   ★ セッションが切れても結果が残るように、**完了を機械に見張らせて**書き出す。
#
# 使い方:  nohup bash scripts/watch-and-summarize.sh <label> > /dev/null 2>&1 & disown
set -uo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="${1:?⚠️ label を渡すこと（★ results/<label>/ の名前）}"
DIR="$HERE/results/$LABEL"
OUT="$DIR/summary.txt"

[ -d "$DIR" ] || { echo "⚠️ $DIR が無い"; exit 2; }

# ⚠️ 上限を置く（★ 置かないと run が死んだとき永遠に待つ）: 8h + 余裕 1h
DEADLINE=$(( $(date +%s) + 9*3600 ))
while [ ! -s "$DIR/finished_utc" ]; do
  if [ "$(date +%s)" -ge "$DEADLINE" ]; then
    {
      echo "⚠️★★★ **run が終わらなかった**（★ 9 時間待った）。→ 判定しない。"
      echo "★ 待ち始め以降の状況:"
      echo "  サンプラ: $(pgrep -f sample-macos.sh >/dev/null && echo '走っている' || echo '⚠️ 居ない＝途中で死んだ')"
      echo "  samples.tsv の行数: $(grep -c '' "$DIR/samples.tsv" 2>/dev/null || echo 0)"
      echo "  最終更新: $(stat -f '%Sm' -t '%F %T' "$DIR/samples.tsv" 2>/dev/null || echo 不明)"
    } > "$OUT"
    exit 3
  fi
  # ⚠️ サンプラが消えたのに finished_utc が無い ＝ 異常終了。★ 黙って待ち続けない
  if ! pgrep -f sample-macos.sh > /dev/null && [ ! -s "$DIR/finished_utc" ]; then
    sleep 60   # ★ run.sh が最後の書き込みをしている最中かもしれないので 1 分だけ猶予
    if ! pgrep -f sample-macos.sh > /dev/null && [ ! -s "$DIR/finished_utc" ]; then
      {
        echo "⚠️★★★ **サンプラが居ないのに finished_utc が無い** ＝ 途中で死んだ。→ 判定しない。"
        echo "  samples.tsv の行数: $(grep -c '' "$DIR/samples.tsv" 2>/dev/null || echo 0)"
        echo "  最終更新: $(stat -f '%Sm' -t '%F %T' "$DIR/samples.tsv" 2>/dev/null || echo 不明)"
      } > "$OUT"
      exit 4
    fi
  fi
  sleep 120
done

{
  echo "★ 完了: $(cat "$DIR/finished_utc")"
  echo "★ 集計時刻: $(date '+%F %T %Z')"
  echo "════════════════════════════════════════"
  python3 "$HERE/scripts/summarize.py" "$LABEL" 2>&1
  echo "════════════════════════════════════════"
  echo "⚠️★★★ **レート系の指標を読む前に校正を確かめること**:"
  echo "   bash $HERE/scripts/calibrate-cpu.sh"
} > "$OUT"
