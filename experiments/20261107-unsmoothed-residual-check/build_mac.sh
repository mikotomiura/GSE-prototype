#!/usr/bin/env bash
# Mac で生データから u・n の新しい中間を作り、P-U（全行・bit まで）を照らす（conditions D1・V1）。データと中間は repo の外。
# 出すのは件数だけ（results/u_gate.json）。1 行でも外れれば止める（直さずに研究者に聞く）。
# HP Z2 へは新しい中間と manifest（SHA-256）を渡す（run.sh が VARIANT_MANIFEST で照らす）。
set -euo pipefail
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${DATA_DIR:=$HOME/gse-public-data}"
COA="$DATA_DIR/landscape/coauthor_work_obs"
CS1="$DATA_DIR/cs1/work2021_obs"
CZIP="$DATA_DIR/coauthor/raw/coauthor.zip"
META1="$DATA_DIR/coauthor/raw/metadata_argumentative.csv"
META2="$DATA_DIR/coauthor/raw/metadata_creative.csv"
K21="$DATA_DIR/cs1/raw/2021/keystrokes.csv"
HOLD="$DATA_DIR/cs1/holdout.json"
SIDE_CO="$DATA_DIR/landscape/unsmoothed_residual_coauthor.json.gz"
SIDE_CS="$DATA_DIR/landscape/unsmoothed_residual_cs1.json.gz"
VMAN="$DATA_DIR/landscape/unsmoothed_residual_manifest.json"
OUT="${OUT:-$EXP_DIR/results}"
SC="$EXP_DIR/scripts"
SEED="$(cat "$EXP_DIR/SEED")"
PY="${PYTHON:-python3}"
sha() { "$PY" -I -X utf8 -c 'import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$1"; }
mkdir -p "$OUT"
[ "$(sha "$CZIP")" = 8d7380ca3811c671e774e43bfb9f5d3265e2a5d425788a066a612831aa1e418b ] || { echo "coauthor.zip の SHA-256 が違う" >&2; exit 1; }
[ "$(sha "$K21")" = 950a587bb3a410efc4aad0e64974d6442806345fddd13af76676dfb8006a22b6 ] || { echo "CS1 2021 の SHA-256 が違う" >&2; exit 1; }
[ "$(sha "$HOLD")" = a5a32fcefeb97b038afd170e2672262fd5a71230d5e851319eaa076b606bdc47 ] || { echo "CS1 の holdout の SHA-256 が違う" >&2; exit 1; }
rm -f "$OUT/u_gate.json" "$SIDE_CO" "$SIDE_CS" "$VMAN"
"$PY" -I -X utf8 "$SC/build_variants.py" coauthor "$CZIP" "$COA" "$SEED" "$SIDE_CO" "$OUT/u_gate.json" "$META1" "$META2"
"$PY" -I -X utf8 "$SC/build_variants.py" cs1 "$K21" "$HOLD" "$CS1" "$SEED" "$SIDE_CS" "$OUT/u_gate.json"
"$PY" -I -X utf8 - "$SIDE_CO" "$SIDE_CS" "$OUT/u_gate.json" "$VMAN" <<'PY'
import hashlib, json, os, sys
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
co, cs, gate, out = sys.argv[1:5]
json.dump(dict(files={os.path.basename(co): h(co), os.path.basename(cs): h(cs)}, u_gate=json.load(open(gate))), open(out, "w"), indent=1)
print(json.dumps(dict(manifest_sha256=h(out))))
PY
