#!/usr/bin/env bash
# 手跡の漏れの机上の確かめ（ADR-051 D3・conditions.md）。
#
#   bash run.sh selftest   統計の自己検査と変異（既定）
#   bash run.sh controls   合成の陰性・陽性の対照（人の記録を使わない・2 時間ほど）
#   RUN_PHASE=early RECORDS_DIR=... TABLE_JSON=... TABLE_SHA=... UTC_OFFSET_SECS=32400 bash run.sh records
#                          本人の記録（conditions.md に「固定」の印が要る・回は事前登録 S1-F5）
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
# 中間の置き場。既定は新しく作る私用のディレクトリ（700）。指定するなら、空でなく、${HOME}・/・repo そのものや
# その上の階層でないこと（rm -rf の範囲を絞る・security-checker LOW）
setup_work() {
  if [ -z "${WORK:-}" ]; then
    WORK="$(mktemp -d "${TMPDIR:-/tmp}/handmark-leak-desk.XXXXXX")"
  fi
  mkdir -p "$WORK"
  local w r
  w="$(cd "$WORK" && pwd -P)"
  r="$(cd "$REPO_ROOT" && pwd -P)"
  case "$w" in
    /|"$HOME"|"${r}"|"${r}"/*) echo "WORK が広すぎる・repo の中: ${WORK}" >&2; exit 2 ;;
  esac
  # repo の祖先（repo を中に含む階層）も拒む
  case "${r}/" in
    "${w}"/*) echo "WORK が repo を含む: ${WORK}" >&2; exit 2 ;;
  esac
  chmod 700 "$WORK"
}
JOBS="${JOBS:-4}"
MODE="${1:-selftest}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
mkdir -p "$EXP_DIR/results"

"$PY" -I -c 'import numpy, sys; sys.exit(0 if numpy.__version__ == "2.5.2" else 1)' \
  || { echo "numpy 2.5.2 の venv が要る（requirements.txt）: PYTHON=$PY" >&2; exit 2; }

case "$MODE" in
  selftest)
    "$PY" -I "$SC/selftest.py"
    "$PY" -I "$SC/check_mutations.py"
    ;;
  controls)
    [ -x "$REPLAY" ] || { echo "gse-replay が無い: ${REPLAY}（cargo build --bin gse-replay）" >&2; exit 2; }
    [ -d "$EXP_DIR/node_modules/@napi-rs/canvas" ] || { echo "npm ci を実験のディレクトリで" >&2; exit 2; }
    "$PY" -I "$SC/selftest.py"
    setup_work
    rm -rf "$WORK/work" "$WORK/tbl"; mkdir -p "$WORK/work" "$WORK/tbl"
    "$TABLE_TOOL" --seed "$SEED" --s1-start-day 20400 --early-min 30 --early-max 30 --late-days 10 --out "$WORK/tbl" --force >/dev/null
    OUT="$EXP_DIR/results/controls"; rm -rf "$OUT"
    # S3（段階をつけた陽性）と S2（陰性）。同じ組の中では λ だけを変える。
    "$PY" -I "$SC/controls.py" --work "$WORK/work" --out "$OUT/graded" --replay "$REPLAY" --table-dir "$WORK/tbl" \
      --sets 10 --first-set 0 --lams 0,0.002,0.005,0.01,0.02,0.05 --seed "$SEED" --jobs "$JOBS"
    "$PY" -I "$SC/controls.py" --work "$WORK/work" --out "$OUT/null" --replay "$REPLAY" --table-dir "$WORK/tbl" \
      --sets 10 --first-set 10 --lams 0 --seed "$SEED" --jobs "$JOBS"
    # S5: 母集団の差の近似（120 日の大きな合成を 1 組・λ = 0）
    "$PY" -I "$SC/controls.py" --work "$WORK/work" --out "$OUT/truth" --replay "$REPLAY" --table-dir "$WORK/tbl" \
      --sets 1 --first-set 100 --lams 0 --days 120 --seed "$SEED" --jobs 1 --truth
    "$PY" -I "$SC/report.py" "$OUT" > "$EXP_DIR/results/controls_report.md" \
      || { echo "S2（陰性）が不合格か組が足りない: results/controls_report.md" >&2; exit 6; }
    ;;
  records)
    # 本人の記録（conditions.md C2・C7・C8、事前登録 S1-F5）。Claude は results/records/ の集計だけを読む。
    grep -q '<!-- conditions: fixed -->' "$EXP_DIR/conditions.md" \
      || { echo "conditions.md に固定の印が無い。記録を開く前に条件を固定してコミットする" >&2; exit 4; }
    : "${RECORDS_DIR:?RECORDS_DIR（本人の段 1 の記録の場所）}"
    : "${TABLE_JSON:?TABLE_JSON（割付の表）}"
    : "${TABLE_SHA:?TABLE_SHA（表の .sha256）}"
    : "${UTC_OFFSET_SECS:?UTC_OFFSET_SECS}"
    : "${RUN_PHASE:?RUN_PHASE（early か late。事前登録 S1-F5 の回）}"
    case "$RUN_PHASE" in early|late) ;; *) echo "RUN_PHASE は early か late: ${RUN_PHASE}" >&2; exit 2 ;; esac
    [ -x "$REPLAY" ] || { echo "gse-replay が無い: ${REPLAY}（cargo build --bin gse-replay）" >&2; exit 2; }
    [ -d "$EXP_DIR/node_modules/@napi-rs/canvas" ] || { echo "npm ci を実験のディレクトリで" >&2; exit 2; }
    # 試しの通し（合成の記録）では RECORDS_OUT で置き場を変える
    OUT="${RECORDS_OUT:-$EXP_DIR/results/records}"
    mkdir -p "$OUT"
    RUNS="$OUT/runs.jsonl"
    # 判定を繰り返さない（S1-F5）: 同じ回で日数の門を越えて判定まで進んだ実行があれば止める。
    # 道具の誤りで回し直すときだけ RERUN_REASON に理由を書く（前の結果は消さずに残る）。
    if [ -f "$RUNS" ] && "$PY" -I - "$RUNS" "$RUN_PHASE" <<'PY'
import json, sys
path, phase = sys.argv[1:]
n = 0
with open(path, encoding="utf-8") as f:
    for line in f:
        if line.strip():
            r = json.loads(line)
            n += r.get("phase") == phase and r.get("judged") is True
sys.exit(0 if n else 1)
PY
    then
      [ -n "${RERUN_REASON:-}" ] || { echo "回 ${RUN_PHASE} は判定まで進んだ実行がある（runs.jsonl）。回し直すなら RERUN_REASON を書く" >&2; exit 7; }
    fi
    "$PY" -I "$SC/selftest.py"
    if [ -z "${WORK:-}" ]; then
      WORK="$(mktemp -d "${TMPDIR:-/tmp}/handmark-leak-desk.XXXXXX")"
      CLEAN="$WORK"
    fi
    setup_work
    RUNW="$WORK/records.$$"
    [ -n "${CLEAN:-}" ] || CLEAN="$RUNW"
    # 中間（記録の写し・窓の表・コマ・画素）は終わったら、失敗しても消す（C8）
    trap 'rm -rf "$CLEAN"' EXIT
    mkdir -m 700 "$RUNW"
    STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
    "$PY" -I "$SC/prepare_records.py" --records-dir "$RECORDS_DIR" --out "$RUNW/rec" \
      --manifest "$RUNW/manifest.json" > "$RUNW/prep.json"
    # Step 0（ADR-013 Migration 4）: この解析が読む行種（写しに対して）
    PYTHONUTF8=1 "$PY" -I "$REPO_ROOT/scripts/capabilities_gate.py" "$RUNW/rec" --require key --require feat \
      --json > "$OUT/capabilities_${STAMP}.json"
    RED=()
    if [ -f "$RECORDS_DIR/redaction_ledger.jsonl" ]; then
      RED=(--handmark-redactions "$RECORDS_DIR/redaction_ledger.jsonl")
    fi
    "$REPLAY" "$RUNW"/rec/*.ndjson --handmark-windows --utc-offset-secs "$UTC_OFFSET_SECS" \
      --handmark-table "$TABLE_JSON" --handmark-table-sha "$TABLE_SHA" --labels recorded --samples 10 \
      ${RED[@]+"${RED[@]}"} --frames "$RUNW/frames.bin" > "$RUNW/w.ndjson"
    node "$SC/pixels.mjs" "$RUNW/frames.bin" 10 "$RUNW/p.ndjson"
    rm -f "$RUNW/frames.bin"
    "$PY" -I "$SC/stats.py" "$RUNW/w.ndjson" --pixels "$RUNW/p.ndjson" --seed "$SEED" --R 2000 \
      --out "$OUT/summary_${RUN_PHASE}_${STAMP}.json"
    # 入力の一覧（元の名前と SHA-256）と、回の記録（追記だけ）
    cp "$RUNW/manifest.json" "$OUT/inputs_${STAMP}.json"
    COMMIT="$(git -C "$REPO_ROOT" rev-parse HEAD)"
    DIRTY="$(git -C "$REPO_ROOT" status --porcelain -- src-tauri/src experiments/20261115-handmark-leak-desk/scripts src/components/handmarkStageDraw.ts | wc -l | tr -d ' ')"
    "$PY" -I - "$OUT/summary_${RUN_PHASE}_${STAMP}.json" "$RUNW/prep.json" "$RUN_PHASE" "$STAMP" "$COMMIT" "$DIRTY" \
      "${RERUN_REASON:-}" >> "$RUNS" <<'PY'
import json, sys
summ, prep, phase, stamp, commit, dirty, reason = sys.argv[1:]
s = json.load(open(summ, encoding="utf-8"))
p = json.load(open(prep, encoding="utf-8"))
judged = s.get("days_with_min_windows", 0) >= 8
c = s.get("combined", {})
print(json.dumps({"phase": phase, "utc": stamp, "commit": commit, "dirty_files": int(dirty),
                  "files": p["files"], "last_line_cut": p["last_line_cut"], "judged": judged,
                  "main": c.get("main"), "sensitivity": c.get("sensitivity"), "overall": c.get("overall"),
                  "provisional_meets": c.get("provisional_meets"), "rerun_reason": reason or None,
                  "summary": f"summary_{phase}_{stamp}.json"}, ensure_ascii=False))
PY
    tail -n 1 "$RUNS"
    ;;
  *) echo "使い方: bash run.sh [selftest|controls|records]" >&2; exit 2 ;;
esac
