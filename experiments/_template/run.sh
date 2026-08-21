#!/usr/bin/env bash
# experiments/<YYYYMMDD>-<exp-name>/run.sh のテンプレート。
#
# ⚠️★★★ **Step 0 を消さないこと。** ADR-013 Migration 4。
#   「対象ログの行種を数える」は**人の手順ではなくコード**である。
#   ★ ADR-013 自身の診断は逐語で「規約は書いてあったのに適用しなかった」であり、
#     ⚠️ 人が適用し忘れられる形のままでは 3 件目の失敗が起きる。
#
# 規約の SSOT: docs/experiment-tracking.md / reproducibility-discipline skill。

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ⚠️★ 入力 NDJSON の場所。★ **repo にコミットしない** (data.md に gse-dataset の
#   commit hash で固定参照する。docs/experiment-tracking.md)。
: "${GSE_DATASET:?GSE_DATASET が未設定。入力 NDJSON の置き場を指すこと}"
INPUT_DIR="${INPUT_DIR:-$GSE_DATASET/raw}"

mkdir -p "$EXP_DIR/results"

# ---------------------------------------------------------------------------
# ⚠️★★★ Step 0: capabilities の機械判定 (ADR-013 D1 / Migration 4)
# ---------------------------------------------------------------------------
#
# ★ **この解析が読む行種をここで宣言する。** 宣言しない解析は検査できない。
#
# ⚠️ 判定表 (3 群 ＋ 「表に無い」):
#   | unconditional  | 0 行 | ★ 信号が無かった (測れて、無かった)          |
#   | threshold_gated| 0 行 | ⚠️ 判定不能 (閾値未達と区別できない)          |
#   | config_gated   | 0 行 | ⚠️ 判定不能 (設定で送出元ごと止まっていた)     |
#   | どれにも無い    | 0 行 | ⚠️ 計器が無かった (★ 過去 2 件の失敗はここ)   |
#
# ⚠️ **旧ログには `capabilities` キー自体が無い** → 「計器が無かった」に倒される。
# ⚠️ 新旧が混ざったコホートは `MIXED` で**止まる** (★ 平均を取る前に止める)。
#
# ★ 「判定不能」を明示的に受け入れる解析だけが `--allow-undecidable` を付けてよい。
#   ⚠️ その場合、`notes.md` の結論を「無かった」ではなく**「判定不能」**と書くこと。

REQUIRED_LINE_TYPES=(
  # 例: --require key --require feat --require starve_window
  --require key
  --require feat
)

# ⚠️★★ **一時ファイルへ書いてから mv する。** リダイレクトを直接張ると、
#   ゲートが赤で落ちたときに `results/capabilities.json` が **0 バイトで残り**、
#   ★ 次に読む人が「宣言 0 件」と誤読する (security-checker LOW)。
#
# ⚠️★★★ 保存されるのは **JSON だけ** である。人が読む本文（★ 実ファイル名を含む）は
#   ゲートが **stderr** へ出すので端末に残る。→ ⚠️ `2>` でコミット先へ回さないこと。
#   ★ 実データのファイル名は「擬似 ID ＋ セッション開始時刻」そのものであり、
#     `.gitignore` は `results/*.json` を塞いでいない。
# ⚠️★ `python` は macOS に無いことがあり、`python3` は Windows の一部環境に無い。
#   ★ CI は `python3`、Windows の git-bash は `python` —— **両方を試す**
#   (code-reviewer LOW・2026-08-21)。
PY="${PYTHON:-$(command -v python3 || command -v python)}"
: "${PY:?python が見つかりません (python3 / python のどちらも無い)}"

CAPS_TMP="$EXP_DIR/results/.capabilities.json.tmp"
PYTHONUTF8=1 "$PY" "$REPO_ROOT/scripts/capabilities_gate.py" \
  "$INPUT_DIR" \
  "${REQUIRED_LINE_TYPES[@]}" \
  --json > "$CAPS_TMP"
mv "$CAPS_TMP" "$EXP_DIR/results/capabilities.json"
# ⚠️★★ `set -e` があるので赤ならここで止まる。★ **`| tail` にパイプしないこと** ——
#   `$?` が tail のものになり、赤を見落とす
#   (`.steering/20260819-g1-reboot-and-instrument-fix/blockers.md` B-3 で実際に踏んだ)。

echo "Step 0 OK: capabilities gate 通過 (結果は results/capabilities.json)"

# ---------------------------------------------------------------------------
# Step 1: 再現性アンカーを刻む (docs/experiment-tracking.md)
# ---------------------------------------------------------------------------
# ★ HMM_VERSION / Cargo.lock / seed / 入力の commit hash は config と結果に刻む。

# grep -m1 'HMM_VERSION' "$REPO_ROOT/src-tauri/src/analysis/engine.rs" > "$EXP_DIR/results/hmm_version.txt"

# ---------------------------------------------------------------------------
# Step 2: 本体 (gse-replay / gse-cohort / Python 解析)
# ---------------------------------------------------------------------------
# ⚠️★★ `Cargo.toml` は repo 直下に無い (`src-tauri/`)。
#   → `cd src-tauri` するか `--manifest-path` を付ける。
#
# cargo run --manifest-path "$REPO_ROOT/src-tauri/Cargo.toml" --bin gse-replay -- \
#   "$INPUT_DIR/P010/..." --metrics --json > "$EXP_DIR/results/metrics.json"

echo "TODO: Step 2 を実装する"
