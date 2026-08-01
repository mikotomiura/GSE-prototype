#!/usr/bin/env bash
# experiments/20260801-signal-diagnostics/run.sh
# 1 コマンド再現エントリ (reproducibility-discipline ルール 4)。
#
#   GSE_DATASET=/path/to/gse-dataset ./experiments/20260801-signal-diagnostics/run.sh
#
# 前提: gse-dataset の raw/P0*/ に Phase1 確証カット (calibration_blind 40 セッション) が
# 復号・配置済みであること。配置手順は
# experiments/20260731-phase1-calibration-analysis/notes.md §1 と同一。
#
# exit code: 0=成功 / 1=前提不足・定数抽出失敗 (fail-closed)

set -uo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(git -C "$HERE" rev-parse --show-toplevel 2>/dev/null || echo "$HERE/../..")

PYTHON=$(command -v python3 || command -v python || true)
if [ -z "$PYTHON" ]; then
  echo "[run] FAILED: python not found" >&2
  exit 1
fi

DATASET="${GSE_DATASET:-$HOME/gse-dataset}"
RAW="$DATASET/raw"
if [ ! -d "$RAW" ]; then
  echo "[run] FAILED: $RAW が無い。GSE_DATASET を指定するか raw/ を配置すること" >&2
  exit 1
fi

# config から seed と反復数を読む (ハードコードしない = 再現条件を 1 箇所に集める)
CFG="$HERE/config.json"
read -r SEED NPERM <<EOF_CFG
$("$PYTHON" -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); print(d['seed'], d['n_perm'])" "$CFG")
EOF_CFG
if [ -z "${SEED:-}" ] || [ -z "${NPERM:-}" ]; then
  echo "[run] FAILED: config.json から seed / n_perm を読めない" >&2
  exit 1
fi

# Rust ソースから β・重み・KAPPA を抽出する。
# Python 側にハードコードすると engine.rs を変えたときに黙ってずれる。
if ! "$PYTHON" "$HERE/extract_constants.py" "$ROOT" "$HERE/constants.json"; then
  echo "[run] FAILED: 定数抽出に失敗 (Rust 側の書き方が変わった可能性)" >&2
  exit 1
fi

if ! "$PYTHON" "$HERE/diagnostics.py" "$RAW" "$HERE/constants.json" \
     "$HERE/results" "$SEED" "$NPERM"; then
  echo "[run] FAILED: diagnostics.py" >&2
  exit 1
fi

# 来歴を機械生成する (reproducibility-discipline ルール 3)。
# data.md の手書き hash は再走時に検証されないので、実行のたびに実測値を残す。
mkdir -p "$HERE/results"
if ! "$PYTHON" - "$HERE/results/provenance.json" \
     "$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo unknown)" \
     "$(git -C "$DATASET" rev-parse HEAD 2>/dev/null || echo unknown)" \
     "$(shasum -a 256 "$ROOT/src-tauri/Cargo.lock" 2>/dev/null | cut -d' ' -f1 || echo unknown)" \
     "$("$PYTHON" -c 'import platform,sys; print(platform.python_version())')" \
     "$RAW" <<'PY'
import hashlib, json, os, sys, glob

out, repo, dataset, cargo_lock, pyver, raw = sys.argv[1:7]
per_subject = {}
for pid in sorted(os.listdir(raw)):
    d = os.path.join(raw, pid)
    if not pid.startswith("P0") or not os.path.isdir(d):
        continue
    h = hashlib.sha256()
    files = sorted(glob.glob(os.path.join(d, "*.ndjson")))
    for f in files:
        with open(f, "rb") as fh:
            h.update(fh.read())
    per_subject[pid] = {"files": len(files), "concat_sha256": h.hexdigest()}

json.dump({
    "_note": "run.sh が実行のたびに生成する。手で編集しない。",
    "repo_commit": repo,
    "dataset_commit": dataset,
    "cargo_lock_sha256": cargo_lock,
    "python_version": pyver,
    "input_per_subject": per_subject,
}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"[run] provenance -> {out}")
PY
then
  echo "[run] FAILED: provenance.json の生成に失敗" >&2
  exit 1
fi

echo "[run] OK: results/diagnostics.json / results/diagnostics.txt / results/provenance.json"
