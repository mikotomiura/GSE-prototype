#!/usr/bin/env bash
# ⚠️★★★ セッション NDJSON の **バイト数だけ** を出す。中身は 1 行も読まない。
set -euo pipefail
printf 'name\tbytes\tmtime_epoch_s\n'
for d in "$HOME/Documents/GSE-sessions" "$HOME/Documents/GSE-sessions"/*; do
  [ -d "$d" ] || continue
  for f in "$d"/gse_o1_*.ndjson; do
    [ -f "$f" ] || continue
    # ⚠️ BSD (macOS) と GNU (Linux/git-bash) で stat の書式が違う。
    if size=$(stat -f '%z %m' "$f" 2>/dev/null); then :; else size=$(stat -c '%s %Y' "$f"); fi
    printf '%s\t%s\n' "$(basename "$f")" "$(printf '%s' "$size" | tr ' ' '\t')"
  done
done
