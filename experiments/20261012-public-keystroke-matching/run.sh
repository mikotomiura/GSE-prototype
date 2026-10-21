#!/usr/bin/env bash
# One-command reproduction (preregistration.md; notes.md). The synthetic stage needs no data; the data stages need the
# acquired files under raw/ (data.md). STAGE=synthetic (default) | data | all.
set -euo pipefail
cd "$(dirname "$0")"
PY="${PY:-$HOME/.venvs/pkm-main/Scripts/python}"
PYK="${PYK:-$HOME/.venvs/pkm-keytar/Scripts/python}"
WORKERS="${WORKERS:-12}"   # 12 of 16 processors: the Windows CI runner on the same machine needs headroom
STAGE="${STAGE:-synthetic}"
KLICKE=raw/klicke/extracted/WritingTask

if [ "$STAGE" = synthetic ] || [ "$STAGE" = all ]; then
  "$PY" scripts/selftest_synthetic.py
  "$PY" scripts/synthetic_check.py --out results/.tmp/synthetic_check.json
  cmp results/.tmp/synthetic_check.json results/synthetic_check.json
  "$PY" scripts/selftest_main.py
  "$PY" scripts/selftest_enja15.py
  "$PY" scripts/selftest_exploratory.py
  "$PY" scripts/selftest_a4.py
  "$PY" scripts/run_main.py --source synthetic --out results/main_synthetic.json --workers "$WORKERS" --no-timing
fi

if [ "$STAGE" = data ] || [ "$STAGE" = all ]; then
  # each run_main.py stage is resumable: rerun the same command after an interruption (deviation D4; the cache
  # holds per-writer results and stays under raw/)
  CACHE=raw/derived/main_cache
  # A4 reconstructions (GPU, about 150 hours for 500 writers; resumable; the reconstructions stay under raw/;
  # chunks that do not fit on the GPU: scripts/a4_keytar_cpu_fallback.py, deviation D3)
  "$PYK" -I scripts/a4_keytar.py --root "$KLICKE" \
      --model raw/keytar/extracted/data_artifact/data/key_ground_truth_olmo \
      --out-dir raw/derived/a4 --summary results/a4_generation.json
  # main tables (500 writers) without A4, and again with the A4 cells (the other cells are the same as in main.json)
  "$PY" -I scripts/run_main.py --source klicke --root "$KLICKE" --out results/main.json --workers "$WORKERS" \
      --cache-dir "$CACHE"
  "$PY" -I scripts/run_main.py --source klicke --root "$KLICKE" --a4-dir raw/derived/a4 \
      --out results/main_a4.json --workers "$WORKERS" --cache-dir "$CACHE"
  # ENJA15 (question 4)
  "$PY" -I scripts/enja15_main.py --root raw/enja15 --out results/enja15_main.json
  # exploratory analyses (decisions 55 and 56; not in the preregistration)
  "$PY" -I scripts/exploratory_unicity.py --source klicke --root "$KLICKE" --out results/exploratory_unicity.json \
      --workers "$WORKERS"
  "$PY" -I scripts/run_main.py --source klicke --root "$KLICKE" --forms dp --out results/exploratory_dp.json \
      --workers "$WORKERS" --cache-dir "$CACHE"
  # the appendix of all writers without A4 (about 10 days on 12 workers; reuses the cached tasks of the sample)
  "$PY" -I scripts/run_main.py --source klicke --root "$KLICKE" --out results/main_all.json --workers "$WORKERS" \
      --all --cache-dir "$CACHE"
fi
