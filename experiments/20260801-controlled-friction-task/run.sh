#!/usr/bin/env bash
# G1 統制タスク実験 — 実施前チェック / 1 コマンド再現
#
#   bash run.sh              実施前チェックだけ（既定）。資材が揃えば緑・欠ければ赤
#   bash run.sh --analyze    実施前チェックのうえ、解析まで走らせる
#
# ★ 判定基準の単一真実源は preregistration.md §3（凍結）。本スクリプトはそれを変更しない。
# ⚠️ 実施は「Phase1 完了 ＋ 研究者承認による凍結解除後」。順序の決定は研究者判断であり、
#    本スクリプトは技術的な準備が整っているかだけを見る。
set -euo pipefail
cd "$(dirname "$0")"

FAIL=0
ok()   { printf '  [ OK ] %s\n' "$1"; }
bad()  { printf '  [FAIL] %s\n' "$1"; FAIL=$((FAIL + 1)); }
note() { printf '  [note] %s\n' "$1"; }

echo "=============================================================="
echo " G1 実施前チェック (experiments/20260801-controlled-friction-task)"
echo "=============================================================="

# --- 0. 前提コマンド（不在を素通りさせない） ---------------------------------
echo
echo "[0] 前提コマンド"
if command -v python3 >/dev/null 2>&1; then
  ok "python3 = $(python3 --version 2>&1)"
else
  bad "python3 が無い。解析スクリプトは標準ライブラリのみで動くが python3 は要る"
  echo
  echo "[RED] 前提コマンドが無いため続行できない"
  exit 1
fi

# --- 1. 凍結文書 -------------------------------------------------------------
echo
echo "[1] 凍結文書"
for f in preregistration.md config.json SEED README.md notes.md env.md data.md; do
  if [ -s "$f" ]; then ok "$f"; else bad "$f が無い/空"; fi
done
if python3 -c "import json; json.load(open('config.json'))" 2>/dev/null; then
  ok "config.json は妥当な JSON"
else
  bad "config.json が JSON として壊れている"
fi
if grep -q 'BLOCK_ORDER_SEED=' SEED 2>/dev/null; then
  ok "SEED に BLOCK_ORDER_SEED がある"
else
  bad "SEED に BLOCK_ORDER_SEED が無い"
fi

# --- 2. 実施資材 -------------------------------------------------------------
echo
echo "[2] 実施資材"
for f in protocol.md consent.md; do
  if [ -s "$f" ]; then ok "$f"; else bad "$f が無い/空（実施できない）"; fi
done
if [ -d materials ]; then ok "materials/"; else bad "materials/ が無い"; fi

# --- 3. 課題文の機械検証（§2.2 / §2.7） --------------------------------------
echo
echo "[3] 課題文の制約検証 (validate_materials.py)"
TMP_MAT=$(mktemp)
if python3 validate_materials.py > "$TMP_MAT" 2>&1; then
  sed 's/^/    /' "$TMP_MAT"
  ok "課題文の制約を満たしている"
else
  sed 's/^/    /' "$TMP_MAT"
  bad "課題文が制約を満たしていない"
fi
rm -f "$TMP_MAT"

if python3 validate_materials.py --strict >/dev/null 2>&1; then
  ok "本番用 8 題材 × 2 版が揃っている（確証セッションを回せる）"
else
  note "本番用 8 題材 × 2 版は未完成 → 回せるのは **パイロット P-1（4 ブロック）まで**"
  note "  生成: python3 assign.py --pilot"
fi

# --- 4. スクリプトの自己検証 -------------------------------------------------
echo
echo "[4] スクリプトの自己検証"
for s in assign analyze; do
  TMP_S=$(mktemp)
  if python3 "$s.py" --selftest > "$TMP_S" 2>&1; then
    ok "$s.py --selftest 緑"
  else
    sed 's/^/    /' "$TMP_S"
    bad "$s.py --selftest 赤"
  fi
  rm -f "$TMP_S"
done

# --- 5. 凍結対象に触れていないこと ------------------------------------------
echo
echo "[5] 凍結対象への非接触（G1 はコード変更ゼロで実施できる）"
if git rev-parse --git-dir >/dev/null 2>&1; then
  DIRTY=$(git status --porcelain -- ../../src-tauri ../../src 2>/dev/null | wc -l | tr -d ' ')
  if [ "$DIRTY" = "0" ]; then
    ok "src-tauri/ と src/ に未コミットの変更が無い"
  else
    bad "src-tauri/ または src/ に変更がある（$DIRTY 件）。G1 はコード変更を要さない"
  fi
else
  note "git repo の外なので凍結対象チェックを飛ばした"
fi

# --- 6. データの状態 ---------------------------------------------------------
echo
echo "[6] データの状態"
SPECS=0
if [ -d blocks ]; then
  SPECS=$(find blocks -maxdepth 1 -name 'P*.json' 2>/dev/null | wc -l | tr -d ' ')
fi
if [ "$SPECS" = "0" ]; then
  note "blocks/ に割付ファイルが無い = **まだ 1 件もデータを取っていない**（事前登録どおり）"
  note "  実施後の手順: python3 assign.py --subject P0xx --json > blocks/P0xx.json"
  note "                → 各 block に \"file\" と \"produced_chars\" を書き足す"
else
  ok "blocks/ に割付ファイルが $SPECS 件ある"
fi

# --- 判定 -------------------------------------------------------------------
echo
echo "=============================================================="
if [ "$FAIL" -ne 0 ]; then
  echo " [RED] 実施前チェック 失敗 $FAIL 件。上の [FAIL] を潰すこと。"
  echo "=============================================================="
  exit 1
fi
echo " [GREEN] 実施前チェック 全項目通過"
echo "   → 資材・プロトコル・同意・解析スクリプトは揃っている。"
echo "   ⚠️ 実施の可否（特に Phase1 の凍結解除前に回してよいか）は **研究者判断**。"
echo "=============================================================="

# --- 解析（明示的に要求されたときだけ） --------------------------------------
if [ "${1:-}" = "--analyze" ]; then
  echo
  if [ "$SPECS" = "0" ]; then
    echo "[NG] --analyze が指定されたが blocks/ に割付ファイルが無い（データ未取得）"
    exit 1
  fi
  DATASET="${GSE_DATASET:-${DATASET_ROOT:-$HOME/gse-dataset}}"
  echo "[analyze] dataset=$DATASET"
  echo "⚠️ preregistration.md §3.4 の見る順序（操作チェック → positive control → FS-A/FS-B）は"
  echo "   出力の並び順で強制される。順序を飛ばして読まないこと。"
  python3 analyze.py --dataset "$DATASET" --blocks-dir blocks --out results/metrics.json
elif [ $# -gt 0 ]; then
  echo
  echo "[NG] 不明な引数: $*  (使えるのは --analyze のみ)"
  exit 2
fi
