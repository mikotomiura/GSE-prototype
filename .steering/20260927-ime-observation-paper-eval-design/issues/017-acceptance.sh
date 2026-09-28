#!/usr/bin/env bash
# issue 017 acceptance — 照合器・検出の指標・パラメータ回復
set -u
. "$(dirname "$0")/_acceptance-lib.sh"
require_os any
A="${K}/analysis"

echo "[017] 照合器と検出の指標"
selftest_ok "${A}/match.py"
selftest_ok "${A}/inject.py"
need_grep "${A}/inject.py" "parameter recovery" "AC2 selftest ケース: パラメータ回復"
need_grep "${A}/match.py" "positive control" "AC3 selftest ケース: 陽性対照"
need_grep "${A}/match.py" "negative control" "AC3 selftest ケース: 陰性対照"

# AC4: 同じ入力で 2 回走らせてバイト一致（入力はここで inject.py から作る）
cat > "${TMP}/twice.py" <<'EOF'
import hashlib, importlib.util, json, sys
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
sys.path.insert(0, sys.argv[1])
match = load("match", sys.argv[1] + "/match.py"); inject = load("inject", sys.argv[1] + "/inject.py")
gt = [{"trial_id": "t%d" % i, "start_wall_ms": 10000 * i, "end_wall_ms": 10000 * i + 1500, "start_mono_ns": 0, "end_mono_ns": 0,
       "outcome": "commit", "candidate_shown": True, "nav_true": 0} for i in range(300)]
out = []
for _ in range(2):
    res = inject.inject(gt, {"miss": 0.05, "split": 0.03, "merge": 0.03, "false_pos": 0.02},
                        {"bias_ms": 20, "sd_ms": 50, "end_lag_ms_max": 100}, seed=11)
    obs = res[0]
    r = match.match(gt, obs, iou_min=0.5)
    out.append(hashlib.sha256(json.dumps(r, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest())
print(out)
sys.exit(0 if out[0] == out[1] else 1)
EOF
run_ok "AC4 同じ入力・同じ seed で結果がバイト一致" "${PY}" "${TMP}/twice.py" "${A}"

# AC5
for f in match inject; do
  forbid_grep "${A}/${f}.py" '^def (wilson|cluster_bootstrap)' "AC5 ${f}.py が統計を再実装していない"
done
need_grep "${A}/match.py" "stats" "AC5 match.py が stats を使う"

check_entry_green
forbid_gse_changes
only_allowed '^papers/ime-observation/kit/analysis/(match|inject)\.py$'
finish
