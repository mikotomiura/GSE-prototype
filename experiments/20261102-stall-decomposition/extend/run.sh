#!/usr/bin/env bash
# 打鍵の外の信号を持つ公開データへの当てはめ（extend/conditions.md）。データと中間は repo の外。記述だけ・検定なし。
# 取っておく一覧（make_holdout.py）は条件のコミットの後・変換の前に 1 回だけ作った。ここでは作り直さず SHA-256 で照合する。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXP="$(cd "$HERE/.." && pwd)"
: "${DATA_DIR:=$HOME/gse-public-data}"
X="$DATA_DIR/extend"
BIN="${GSE_REPLAY:-$DATA_DIR/klicke/bin/gse-replay}"
OUT="${OUT:-$HERE/results}"
V0="$DATA_DIR/dux/raw/v0.csv"; V1="$DATA_DIR/dux/raw/v1.csv"; SW="$DATA_DIR/swell/raw"
sha() { shasum -a 256 "$1" | cut -d' ' -f1; }
[ "$(sha "$V0")" = 8909dc6286cbfba32f615688d11e73c8873b97b0f7efad8d3cdf56e5096c63bf ] || { echo "v0.csv の SHA-256 が違う" >&2; exit 1; }
[ "$(sha "$V1")" = 5879bea5977903a772393bee2d85e8879df871912d8105ff786823529e87a22b ] || { echo "v1.csv の SHA-256 が違う" >&2; exit 1; }
[ "$(sha "$BIN")" = 26cae610383fb6de01651cc904895efa72a691c3dd1e27689a14a4ca51c33bb3 ] || { echo "gse-replay の SHA-256 が違う" >&2; exit 1; }
[ "$(sha "$X/holdout.json")" = 0caa29e88d3bf056df55f2c0da0a78a011cafbae46809ec3e35e565633c86e00 ] || { echo "取っておく一覧が違う" >&2; exit 1; }
avail_kb="$(df -k "$DATA_DIR" | awk 'NR==2{print $4}')"
[ "$avail_kb" -gt $((3 * 1024 * 1024)) ] || { echo "空きが 3 GB を切っている" >&2; exit 1; }
python3 -I "$HERE/convert_extend.py" --selftest
python3 -I "$HERE/analyze_extend.py" --selftest
mkdir -p "$OUT"
if [ "${REBUILD:-0}" = 1 ]; then
  rm -rf "$X/dux_work" "$X/dux_work_tabnav" "$X/swell_work"
  python3 -I "$HERE/build_extend.py" dux "$BIN" "$X/holdout.json" "$X/dux_work" "${JOBS:-6}" "$V0" "$V1" > /dev/null
  python3 -I "$HERE/build_extend.py" dux "$BIN" "$X/holdout.json" "$X/dux_work_tabnav" "${JOBS:-6}" "$V0" "$V1" --tab-as-nav > /dev/null
  python3 -I "$HERE/build_extend.py" swell "$BIN" "$X/holdout.json" "$X/swell_work" "${JOBS:-6}" "$SW" > /dev/null
fi
# 中間は、入力・取っておく一覧・変換器・build・add_feat・replay の SHA-256 と版（TAB の扱い）が今のものと同じで、
# build が最後まで成功したときだけ使う
SWD="$(python3 -I - "$SW" <<'PY'
import hashlib, os, sys
raw = sys.argv[1]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
cat = hashlib.sha256()
for n in sorted(n for n in os.listdir(raw) if n.endswith(".xml")):
    cat.update(n.encode()); cat.update(h(os.path.join(raw, n)).encode())
print(cat.hexdigest())
PY
)"
ADDF="$EXP/../20261031-coauthor-pre-request-signal/scripts/add_feat.py"
for w in dux_work dux_work_tabnav swell_work; do
  [ -f "$X/$w/build_ok" ] || { echo "build が最後まで成功していない: $w（REBUILD=1 で作り直す）" >&2; exit 1; }
  python3 -I - "$X/$w/build_summary.json" "$w" "$(sha "$HERE/convert_extend.py")" "$(sha "$HERE/build_extend.py")" \
    "$(sha "$X/holdout.json")" "$(sha "$ADDF")" "$(sha "$BIN")" "$(sha "$V0")" "$(sha "$V1")" "$SWD" <<'PY'
import json, sys
p, w, conv, build, hold, addf, rep, v0, v1, swd = sys.argv[1:]
s = json.load(open(p))
want = {"converter_sha256": conv, "build_sha256": build, "holdout_sha256": hold, "add_feat_sha256": addf,
        "replay_sha256": rep}
if w.startswith("dux"):
    want["inputs_sha256"] = [v0, v1]
    want["tab_as_nav"] = (w == "dux_work_tabnav")
else:
    want["inputs_digest"] = swd
bad = [k for k, v in want.items() if s.get(k) != v]
if bad or s["status"].get("replay_failed") or s["status"].get("features_failed"):
    sys.exit("中間が今のものと違う（REBUILD=1 で作り直す）: %s %s" % (w, bad))
PY
  cp "$X/$w/build_summary.json" "$OUT/build_summary_$w.json"
done
python3 -I "$HERE/analyze_extend.py" "$(cat "$EXP/SEED")" "$X/holdout.json" "$X/dux_work" "$X/dux_work_tabnav" "$X/swell_work" "$OUT"
python3 -I - "$REPO_ROOT" "$HERE" "$OUT/provenance.json" <<'PY'
import hashlib, json, os, subprocess, sys
root, here, out = sys.argv[1:]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
scripts = [os.path.join(here, n) for n in ("make_holdout.py", "convert_extend.py", "build_extend.py", "analyze_extend.py")]
scripts += [os.path.join(here, p) for p in ("../types_core.py", "../public/analyze_public.py", "../checks/analyze_checks.py",
            "../../20261102-public-data-landscape/scripts/analyze_landscape.py",
            "../../20261101-klicke-early-stall-trigger/scripts/analyze_item2.py",
            "../../20261031-coauthor-pre-request-signal/scripts/add_feat.py")]
json.dump({"git_head": subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"], text=True).strip(),
           "git_dirty_paths": [l for l in subprocess.check_output(["git", "-C", root, "status", "--porcelain", "--", "experiments/20261102-stall-decomposition", ":!experiments/20261102-stall-decomposition/extend/results"], text=True).splitlines() if l],
           "python": sys.version.split()[0],
           "scripts_sha256": {os.path.relpath(os.path.realpath(p), root): h(p) for p in scripts}},
          open(out, "w"), indent=1)
PY
