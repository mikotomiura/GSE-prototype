#!/usr/bin/env bash
# 重みを見る目の合成の較正（conditions.md）。実データは使わない。段ごとに回す（D8 の回す順。コミットは段の間に人が行う）。
#   bash run.sh v1                      V1（selftest）→ 変異 w1〜w7 → 照合 → provenance
#   bash run.sh select|report           本計算（第 1 の帰無・この Mac）
#   NPZ=<path> bash run.sh select2|report2   第 2 の帰無（HP Z2・npz は repo の外）
#   bash run.sh xmach <他機の selftest.json>  P-XMACH（両機の記号の列と版の一致）
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${OUT:-$EXP_DIR/results}"
SC="$EXP_DIR/scripts"
JOBS="${JOBS:-8}"
PY="${PYTHON:-$HOME/venvs/weight-eye/bin/python}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
RUN_ID="${RUN_ID:-$(date +%Y%m%dT%H%M%S)-$$}"
STAGE="${1:?段を渡す（v1・select・report・select2・report2・xmach）}"
[ "$(cat "$EXP_DIR/SEED")" = 2026112201 ] || { echo "SEED が条件の値と違う" >&2; exit 1; }
"$PY" -I -X utf8 -c 'import sys; v=sys.version_info; import numpy; assert (v[:3], numpy.__version__) == ((3, 11, 9), "2.4.4"), (v, numpy.__version__)' \
  || { echo "Python 3.11.9・numpy 2.4.4 で回す（P-XMACH・V2）" >&2; exit 1; }
mkdir -p "$OUT"
prov() {
"$PY" -I -X utf8 - "$(git -C "$REPO_ROOT" rev-parse HEAD)" \
  "$(cd "$REPO_ROOT" && git status --porcelain -- experiments/20261126-per-person-weight-eye-v2/scripts experiments/20261126-per-person-weight-eye-v2/run.sh experiments/20261126-per-person-weight-eye-v2/conditions.md experiments/20261126-per-person-weight-eye-v2/SEED experiments/20261110-per-person-sensitivity/scripts experiments/20261110-per-person-sensitivity/results/calibration.json experiments/20261104-timeseries-tau-extend/scripts)" \
  "$EXP_DIR" "$RUN_ID" "$JOBS" "$1" "$STAGE" <<'PY'
import glob, hashlib, json, os, platform, sys
import numpy
head, dirty, exp, run_id, jobs, out, stage = sys.argv[1:8]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
sys.path.insert(0, os.path.join(exp, "scripts"))
import gen, run_eye
P = dict(run_id=run_id, stage=stage, git_head=head, uncommitted=dirty.splitlines(), jobs=int(jobs), seed=gen.SEED,
         code_hash=run_eye.code_hash(), python=platform.python_version(), numpy=numpy.__version__,
         machine=platform.platform(),
         scripts={os.path.basename(p): h(p) for p in sorted(glob.glob(os.path.join(exp, "scripts", "*.py")))},
         run_sh=h(os.path.join(exp, "run.sh")), conditions=h(os.path.join(exp, "conditions.md")),
         pinned={os.path.relpath(p, exp).replace(os.sep, "/"): v for p, v in gen.PIN1.items()})
json.dump(P, open(out, "w"), indent=1)
PY
}
case "$STAGE" in
  v1)
    D="$OUT/v1"; rm -rf "$D"; mkdir -p "$D/mutations"
    prov "$D/provenance.pre.json"
    set +e
    "$PY" -I -X utf8 "$SC/selftest.py" "$D/selftest.json" --jobs "$JOBS" --run-id "$RUN_ID" ${NPZ:+--npz "$NPZ"}; base=$?
    for m in w1 w2 w3 w4 w5 w6 w7; do
      "$PY" -I -X utf8 "$SC/selftest.py" "$D/mutations/$m.json" --mutate "$m" --jobs "$JOBS" --run-id "$RUN_ID" > "$D/mutations/$m.log" 2>&1
      echo $? > "$D/mutations/$m.exit"
    done
    set -e
    [ "$base" = 0 ] || { echo "V1 が赤（止めて研究者に問う・D8）" >&2; exit 3; }
    "$PY" -I -X utf8 "$SC/check_mutations.py" "$D/mutations" "$D/selftest.json" "$RUN_ID"
    prov "$D/provenance.json" ;;
  select|report)
    prov "$OUT/provenance.$STAGE.null1.pre.json"
    "$PY" -I -X utf8 "$SC/run_eye.py" "$STAGE" "$OUT" "$JOBS" --null 1 --run-id "$RUN_ID"
    prov "$OUT/provenance.$STAGE.null1.json" ;;
  select2|report2)
    S="${STAGE%2}"
    prov "$OUT/provenance.$S.null2.pre.json"
    "$PY" -I -X utf8 "$SC/run_eye.py" "$S" "$OUT" "$JOBS" --null 2 --npz "${NPZ:?NPZ（第 2 の帰無の m0）が要る}" --run-id "$RUN_ID"
    prov "$OUT/provenance.$S.null2.json" ;;
  xmach)
    "$PY" -I -X utf8 "$SC/check_xmach.py" "$OUT/v1/selftest.json" "${2:?他機の selftest.json}" "$OUT/v1/xmach.json" ;;
  *) echo "段が違う: $STAGE" >&2; exit 1 ;;
esac
echo "終わり: $STAGE $RUN_ID"
