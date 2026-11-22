#!/usr/bin/env bash
# 手跡の止まりの層（ADR-056）の机上の確かめ（conditions.md）。
#
#   bash run.sh selftest   検定の自己検査（既定・人の記録を使わない）
#   bash run.sh controls   合成の記録で、陽性・陰性の対照と漏れの検査の通し（人の記録を使わない・30 分ほど）
#   RECORDS_DIR=... TABLE_JSON=... TABLE_SHA=... UTC_OFFSET_SECS=32400 bash run.sh records
#                          本人の段 1 の記録（conditions.md に「固定」の印が要る）
#
# 中間（記録の写し・止まりの一覧・問い合わせ・コマ・明るさ・窓の表）は repo の外（WORK）に置き、終わったら消す。
# results/ には集計だけを置く。漏れの検査の統計は、漏れの机上の道具（20261115-handmark-leak-desk）の stats.py を
# 書き換えずに使う。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SC="$EXP_DIR/scripts"
LEAK="$REPO_ROOT/experiments/20261115-handmark-leak-desk"
SEED="$(cat "$EXP_DIR/SEED")"
PY="${PYTHON:-$HOME/gse-venvs/handmark-desk/bin/python}"
REPLAY="${REPLAY:-$REPO_ROOT/src-tauri/target/debug/gse-replay}"
TABLE_TOOL="${TABLE_TOOL:-$REPO_ROOT/src-tauri/target/debug/gse-handmark-table}"
R_ELAPSED="${R_ELAPSED:-1000}"
R_LEAK="${R_LEAK:-2000}"
MODE="${1:-selftest}"
# 試作の版（conditions.md E1）: 形 3 つ × 記憶の窓 W 3 つ。立ち上がりと強さは固定
FORMS=(band motes wind)
WINDOWS=(10 20 30)
RISE_MS=2000
STRENGTH=0.5
LAG_MS=500   # state.rs の LIVE_LAG_MS（gse-replay のヘッダの live_lag_ms と照らす）
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
mkdir -p "$EXP_DIR/results"

"$PY" -I -c 'import numpy, sys; sys.exit(0 if numpy.__version__ == "2.5.2" else 1)' \
  || { echo "numpy 2.5.2 の venv が要る（requirements.txt）: PYTHON=$PY" >&2; exit 2; }

need_tools() {
  [ -x "$REPLAY" ] || { echo "gse-replay が無い: ${REPLAY}（cargo build --bin gse-replay）" >&2; exit 2; }
  for d in "$EXP_DIR" "$LEAK"; do
    [ -d "$d/node_modules/@napi-rs/canvas" ] || { echo "npm ci --ignore-scripts を ${d} で" >&2; exit 2; }
  done
}

# 中間の置き場（新しく作る私用のディレクトリ・700）。指定するなら、空でなく、${HOME}・/・repo とその上でないこと
setup_work() {
  if [ -z "${WORK:-}" ]; then
    WORK="$(mktemp -d "${TMPDIR:-/tmp}/handmark-stopped-desk.XXXXXX")"
    CLEAN="$WORK"
  fi
  mkdir -p "$WORK"
  local w r
  w="$(cd "$WORK" && pwd -P)"
  r="$(cd "$REPO_ROOT" && pwd -P)"
  case "$w" in
    /|"$HOME"|"${r}"|"${r}"/*) echo "WORK が広すぎる・repo の中: ${WORK}" >&2; exit 2 ;;
  esac
  case "${r}/" in
    "${w}"/*) echo "WORK が repo を含む: ${WORK}" >&2; exit 2 ;;
  esac
  chmod 700 "$WORK"
}

# replay の共通の引数（記録の写し・表・時差・対象）。LABELS は records では recorded、合成では recomputed
replay() {
  "$REPLAY" "$@" --handmark-windows --utc-offset-secs "$UTC_OFFSET_SECS" \
    --handmark-table "$TJ" --handmark-table-sha "$TS" --labels "$LABELS" ${RED[@]+"${RED[@]}"}
}

cfg_of() { echo "form=$1;rise_ms=$RISE_MS;window_s=$2;strength=$STRENGTH"; }

# 経過が読めないことの確かめ (i)〜(iii)。引数: 記録の写し（ディレクトリ）・作業・結果の置き場・描く層の対照
elapsed_all() {
  local rec="$1" work="$2" out="$3" control="${4:-none}"
  mkdir -p "$out"
  for w in "${WINDOWS[@]}"; do
    local d="$work/W$w"
    mkdir -p "$d"
    replay "$rec"/*.ndjson --stopped "$(cfg_of band "$w")" --stopped-stops "$d/stops.ndjson" > "$d/w.ndjson"
    "$PY" -I - "$d/w.ndjson" "$LAG_MS" <<'PY'
import json, sys
h = json.loads(open(sys.argv[1], encoding="utf-8").readline())
if h.get("live_lag_ms") != int(sys.argv[2]):
    raise SystemExit(f"ライブの遅れが合わない: {h.get('live_lag_ms')}")
PY
    "$PY" -I "$SC/queries.py" "$d/stops.ndjson" --rise-ms "$RISE_MS" --window-s "$w" --lag-ms "$LAG_MS" \
      --seed "$SEED" --queries "$d/q.ndjson" --items "$d/items.json"
    local first=1
    for f in "${FORMS[@]}"; do
      local tag="${f}_W${w}"
      rm -f "$d/qf.bin"
      replay "$rec"/*.ndjson --stopped "$(cfg_of "$f" "$w")" \
        --stopped-queries "$d/q.ndjson" --stopped-query-frames "$d/qf.bin" > /dev/null
      local layers=(final stopped)
      [ "$first" = 1 ] && layers+=(base)   # 基層だけの画は形に依らない（W ごとに 1 回）
      for layer in "${layers[@]}"; do
        local name
        case "$layer" in
          final) name="$tag" ;;
          stopped) name="${tag}_stopped" ;;
          base) name="base_W${w}" ;;
        esac
        node "$SC/overlay.mjs" queries "$d/qf.bin" "$d/q.ndjson" "$d/lum.f32" --layer "$layer" --control "$control"
        "$PY" -I "$SC/elapsed.py" "$d/items.json" --lum "$d/lum.f32" --seed "$SEED" --R "$R_ELAPSED" \
          --tag "$name" --out "$out/elapsed_${name}.json"
        rm -f "$d/lum.f32"
      done
      first=0
      rm -f "$d/qf.bin"
    done
    rm -rf "$d"
  done
}

# 漏れの検査（ADR-051 D3・ADR-056 D4）。B′ = B_state + 止まりの層の列、B_pixel′ = 止まりの層を重ねた画素
leak_all() {
  local rec="$1" work="$2" out="$3" extra="${4:-}"
  mkdir -p "$out"
  for w in "${WINDOWS[@]}"; do
    for f in "${FORMS[@]}"; do
      local tag="${f}_W${w}" d="$work/L_${f}_${w}"
      mkdir -p "$d"
      replay "$rec"/*.ndjson --samples 10 --stopped "$(cfg_of "$f" "$w")" \
        --frames "$d/f.bin" --stopped-frames "$d/sf.bin" > "$d/w.ndjson"
      node "$SC/overlay.mjs" windows "$d/f.bin" "$d/sf.bin" 10 "$d/p.ndjson"
      rm -f "$d/f.bin" "$d/sf.bin"
      "$PY" -I "$SC/leak_prime.py" "$d/w.ndjson" "$d/wp.ndjson" > /dev/null
      "$PY" -I "$LEAK/scripts/stats.py" "$d/wp.ndjson" --pixels "$d/p.ndjson" --seed "$SEED" --R "$R_LEAK" \
        --no-sensitivity $extra --out "$out/leak_${tag}.json"
      rm -rf "$d"
    done
  done
}

case "$MODE" in
  selftest)
    "$PY" -I "$SC/selftest.py"
    ;;
  controls)
    need_tools
    "$PY" -I "$SC/selftest.py"
    CLEAN=""
    trap '[ -z "$CLEAN" ] || rm -rf "$CLEAN"' EXIT
    setup_work
    rm -rf "$WORK/tbl" "$WORK/rec" "$WORK/recL"; mkdir -p "$WORK/tbl"
    "$TABLE_TOOL" --seed "$SEED" --s1-start-day 20400 --early-min 30 --early-max 30 --late-days 10 --out "$WORK/tbl" --force >/dev/null
    TJ="$WORK/tbl/handmark_assignment.json"; TS="$WORK/tbl/handmark_assignment.sha256"
    UTC_OFFSET_SECS=32400; LABELS=recomputed; RED=()
    OUT="$EXP_DIR/results/controls"; rm -rf "$OUT"; mkdir -p "$OUT"
    # 止まりの多い合成（12 日・3 時間）。陰性（そのまま）と陽性（経過の印を足した画）
    "$PY" -I "$SC/synth_stops.py" --seed "$SEED" --days 12 --hours 3 --out "$WORK/rec"
    FORMS=(band); WINDOWS=(20)
    elapsed_all "$WORK/rec" "$WORK" "$OUT/negative" none
    elapsed_all "$WORK/rec" "$WORK" "$OUT/clock_stop" clock_stop
    elapsed_all "$WORK/rec" "$WORK" "$OUT/clock_start" clock_start
    # 漏れの検査の通し（漏れの道具の合成・20 日・1.5 時間・注入なし）
    "$PY" -I "$LEAK/scripts/synth.py" --seed "$SEED" --days 20 --hours 1.5 --out "$WORK/recL"
    FORMS=(wind)
    leak_all "$WORK/recL" "$WORK" "$OUT/leak"
    PYTHONUTF8=1 "$PY" -I "$SC/report.py" "$OUT" > "$EXP_DIR/results/controls_report.md"
    ;;
  records)
    grep -q '<!-- conditions: fixed -->' "$EXP_DIR/conditions.md" \
      || { echo "conditions.md に固定の印が無い。記録を開く前に条件を固定してコミットする" >&2; exit 4; }
    : "${RECORDS_DIR:?RECORDS_DIR（本人の段 1 の記録の場所）}"
    : "${TABLE_JSON:?TABLE_JSON（割付の表）}"
    : "${TABLE_SHA:?TABLE_SHA（表の .sha256）}"
    : "${UTC_OFFSET_SECS:?UTC_OFFSET_SECS}"
    LEDGER="${REDACTION_LEDGER:-$RECORDS_DIR/redaction_ledger.jsonl}"
    if [ "$LEDGER" != none ] && [ ! -f "$LEDGER" ]; then
      echo "削除の台帳が無い: ${LEDGER}（使っていないなら REDACTION_LEDGER=none）" >&2; exit 2
    fi
    need_tools
    "$PY" -I "$SC/selftest.py"
    CLEAN=""
    trap '[ -z "$CLEAN" ] || rm -rf "$CLEAN"' EXIT
    setup_work
    RUNW="$(mktemp -d "$WORK/records.XXXXXX")"
    [ -n "$CLEAN" ] || CLEAN="$RUNW"
    chmod 700 "$RUNW"
    RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)_$$"
    OUT="$EXP_DIR/results/records/$RUN_ID"
    mkdir -p "$OUT"
    COMMIT="$(git -C "$REPO_ROOT" rev-parse HEAD)"
    DIRTY="$(git -C "$REPO_ROOT" status --porcelain -- src-tauri/src src/components experiments/20261121-handmark-stopped-desk/scripts experiments/20261121-handmark-stopped-desk/run.sh experiments/20261121-handmark-stopped-desk/conditions.md experiments/20261115-handmark-leak-desk/scripts | wc -l | tr -d ' ')"
    LEDGER_ARG=()
    [ "$LEDGER" = none ] || LEDGER_ARG=(--ledger "$LEDGER")
    "$PY" -I "$LEAK/scripts/prepare_records.py" --records-dir "$RECORDS_DIR" --out "$RUNW/rec" \
      --manifest "$RUNW/manifest.json" ${LEDGER_ARG[@]+"${LEDGER_ARG[@]}"} > "$RUNW/prep.json"
    PYTHONUTF8=1 "$PY" -I "$REPO_ROOT/scripts/capabilities_gate.py" "$RUNW/rec" --require key --require feat \
      --json > "$OUT/capabilities.json"
    RED=()
    [ "$LEDGER" = none ] || RED=(--handmark-redactions "$RUNW/ledger.jsonl")
    TJ="$TABLE_JSON"; TS="$TABLE_SHA"; LABELS=recorded
    printf '{"event":"started","run":"%s","commit":"%s","dirty_files":%s}\n' "$RUN_ID" "$COMMIT" "$DIRTY" \
      >> "$EXP_DIR/results/records/runs.txt"
    elapsed_all "$RUNW/rec" "$RUNW" "$OUT"
    leak_all "$RUNW/rec" "$RUNW" "$OUT"
    # repo に残すのは集計・入力の SHA-256 だけ（元のファイル名は日付と時刻なので残さない）
    "$PY" -I - "$RUNW/manifest.json" > "$OUT/inputs.json" <<'PY'
import json, sys
m = json.load(open(sys.argv[1], encoding="utf-8"))
out = {"records": [{k: r[k] for k in ("copy", "sha256", "last_line_cut")} for r in m["records"]],
       "redaction_ledger": m["redaction_ledger"] and {"sha256": m["redaction_ledger"]["sha256"]}}
print(json.dumps(out, ensure_ascii=False, indent=1))
PY
    PYTHONUTF8=1 "$PY" -I "$SC/report.py" "$OUT" > "$OUT/report.md"
    printf '{"event":"finished","run":"%s"}\n' "$RUN_ID" >> "$EXP_DIR/results/records/runs.txt"
    echo "結果: results/records/${RUN_ID}/report.md"
    ;;
  *)
    echo "使い方: bash run.sh selftest|controls|records" >&2; exit 2 ;;
esac
