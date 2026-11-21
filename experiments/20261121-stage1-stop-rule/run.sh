#!/usr/bin/env bash
# 段 1 の終了判定（conditions.md）。
#
#   bash run.sh selftest   数え方と判定の自己検査・変異・daysim の陽性対照（既定）
#   RECORDS_DIR=... UTC_OFFSET_SECS=32400 [VALUES_JSON=...] bash run.sh records
#                          段 1 の記録で件数（と値があれば判定）を出す。conditions.md に固定の印が要る
#   COUNTS_JSON=... bash run.sh need
#                          件数の要約（λ・π）から要る日数を見込む（記録を読まない）
#
# 写しと中間は repo の外（WORK・700）に置く。results/ には件数と見込みだけを置く。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SC="$EXP_DIR/scripts"
SEED="$(cat "$EXP_DIR/SEED")"
PY="${PYTHON:-$HOME/gse-venvs/handmark-desk/bin/python}"
REPLAY="${REPLAY:-$REPO_ROOT/src-tauri/target/debug/gse-replay}"
PREP="$REPO_ROOT/experiments/20261115-handmark-leak-desk/scripts/prepare_records.py"
MODE="${1:-selftest}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
"$PY" -I -c 'import numpy, sys; sys.exit(0 if numpy.__version__ == "2.5.2" else 1)' \
  || { echo "numpy 2.5.2 の venv が要る: PYTHON=$PY" >&2; exit 2; }
mkdir -p "$EXP_DIR/results"

case "$MODE" in
  selftest)
    "$PY" -I "$SC/selftest.py"
    "$PY" -I "$SC/check_mutations.py"
    "$PY" -I "$REPO_ROOT/experiments/20261103-mhd-dryrun-v2/scripts/daysim.py" --selftest "$SEED" "$EXP_DIR/results/selftest"
    "$PY" -I "$REPO_ROOT/experiments/20261103-stall-candidates-c1c2c6/candidates.py" --selftest
    ;;
  records)
    : "${RECORDS_DIR:?RECORDS_DIR（段 1 の記録の場所）}"
    : "${UTC_OFFSET_SECS:?UTC_OFFSET_SECS}"
    grep -q '^<!-- conditions: fixed -->$' "$EXP_DIR/conditions.md" \
      || { echo "conditions.md に固定の印が無い（記録で回す前に固定してコミットする）" >&2; exit 3; }
    [ -x "$REPLAY" ] || { echo "gse-replay が無い: ${REPLAY}（cargo build --bin gse-replay）" >&2; exit 2; }
    "$PY" -I "$SC/selftest.py" >/dev/null
    WORK="$(mktemp -d "${TMPDIR:-/tmp}/stage1-stop-rule.XXXXXX")"; chmod 700 "$WORK"
    trap 'rm -rf "$WORK"' EXIT
    "$PY" -I "$PREP" --records-dir "$RECORDS_DIR" --out "$WORK/rec" --manifest "$WORK/manifest.json" >&2
    OUT="${COUNTS_OUT:-$EXP_DIR/results/records/counts.json}"; mkdir -p "$(dirname "$OUT")"
    ARGS=(count --records "$WORK/rec" --work "$WORK/mid" --replay "$REPLAY" --utc-offset-secs "$UTC_OFFSET_SECS" --out "$OUT" --seed "$SEED")
    [ -n "${VALUES_JSON:-}" ] && ARGS+=(--values "$VALUES_JSON")
    "$PY" -I "$SC/stoprule.py" "${ARGS[@]}"
    ;;
  need)
    : "${COUNTS_JSON:?COUNTS_JSON（records の出力）}"
    OUT="${NEED_OUT:-$EXP_DIR/results/records/need.json}"; mkdir -p "$(dirname "$OUT")"
    "$PY" -I "$SC/stoprule.py" need --counts "$COUNTS_JSON" --out "$OUT" --seed "$SEED" ${NEED_ARGS:-}
    ;;
  *) echo "使い方: bash run.sh [selftest|records|need]" >&2; exit 2 ;;
esac
