#!/usr/bin/env bash
# O1 の実施の記録・全期間の記述・探索の AUC（conditions.md）。.age を repo の外で復号し、記号を付けた集計値だけを出す。
# 平文・中間・結果の本文を外部の LLM に送らない（data-privacy）。
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1   # 依存のフォルダに pyc を書かない（-I はこの変数を無視するので、python3 の呼び出しにはすべて -B も付ける）
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REL="experiments/20261116-o1-conduct-record"
N4="experiments/20261103-o1-n4-pause-stall"
: "${RECEIVING:=$HOME/Downloads/GSE_Observation-1_.age-receiving}"
: "${WORK:=$HOME/gse-o1-derived/20261116-o1-conduct-record}"
: "${N4_WORK:=$HOME/gse-o1-derived/20261103-o1-n4-pause-stall}"
: "${UNPACK:=$HOME/GSE-prototype/bin/gse-unpack}"
: "${IDENTITY:=$HOME/.gse/age-identity.txt}"
BIN="${GSE_REPLAY:-$HOME/gse-public-data/klicke/bin/gse-replay}"
OUT="${OUT:-$HERE/results}"
SEED="$(cat "$HERE/SEED")"
DIGEST=c389bf06a18ac7e3a4c7934cdc9b952a8186a9777d3c3230144b2b23722f6cb1   # R1: 入力の固定
[ "$(shasum -a 256 "$BIN" | cut -d' ' -f1)" = 26cae610383fb6de01651cc904895efa72a691c3dd1e27689a14a4ca51c33bb3 ] || { echo "gse-replay の SHA-256 が違う" >&2; exit 1; }
avail_kb="$(df -k "$HOME" | awk 'NR==2{print $4}')"
[ "$avail_kb" -gt $((10 * 1024 * 1024)) ] || { echo "空きが 10 GB を切っている" >&2; exit 1; }
# 平文の置き場が repo の外であること
mkdir -p "$WORK"
case "$(cd "$WORK" && pwd -P)/" in "$(cd "$REPO_ROOT" && pwd -P)/"*) echo "WORK が repo の中にある" >&2; exit 1;; esac
# R1: 削除台帳 §6 に実施記録が無いこと（枝ではなく最新の origin/main の台帳を読む。表の行のうち見本の行以外が 0 行）
git -C "$REPO_ROOT" fetch -q origin main
git -C "$REPO_ROOT" show origin/main:docs/o1-deletion-ledger.md | python3 -I -B "$HERE/ledger_gate.py" \
  || { echo "削除台帳 §6 に実施記録がある（中身を読んでから進める）" >&2; exit 1; }
# 条件・コードと読み込む依存に未コミットの変更が無いこと
DIRTY="$(git -C "$REPO_ROOT" status --porcelain --ignored -- "$REL" ":!$REL/results" ":!$REL/notes.md" "$N4" ":!$N4/notes.md" \
  experiments/20261103-stall-candidates-c1c2c6/candidates.py experiments/20261102-stall-decomposition/types_core.py \
  experiments/20261102-stall-decomposition/o1/build_o1.py experiments/20261102-stall-decomposition/o1/analyze_o1.py \
  experiments/20261102-stall-decomposition/o1/posthoc.py \
  experiments/20261101-klicke-early-stall-trigger/scripts/analyze_item2.py src-tauri/prereg/p1-episode.json)"
[ -z "$DIRTY" ] || { echo "条件・コードに未コミットの変更がある" >&2; echo "$DIRTY" >&2; exit 1; }
# R8: 陽性対照と変異（実データの前）
python3 -I -B "$REPO_ROOT/experiments/20261103-stall-candidates-c1c2c6/candidates.py" --selftest
python3 -I -B "$REPO_ROOT/$N4/pausestall.py" --selftest
python3 -I -B "$REPO_ROOT/experiments/20261102-stall-decomposition/o1/posthoc.py" --selftest
python3 -I -B "$HERE/conduct.py" --selftest
python3 -I -B "$HERE/prewin.py" --selftest
python3 -I -B "$HERE/auc.py" --selftest
python3 -I -B "$HERE/cr_common_test.py"
python3 -I -B "$HERE/ledger_gate.py" --selftest
python3 -I -B "$HERE/build_cr_test.py"
python3 -I -B "$HERE/e2e_test.py" "$BIN"
python3 -I -B "$HERE/mutants.py"
mkdir -p "$OUT"
chmod 700 "$WORK"
# R1: 入力の digest を照らしてから復号・中間
python3 -I -B "$HERE/build_cr.py" "$RECEIVING" "$UNPACK" "$IDENTITY" "$BIN" "$WORK" "$N4_WORK" \
  "$REPO_ROOT/$N4/results/provenance.json" "$DIGEST"
# R2・R3・R4・R5
python3 -I -B "$HERE/conduct.py" "$WORK" "$OUT/conduct.json"
# R3 は n4 の pausestall.run を、R7 の包み（半分以上は切り上げ・割合と率の粗さ）を通して回す
python3 -I -B "$HERE/cr_common.py" --r3 "$WORK" "$SEED" "$OUT/pausestall.json"
python3 -I -B "$HERE/prewin.py" "$WORK" "$SEED" "$OUT/prewin.json"
python3 -I -B "$HERE/auc.py" "$WORK" "$SEED" "$OUT/auc.json"
python3 -I -B - "$REPO_ROOT" "$HERE" "$OUT/provenance.json" "$WORK/files.json" "$BIN" "$UNPACK" <<'PY'
import hashlib, json, os, subprocess, sys
root, here, out, files_json, binp, unpack = sys.argv[1:]
sys.path.insert(0, here)
import cr_common as cm
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
t = json.load(open(files_json))
cat = hashlib.sha256()
n = 0
for pid in sorted(t["people"]):
    for f in t["people"][pid]["files"]:
        cat.update(f["plain_sha256"].encode())
        n += 1
rel = "experiments/20261116-o1-conduct-record"
deps = ["experiments/20261103-o1-n4-pause-stall/build_n4.py", "experiments/20261103-o1-n4-pause-stall/pausestall.py",
        "experiments/20261103-stall-candidates-c1c2c6/candidates.py", "experiments/20261102-stall-decomposition/types_core.py",
        "experiments/20261102-stall-decomposition/o1/build_o1.py", "experiments/20261102-stall-decomposition/o1/analyze_o1.py",
        "experiments/20261102-stall-decomposition/o1/posthoc.py",
        "experiments/20261101-klicke-early-stall-trigger/scripts/analyze_item2.py", "src-tauri/prereg/p1-episode.json"]
own = sorted(f for f in os.listdir(here) if f.endswith((".py", ".sh", ".md")) and f != "notes.md") + ["SEED"]
prov = {"git_head": subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"], text=True).strip(),
           "git_dirty_paths": [l for l in subprocess.check_output(["git", "-C", root, "status", "--porcelain", "--", rel, ":!" + rel + "/results"], text=True).splitlines() if l],
           "gse_replay_sha256": h(binp), "gse_unpack_sha256": h(unpack),
           "symbol_salt_sha256": h(os.path.join(os.path.dirname(files_json), "symbol_salt")),
           "input_age_digest": "c389bf06a18ac7e3a4c7934cdc9b952a8186a9777d3c3230144b2b23722f6cb1",
           "input_files_rounded": cm.round_half_up(n), "plain_sha256_digest": cat.hexdigest(),
           "scripts_sha256": {**{os.path.join(rel, f): h(os.path.join(here, f)) for f in own},
                              **{d: h(os.path.join(root, d)) for d in deps}}}
text = json.dumps(prov, indent=1)
vers = {str(f.get(k)) for p in t["people"].values() for f in p["files"] for k in ("app_version", "hmm_version")}
# 逸脱 2: repo の中の実験のフォルダ名（実験の日付を含む）とハッシュの値は、参加者の日付ではないので伏せてから走査する
import re
scan = re.sub(r"experiments/\d{8}-[a-z0-9-]+", "experiments/<dir>", text)
scan = re.sub(r"(?<![0-9a-f])[0-9a-f]{40,64}(?![0-9a-f])", "<hash>", scan)
if cm.ps.leaks(scan, t["people"], vers):
    sys.exit("来歴に漏れ")
open(out, "w").write(text)
PY
echo "done" >&2
