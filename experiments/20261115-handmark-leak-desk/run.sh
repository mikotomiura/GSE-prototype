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
    # 区間指定削除の台帳: 既定は記録の場所の redaction_ledger.jsonl。無いなら REDACTION_LEDGER=none と明示する
    LEDGER="${REDACTION_LEDGER:-$RECORDS_DIR/redaction_ledger.jsonl}"
    if [ "$LEDGER" != none ] && [ ! -f "$LEDGER" ]; then
      echo "削除の台帳が無い: ${LEDGER}（使っていないなら REDACTION_LEDGER=none）" >&2; exit 2
    fi
    [ -x "$REPLAY" ] || { echo "gse-replay が無い: ${REPLAY}（cargo build --bin gse-replay）" >&2; exit 2; }
    [ -d "$EXP_DIR/node_modules/@napi-rs/canvas" ] || { echo "npm ci を実験のディレクトリで" >&2; exit 2; }
    # 試しの通し（合成の記録）では RECORDS_OUT で置き場を変える。そのときは合成の記録しか受けない
    # （置き場を変えて回の記録を空にし、本人の記録を回し直す抜け道を塞ぐ・code-reviewer の指摘）
    OUT="${RECORDS_OUT:-$EXP_DIR/results/records}"
    SYN=()
    [ -z "${RECORDS_OUT:-}" ] || SYN=(--require-synthetic)
    mkdir -p "$OUT"
    RUNS="$OUT/runs.jsonl"
    # 同じ回を同時に 2 つ走らせない（mkdir の印。macOS の mkdir は排他）
    LOCK="$OUT/.lock"
    mkdir "$LOCK" 2>/dev/null || { echo "別の records が走っているか、前の回の印が残っている: ${LOCK}" >&2; exit 7; }
    CLEAN=""   # 環境から受け継がない（security-checker の指摘）
    trap 'rmdir "$LOCK"; [ -z "$CLEAN" ] || rm -rf "$CLEAN"' EXIT
    # 判定を繰り返さない（S1-F5）: 同じ回で始めた実行が 1 つでもあれば止める（判定まで進んだもの・途中で
    # 落ちて終わりの行が無いものの両方）。日数の門で止まった実行だけは数えない。読めない行があれば止める。
    # 道具の誤りで回し直すときだけ RERUN_REASON に理由を書く（前の結果は消さずに残る）。
    set +e
    "$PY" -I "$SC/runs_gate.py" "$RUNS" "$RUN_PHASE"
    rc=$?
    set -e
    case "$rc" in
      10) ;;
      0) [ -n "${RERUN_REASON:-}" ] || { echo "回 ${RUN_PHASE} は統計に入った実行がある（runs.jsonl）。回し直すなら RERUN_REASON を書く" >&2; exit 7; } ;;
      *) echo "runs.jsonl が読めないか形が違う（rc=${rc}）。直すまで回さない" >&2; exit 7 ;;
    esac
    "$PY" -I "$SC/selftest.py"
    if [ -z "${WORK:-}" ]; then
      WORK="$(mktemp -d "${TMPDIR:-/tmp}/handmark-leak-desk.XXXXXX")"
      CLEAN="$WORK"
    fi
    setup_work
    RUNW="$(mktemp -d "$WORK/records.XXXXXX")"
    [ -n "$CLEAN" ] || CLEAN="$RUNW"
    # 中間（記録の写し・窓の表・コマ・画素）は終わったら、失敗・中断しても消す（C8）。SIGKILL・電源断では残る
    chmod 700 "$RUNW"
    RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)_$$"
    COMMIT="$(git -C "$REPO_ROOT" rev-parse HEAD)"
    DIRTY="$(git -C "$REPO_ROOT" status --porcelain -- src-tauri/src experiments/20261115-handmark-leak-desk/scripts experiments/20261115-handmark-leak-desk/run.sh experiments/20261115-handmark-leak-desk/conditions.md src/components/handmarkStageDraw.ts | wc -l | tr -d ' ')"
    LEDGER_ARG=()
    [ "$LEDGER" = none ] || LEDGER_ARG=(--ledger "$LEDGER")
    "$PY" -I "$SC/prepare_records.py" --records-dir "$RECORDS_DIR" --out "$RUNW/rec" \
      --manifest "$RUNW/manifest.json" ${LEDGER_ARG[@]+"${LEDGER_ARG[@]}"} ${SYN[@]+"${SYN[@]}"} > "$RUNW/prep.json"
    # Step 0（ADR-013 Migration 4）: この解析が読む行種（写しに対して）
    PYTHONUTF8=1 "$PY" -I "$REPO_ROOT/scripts/capabilities_gate.py" "$RUNW/rec" --require key --require feat \
      --json > "$RUNW/capabilities.json"
    RED=()
    [ "$LEDGER" = none ] || RED=(--handmark-redactions "$RUNW/ledger.jsonl")
    "$REPLAY" "$RUNW"/rec/*.ndjson --handmark-windows --utc-offset-secs "$UTC_OFFSET_SECS" \
      --handmark-table "$TABLE_JSON" --handmark-table-sha "$TABLE_SHA" --labels recorded --samples 10 \
      ${RED[@]+"${RED[@]}"} --frames "$RUNW/frames.bin" > "$RUNW/w.ndjson"
    node "$SC/pixels.mjs" "$RUNW/frames.bin" 10 "$RUNW/p.ndjson"
    rm -f "$RUNW/frames.bin"
    # 回と記録の中身を照らす（S1-F5）: 回 1（early）は後期の日を含まない記録で、回 2（late）は後期の日を含む記録で。
    # 表の最後の日を過ぎたか（回 2 の時期）は回す人が確かめる。
    LATE_DAYS="$("$PY" -I -c 'import json,sys; print(json.loads(open(sys.argv[1]).readlines()[-1])["sensitivity"]["late_days"])' "$RUNW/w.ndjson")"
    if [ "$RUN_PHASE" = early ] && [ "$LATE_DAYS" -gt 0 ]; then
      echo "回 1（early）なのに記録に後期の日（割付 late_first・on）が ${LATE_DAYS} 日ある" >&2; exit 8
    fi
    if [ "$RUN_PHASE" = late ] && [ "$LATE_DAYS" -eq 0 ]; then
      echo "回 2（late）なのに記録に後期の日が無い" >&2; exit 8
    fi
    SENS=()
    [ "$RUN_PHASE" = late ] || SENS=(--no-sensitivity)   # 回 1 は主のみ（S1-F5・/cross-review 指摘 7）
    # 統計に入る直前に「始めた」を書く。これより後で落ちても、この回は「始めた」として次を止める
    # （/cross-review 指摘 2）。これより前の失敗は AUC を計算していないので回に数えない。
    printf '{"event":"started","run":"%s","phase":"%s","commit":"%s","dirty_files":%s,"rerun_reason":%s}\n' \
      "$RUN_ID" "$RUN_PHASE" "$COMMIT" "$DIRTY" \
      "$("$PY" -I -c 'import json,sys; print(json.dumps(sys.argv[1] or None, ensure_ascii=False))' "${RERUN_REASON:-}")" >> "$RUNS"
    "$PY" -I "$SC/stats.py" "$RUNW/w.ndjson" --pixels "$RUNW/p.ndjson" --seed "$SEED" --R 2000 \
      ${SENS[@]+"${SENS[@]}"} --out "$RUNW/summary.json"
    # repo に残すのは集計・入力の SHA-256・行種の門の結果だけ（元のファイル名は日付と時刻なので残さない）
    cp "$RUNW/summary.json" "$OUT/summary_${RUN_PHASE}_${RUN_ID}.json"
    cp "$RUNW/capabilities.json" "$OUT/capabilities_${RUN_ID}.json"
    "$PY" -I - "$RUNW/manifest.json" > "$OUT/inputs_${RUN_ID}.json" <<'PY'
import json, sys
m = json.load(open(sys.argv[1], encoding="utf-8"))
out = {"records": [{k: r[k] for k in ("copy", "sha256", "last_line_cut")} for r in m["records"]],
       "redaction_ledger": m["redaction_ledger"] and {"sha256": m["redaction_ledger"]["sha256"]}}
print(json.dumps(out, ensure_ascii=False, indent=1))
PY
    "$PY" -I - "$RUNW/summary.json" "$RUNW/prep.json" "$RUN_PHASE" "$RUN_ID" >> "$RUNS" <<'PY'
import json, sys
summ, prep, phase, run = sys.argv[1:]
s = json.load(open(summ, encoding="utf-8"))
p = json.load(open(prep, encoding="utf-8"))
judged = s.get("day_gate_passed") is True   # C6 の日数の門を越えたか（越えなければ回に数えない）
c = s.get("combined", {})
print(json.dumps({"event": "finished", "run": run, "phase": phase, "files": p["files"],
                  "last_line_cut": p["last_line_cut"], "ledger": p["ledger"], "judged": judged,
                  "main": c.get("main"), "sensitivity": c.get("sensitivity"), "overall": c.get("overall"),
                  "provisional_meets": c.get("provisional_meets"), "summary": f"summary_{phase}_{run}.json"},
                 ensure_ascii=False))
PY
    tail -n 1 "$RUNS"
    ;;
  *) echo "使い方: bash run.sh [selftest|controls|records]" >&2; exit 2 ;;
esac
