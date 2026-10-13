#!/usr/bin/env bash
# Runs scripts/a4_keytar.py until every writer of the A4 sample has a file (the script skips finished writers).
# A run that stops with an error (a CUDA error on 2026-10-13 after 3 writers, then the GPU was lost until a reboot)
# is restarted after a pause; when the GPU is not visible the loop waits for it. Progress lines only (no content).
set -u
cd "$(dirname "$0")/.."
PYK="${PYK:-$HOME/.venvs/pkm-keytar/Scripts/python}"
LOG=raw/derived_a4_progress.log
for attempt in $(seq 1 200); do
  until nvidia-smi -L >/dev/null 2>&1; do echo "$(date -u +%FT%TZ) GPU not visible; waiting" >> "$LOG"; sleep 300; done
  echo "$(date -u +%FT%TZ) attempt $attempt" >> "$LOG"
  if "$PYK" -I scripts/a4_keytar.py --root raw/klicke/extracted/WritingTask \
      --model raw/keytar/extracted/data_artifact/data/key_ground_truth_olmo \
      --out-dir raw/derived/a4 --summary results/a4_generation.json >> "$LOG" 2>&1; then
    echo "$(date -u +%FT%TZ) finished" >> "$LOG"
    exit 0
  fi
  echo "$(date -u +%FT%TZ) stopped with an error; restarting in 120 s" >> "$LOG"
  sleep 120
done
exit 1
