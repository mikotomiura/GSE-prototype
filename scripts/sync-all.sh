#!/usr/bin/env bash
# GSE セッション NDJSON を一括で gse-dataset に同期する (macOS/Linux)。
#
# 処理:
#   1. fallback ディレクトリの未同期 NDJSON を raw/P000/ にコピー
#   2. raw 内で metrics 未生成のファイルに sync-session.sh --no-commit を実行
#   3. まとめて 1 commit + push
#
# Usage:
#   ./scripts/sync-all.sh [--no-commit] [--fallback DIR]
#
# Env vars:
#   GSE_DATASET — gse-dataset ルート (default: ../gse-dataset from repo root)
#   GSE_PID     — 被験者 ID (default: P000)
#
# Exit codes: 0=OK, 1=cargo fail, 2=schema fail, 3=git fail

set -euo pipefail

NO_COMMIT=0
FALLBACK_DIR=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-commit)
            NO_COMMIT=1; shift ;;
        --fallback)
            FALLBACK_DIR="$2"; shift 2 ;;
        --help|-h)
            sed -n '2,16p' "$0"; exit 0 ;;
        *)
            echo "[sync-all] unknown option: $1" >&2; exit 1 ;;
    esac
done

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATASET_ROOT="${GSE_DATASET:-$REPO_ROOT/../gse-dataset}"
PID="${GSE_PID:-P000}"

OS_NAME="macos"
if [[ "$(uname -s)" == "Linux" ]]; then
    OS_NAME="linux"
fi

if [[ -z "$FALLBACK_DIR" ]]; then
    FALLBACK_DIR="$HOME/Documents/GSE-sessions"
fi

RAW_DIR="$DATASET_ROOT/raw/$PID"
METRICS_DIR="$DATASET_ROOT/metrics/$PID/$OS_NAME"

if [[ ! -d "$DATASET_ROOT" ]]; then
    echo "[sync-all] ERROR: gse-dataset not found at $DATASET_ROOT" >&2
    echo "  set GSE_DATASET env or clone the repo beside gse-prototype" >&2
    exit 1
fi

mkdir -p "$RAW_DIR" "$METRICS_DIR"

# === Step 1: fallback → raw コピー (重複スキップ) ===
COPIED=0
if [[ -d "$FALLBACK_DIR" ]]; then
    echo "[sync-all] Step 1/3: copying unsynced NDJSON from $FALLBACK_DIR"
    for f in "$FALLBACK_DIR"/gse_*.ndjson; do
        [[ -f "$f" ]] || continue
        BASENAME="$(basename "$f")"
        if [[ ! -f "$RAW_DIR/$BASENAME" ]]; then
            cp "$f" "$RAW_DIR/$BASENAME"
            echo "  copied: $BASENAME"
            COPIED=$((COPIED + 1))
        fi
    done
    echo "[sync-all] Step 1/3 OK ($COPIED files copied)"
else
    echo "[sync-all] Step 1/3: fallback dir not found ($FALLBACK_DIR) — skipping"
fi

# === Step 2: metrics 未生成ファイルを検出して sync-session 実行 ===
PROCESSED=0
FAILED=0
echo "[sync-all] Step 2/3: generating metrics for unprocessed sessions"
for f in "$RAW_DIR"/gse_*.ndjson; do
    [[ -f "$f" ]] || continue
    BASENAME="$(basename "$f" .ndjson)"
    METRICS_FILE="$METRICS_DIR/$BASENAME.metrics.json"
    if [[ -f "$METRICS_FILE" ]]; then
        echo "  skip (already has metrics): $BASENAME"
        continue
    fi
    echo "  processing: $BASENAME"
    # sync-session.sh は GSE_DATASET / GSE_PID を env から読むため明示的に export
    if GSE_DATASET="$DATASET_ROOT" GSE_PID="$PID" "$REPO_ROOT/scripts/sync-session.sh" "$f" --no-commit; then
        PROCESSED=$((PROCESSED + 1))
    else
        rc=$?
        echo "  FAILED: $BASENAME (exit $rc)" >&2
        FAILED=$((FAILED + 1))
    fi
done
echo "[sync-all] Step 2/3 done ($PROCESSED processed, $FAILED failed)"

if [[ "$FAILED" -gt 0 ]]; then
    echo "[sync-all] ERROR: $FAILED files failed — aborting before commit" >&2
    exit 1
fi

if [[ "$PROCESSED" -eq 0 && "$COPIED" -eq 0 ]]; then
    echo "[sync-all] nothing to sync"
    exit 0
fi

# === Step 3: git commit + push ===
if [[ "$NO_COMMIT" -eq 1 ]]; then
    echo "[sync-all] Step 3/3 skipped (--no-commit)"
    echo "[sync-all] done (dry-run): $PROCESSED metrics generated, $COPIED files copied"
    exit 0
fi

echo "[sync-all] Step 3/3: committing to $DATASET_ROOT"
cd "$DATASET_ROOT"
git add "raw/$PID/" "metrics/$PID/"
DATE="$(date +%Y-%m-%d)"
PID_LOWER="$(echo "$PID" | tr '[:upper:]' '[:lower:]')"
TOTAL=$((COPIED + PROCESSED))
if ! git commit -m "data($PID_LOWER-$OS_NAME): batch sync $DATE ($TOTAL files)"; then
    echo "[sync-all] git commit failed (maybe nothing to commit?)" >&2
    exit 3
fi
if ! git push origin main; then
    echo "[sync-all] git push failed. Try: cd $DATASET_ROOT && git push origin main" >&2
    exit 3
fi
echo "[sync-all] done: $PROCESSED metrics generated, $COPIED files copied, committed and pushed"
