#!/usr/bin/env bash
# 事後の頑健性（レビュー指摘）のため、停滞の始まりを s_ms・t0_ms つきで作り直す。
# 前の実験の run2.sh と同じ手順（convert → replay → add_feat → 書き手ごとに詰めてつなぐ → --features）で、
# onset の行の s_ms・t0_ms・theta_person_ms を残す。出力は $WORK/writers/<wid>_onsets_full.json（repo の外）。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
: "${COAUTHOR_DIR:=$HOME/gse-public-data/coauthor}"
RAW="$COAUTHOR_DIR/raw/unz/coauthor-v1.0"
WORK="$COAUTHOR_DIR/work2_dwell100"
TMP="$COAUTHOR_DIR/tmp_rebuild"
BIN="$REPO_ROOT/src-tauri/target/release/gse-replay"
SC="$REPO_ROOT/experiments/20261031-coauthor-pre-request-signal/scripts"
[ -x "$BIN" ] || (cd "$REPO_ROOT/src-tauri" && cargo build --release --bin gse-replay)
rm -rf "$TMP"; mkdir -p "$TMP"
: > "$TMP/replay_stderr.log"
for f in "$RAW"/*.jsonl; do
  sid="$(basename "$f" .jsonl)"
  python3 -I "$SC/convert.py" "$f" "$TMP/$sid.ndjson" "$TMP/${sid}_events.json" 100 > /dev/null
  "$BIN" "$TMP/$sid.ndjson" > "$TMP/${sid}_featfull.json" 2>>"$TMP/replay_stderr.log" < /dev/null
  python3 -I "$SC/add_feat.py" "$TMP/$sid.ndjson" "$TMP/${sid}_featfull.json" "$TMP/$sid.withfeat.ndjson"
  rm "$TMP/$sid.ndjson" "$TMP/${sid}_featfull.json" "$TMP/${sid}_events.json"
done
while read -r wid sids; do
  files=()
  for s in $sids; do [ -f "$TMP/$s.withfeat.ndjson" ] && files+=("$TMP/$s.withfeat.ndjson"); done
  [ "${#files[@]}" -gt 0 ] || continue
  python3 -I "$SC/concat_writer.py" "$TMP/$wid.ndjson" "$TMP/${wid}_offsets.json" "${files[@]}" < /dev/null
  cmp -s "$TMP/${wid}_offsets.json" "$WORK/writers/${wid}_offsets.json" || { echo "offsets differ: writer" >&2; exit 1; }
  "$BIN" "$TMP/$wid.ndjson" --features > "$TMP/${wid}_ft.json" 2>>"$TMP/replay_stderr.log" < /dev/null
  python3 -I -c "import json,sys;d=json.load(open(sys.argv[1]));json.dump([{k:r['stall_onset'].get(k) for k in ('s_ms','t0_ms','theta_person_ms')}|{'t_ms':r['t_ms']} for r in d['rows'] if r['stall_onset'].get('is_onset')],open(sys.argv[2],'w'))" \
    "$TMP/${wid}_ft.json" "$WORK/writers/${wid}_onsets_full.json" < /dev/null
  rm "$TMP/$wid.ndjson" "$TMP/${wid}_ft.json"
done < "$WORK/writers/groups.txt"
echo "replay stderr bytes: $(wc -c < "$TMP/replay_stderr.log")"
rm -rf "$TMP"
