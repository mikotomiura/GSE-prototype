#!/usr/bin/env bash
# repro.sh — 代表実験 (較正コホート 1 本) の 1 コマンド再現エントリ (git-bash 前提)
#
# reproducibility-discipline / docs/experiment-tracking.md §「scripts/repro.sh の方針」の実体。
# 集計パイプライン自体が刻まない**来歴 (provenance)** を experiments/<exp>/ に固定してから、
# 既存の scripts/run-calibration-cohort.sh (raw/P*/ → gse-replay --calibration →
# metrics/Pxxx/<os>/*.calib.json → gse-cohort) に委譲する。パイプラインは再実装しない。
#
# 刻む来歴 (パイプライン出力に無い・再現に必須):
#   - HMM_VERSION       : engine.rs の const から抽出 (単一 SSOT・ドリフト不可)
#   - repo commit       : GSE リポジトリの git HEAD
#   - dataset commit    : gse-dataset が git repo なら HEAD (生ログはコミットしない)
#   - 入力 NDJSON hash  : raw/**/*.ndjson の sha256 一覧 → data.md
#   - env               : rustc --version / Cargo.lock hash → env.md
#
# 使い方:
#   GSE_DATASET=C:/gse-dataset ./scripts/repro.sh --exp calib-cohort
#   ./scripts/repro.sh --exp calib-cohort --root /c/gse-dataset --os windows
#   ./scripts/repro.sh --exp calib-cohort --dry-run     # 生成せず実行予定を表示
#
# プライバシー: NDJSON 生ログは読むだけ (hash のみ記録・コピーしない)。共有は集計 JSON のみ (§10)。
set -euo pipefail

EXP_NAME=""
ROOT="${GSE_DATASET:-C:/gse-dataset}"
OS_OVERRIDE=""
DRY_RUN=0

usage() {
  cat >&2 <<'USAGE'
repro.sh — 較正コホート 1 本の来歴固定 + 1 コマンド再現 (run-calibration-cohort.sh をラップ)

USAGE:
  repro.sh --exp <name> [--root <dataset>] [--os <macos|windows|linux>] [--dry-run] [-h]

OPTIONS:
  --exp <name>    実験名。experiments/<YYYYMMDD>-<name>/ を作成し来歴と結果を格納 (必須)
  --root <path>   gse-dataset ルート (既定: $GSE_DATASET → なければ C:/gse-dataset)
  --os <name>     metrics/Pxxx/<os>/ の <os> 名 (既定: run-calibration-cohort.sh が uname 判定)
  --dry-run       生成せず実行予定コマンドを表示 (来歴ファイルも書かない)
  -h, --help      このヘルプ
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --exp) EXP_NAME="${2:?--exp requires a name}"; shift 2 ;;
    --root) ROOT="${2:?--root requires a path}"; shift 2 ;;
    --os) OS_OVERRIDE="${2:?--os requires a name}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

if [ -z "$EXP_NAME" ]; then
  echo "ERROR: --exp <name> is required" >&2
  usage
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COHORT_SCRIPT="$SCRIPT_DIR/run-calibration-cohort.sh"
ENGINE_RS="$REPO_ROOT/src-tauri/src/analysis/engine.rs"

if [ ! -f "$COHORT_SCRIPT" ]; then
  echo "ERROR: run-calibration-cohort.sh not found at $COHORT_SCRIPT" >&2
  exit 3
fi

# sha256 コマンドの差異を吸収 (macOS=shasum / linux・git-bash=sha256sum)。
sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}';
  elif command -v shasum   >/dev/null 2>&1; then shasum -a 256 "$1" | awk '{print $1}';
  else echo "NO_SHA256_TOOL"; fi
}

# HMM_VERSION を engine.rs の const から抽出 (SSOT・手打ちでドリフトさせない)。
# 末尾 `|| true`: 未マッチ時のパイプライン非ゼロで代入が errexit abort するのを防ぎ :-UNKNOWN に落とす
# (他の来歴変数の || echo UNKNOWN と挙動を揃える・git-bash 移植性)。
HMM_VERSION="$(grep -oE 'HMM_VERSION[^"]*"[0-9]+\.[0-9]+\.[0-9]+"' "$ENGINE_RS" 2>/dev/null \
  | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || true)"
HMM_VERSION="${HMM_VERSION:-UNKNOWN}"

REPO_COMMIT="$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || echo UNKNOWN)"
REPO_DIRTY="$(git -C "$REPO_ROOT" status --porcelain 2>/dev/null | head -1 || true)"
[ -n "$REPO_DIRTY" ] && REPO_COMMIT="$REPO_COMMIT (dirty)"
DATASET_COMMIT="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo 'not-a-git-repo')"
RUSTC_VER="$(rustc --version 2>/dev/null || echo UNKNOWN)"
CARGO_LOCK="$REPO_ROOT/src-tauri/Cargo.lock"
CARGO_LOCK_HASH="$( [ -f "$CARGO_LOCK" ] && sha256_of "$CARGO_LOCK" || echo MISSING )"
STAMP="$(date +%Y%m%d)"
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
EXP_DIR="$REPO_ROOT/experiments/${STAMP}-${EXP_NAME}"

RAW="$ROOT/raw"

if [ "$DRY_RUN" -eq 1 ]; then
  echo "[dry-run] exp dir      : $EXP_DIR" >&2
  echo "[dry-run] HMM_VERSION  : $HMM_VERSION" >&2
  echo "[dry-run] repo commit  : $REPO_COMMIT" >&2
  echo "[dry-run] dataset root : $ROOT (commit: $DATASET_COMMIT)" >&2
  echo "[dry-run] would stamp provenance.json / data.md / env.md, then run:" >&2
  echo "  bash $COHORT_SCRIPT --root $ROOT ${OS_OVERRIDE:+--os $OS_OVERRIDE} --dry-run" >&2
  exec bash "$COHORT_SCRIPT" --root "$ROOT" ${OS_OVERRIDE:+--os "$OS_OVERRIDE"} --dry-run
fi

mkdir -p "$EXP_DIR/results"

# --- provenance.json (パイプライン出力に無い外部 sidecar・機械可読) ---
cat > "$EXP_DIR/provenance.json" <<JSON
{
  "experiment": "${STAMP}-${EXP_NAME}",
  "generated_utc": "$NOW",
  "hmm_version": "$HMM_VERSION",
  "repo_commit": "$REPO_COMMIT",
  "dataset_root": "$ROOT",
  "dataset_commit": "$DATASET_COMMIT",
  "rustc": "$RUSTC_VER",
  "cargo_lock_sha256": "$CARGO_LOCK_HASH",
  "pipeline": "run-calibration-cohort.sh (gse-replay --calibration -> gse-cohort)"
}
JSON

# --- data.md (入力 NDJSON の hash・生ログはコピーしない) ---
{
  echo "# 入力データ来歴 (${STAMP}-${EXP_NAME})"
  echo
  echo "- dataset root: \`$ROOT\`"
  echo "- dataset commit: \`$DATASET_COMMIT\`"
  echo "- 生成日時 (UTC): $NOW"
  echo
  echo "## raw NDJSON sha256 (生ログはコミットしない・hash のみ)"
  echo
  echo "> ⚠️ 相対パス (=ファイル名) も記録される。gse-dataset の raw ファイル名は participant_id 化"
  echo "> 済み前提 (実名を含めない)。ファイル名に PII が入る運用では experiments/ をコミットしないこと。"
  echo
  echo '| file | sha256 |'
  echo '|---|---|'
  if [ -d "$RAW" ]; then
    while IFS= read -r f; do
      rel="${f#"$ROOT"/}"
      echo "| \`$rel\` | \`$(sha256_of "$f")\` |"
    done < <(find "$RAW" -name '*.ndjson' | sort)
  else
    echo "| (raw/ が見つからない: $RAW) | — |"
  fi
} > "$EXP_DIR/data.md"

# --- env.md (環境固定) ---
{
  echo "# 環境固定 (${STAMP}-${EXP_NAME})"
  echo
  echo "- rustc: \`$RUSTC_VER\`"
  echo "- Cargo.lock sha256: \`$CARGO_LOCK_HASH\` (\`src-tauri/Cargo.lock\`)"
  echo "- HMM_VERSION: \`$HMM_VERSION\` (\`src-tauri/src/analysis/engine.rs\`)"
  echo "- repo commit: \`$REPO_COMMIT\`"
} > "$EXP_DIR/env.md"

# --- notes.md stub (仮説・PreReg・出典リンクは手で埋める) ---
if [ ! -f "$EXP_DIR/notes.md" ]; then
  cat > "$EXP_DIR/notes.md" <<'NOTES'
# notes

- 検証する仮説: docs/research-positioning.md §5 H?  <!-- 埋める -->
- 事前登録: docs/preregistration-v0.3.md PreReg-?    <!-- 埋める -->
- 借用手法の出典: [n] (docs/references.md)           <!-- 該当あれば -->

## 逸脱・気づき
NOTES
fi

echo "[repro] provenance stamped -> $EXP_DIR (HMM_VERSION=$HMM_VERSION, repo=$REPO_COMMIT)" >&2

# --- パイプライン本体に委譲 (raw/P*/ → calib.json → cohort verdict) ---
bash "$COHORT_SCRIPT" --root "$ROOT" ${OS_OVERRIDE:+--os "$OS_OVERRIDE"}

# --- 生成された集計 JSON を results/ に回収 (共有可能・生ログは含まない) ---
if compgen -G "$ROOT/cohort/cohort_*.json" >/dev/null; then
  latest="$(ls -t "$ROOT"/cohort/cohort_*.json | head -1 || true)"
  cp -f "$latest" "$EXP_DIR/results/"
  cp -f "$latest" "$EXP_DIR/metrics.json"
  echo "[repro] cohort verdict -> $EXP_DIR/results/$(basename "$latest")" >&2
fi
while IFS= read -r cj; do
  # metrics/Pxxx/<os>/Pxxx.calib.json → results/ に平坦コピー (被験者名を保持)
  cp -f "$cj" "$EXP_DIR/results/$(echo "${cj#"$ROOT"/}" | tr '/' '_')"
done < <(find "$ROOT/metrics" -name '*.calib.json' 2>/dev/null | sort)

echo "[repro] done. experiment: $EXP_DIR" >&2
