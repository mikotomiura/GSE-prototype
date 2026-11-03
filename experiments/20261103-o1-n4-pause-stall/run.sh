#!/usr/bin/env bash
# O1 の 4 人の休止の分布と停滞の率（conditions.md）。.age を repo の外で復号し、記号を付けた集計値だけを出す。
# 平文・中間・結果の本文を外部の LLM に送らない（data-privacy）。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REL="experiments/20261103-o1-n4-pause-stall"
: "${RECEIVING:=$HOME/Downloads/GSE_Observation-1_.age-receiving}"
: "${WORK:=$HOME/gse-o1-derived/20261103-o1-n4-pause-stall}"
: "${UNPACK:=$HOME/GSE-prototype/bin/gse-unpack}"
: "${IDENTITY:=$HOME/.gse/age-identity.txt}"
BIN="${GSE_REPLAY:-$HOME/gse-public-data/klicke/bin/gse-replay}"
OUT="${OUT:-$HERE/results}"
SEED="$(cat "$HERE/SEED")"
[ "$(shasum -a 256 "$BIN" | cut -d' ' -f1)" = 26cae610383fb6de01651cc904895efa72a691c3dd1e27689a14a4ca51c33bb3 ] || { echo "gse-replay の SHA-256 が違う" >&2; exit 1; }
avail_kb="$(df -k "$HOME" | awk 'NR==2{print $4}')"
[ "$avail_kb" -gt $((5 * 1024 * 1024)) ] || { echo "空きが 5 GB を切っている" >&2; exit 1; }
# N1: 削除台帳 §6 に実施記録が無いこと
grep -q '^| （まだ 1 件も無い） |' "$REPO_ROOT/docs/o1-deletion-ledger.md" || { echo "削除台帳 §6 に実施記録がある（中身を読んでから進める）" >&2; exit 1; }
# 条件・コードと読み込む依存に未コミットの変更が無いこと
DIRTY="$(git -C "$REPO_ROOT" status --porcelain -- "$REL" ":!$REL/results" ":!$REL/notes.md" \
  experiments/20261103-stall-candidates-c1c2c6/candidates.py experiments/20261102-stall-decomposition/types_core.py \
  experiments/20261102-stall-decomposition/o1/build_o1.py experiments/20261102-stall-decomposition/o1/analyze_o1.py \
  experiments/20261101-klicke-early-stall-trigger/scripts/analyze_item2.py src-tauri/prereg/p1-episode.json)"
[ -z "$DIRTY" ] || { echo "条件・コードに未コミットの変更がある" >&2; echo "$DIRTY" >&2; exit 1; }
# N6: 陽性対照と変異（実データの前）
python3 -I "$REPO_ROOT/experiments/20261103-stall-candidates-c1c2c6/candidates.py" --selftest
python3 -I "$HERE/pausestall.py" --selftest
python3 -I -B "$HERE/mutants.py"
mkdir -p "$WORK" "$OUT"
chmod 700 "$WORK"
python3 -I "$HERE/build_n4.py" "$RECEIVING" "$UNPACK" "$IDENTITY" "$BIN" "$WORK" "$SEED"
python3 -I "$HERE/pausestall.py" "$WORK" "$SEED" "$OUT/pausestall.json"
python3 -I - "$REPO_ROOT" "$HERE" "$OUT/provenance.json" "$WORK/files.json" "$BIN" "$UNPACK" <<'PY'
import hashlib, json, os, subprocess, sys
root, here, out, files_json, binp, unpack = sys.argv[1:]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
t = json.load(open(files_json))
cat = hashlib.sha256()
n = 0
for pid in sorted(t["people"]):
    for f in t["people"][pid]["files"]:
        cat.update(f["plain_sha256"].encode())
        n += 1
rel = "experiments/20261103-o1-n4-pause-stall"
json.dump({"git_head": subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"], text=True).strip(),
           "git_dirty_paths": [l for l in subprocess.check_output(["git", "-C", root, "status", "--porcelain", "--", rel, ":!" + rel + "/results"], text=True).splitlines() if l],
           "gse_replay_sha256": h(binp), "gse_unpack_sha256": h(unpack),
           "input_files": n, "plain_sha256_digest": cat.hexdigest(),
           "prereg_p1_episode_sha256": h(os.path.join(root, "src-tauri/prereg/p1-episode.json")),
           "scripts_sha256": {os.path.relpath(p, root): h(p) for p in [
               os.path.join(here, "build_n4.py"), os.path.join(here, "pausestall.py"), os.path.join(here, "mutants.py"),
               os.path.join(here, "run.sh"), os.path.join(here, "conditions.md"), os.path.join(here, "SEED"),
               os.path.join(root, "experiments/20261103-stall-candidates-c1c2c6/candidates.py"),
               os.path.join(root, "experiments/20261102-stall-decomposition/types_core.py"),
               os.path.join(root, "experiments/20261102-stall-decomposition/o1/build_o1.py"),
               os.path.join(root, "experiments/20261102-stall-decomposition/o1/analyze_o1.py"),
               os.path.join(root, "experiments/20261101-klicke-early-stall-trigger/scripts/analyze_item2.py")]}},
          open(out, "w"), indent=1)
PY
echo "done" >&2
