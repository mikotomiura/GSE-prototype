#!/usr/bin/env bash
# O1 の稼働コストを 1 コマンドで測る (reproducibility-discipline ルール 4)。
#
# 使い方:
#   bash run.sh with-gse      # ★ GSE を起動した状態で回す
#   bash run.sh without-gse   # ★ 対照 (GSE を終了した状態) で回す
#
# ⚠️ Windows は git-bash から叩く (中で PowerShell を呼ぶ)。
set -euo pipefail

RUN="${1:-}"
case "$RUN" in
  with-gse|without-gse) ;;
  *) echo "usage: bash run.sh {with-gse|without-gse}" >&2; exit 2 ;;
esac

# ★ 測る長さ (秒) と間隔 (秒)。⚠️ 既定は 8 時間 / 30 秒。
DURATION_S="${GSE_COST_DURATION_S:-28800}"
INTERVAL_S="${GSE_COST_INTERVAL_S:-30}"
# ⚠️★★ **数字であることを確かめる。** bash の算術評価は配列添字を経由して
#   コマンド置換を起こすので、`GSE_COST_DURATION_S='x[$(cmd)]'` で任意コマンドが走る
#   (★ 設定者＝実行者なので実害は無いが、塞がない理由も無い)。
for v in "$DURATION_S" "$INTERVAL_S"; do
  case "$v" in ''|*[!0-9]*) echo "⚠️ 秒数は正の整数で指定すること: $v" >&2; exit 2 ;; esac
done
[ "$DURATION_S" -gt 0 ] && [ "$INTERVAL_S" -gt 0 ] || { echo "⚠️ 秒数は 1 以上" >&2; exit 2; }

HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/results/$RUN"
mkdir -p "$OUT"

# ⚠️★★★ 既存の結果を黙って上書きしない (★ 対照が消えると実験が成立しない)。
if [ -s "$OUT/samples.tsv" ]; then
  echo "⚠️ $OUT/samples.tsv が既にある。★ 消すか別名に退避してから回すこと。" >&2
  exit 3
fi

case "$(uname -s)" in
  Darwin) OS=macos ;;
  Linux)  OS=linux ;;
  *)      OS=windows ;;
esac

started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf '%s\n' "{\"run\":\"$RUN\",\"os\":\"$OS\",\"started_utc\":\"$started\",\"duration_s\":$DURATION_S,\"interval_s\":$INTERVAL_S}" > "$OUT/meta.json"

echo "★ $RUN を $OS で $((DURATION_S / 3600)) 時間ぶん測ります (間隔 ${INTERVAL_S}s)。"
echo "⚠️ 途中で端末を閉じないこと。★ 結果: $OUT"

# ⚠️★ ヘッダは summarize.py が読む。列を増やすなら向こうも直すこと。
# ⚠️★★★ **メモリは 2 つ記録する。** ★ OS ごとに「メモリ使用量」の定義が違う:
#   - macOS `top` の MEM = **phys_footprint**（Activity Monitor の「メモリ」）
#   - `ps rss` / Windows `WorkingSet64` = **常駐セット**
#   ⚠️ 2026-09-03 に Finder で実測したら **546M vs 36MB（15 倍差）**だった。
#   ★ どちらか一方だけ残すと、後から「何を測ったのか」が決められない。
#   → ★ `rss_kb` = その OS の主指標 / `rss_alt_kb` = 対照（定義は env.md）。
printf 'epoch_s\tcpu_pct\trss_kb\tthreads\tbattery_pct\trss_alt_kb\n' > "$OUT/samples.tsv"

bash "$HERE/scripts/sample-$OS.sh" "$DURATION_S" "$INTERVAL_S" >> "$OUT/samples.tsv"

# ★ NDJSON は **バイト数だけ** 記録する (⚠️ 中身は 1 行も読まない・data.md)。
bash "$HERE/scripts/ndjson-size.sh" > "$OUT/ndjson-size.tsv" || true

printf '%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$OUT/finished_utc"
echo "★ 終わりました。次: python3 $HERE/scripts/summarize.py"
