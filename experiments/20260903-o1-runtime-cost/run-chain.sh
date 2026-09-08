#!/usr/bin/env bash
# ⚠️★★★ 稼働コスト実測の**連鎖実行**（★ Claude のセッションに依存しない）。
#
# ★ なぜ要るか: `CronCreate` は**セッション限り**（Claude が終わると消える）。
#   ⚠️ 8〜16 時間の作業をセッションに預けると、⚠️ **端末を閉じただけで全部消える**。
#   → ★ 作業そのものは nohup で切り離し、Claude は**報告だけ**を担う。
#
# 使い方（★ すでに with-gse が走っている前提）:
#   nohup bash run-chain.sh > /dev/null 2>&1 & disown
set -uo pipefail

D="$(cd "$(dirname "$0")" && pwd)"
# ⚠️★ **拡張子を `.log` にしない。** ★ repo の `.gitignore:11` が `*.log` を無視するので、
#   ⚠️ **自動実行の来歴が黙って追跡対象から外れる**（2026-09-04 に実測して気づいた）。
LOG="$D/results/_chain.txt"
mkdir -p "$D/results"
log () { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*" >> "$LOG"; }

log "=== chain started (pid $$) ==="

# ─── ① with-gse の完了を待つ ──────────────────────────────────────────
# ⚠️ ★ **サンプラが死んだだけ**で先へ進まないよう、行数も見る。
log "waiting for the with-gse sampler to finish"
while pgrep -f "sample-macos.sh" > /dev/null 2>&1; do sleep 60; done
WITH_LINES=$(wc -l < "$D/results/with-gse/samples.tsv" 2>/dev/null | tr -d ' ')
log "with-gse finished: ${WITH_LINES:-0} lines"
if [ "${WITH_LINES:-0}" -lt 480 ]; then
  # ⚠️★★ **短すぎる = 途中で死んだ。** ★ 対照だけ回しても意味が無いので止める。
  log "ABORT: with-gse has only ${WITH_LINES:-0} samples (< 480). Not starting the control."
  exit 2
fi

# ─── ② GSE を止める（★ 対照の条件） ──────────────────────────────────
if pgrep -x gse-next > /dev/null 2>&1; then
  # ⚠️★★★ **強制終了になる。** ★ repo に SIGTERM ハンドラは無い（grep 0 件）ので、
  #   `session_end` は書かれず**孤児が 1 本できる**。
  #   → ★ これは想定どおりであり、⚠️ **次回起動時に PR #151 の回収が発火するか**の
  #     もう 1 回の実機試験になる。
  log "stopping gse-next (force kill; no SIGTERM handler exists -> an orphan will be left on purpose)"
  pkill -x gse-next
  sleep 8
fi
if pgrep -x gse-next > /dev/null 2>&1; then
  log "ABORT: gse-next is still running; the control condition would be invalid"
  exit 3
fi
log "gse-next is down"

# ─── ③ without-gse（対照）を回す ─────────────────────────────────────
rm -rf "$D/results/without-gse"
log "starting without-gse"
bash "$D/run.sh" without-gse >> "$LOG" 2>&1
WITHOUT_LINES=$(wc -l < "$D/results/without-gse/samples.tsv" 2>/dev/null | tr -d ' ')
log "without-gse finished: ${WITHOUT_LINES:-0} lines"

# ─── ④ まとめる ──────────────────────────────────────────────────────
python3 "$D/scripts/summarize.py" > "$D/results/_summary.txt" 2>&1
log "summary written (summarize.py exit=$?)"
log "=== chain done ==="
