#!/usr/bin/env bash
# 最頻値を他人で選ぶ候補と比べの相手に置いた集計（conditions.md）。当てはめは回さない。場所は HP Z2（git-bash）。
# selftest → 変異 → P-REPRO（mode の本計算の pickle に mode の集計を当て直して照らす）→ 集計 → provenance。
# 書き手ごとの値（pickle）は repo の外。人は開かない。repo に置くのは集計値だけ。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${DATA_DIR:=$HOME/gse-public-data}"
RAW="${RAW:-$DATA_DIR/landscape/tau_mode_candidate_writer_values}"
OUT="${OUT:-$EXP_DIR/results}"
SC="$EXP_DIR/scripts"
PY="${PYTHON:-python3}"
RUN_ID="${RUN_ID:-$(date +%Y%m%dT%H%M%S)-$$}"
[ "$(cat "$EXP_DIR/SEED")" = 2026110401 ] || { echo "SEED が条件の値と違う" >&2; exit 1; }
mkdir -p "$OUT/mutations"
"$PY" -I -X utf8 "$SC/selftest.py" "$OUT/selftest.json" --run-id "$RUN_ID"
for m in n1 n2 n3 n4; do
  set +e
  "$PY" -I -X utf8 "$SC/selftest.py" "$OUT/mutations/$m.json" --mutate "$m" --run-id "$RUN_ID" > "$OUT/mutations/$m.log" 2>&1
  echo $? > "$OUT/mutations/$m.exit"
  set -e
done
"$PY" -I -X utf8 "$SC/check_mutations.py" "$OUT/mutations" "$RUN_ID"
if [ "${SELFTEST_ONLY:-0}" = 1 ]; then echo "selftest と変異だけ（SELFTEST_ONLY=1）: $RUN_ID"; exit 0; fi
"$PY" -I -X utf8 "$SC/sel.py" "$RAW" "$OUT" --run-id "$RUN_ID"
"$PY" -I -X utf8 - "$(git -C "$REPO_ROOT" rev-parse HEAD)" \
  "$(cd "$REPO_ROOT" && git status --porcelain -- experiments/20261111-mode-in-selection experiments/20261106-tau-mode-candidate/scripts experiments/20261106-tau-mode-candidate/results/summary.json)" \
  "$EXP_DIR" "$RUN_ID" "$OUT/provenance.json" <<'PY'
import glob, hashlib, json, os, platform, sys
import numpy
head, dirty, exp, run_id, out = sys.argv[1:6]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
sys.path.insert(0, os.path.join(exp, "scripts"))
import pinned3
d = os.path.dirname(out)
json.dump(dict(run_id=run_id, git_head=head, git_dirty_paths=[l for l in dirty.splitlines() if l],
               python=platform.python_version(), numpy=numpy.__version__, machine=platform.platform(),
               scripts={os.path.basename(p): h(p) for p in sorted(glob.glob(os.path.join(exp, "scripts", "*.py")))},
               run_sh=h(os.path.join(exp, "run.sh")), conditions=h(os.path.join(exp, "conditions.md")),
               seed_file=h(os.path.join(exp, "SEED")), pinned=pinned3.hashes(),
               repro_check=json.load(open(os.path.join(d, "repro_check.json"))),
               summary_sha256=h(os.path.join(d, "summary.json"))), open(out, "w"), indent=1)
PY
echo "終わり: $RUN_ID"
