#!/usr/bin/env bash
# Runs scripts/a4_keytar.py until every writer of the A4 sample has a file (the script skips finished writers).
# A run that stops with an error (a CUDA error on 2026-10-13 after 3 writers, then the GPU was lost until a reboot)
# is restarted after a pause; when the GPU is not visible the loop waits for it. A stop that a restart cannot cure
# (exit 3: a checkpoint hash, an ID format, a file of another generation, a mutant writing under raw/) ends the loop.
# Progress lines only (no content).
set -u
cd "$(dirname "$0")/.."
PYK="${PYK:-$HOME/.venvs/pkm-keytar/Scripts/python}"
# A4_SCRIPT=scripts/a4_keytar_cpu_fallback.py adds the CPU fallback of deviation D3 (notes.md)
A4_SCRIPT="${A4_SCRIPT:-scripts/a4_keytar.py}"
LOG=raw/derived_a4_progress.log
for attempt in $(seq 1 200); do
  until nvidia-smi -L >/dev/null 2>&1; do echo "$(date -u +%FT%TZ) GPU not visible; waiting" >> "$LOG"; sleep 300; done
  echo "$(date -u +%FT%TZ) attempt $attempt" >> "$LOG"
  "$PYK" -I "$A4_SCRIPT" --root raw/klicke/extracted/WritingTask \
      --model raw/keytar/extracted/data_artifact/data/key_ground_truth_olmo \
      --out-dir raw/derived/a4 --summary results/a4_generation.json >> "$LOG" 2>&1
  code=$?
  if [ "$code" -eq 0 ]; then
    echo "$(date -u +%FT%TZ) finished" >> "$LOG"
    exit 0
  fi
  if [ "$code" -eq 3 ]; then
    echo "$(date -u +%FT%TZ) stopped for a reason a restart cannot cure (exit 3)" >> "$LOG"
    exit 3
  fi
  echo "$(date -u +%FT%TZ) stopped with an error (exit $code); restarting in 120 s" >> "$LOG"
  sleep 120
done
exit 1
