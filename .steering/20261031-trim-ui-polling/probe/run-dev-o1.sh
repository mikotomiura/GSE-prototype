#!/bin/bash
# 開発版を O1 の形（GSE_O1_MODE=1）で、研究者の O1 の収集アプリと並べて起動する。
# 識別子を変え、HOME も一時フォルダに向ける（~/.gse・~/Documents/GSE-submissions を研究者の O1 と分けるため）。
# GSE_O1_MODE は自動起動を登録しない（autostart.rs）。cargo と rustup は元の場所を渡す。
set -u
OUT="$1"
cd /Users/johnd/GSE-prototype-pause-resume || { echo "cd に失敗した" >&2; exit 1; }
TMPD="$(mktemp -d)" || { echo "mktemp に失敗した" >&2; exit 1; }
mkdir -p "$TMPD/home/Documents"
REAL_HOME="$HOME"
echo "TMPD=$TMPD" > "$OUT"
env -u GSE_HANDMARK_SPIKE -u GSE_HANDMARK_SPIKE_MEASURE -u GSE_HANDMARK_STAGE_SPIKE -u USERPROFILE \
  HOME="$TMPD/home" CARGO_HOME="$REAL_HOME/.cargo" RUSTUP_HOME="$REAL_HOME/.rustup" \
  npm_config_cache="$TMPD/npm-cache" \
  GSE_DATASET="$TMPD/dataset" GSE_O1_MODE=1 GSE_DEBUG=1 VITE_GSE_DEBUG=1 \
  PATH="$REAL_HOME/.cargo/bin:$PATH" \
  npx tauri dev --config '{"identifier":"com.johnd.gse-next-trim-polling"}' >> "$OUT" 2>&1
