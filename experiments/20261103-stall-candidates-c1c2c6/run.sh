#!/usr/bin/env bash
# 停滞の定義の候補 C1・C2・C6（conditions.md）。停滞の分解の中間だけを読み、集計値だけを出す。
# 中間と結果の本文を外部の LLM に送らない（data-privacy）。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DECOMP="$REPO_ROOT/experiments/20261102-stall-decomposition"
: "${GSE_SESSIONS:=$HOME/Documents/GSE-sessions}"
: "${WORK:=$HOME/gse-o1-derived/20261102-stall-decomposition}"
OUT="${OUT:-$HERE/results}"
# K1: 停滞の分解と同じファイル（名前の日付 20261018〜20261101・条件のコミット 28a91da0 より後に更新されたものを除く）
COND_TS="$(git -C "$REPO_ROOT" log -1 --format=%ct 28a91da0)"
FILES=()
SKIPPED=0
for f in "$GSE_SESSIONS"/gse_o1_*.ndjson; do
  d="$(basename "$f" .ndjson | cut -d_ -f3)"
  { [ "$d" \< 20261018 ] || [ "$d" \> 20261101 ]; } && continue
  if [ "$(stat -f %m "$f")" -ge "$COND_TS" ]; then SKIPPED=$((SKIPPED + 1)); continue; fi
  FILES+=("$f")
done
[ "$SKIPPED" -eq 1 ] || { echo "外したファイルが 1 本でない: $SKIPPED" >&2; exit 1; }
DIGEST="$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["inputs_sha256_digest"])' "$DECOMP/o1/results/provenance.json")"
python3 -I "$HERE/candidates.py" --selftest
mkdir -p "$OUT"
python3 -I "$HERE/candidates.py" "$WORK" "$OUT/candidates.json" "$DIGEST" "${FILES[@]}"
python3 -I - "$REPO_ROOT" "$HERE" "$OUT/provenance.json" "$DIGEST" <<'PY'
import hashlib, json, os, subprocess, sys
root, here, out, digest = sys.argv[1:]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
rel = "experiments/20261103-stall-candidates-c1c2c6"
json.dump({"git_head": subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"], text=True).strip(),
           "git_dirty_paths": [l for l in subprocess.check_output(["git", "-C", root, "status", "--porcelain", "--", rel, ":!" + rel + "/results"], text=True).splitlines() if l],
           "inputs_sha256_digest": digest,
           "prereg_p1_episode_sha256": h(os.path.join(root, "src-tauri/prereg/p1-episode.json")),
           "scripts_sha256": {os.path.relpath(p, root): h(p) for p in [
               os.path.join(here, "candidates.py"),
               os.path.join(root, "experiments/20261102-stall-decomposition/types_core.py"),
               os.path.join(root, "experiments/20261102-stall-decomposition/o1/analyze_o1.py"),
               os.path.join(root, "experiments/20261101-klicke-early-stall-trigger/scripts/analyze_item2.py")]}},
          open(out, "w"), indent=1)
PY
