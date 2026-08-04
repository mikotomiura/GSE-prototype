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
for f in protocol.md consent.md participant-guide.md; do
  if [ -s "$f" ]; then ok "$f"; else bad "$f が無い/空（実施できない）"; fi
done
if [ -d materials ]; then ok "materials/"; else bad "materials/ が無い"; fi
# ★ 第 5 版 §2.11: 被験者の入力先は固定する（無いと「どこに打つか」が未定になる）
if [ -s writing-pad.html ]; then
  ok "writing-pad.html（被験者の入力先・§2.11）"
else
  bad "writing-pad.html が無い。被験者の入力先が固定されていない（§2.11）"
fi

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
for s in assign analyze validate_blocks forms_to_blocks build_task_pages; do
  TMP_S=$(mktemp)
  if python3 "$s.py" --selftest > "$TMP_S" 2>&1; then
    ok "$s.py --selftest 緑"
  else
    sed 's/^/    /' "$TMP_S"
    bad "$s.py --selftest 赤"
  fi
  rm -f "$TMP_S"
done

# ★ 第 7 版 §2.12: 被験者への事前連絡に**題材（分野）と課題の型を書かない**と凍結した
#   （当日その場で画面提示するので教える必要が無い・§2.13）。
#   ⚠️ 一度「分野を書く」と決めて第 6 版で実装し、第 7 版で撤回した経緯がある。
#      **書き戻されたら赤にする**。node で本文生成関数を実際に呼ぶので、
#      未定義参照（実例: G1_TOPIC_TITLES の残存）も同時に捕まる。
TMP_T=$(mktemp)
if python3 ../../scripts/check_g1_emails.py > "$TMP_T" 2>&1; then
  ok "受付メールが §2.12 の開示範囲を守っている"
else
  sed 's/^/    /' "$TMP_T"
  bad "受付メールが §2.12 の開示範囲から外れている"
fi
rm -f "$TMP_T"

# --- 5. アプリ側の前提 -------------------------------------------------------
# ★ 第 5 版 §5.4 で検査の意図を置き換えた。
#   旧: 「G1 はコード変更ゼロで実施できる」→ src-tauri/ src/ に変更が無いこと
#   新: 「G1 が要求する変更 (プローブ kill switch) が入っており、それ以外の未コミット変更が無い」
#
#   ⚠️ 旧検査は `git status` を見るだけなので、**変更をコミットした瞬間に黙って緑に戻った**。
#      すなわち「コード変更ゼロ」を検査しているつもりで、実際には何も検査していなかった
#      (silent pass)。kill switch の存在を直接見ることで、失われたら赤になるようにする。
echo
echo "[5] アプリ側の前提（プローブ kill switch・§5.4）"
KILL_SWITCH_FN="src-tauri/src/analysis/probe_scheduler.rs"
KILL_SWITCH_USE="src-tauri/src/lib.rs"
if [ -f "../../$KILL_SWITCH_FN" ] && [ -f "../../$KILL_SWITCH_USE" ]; then
  if grep -q 'pub fn probes_disabled_by_env' "../../$KILL_SWITCH_FN" \
     && grep -q 'GSE_DISABLE_PROBES' "../../$KILL_SWITCH_USE"; then
    ok "プローブ kill switch がある（GSE_DISABLE_PROBES / probes_disabled_by_env）"
    # ★ grep は「文字列があること」しか見ない。挙動（★ 未設定で無効化しないこと）は
    #   Rust のユニットテストが持っているので、cargo があるなら実際に走らせる。
    #   ⚠️ cargo が無い環境（被験者端末は CI ビルド済みバイナリを使う）では**飛ばしたことを明示**する。
    #      黙って飛ばすと silent-failure-in-guard-scripts の「外部コマンド不在で素通り」になる。
    CARGO_BIN=$(command -v cargo || echo "$HOME/.cargo/bin/cargo")
    if [ -x "$CARGO_BIN" ]; then
      TMP_KS=$(mktemp)
      if (cd ../.. && "$CARGO_BIN" test --quiet --manifest-path src-tauri/Cargo.toml --lib \
            probe_scheduler::tests::probes_kill_switch) > "$TMP_KS" 2>&1; then
        ok "kill switch の挙動テストが緑（未設定では無効化しない・\"1\" のときだけ無効化する）"
      else
        sed 's/^/    /' "$TMP_KS"
        bad "kill switch の挙動テストが赤。★ 既定挙動が変わっている可能性がある"
      fi
      rm -f "$TMP_KS"
    else
      note "cargo が無いので kill switch の挙動テストは飛ばした（★ 飛ばしたことを明示している）"
      note "  → 実施後の客観検証は validate_blocks.py --dataset（probe 行 0）で行う"
    fi
  else
    bad "プローブ kill switch が見つからない（GSE_DISABLE_PROBES / probes_disabled_by_env）"
    note "  §2.6 は「アプリ内プローブを使わない」と凍結し、§3.6 が事後のブロック除外を"
    note "  禁じているので、**実施前に止めるしかない**（§5.4）"
  fi
else
  note "src-tauri/ が見つからない（この repo の外で走らせている）"
fi
if git rev-parse --git-dir >/dev/null 2>&1; then
  DIRTY=$(git status --porcelain -- ../../src-tauri ../../src 2>/dev/null | wc -l | tr -d ' ')
  if [ "$DIRTY" = "0" ]; then
    ok "src-tauri/ と src/ に未コミットの変更が無い（実施は検証済みビルドで行う）"
  else
    bad "src-tauri/ または src/ に未コミットの変更がある（$DIRTY 件）"
    note "  ★ 未検証のビルドで実験を回さないこと（kill switch 以外の変更は G1 に不要）"
  fi
else
  note "git repo の外なのでコミット状態のチェックを飛ばした"
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
  note "                → python3 forms_to_blocks.py --csv <G1-M回答.csv> --subject P0xx --write"
  note "                → python3 validate_blocks.py --dataset ~/gse-dataset"
else
  ok "blocks/ に割付ファイルが $SPECS 件ある"
  # ★ 転記ミスの検出（除外も判定もしない・§3.6 に触れない）
  TMP_VB=$(mktemp)
  if python3 validate_blocks.py > "$TMP_VB" 2>&1; then
    sed 's/^/    /' "$TMP_VB"
    ok "割付ファイルの転記に問題なし"
  else
    sed 's/^/    /' "$TMP_VB"
    bad "割付ファイルに転記ミスの疑いがある（validate_blocks.py）"
  fi
  rm -f "$TMP_VB"
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
