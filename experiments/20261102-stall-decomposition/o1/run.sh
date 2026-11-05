#!/usr/bin/env bash
# O1 の停滞の型と主要アウトカムの候補（../conditions.md）。研究者本人の O1 の記録（この Mac）から集計だけを出す。
# 中間は repo の外。NDJSON と中間を外部の LLM に送らない（data-privacy）。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXP="$(cd "$HERE/.." && pwd)"
: "${GSE_SESSIONS:=$HOME/Documents/GSE-sessions}"
: "${WORK:=$HOME/gse-o1-derived/20261102-stall-decomposition}"
BIN="${GSE_REPLAY:-$HOME/gse-public-data/klicke/bin/gse-replay}"
OUT="${OUT:-$HERE/results}"
[ "$(shasum -a 256 "$BIN" | cut -d' ' -f1)" = 26cae610383fb6de01651cc904895efa72a691c3dd1e27689a14a4ca51c33bb3 ] || { echo "gse-replay の SHA-256 が違う" >&2; exit 1; }
avail_kb="$(df -k "$HOME" | awk 'NR==2{print $4}')"
[ "$avail_kb" -gt $((3 * 1024 * 1024)) ] || { echo "空きが 3 GB を切っている" >&2; exit 1; }
# C1: 名前の日付が 20261018〜20261101。条件のコミット（28a91da0）の時点で書き込み中だったファイル
# （コミットより後に更新されたもの）は入れず、数だけを出す。ファイル名はコードに書かない（レビューの後に改めた）。
COND_TS="$(git -C "$REPO_ROOT" log -1 --format=%ct 28a91da0)"
FILES=()
SKIPPED_WRITING=0
for f in "$GSE_SESSIONS"/gse_o1_*.ndjson; do
  d="$(basename "$f" .ndjson | cut -d_ -f3)"
  { [ "$d" \< 20261018 ] || [ "$d" \> 20261101 ]; } && continue
  m="$(stat -f %m "$f")"
  if [ "$m" -ge "$COND_TS" ]; then SKIPPED_WRITING=$((SKIPPED_WRITING + 1)); continue; fi
  FILES+=("$f")
done
echo "書き込み中だったので外したファイル: $SKIPPED_WRITING" >&2
[ "$SKIPPED_WRITING" -eq 1 ] || { echo "書き込み中だったファイルが 1 本でない（条件の時点では 1 本）" >&2; exit 1; }
python3 -I "$HERE/analyze_o1.py" --selftest
mkdir -p "$WORK" "$OUT"
python3 -I "$HERE/build_o1.py" "$BIN" "$WORK" "${FILES[@]}"
python3 -I "$HERE/analyze_o1.py" "$WORK" "$(cat "$EXP/SEED")" "$OUT" "${FILES[@]}"
# 事後（conditions.md に無い・判定に使わない・notes の逸脱 2）
python3 -I "$HERE/posthoc.py" --selftest
python3 -I "$HERE/posthoc.py" "$WORK" "$(cat "$EXP/SEED")" "$OUT/posthoc.json" "${FILES[@]}"
python3 -I - "$REPO_ROOT" "$BIN" "$HERE" "$OUT/provenance.json" "${FILES[@]}" <<'PY'
import hashlib, json, os, subprocess, sys
root, binp, here, out, *files = sys.argv[1:]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
cat = hashlib.sha256()
for p in files:
    cat.update(h(p).encode())
json.dump({"git_head": subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"], text=True).strip(),
           "git_dirty_paths": [l for l in subprocess.check_output(["git", "-C", root, "status", "--porcelain", "--", "experiments/20261102-stall-decomposition", ":!experiments/20261102-stall-decomposition/o1/results"], text=True).splitlines() if l],
           "gse_replay_sha256": h(binp), "input_files": len(files), "inputs_sha256_digest": cat.hexdigest(),
           "prereg_p1_episode_sha256": h(os.path.join(root, "src-tauri/prereg/p1-episode.json")),
           "scripts_sha256": {os.path.relpath(p, root): h(p) for p in [os.path.join(here, "build_o1.py"), os.path.join(here, "analyze_o1.py"), os.path.join(here, "posthoc.py"), os.path.join(here, "../types_core.py"), os.path.join(here, "../../20261101-klicke-early-stall-trigger/scripts/analyze_item2.py")]}},
          open(out, "w"), indent=1)
PY
