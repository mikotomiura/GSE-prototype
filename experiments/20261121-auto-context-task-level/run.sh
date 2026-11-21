#!/usr/bin/env bash
# auto-context-task-level（2 段目）の 1 コマンド再現。
#
#   bash run.sh synth [seed ...]   合成の対照（seed を省くと SEED の値）。終了コードで合否を返す。
#   bash run.sh real               実データ（PEOPLE_JSON）。人ごとの判定を work/real.json に書く。
#
# ⚠️ Step 0（capabilities の機械判定・ADR-013 Migration 4）を消さないこと。どちらの形でも、読む記録を
#   ゲートに通してから解析する。
# ⚠️ 記録・封筒・作業の記録・コミットの一覧・結果は work/ に置き（.gitignore 済み）、外部へ送らない。
# 規約の SSOT: docs/experiment-tracking.md / reproducibility-discipline skill。

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="$EXP_DIR/work"
MODE="${1:?synth か real を指定する}"
shift || true

PY="${PYTHON:-$(command -v python3 || command -v python)}"
: "${PY:?python が見つかりません (python3 / python のどちらも無い)}"
export PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1
mkdir -p "$EXP_DIR/results" "$WORK"

# 打鍵の量は key、推定状態（状態の写しの検査）は feat から読む。focus_transition / pointer_bin は
# config_gated で 0 行は判定不能 → --features 側で null になり、1 段目の解析がその列を落とす。
REQUIRED_LINE_TYPES=(--require key --require feat)

gate() {  # gate <出力名> <ファイル...>
  local name="$1"; shift
  local tmp="$EXP_DIR/results/.$name.tmp"
  "$PY" "$REPO_ROOT/scripts/capabilities_gate.py" "$@" "${REQUIRED_LINE_TYPES[@]}" --json > "$tmp"
  mv "$tmp" "$EXP_DIR/results/$name.json"
}

grep -m1 'HMM_VERSION' "$REPO_ROOT/src-tauri/src/analysis/engine.rs" > "$EXP_DIR/results/hmm_version.txt"
git -C "$REPO_ROOT" rev-parse HEAD > "$EXP_DIR/results/git_head.txt"

expect_rc() {  # expect_rc <期待する終了コード> <出力> <コマンド...>
  local want="$1" out="$2"; shift 2
  set +e
  "$@" > "$out"
  local rc=$?
  set -e
  # 例外（1 など 0・3 以外）はいつでも止める。0 と 3 の取り違えは、V2_STRICT=0 なら記録だけして進む。
  if [ "$rc" -ne 0 ] && [ "$rc" -ne 3 ]; then
    echo "NG: 例外で終わった（終了コード ${rc}）: $*" >&2
    exit 1
  fi
  if [ "$rc" -ne "$want" ]; then
    echo "${V2_STRICT:-1}" | grep -q 0 && { echo "v2: 期待と違う（終了コード ${rc}・期待 ${want}）: $out" >&2; return 0; }
    echo "NG: 終了コード ${rc}（期待 ${want}）: $*" >&2
    exit 1
  fi
  # 不合格（3）のときは pass:false も見る（例外の 1 を「正しく落ちた」と読まない）。
  if [ "$want" -eq 3 ] && ! "$PY" -I -c 'import json,sys; sys.exit(0 if json.load(open(sys.argv[1]))["pass"] is False else 1)' "$out"; then
    echo "NG: 終了コード 3 だが pass:false ではない: $out" >&2
    exit 1
  fi
}

if [ "$MODE" = synth ]; then
  SEEDS=("$@")
  [ "${#SEEDS[@]}" -gt 0 ] || SEEDS=("$(cat "$EXP_DIR/SEED")")
  for seed in "${SEEDS[@]}"; do
    d="$WORK/synth/$seed"
    rm -rf "$d"
    for kind in positive long negative; do
      "$PY" -I "$EXP_DIR/gen_synth_task.py" --kind "$kind" --seed "$seed" --out-dir "$d/$kind"
    done
    files=()
    for kind in positive long negative; do
      while IFS= read -r f; do files+=("$f"); done < <("$PY" -I -c 'import json,sys; [print(f) for f in json.load(open(sys.argv[1]))]' "$d/$kind/files.json")
    done
    gate "capabilities.synth.$seed" "${files[@]}"
    r="$EXP_DIR/results/synth.$seed"
    # v2（自動のまとめ・記述）: 長く違う作業で陽性・混ぜ方が同じ作業で陰性・陰性の記録を陽性の基準で（壊した入力）。
    # v2 は主の判定ではないので、合否は記録して先へ進む（主の問いの経路だけが run.sh の合否を決める・判断 14）。
    V2_STRICT=0 expect_rc 0 "$r.v2_long.json" "$PY" -I "$EXP_DIR/evaluate.py" synth --dir "$d/long" --criteria positive --work "$d"
    V2_STRICT=0 expect_rc 0 "$r.v2_negative.json" "$PY" -I "$EXP_DIR/evaluate.py" synth --dir "$d/negative" --criteria negative --work "$d"
    V2_STRICT=0 expect_rc 3 "$r.v2_broken.json" "$PY" -I "$EXP_DIR/evaluate.py" synth --dir "$d/negative" --criteria positive --work "$d"
    # 主の問いと照合の経路（合成の人に作業の記録を付けて real で回す）
    "$PY" -I - "$d" <<'PYEOF'
import json, sys
from pathlib import Path
d = Path(sys.argv[1])
f = lambda k: json.loads((d / k / "files.json").read_text())
people = [
    {"id": "pos_match", "files": f("positive"), "diary": str(d / "positive/diary_match.json"),
     "commits": str(d / "positive/commits_match.json")},
    {"id": "pos_mismatch", "files": f("positive"), "diary": str(d / "positive/diary_mismatch.json")},
    {"id": "pos_few", "files": f("positive"), "diary": str(d / "positive/diary_few.json")},
    {"id": "neg_match", "files": f("negative"), "diary": str(d / "negative/diary_match.json")},
]
(d / "people.json").write_text(json.dumps(people, indent=1))
(d / "expect.json").write_text(json.dumps({"pos_match": {"premise": "differs"}, "pos_mismatch": {"premise": "not_shown"},
                                           "pos_few": {"premise": "undecidable"}, "neg_match": {"premise": "not_shown"}}))
PYEOF
    "$PY" -I "$EXP_DIR/evaluate.py" real --people "$d/people.json" --work "$d" --out "$d/real.json" --expect "$d/expect.json"
    # 合成の人の結果は合成だけからできているので results/ に写してよい（実データの区間を含まない）。
    cp "$d/real.json" "$r.paths.json"
    echo "Step 2a OK: seed ${seed}（v2 の 3 本・主の問いと照合の経路の 4 人）"
  done
  exit 0
fi

if [ "$MODE" = real ]; then
  : "${PEOPLE_JSON:?PEOPLE_JSON が未設定。[{id, files:[...], diary?, commits?}] の JSON（実パスを含むのでコミットしない）}"
  INPUT_FILES=()
  while IFS= read -r f; do INPUT_FILES+=("$f"); done < <(
    "$PY" -I -c 'import json,sys; [print(f) for p in json.load(open(sys.argv[1], encoding="utf-8")) for f in p["files"]]' "$PEOPLE_JSON"
  )
  [ "${#INPUT_FILES[@]}" -gt 0 ] || { echo "PEOPLE_JSON にファイルが 1 本も無い" >&2; exit 2; }
  gate capabilities "${INPUT_FILES[@]}"
  echo "Step 0 OK: capabilities gate 通過"
  "$PY" -I "$EXP_DIR/evaluate.py" real --people "$PEOPLE_JSON" --work "$WORK" --out "$WORK/real.json"
  echo "Step 2b OK: 実データの判定は work/real.json（区間と照合を含むのでコミットしない。notes.md へは集計だけを写す）"
  exit 0
fi

echo "MODE は synth か real" >&2
exit 2
