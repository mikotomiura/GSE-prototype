#!/usr/bin/env bash
# フォーカスの遷移と受領（conditions.md）。研究者本人の O1 の記録（この Mac）から集計だけを出す。
# 中間（停滞の始まりの行だけ）は repo の外に置く。NDJSON と中間を外部の LLM に送らない（data-privacy）。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${GSE_SESSIONS:=$HOME/Documents/GSE-sessions}"
: "${WORK:=$HOME/gse-o1-derived/20261101-focus-leave-before-receipt}"
OUT="$EXP_DIR/results"
mkdir -p "$WORK" "$OUT"
(cd "$REPO_ROOT/src-tauri" && cargo build --bin gse-replay)
REPLAY="$REPO_ROOT/src-tauri/target/debug/gse-replay"
# 期間（conditions.md C2）。期間外のファイルは中間を作らない。
DATE_FROM=20261018
# 10-31 のファイルは集計の時点で O1 が書き込み中で、入力を固定できないので外す（decisions.md 判断 4）。
DATE_TO=20261030
for f in "$GSE_SESSIONS"/gse_o1_*.ndjson; do
  b="$(basename "$f" .ndjson)"
  d="$(echo "$b" | cut -d_ -f3)"
  { [ "$d" \< "$DATE_FROM" ] || [ "$d" \> "$DATE_TO" ]; } && continue
  # 中間を使い回すときは、analyze.py が入力の sha256 と照合し、合わなければ止まる。
  # gse-replay・prereg・slim.py を変えたときは WORK を消してから回す。
  [ -s "$WORK/$b.onsets.json" ] && continue
  "$REPLAY" "$f" --features > "$WORK/tmp.json" 2> "$WORK/$b.err"
  python3 -I "$EXP_DIR/scripts/slim.py" "$WORK/tmp.json" "$WORK/$b.onsets.json"
  rm -f "$WORK/tmp.json"
done
python3 -I "$EXP_DIR/scripts/test_analyze.py"
python3 -I "$EXP_DIR/scripts/analyze.py" "$WORK" "$GSE_SESSIONS" "$(cat "$EXP_DIR/SEED")" "$OUT" "$DATE_FROM" "$DATE_TO"
# replay の警告（解析できなかった行）があったファイルの数。行の中身は記録しない。
# git_head は集計を回したコードの版。中間を作った版は result.json の files_used（入力の sha256・hmm_version・prereg_version）で読む。
python3 -I -c "import json,sys;json.dump({'git_head':sys.argv[1],'worktree_clean':sys.argv[2]=='','files_with_replay_parse_warnings':int(sys.argv[3]),'files_total':int(sys.argv[4])},open(sys.argv[5],'w'),indent=1)" \
  "$(git -C "$REPO_ROOT" rev-parse HEAD)" "$(git -C "$REPO_ROOT" status --porcelain -- . ':!.codex/budget.json' ':!experiments/20261101-focus-leave-before-receipt/results')" "$(grep -l 'failed to parse\|not JSON objects' "$WORK"/*.err | wc -l | tr -d ' ')" "$(ls "$WORK"/*.err | wc -l | tr -d ' ')" "$OUT/provenance.json"
