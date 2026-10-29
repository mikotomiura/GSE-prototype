#!/bin/bash
# 開発版を O1 と並べて起動する（判断 2）。識別子だけ変え、記録は一時フォルダに書かせる。
# 標準出力（tracing）は $1 に書く。止めるときは、このスクリプトが出すプロセス番号だけを止める。
set -u
OUT="$1"
cd /Users/johnd/GSE-prototype-handmark-stage
export GSE_DATASET="$(mktemp -d)/gse-spike"
echo "GSE_DATASET=$GSE_DATASET" > "$OUT"
env -u GSE_HANDMARK_SPIKE -u GSE_HANDMARK_SPIKE_MEASURE -u GSE_HANDMARK_STAGE_SPIKE_SYNTH_POINTER -u GSE_HANDMARK_STAGE_SPIKE_POINTER_OFF \
  GSE_HANDMARK_STAGE_SPIKE=1 GSE_DEBUG=1 VITE_GSE_DEBUG=1 \
  npx tauri dev --config '{"identifier":"com.johnd.gse-next-spike"}' >> "$OUT" 2>&1
