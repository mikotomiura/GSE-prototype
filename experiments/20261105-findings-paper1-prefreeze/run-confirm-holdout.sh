#!/usr/bin/env bash
# 確認（凍結の後に 1 回だけ）: CS1 2019 年版の取り置きの書き手だけの中間を作り、確認の解析を回す。
# 事前登録 v4 の P2・P10。凍結の前には走らせない（OSF の登録の URL を引数に取り、無ければ止める）。
set -euo pipefail
OSF_URL="${1:?OSF の凍結の URL を渡す（凍結の前に走らせない）}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${DATA_DIR:=$HOME/gse-public-data}"
PY="${CONFIRM_PY:-$DATA_DIR/venv-findings1/bin/python}"
CS1="$DATA_DIR/cs1"
K19="$CS1/raw/2019/keystrokes.csv"
BIN="${GSE_REPLAY:-$DATA_DIR/klicke/bin/gse-replay}"
WORK="$CS1/work2019_holdout"
OUT="$EXP_DIR/results_holdout"
sha() { shasum -a 256 "$1" | cut -d' ' -f1; }
[ "$(sha "$K19")" = b54d8cf56b7719ae0ec9ecf19e5b3788168f087bd4a50238dca1e06f6bfe7955 ] || { echo "2019 年版の SHA-256 が違う" >&2; exit 1; }
[ "$(sha "$CS1/holdout.json")" = a5a32fcefeb97b038afd170e2672262fd5a71230d5e851319eaa076b606bdc47 ] || { echo "取り置きの一覧が違う" >&2; exit 1; }
[ "$(sha "$BIN")" = 26cae610383fb6de01651cc904895efa72a691c3dd1e27689a14a4ca51c33bb3 ] || { echo "gse-replay が違う" >&2; exit 1; }
[ "$(sha "$EXP_DIR/scripts/confirm_p1.py")" = a17930a772969cc04d80df0c758d43efe96614959708ec318db8c8133a2eba20 ] || { echo "confirm_p1.py が登録の版と違う" >&2; exit 1; }
[ "$(sha "$EXP_DIR/scripts/prefreeze.py")" = c1ab0c1825e7b6ce4268d646b25ae209c9253c52c64a82818c6feed4789fc632 ] || { echo "prefreeze.py が登録の版と違う" >&2; exit 1; }
[ "$("$PY" -m pip freeze)" = "$(cat "$EXP_DIR/requirements-confirm.txt")" ] || { echo "環境が違う" >&2; exit 1; }
[ ! -e "$OUT" ] || { echo "取り置きの結果が既にある（最初の完走だけを使う・P10）" >&2; exit 1; }
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
# 見た書き手を読み飛ばす一覧（取り置きの書き手だけが残る）。ID は repo の外にだけ置く
SKIP="$CS1/skip_seen_2019.json"
"$PY" -I -c "import csv,json,sys;csv.field_size_limit(10**9);r=csv.reader(open(sys.argv[1],newline=''));i=next(r).index('SubjectID');s={x[i] for x in r};h=set(json.load(open(sys.argv[2]))['2019']);assert h<=s;json.dump({'2019':sorted(s-h)},open(sys.argv[3],'w'))" "$K19" "$CS1/holdout.json" "$SKIP"
rm -rf "$WORK"
python3 -I "$REPO_ROOT/experiments/20261104-cs1-landscape/scripts/build_cs1.py" 2019 "$K19" "$BIN" "$SKIP" "$WORK" "${JOBS:-6}"
mkdir -p "$OUT"
cp "$WORK/build_summary.json" "$OUT/build_summary_holdout.json"
printf '%s\n' "$OSF_URL" > "$OUT/osf_registration.txt"
"$PY" -I "$EXP_DIR/scripts/confirm_p1.py" holdout "$WORK" "$CS1/holdout.json" 20261106 "$OUT"
"$PY" -I -c "import json,sys;json.dump({'git_head':sys.argv[1]},open(sys.argv[2],'w'))" "$(git -C "$REPO_ROOT" rev-parse HEAD)" "$OUT/provenance_holdout.json"
