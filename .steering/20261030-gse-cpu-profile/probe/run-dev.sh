#!/bin/bash
# 開発版を O1 の収集アプリと並べて起動する。識別子だけ変え、記録は一時フォルダに書かせる。
# 試作の枝の run-dev.sh から、試作の環境変数（GSE_HANDMARK_STAGE_SPIKE など）を外して写した。
# 標準出力（tracing）は $1 に書く。止めるときは、自分が起動したプロセス番号・npx・vite だけを止める。
set -u
OUT="$1"
cd /Users/johnd/GSE-prototype-cpu-profile || { echo "cd に失敗した" >&2; exit 1; }
TMPD="$(mktemp -d)" || { echo "mktemp に失敗した" >&2; exit 1; }
export GSE_DATASET="$TMPD/gse-cpu-profile"
echo "GSE_DATASET=$GSE_DATASET" > "$OUT"
env -u GSE_HANDMARK_SPIKE -u GSE_HANDMARK_SPIKE_MEASURE -u GSE_HANDMARK_STAGE_SPIKE \
  GSE_DEBUG=1 VITE_GSE_DEBUG=1 \
  npx tauri dev --config '{"identifier":"com.johnd.gse-next-cpu-profile"}' >> "$OUT" 2>&1
