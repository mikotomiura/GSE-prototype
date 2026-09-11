#!/usr/bin/env bash
# experiments/20260906-interruption-resumption-arm1/run.sh
#
# ★ M1: 「中断 → 再開」の観測（★ 第 1 弾 = **離席候補アームのみ**）。
# ⚠️★★★ **現状は設計 ＋ 実行可能性プローブまで。** アウトカムの本解析 (Step 2) は
#   未実装であり、★ 実装する前に `notes.md` §7 / §8 を読むこと。
#
# 規約の SSOT: docs/experiment-tracking.md

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

: "${GSE_DATASET:?GSE_DATASET が未設定。入力 NDJSON の置き場を指すこと (例: C:/gse-dataset)}"
INPUT_DIR="${INPUT_DIR:-$GSE_DATASET/raw}"

PY="${PYTHON:-$(command -v python3 || command -v python)}"
: "${PY:?python が見つかりません (python3 / python のどちらも無い)}"

mkdir -p "$EXP_DIR/results"

# ---------------------------------------------------------------------------
# ⚠️★★★ Step 0: capabilities の機械判定 (ADR-013 D1 / Migration 4)
# ---------------------------------------------------------------------------
#
# ⚠️★★★ **本実験は GSE が収集した信号を読むので、ゲートは *適用される*。消さないこと。**
#   (★ 対照的に B1 = `20260906-p321-resumption-baseline` は外部データなので適用外だった)
#
# ★ 本アームが読む行種を宣言する:
#     key   — 離席候補 (>=180s の打鍵間隔) の検出に使う
#     feat  — p_stuck / p_flow (エピソード境界と回復判定)
#     paste — receipt (受領)。⚠️ 実体は PasteEvent (時刻 + 文字数) のみ
#
# ⚠️★★★ **`focus_transition` を足してはならない。**
#   ★ 2026-09-06 実測: 既存 76 本は `capabilities` キーを **1 本も持たず**、
#     `focus_transition` は **INSTRUMENT_ABSENT (exit 4)** になる。
#     ★ 計器 (`observe.rs`) の実装は **2026-08-24** で、収集 (2026-04〜07) の **後**である。
#   → ★ 足すとここで止まる。★ **それが正しい挙動**である (notes.md §2)。
#   ⚠️ フォーカス遷移アームは **新規収集後**に、別の実験ディレクトリで回す。

REQUIRED_LINE_TYPES=(
  --require key
  --require feat
  --require paste
)

# ⚠️★★ 一時ファイルへ書いてから mv する（赤で落ちたとき 0 バイトを残さない）。
# ⚠️★★★ 人が読む本文（★ 実ファイル名を含む）はゲートが **stderr** へ出す。
#   → `2>` でコミット先へ回さないこと。
CAPS_TMP="$EXP_DIR/results/.capabilities.json.tmp"
PYTHONUTF8=1 "$PY" "$REPO_ROOT/scripts/capabilities_gate.py" \
  "$INPUT_DIR" \
  "${REQUIRED_LINE_TYPES[@]}" \
  --json > "$CAPS_TMP"

# ⚠️★★★ **`files[]` を落としてからコミット先へ置く** (security-checker HIGH-2)。
#   ★ `capabilities_gate.py` の `file_id` は `sha256(ファイル名)[:8]` であり、
#     ⚠️★★★ **不可逆ではない** —— ★ 命名規則 (擬似 ID ＋ 秒単位の開始日時) は repo に
#     書いてあるので、探索空間が小さく **総当たりで実ファイル名に戻せる**
#     (★ レビューで 76/76 が数分で復元された)。
#   → ★ 解析に要るのは **verdicts** だけである。★ 診断のための件数は集計して残す。
PYTHONUTF8=1 "$PY" - "$CAPS_TMP" "$EXP_DIR/results/capabilities.json" <<'PYEOF'
import json, sys
src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src, encoding="utf-8"))
files = d.pop("files", [])
d["files_summary"] = {
    "n_files": len(files),
    "n_declaring_capabilities": sum(1 for f in files if f.get("declares_capabilities")),
    "malformed_lines_total": sum(f.get("malformed_lines") or 0 for f in files),
    "note": "⚠️ file_id は sha256(ファイル名)[:8] で不可逆ではないため、"
            "個別の files[] はコミットしない (security-checker HIGH-2)",
}
json.dump(d, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
open(dst, "a", encoding="utf-8").write("\n")
PYEOF
rm -f "$CAPS_TMP"

echo "Step 0 OK: capabilities gate 通過 (結果は results/capabilities.json)"
echo "⚠️ 注意: 本コホートは capabilities 宣言 0/76 の旧ログである。"
echo "   → ★ 結論に「〜が無かった」という形の文を書かないこと (notes.md §7-4)。"

# ---------------------------------------------------------------------------
# Step 1: 再現性アンカーを刻む  ⚠️★★★ 「記録」ではなく「ゲート」にする
# ---------------------------------------------------------------------------
#
# ⚠️★★★ `echo "x=$(grep ...)"` は **コマンド置換が失敗しても echo が成功する**ので
#   `set -e` が発火せず、★ **空値が provenance に残るだけ**になる (code-reviewer H-2)。
#   → ★ 値を取り出して**照合し、合わなければ止める**。

# ⚠️★★ macOS には `sha256sum` が無い (`shasum -a 256`)。
if command -v sha256sum > /dev/null 2>&1; then
  sha256_of() { sha256sum "$1" | cut -d' ' -f1; }
elif command -v shasum > /dev/null 2>&1; then
  sha256_of() { shasum -a 256 "$1" | cut -d' ' -f1; }
else
  echo "⚠️ sha256sum も shasum も見つかりません。止まります。" >&2; exit 1
fi

# ★★★ Rust 側の閾値と Python 側の手写しが一致することを **検査する**。
#   ⚠️ 一致を検査しないと、Rust 側を変えた瞬間に本アームの主要閾値が黙ってずれる。
AWAY_RS="$(grep -m1 -oE 'AWAY_IDLE_MS: u64 = [0-9_]+' \
  "$REPO_ROOT/src-tauri/src/analysis/intervention.rs" | grep -oE '[0-9_]+$' | tr -d '_' || true)"
AWAY_PY="$(grep -m1 -oE '^AWAY_IDLE_MS = [0-9_]+' "$EXP_DIR/feasibility_probe.py" \
  | grep -oE '[0-9_]+$' | tr -d '_' || true)"
[ -n "$AWAY_RS" ] || { echo "⚠️★★★ intervention.rs から AWAY_IDLE_MS を取れなかった。止まる。" >&2; exit 1; }
[ -n "$AWAY_PY" ] || { echo "⚠️★★★ feasibility_probe.py から AWAY_IDLE_MS を取れなかった。止まる。" >&2; exit 1; }
[ "$AWAY_RS" = "$AWAY_PY" ] || {
  echo "⚠️★★★ AWAY_IDLE_MS が Rust ($AWAY_RS) と Python ($AWAY_PY) でずれている。止まる。" >&2
  echo "   → ★ 本アームの主要閾値なので、直してから回すこと。" >&2
  exit 1
}

HMM_V="$(grep -m1 -oE 'HMM_VERSION: &str = "[^"]+"' \
  "$REPO_ROOT/src-tauri/src/analysis/engine.rs" | grep -oE '"[^"]+"' | tr -d '"' || true)"
[ -n "$HMM_V" ] || { echo "⚠️★★★ engine.rs から HMM_VERSION を取れなかった。止まる。" >&2; exit 1; }

{
  echo "hmm_version_current_code=$HMM_V"
  echo "away_idle_ms=$AWAY_RS  (Rust と Python の一致を検査済み)"
  echo "probe_sha256=$(sha256_of "$EXP_DIR/feasibility_probe.py")"
  echo "git_head=$(git -C "$REPO_ROOT" rev-parse --short HEAD)"
  echo "git_dirty=$(git -C "$REPO_ROOT" status --porcelain | wc -l | tr -d ' ') 件の未コミット変更"
  echo "seed=N/A (乱数要素なし)"
} > "$EXP_DIR/results/provenance.txt"
cat "$EXP_DIR/results/provenance.txt"
echo "⚠️★★★ 注意: 本コホートの feat 行は HMM 0.2.0 / 0.3.0 で生成されている"
echo "   (★ 実測: 0.2.0 が 8 本 / 0.3.0 が 68 本)。★ 現行コードは ${HMM_V}。"
echo "   → ⚠️ Step 2b で **ログ済みの p_stuck / p_flow をそのまま使うと版が混ざる**。"
echo "     ★ gse-replay で現行エンジンに通し直すこと (notes.md §7-6)。"

# ---------------------------------------------------------------------------
# Step 2a: 実行可能性プローブ (★ アウトカムの本解析ではない)
# ---------------------------------------------------------------------------
echo
echo "Step 2a-1: selftest (★ 境界ガードが空回りしていないか)"
# ⚠️★★★ 実データでは `excluded_boundary_crossing = 0` になる。
#   ★ それだけでは「効いている」のか「動いていない」のか区別できないので、
#     合成データで **効く場合 / 効かない場合** の両方を作って確かめる。
PYTHONUTF8=1 "$PY" "$EXP_DIR/feasibility_probe.py" --selftest

echo
echo "Step 2a-2: 実行可能性プローブ"
PYTHONUTF8=1 "$PY" "$EXP_DIR/feasibility_probe.py" \
  --input "$INPUT_DIR" --out "$EXP_DIR/results/feasibility.json"

# ---------------------------------------------------------------------------
# Step 2b: アウトカムの本解析  ⚠️★★★ **未実装**
# ---------------------------------------------------------------------------
# ★ 実装するときに必ず満たすこと (notes.md §4 の制約表 / §5 の形):
#   - `receipt_free_resumption` を **生存時間 / 競合リスク** (5 分 / 10 分の CIF) で出す
#   - `stuck_exit_without_receipt` は **副次**に留める
#   - **R0 型 / R0' 型 / R1 型を並べて出す** (★ B1 の知見。notes.md §6)
#   - `stuck_episode_count` / `recovered_episode_count` / 差分を必ず出す (ADR-023 D8)
#   - `manual_contribution_ratio` を**必ず併報**する (★ 推定に依存しない唯一の対照)
#   - ★ §5 の定型文 (p_flow 相補性) をレポートに貼る (ADR-023 D7)
#
echo
echo "⚠️★★★ Step 2b (アウトカムの本解析) は未実装である。"
echo "   ★ 実装前に notes.md §7 (限界) と §8 (手順) を読むこと。"
echo "   ⚠️ 本アームは探索的であり、確証ゲート (GATE1-3) に載せない。"
