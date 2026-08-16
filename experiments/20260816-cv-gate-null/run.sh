#!/usr/bin/env bash
# 1 コマンド再現 — experiments/20260816-cv-gate-null
# reproducibility-discipline ルール 4。
#
# 使い方:
#   export GSE_PHASE1_NDJSON=<Phase1 生 NDJSON を置いたディレクトリ>   # ★ repo 外
#   bash run.sh
#
# ⚠️★★ Windows コンソールは cp932。PYTHONIOENCODING / PYTHONUTF8 を必ず立てる。
# ⚠️★★★ 入力パスはリポジトリに書かない（OS ユーザー名を含むため・S5C-D8 / security-checker M1）。
set -euo pipefail

cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1

PY="${PYTHON:-python}"
SEED="$(tr -d '[:space:]' < SEED)"

if [ -z "${GSE_PHASE1_NDJSON:-}" ] || [ ! -d "${GSE_PHASE1_NDJSON}" ]; then
  echo "!! GSE_PHASE1_NDJSON が未設定 / 不在。本実験は生 NDJSON が要る（repo 外）。" >&2
  exit 1
fi

echo "== 自己検査（★ 本解析より先に回す。落ちたら結果を書かない）=="
"$PY" scripts/selftest.py

echo "== EP-Q8 帰無比較（ゲートの算術効果と非打鍵ノイズを分ける）=="
"$PY" scripts/gate_null.py \
  --flat-dir "${GSE_PHASE1_NDJSON}" \
  --window-minutes 5 \
  --seed "$SEED" \
  --bootstrap 200 \
  --out results/gate_null.json
