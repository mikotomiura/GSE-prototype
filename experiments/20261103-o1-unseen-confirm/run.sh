#!/usr/bin/env bash
# O1 の見ていない期間での H4a・H5 と C1・C2・C6 の読み（conditions.md U1〜U5）。O1 の終了後に 1 回だけ回す。
# 中間は repo の外。NDJSON・中間・結果の本文を外部の LLM に送らない（data-privacy）。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REL="experiments/20261103-o1-unseen-confirm"
DECOMP="$REPO_ROOT/experiments/20261102-stall-decomposition"
: "${GSE_SESSIONS:=$HOME/Documents/GSE-sessions}"
: "${WORK:=$HOME/gse-o1-derived/20261103-o1-unseen-confirm}"
BIN="${GSE_REPLAY:-$HOME/gse-public-data/klicke/bin/gse-replay}"
OUT="$HERE/results"   # 固定（判断 8・上書きで 1 回だけの守りを外させない）
START="20261101_083030"
FRESH_S=600
[ "$(shasum -a 256 "$BIN" | cut -d' ' -f1)" = 26cae610383fb6de01651cc904895efa72a691c3dd1e27689a14a4ca51c33bb3 ] || { echo "gse-replay の SHA-256 が違う" >&2; exit 1; }
# U1: O1 の終了後だけ
if pgrep -f 'gse-next\.app/Contents/MacOS/gse-next' >/dev/null || pgrep -f -- '--mode o1' >/dev/null; then
  echo "O1 のアプリが動いている。O1 の終了後に回す（U1）" >&2; exit 2
fi
# 判定に使うのは最初の 1 回だけ（判断 7）。結果か来歴があれば止める。
# started.json だけがある（前の回が途中で落ちた）ときは、入力が同じなら再実行を許す（判断 8・下で照合）
if [ -e "$OUT/confirm.json" ] || [ -e "$OUT/provenance.json" ]; then
  echo "結果が既にある。判定に使うのは最初の 1 回だけ（U1）" >&2; exit 3
fi
# 条件とコードと依存のファイルがコミット済みであること（結果の置き場は除く）
DIRTY="$(git -C "$REPO_ROOT" status --porcelain -- "$REL" ":!$REL/results" \
  experiments/20261103-stall-candidates-c1c2c6/candidates.py \
  experiments/20261103-stall-candidates-c1c2c6/results/candidates.json \
  experiments/20261102-stall-decomposition/types_core.py \
  experiments/20261102-stall-decomposition/o1/build_o1.py \
  experiments/20261102-stall-decomposition/o1/analyze_o1.py \
  experiments/20261101-klicke-early-stall-trigger/scripts/analyze_item2.py \
  src-tauri/prereg/p1-episode.json)"
[ -z "$DIRTY" ] || { echo "条件・コード・依存のファイルに未コミットの変更がある" >&2; echo "$DIRTY" >&2; exit 1; }
FILES=()
NOW="$(date +%s)"
for f in "$GSE_SESSIONS"/gse_o1_*.ndjson; do
  [ -e "$f" ] || continue
  dt="$(basename "$f" .ndjson)"; dt="${dt#gse_o1_}"
  [ "$dt" \< "$START" ] && continue
  if [ $((NOW - $(stat -f %m "$f"))) -lt "$FRESH_S" ]; then
    echo "10 分以内に更新されたファイルがある（書き込み中の可能性・U1）" >&2; exit 2
  fi
  FILES+=("$f")
done
[ "${#FILES[@]}" -gt 0 ] || { echo "対象のファイルが無い" >&2; exit 1; }
[ "$(basename "${FILES[0]}")" = "gse_o1_${START}.ndjson" ] || { echo "最初の本が ${START} でない" >&2; exit 1; }
echo "対象のファイル: ${#FILES[@]} 本" >&2
python3 -I "$HERE/confirm.py" --selftest
python3 -I "$HERE/started.py" --selftest
python3 -I "$HERE/mutants.py"
# 記録を開く前に、計算の前提を確かめる（落ちて 1 回を燃やさない）
python3 -I -c 'import json,sys; int(open(sys.argv[1]).read().strip()); json.load(open(sys.argv[2]))' \
  "$HERE/SEED" "$REPO_ROOT/experiments/20261103-stall-candidates-c1c2c6/results/candidates.json"
avail_kb="$(df -k "$HOME" | awk 'NR==2{print $4}')"
[ "$avail_kb" -gt $((3 * 1024 * 1024)) ] || { echo "空きが 3 GB を切っている" >&2; exit 1; }
mkdir -p "$WORK" "$OUT"
# 中間を作る（記録を開く）直前に、回したことを書く（排他で作る・途中で落ちても「回した」ことが残る）。
# 既にあれば、本の数と SHA-256 が同じときだけ続け、回数を追記する（判断 8）
python3 -I "$HERE/started.py" begin "$OUT/started.json" "${FILES[@]}"
python3 -I "$DECOMP/o1/build_o1.py" "$BIN" "$WORK" "${FILES[@]}"
python3 -I "$HERE/started.py" check "$OUT/started.json" "${FILES[@]}"   # 中間を作る間に入力が変わっていない
python3 -I "$HERE/confirm.py" "$WORK" "$HERE/SEED" "$OUT/confirm.json" "${FILES[@]}"
python3 -I - "$REPO_ROOT" "$BIN" "$HERE" "$OUT/provenance.json" "${FILES[@]}" <<'PY'
import hashlib, json, os, subprocess, sys
root, binp, here, out, *files = sys.argv[1:]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
cat = hashlib.sha256()
for p in files:
    cat.update(h(p).encode())
rel = "experiments/20261103-o1-unseen-confirm"
json.dump({"git_head": subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"], text=True).strip(),
           "gse_replay_sha256": h(binp), "input_files": len(files), "inputs_sha256_digest": cat.hexdigest(),
           "seed": open(os.path.join(here, "SEED")).read().strip(),
           "prereg_p1_episode_sha256": h(os.path.join(root, "src-tauri/prereg/p1-episode.json")),
           "scripts_sha256": {os.path.relpath(p, root): h(p) for p in [
               os.path.join(here, "confirm.py"), os.path.join(here, "mutants.py"), os.path.join(here, "started.py"),
               os.path.join(root, "experiments/20261103-stall-candidates-c1c2c6/candidates.py"),
               os.path.join(root, "experiments/20261103-stall-candidates-c1c2c6/results/candidates.json"),
               os.path.join(root, "experiments/20261102-stall-decomposition/o1/build_o1.py"),
               os.path.join(root, "experiments/20261102-stall-decomposition/o1/analyze_o1.py"),
               os.path.join(root, "experiments/20261102-stall-decomposition/types_core.py"),
               os.path.join(root, "experiments/20261101-klicke-early-stall-trigger/scripts/analyze_item2.py")]}},
          open(out, "w"), indent=1)
PY
