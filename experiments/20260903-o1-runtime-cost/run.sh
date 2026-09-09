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

# ★ 出力ディレクトリ名。⚠️ 既定は `$RUN` だが、★ OS や日付で分けたいときは
#   `GSE_COST_LABEL` を付ける (例: with-gse-20260910-macos-startup)。
LABEL="${GSE_COST_LABEL:-$RUN}"
case "$LABEL" in
  *[!A-Za-z0-9._-]*|''|.|..) echo "⚠️ GSE_COST_LABEL は英数と . _ - だけ: $LABEL" >&2; exit 2 ;;
esac
OUT="$HERE/results/$LABEL"
mkdir -p "$OUT"

# ⚠️★★★ 既存の結果を黙って上書きしない (★ 対照が消えると実験が成立しない)。
# ⚠️★★ **`samples.tsv` だけを見てはいけない。** ★ 2026-09-09 に Windows 側が踏んだ:
#   `samples.tsv` は `.gitignore` 済みなので、⚠️ **git 管理下の `meta.json` /
#   `finished_utc` を黙って上書きできた**（★ `git checkout` で復旧した）。
#   → ★ run が「あった痕跡」すべてを門にする。
for f in samples.tsv meta.json finished_utc ndjson-size.tsv ndjson-size-start.tsv; do
  if [ -e "$OUT/$f" ]; then
    echo "⚠️ $OUT/$f が既にある。★ 消すか別名に退避するか、GSE_COST_LABEL で別名にすること。" >&2
    exit 3
  fi
done

case "$(uname -s)" in
  Darwin) OS=macos ;;
  Linux)  OS=linux ;;
  *)      OS=windows ;;
esac

# ⚠️★★★ **CPU% の「基準」を meta.json に残す。** ★ 2026-09-10 まで基準は
#   サンプラの**コメントにしか無く**、⚠️ 読んだ人が Windows を「全コア基準」と推測して
#   **×16 換算し FAIL 相当と誤判定**しかけた。→ ★ 機械可読にする。
#   ★ `one_core_100`  = 1 コア飽和で 100 %（全コア飽和なら 100×コア数）。
#   ⚠️ `all_cores_100` = 全コア飽和で 100 %（Task Manager 方式）。
case "$OS" in
  macos)
    # ★ `ps -o cputime` の増分 / 実時間。⚠️ 校正済 (scripts/calibrate-cpu.sh)。
    CPU_SOURCE="ps -o cputime delta"
    CPU_BASIS="one_core_100"
    NCPU="$(sysctl -n hw.logicalcpu 2>/dev/null || echo '')"
    ;;
  windows)
    # ⚠️★★★ **Windows の基準は 2026-09-10 時点で未確定**。
    #   ★ Microsoft の逐語 (*Examining Processor Time Data*):
    #     「the value of the % Processor Time reported for the Process object can
    #      report values over 100 percent」→ ★ **1 コア = 100 % 基準**を強く示唆。
    #   ⚠️ ただし**この repo は Windows 実機で確かめていない**。
    #   → ★ 確かめたら `one_core_100` に確定し、この注記を消すこと。
    #     手順: .steering/20260910-intake-windows-and-cpu-convention/windows-cpu-convention-probe.md
    CPU_SOURCE="Get-Counter \\Process(name)\\% Processor Time"
    CPU_BASIS="${GSE_COST_CPU_BASIS:-one_core_100_unverified}"
    NCPU="$(powershell.exe -NoProfile -NonInteractive -Command '(Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors' 2>/dev/null | tr -d '\r' | tail -1 || echo '')"
    ;;
  *)
    CPU_SOURCE="unknown"; CPU_BASIS="unknown"; NCPU="$(nproc 2>/dev/null || echo '')"
    ;;
esac
case "$NCPU" in ''|*[!0-9]*) NCPU_JSON=null ;; *) NCPU_JSON="$NCPU" ;; esac

started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf '%s\n' "{\"run\":\"$RUN\",\"label\":\"$LABEL\",\"os\":\"$OS\",\"started_utc\":\"$started\",\"duration_s\":$DURATION_S,\"interval_s\":$INTERVAL_S,\"cpu_source\":\"$CPU_SOURCE\",\"cpu_pct_basis\":\"$CPU_BASIS\",\"logical_processors\":$NCPU_JSON}" > "$OUT/meta.json"

echo "★ $RUN を $OS で $((DURATION_S / 3600)) 時間ぶん測ります (間隔 ${INTERVAL_S}s)。"
echo "⚠️ 途中で端末を閉じないこと。★ 結果: $OUT"

# ⚠️★ ヘッダは summarize.py が読む。列を増やすなら向こうも直すこと。
# ⚠️★★★ **メモリは 2 つ記録する。** ★ OS ごとに「メモリ使用量」の定義が違う:
#   - macOS `top` の MEM = **phys_footprint**（Activity Monitor の「メモリ」）
#   - `ps rss` / Windows `WorkingSet64` = **常駐セット**
#   ⚠️ 2026-09-03 に Finder で実測したら **546M vs 36MB（15 倍差）**だった。
#   ★ どちらか一方だけ残すと、後から「何を測ったのか」が決められない。
#   → ★ `rss_kb` = その OS の主指標 / `rss_alt_kb` = 対照（定義は env.md）。
printf 'epoch_s\tcpu_pct\trss_kb\tthreads\tbattery_pct\trss_alt_kb\tenergy_impact\tref_energy_impact\n' > "$OUT/samples.tsv"

# ⚠️★★★ **開始時のサイズを先に採る。** ★ 2026-09-05 の欠陥: 終了時のサイズしか無いと、
#   run より前から書かれていたファイルを「run 中に書かれた量」と読んでしまう。
#   ★ 差分が取れれば外挿の前提が要らなくなる。
bash "$HERE/scripts/ndjson-size.sh" > "$OUT/ndjson-size-start.tsv" || true

bash "$HERE/scripts/sample-$OS.sh" "$DURATION_S" "$INTERVAL_S" >> "$OUT/samples.tsv"

# ★ NDJSON は **バイト数だけ** 記録する (⚠️ 中身は 1 行も読まない・data.md)。
bash "$HERE/scripts/ndjson-size.sh" > "$OUT/ndjson-size.tsv" || true

printf '%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$OUT/finished_utc"
echo "★ 終わりました。次: python3 $HERE/scripts/summarize.py"
