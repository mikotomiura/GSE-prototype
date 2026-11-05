#!/usr/bin/env bash
# 取り置きの手順が照合するファイルの一覧 confirm-manifest.sha256 を作る（凍結の前に 1 回・登録にはこの一覧の SHA-256 を書く）。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
E=experiments/20261105-findings-paper1-prefreeze
cd "$REPO_ROOT"
shasum -a 256 \
  "$E/run-confirm-holdout.sh" "$E/build-variants.sh" "$E/requirements-confirm.txt" \
  "$E/scripts/confirm_p1.py" "$E/scripts/prefreeze.py" "$E/scripts/rebuild_onsets.py" \
  experiments/20261104-cs1-landscape/scripts/build_cs1.py experiments/20261104-cs1-landscape/scripts/analyze_cs1.py \
  experiments/20261102-public-data-landscape/scripts/analyze_landscape.py \
  experiments/20261101-klicke-early-stall-trigger/scripts/analyze_item2.py \
  experiments/20261031-coauthor-pre-request-signal/scripts/convert.py \
  experiments/20261031-coauthor-pre-request-signal/scripts/add_feat.py \
  src-tauri/prereg/p1-episode.json > "$E/confirm-manifest.sha256"
shasum -a 256 "$E/confirm-manifest.sha256"
