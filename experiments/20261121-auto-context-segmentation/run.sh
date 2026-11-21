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
: "${PEOPLE_JSON:?PEOPLE_JSON が未設定。[{id, files:[...]}] の JSON を指すこと（実パスを含むのでコミットしない・people*.json は .gitignore 済み）}"

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
  # 打鍵の量は key、推定状態（循環の検査）は feat から読む。
  # focus_transition / pointer_bin は config_gated で 0 行は判定不能 → --features 側で null になり、
  # 解析はその列を落とす（acs_core.standardize）。ここでは必須にしない。
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

# 判定に使うファイルそのもの（PEOPLE_JSON に書いたもの）をゲートに通す（security-checker LOW）。
INPUT_FILES=()
while IFS= read -r f; do INPUT_FILES+=("$f"); done < <(
  PYTHONUTF8=1 "$PY" -I -c 'import json,sys; [print(f) for p in json.load(open(sys.argv[1], encoding="utf-8")) for f in p["files"]]' "$PEOPLE_JSON"
)
[ "${#INPUT_FILES[@]}" -gt 0 ] || { echo "PEOPLE_JSON にファイルが 1 本も無い" >&2; exit 2; }
CAPS_TMP="$EXP_DIR/results/.capabilities.json.tmp"
PYTHONUTF8=1 "$PY" "$REPO_ROOT/scripts/capabilities_gate.py" \
  "${INPUT_FILES[@]}" \
  "${REQUIRED_LINE_TYPES[@]}" \
  --json > "$CAPS_TMP"
mv "$CAPS_TMP" "$EXP_DIR/results/capabilities.json"
# ⚠️★★ `set -e` があるので赤ならここで止まる。★ **`| tail` にパイプしないこと** ——
#   `$?` が tail のものになり、赤を見落とす
#   (`.steering/20260819-g1-reboot-and-instrument-fix/blockers.md` B-3 で実際に踏んだ)。

echo "Step 0 OK: capabilities gate 通過 (結果は results/capabilities.json)"

# ---------------------------------------------------------------------------
# Step 1: 再現性アンカー
# ---------------------------------------------------------------------------
grep -m1 'HMM_VERSION' "$REPO_ROOT/src-tauri/src/analysis/engine.rs" > "$EXP_DIR/results/hmm_version.txt"
git -C "$REPO_ROOT" rev-parse HEAD > "$EXP_DIR/results/git_head.txt"

# ---------------------------------------------------------------------------
# Step 2: 合成の対照 → 実データ
# ---------------------------------------------------------------------------
# ⚠️ 特徴行（封筒）は work/ に置く（.gitignore 済み・共有しない・外部へ送らない）。
WORK="$EXP_DIR/work"
mkdir -p "$WORK"
SEED_VAL="$(cat "$EXP_DIR/SEED")"
for kind in positive negative; do
  PYTHONUTF8=1 "$PY" -I "$EXP_DIR/gen_synth.py" --kind "$kind" --seed "$SEED_VAL" \
    --out-ndjson "$WORK/synth_$kind.ndjson" --out-truth "$WORK/synth_$kind.truth.json"
done
# 陽性: 陽性の基準で通る。陰性: 陰性の基準で通る。壊した入力: 陰性の記録は陽性の基準で落ちる。
PYTHONUTF8=1 "$PY" -I "$EXP_DIR/evaluate.py" synth --ndjson "$WORK/synth_positive.ndjson" \
  --truth "$WORK/synth_positive.truth.json" --criteria positive --work "$WORK" > "$EXP_DIR/results/synth_positive.json"
PYTHONUTF8=1 "$PY" -I "$EXP_DIR/evaluate.py" synth --ndjson "$WORK/synth_negative.ndjson" \
  --truth "$WORK/synth_negative.truth.json" --criteria negative --work "$WORK" > "$EXP_DIR/results/synth_negative.json"
# ⚠️ 不合格は終了コード 3。例外（traceback）の 1 を「正しく落ちた」と読まないよう、3 と pass:false の両方を見る。
set +e
PYTHONUTF8=1 "$PY" -I "$EXP_DIR/evaluate.py" synth --ndjson "$WORK/synth_negative.ndjson" \
  --truth "$WORK/synth_negative.truth.json" --criteria positive --work "$WORK" > "$EXP_DIR/results/synth_broken.json"
broken_rc=$?
set -e
if [ "$broken_rc" -ne 3 ] || ! "$PY" -I -c 'import json,sys; sys.exit(0 if json.load(open(sys.argv[1]))["pass"] is False else 1)' "$EXP_DIR/results/synth_broken.json"; then
  echo "NG: 境界を消した入力が、陽性の基準で期待どおりに落ちなかった（rc=$broken_rc）" >&2
  exit 1
fi
echo "Step 2a OK: 合成の対照 3 本"

# 実データ: 人ごとのファイルの一覧（Step 0 と同じ PEOPLE_JSON）。
PYTHONUTF8=1 "$PY" -I "$EXP_DIR/evaluate.py" real --people "$PEOPLE_JSON" --work "$WORK" \
  --out "$WORK/real.json"
echo "Step 2b OK: 実データの判定は work/real.json（区間の一覧を含むのでコミットしない。notes.md へは集計だけを写す）"
