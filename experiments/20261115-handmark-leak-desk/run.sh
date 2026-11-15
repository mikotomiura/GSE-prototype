#!/usr/bin/env bash
# 手跡の漏れの机上の確かめ（ADR-051 D3・conditions.md）。
#
#   bash run.sh selftest   統計の自己検査と変異（既定）
#   bash run.sh controls   合成の陰性・陽性の対照（人の記録を使わない・2 時間ほど）
#   bash run.sh records    本人の記録（次のタスク。conditions.md に「固定」の印が要る）
#
# 中間（窓の表・コマ・画素の特徴）は repo の外（WORK）に置く。results/ には集計だけを置く。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SC="$EXP_DIR/scripts"
SEED="$(cat "$EXP_DIR/SEED")"
PY="${PYTHON:-$HOME/gse-venvs/handmark-desk/bin/python}"
REPLAY="${REPLAY:-$REPO_ROOT/src-tauri/target/debug/gse-replay}"
TABLE_TOOL="${TABLE_TOOL:-$REPO_ROOT/src-tauri/target/debug/gse-handmark-table}"
: "${WORK:=${TMPDIR:-/tmp}/handmark-leak-desk}"
JOBS="${JOBS:-4}"
MODE="${1:-selftest}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
mkdir -p "$EXP_DIR/results"

"$PY" -c 'import numpy, sys; sys.exit(0 if numpy.__version__ == "2.5.2" else 1)' \
  || { echo "numpy 2.5.2 の venv が要る（requirements.txt）: PYTHON=$PY" >&2; exit 2; }

case "$MODE" in
  selftest)
    "$PY" -I "$SC/selftest.py"
    "$PY" -I "$SC/check_mutations.py"
    ;;
  controls)
    [ -x "$REPLAY" ] || { echo "gse-replay が無い: $REPLAY（cargo build --bin gse-replay）" >&2; exit 2; }
    [ -d "$EXP_DIR/node_modules/@napi-rs/canvas" ] || { echo "npm ci を実験のディレクトリで" >&2; exit 2; }
    "$PY" -I "$SC/selftest.py"
    rm -rf "$WORK"; mkdir -p "$WORK/work" "$WORK/tbl"
    "$TABLE_TOOL" --seed "$SEED" --s1-start-day 20400 --early-min 30 --early-max 30 --late-days 10 --out "$WORK/tbl" --force >/dev/null
    OUT="$EXP_DIR/results/controls"; rm -rf "$OUT"
    # S3（段階をつけた陽性）と S2（陰性）。同じ組の中では λ だけを変える。
    "$PY" -I "$SC/controls.py" --work "$WORK/work" --out "$OUT/graded" --replay "$REPLAY" --table-dir "$WORK/tbl" \
      --sets 10 --first-set 0 --lams 0,0.002,0.005,0.01,0.02,0.05 --seed "$SEED" --jobs "$JOBS"
    "$PY" -I "$SC/controls.py" --work "$WORK/work" --out "$OUT/null" --replay "$REPLAY" --table-dir "$WORK/tbl" \
      --sets 10 --first-set 10 --lams 0 --seed "$SEED" --jobs "$JOBS"
    "$PY" -I "$SC/report.py" "$OUT" > "$EXP_DIR/results/controls_report.md"
    ;;
  records)
    grep -q '<!-- conditions: fixed -->' "$EXP_DIR/conditions.md" \
      || { echo "conditions.md に固定の印が無い。記録を開く前に条件を固定してコミットする" >&2; exit 4; }
    : "${RECORDS_DIR:?RECORDS_DIR（本人の段 1 の記録の場所）}"
    : "${TABLE_JSON:?TABLE_JSON（割付の表）}"
    : "${TABLE_SHA:?TABLE_SHA（表の .sha256）}"
    : "${UTC_OFFSET_SECS:?UTC_OFFSET_SECS}"
    # Step 0（ADR-013 Migration 4）: この解析が読む行種
    PYTHONUTF8=1 "$PY" "$REPO_ROOT/scripts/capabilities_gate.py" "$RECORDS_DIR" --require key --require feat \
      --json > "$EXP_DIR/results/capabilities.json"
    echo "records は次のタスクで実装する（conditions.md C8）" >&2
    exit 5
    ;;
  *) echo "使い方: bash run.sh [selftest|controls|records]" >&2; exit 2 ;;
esac
