#!/usr/bin/env bash
# GSE セッション NDJSON を gse-dataset にメトリクス化して同期する (macOS/Linux)。
#
# Stage E の 3 ステップ (gse-replay --metrics → validate_schema.py → git commit/push)
# を 1 コマンド化する。Windows 側は scripts/sync-session.ps1 を使う (同じ I/O 契約)。
#
# Usage:
#   ./scripts/sync-session.sh <session-ndjson> [--output-dir DIR] [--no-commit]
#
# Env vars:
#   GSE_DATASET — gse-dataset ルート (default: ../gse-dataset from repo root)
#   GSE_PID     — 被験者 ID (default: P000)
#
# Exit codes (scripts/sync-session.ps1 と整合):
#   0  OK
#   1  cargo 失敗
#   2  schema 失敗
#   3  git 失敗
#
# 関連: docs/development-guidelines.md §10.2、.steering/20260415-windows-onboarding/ Stage E

set -euo pipefail

SESSION_PATH=""
OUTPUT_DIR=""
NO_COMMIT=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --output-dir)
            OUTPUT_DIR="$2"; shift 2 ;;
        --no-commit)
            NO_COMMIT=1; shift ;;
        --help|-h)
            sed -n '2,20p' "$0"; exit 0 ;;
        -*)
            echo "[sync-session] unknown option: $1" >&2
            exit 1 ;;
        *)
            if [[ -z "$SESSION_PATH" ]]; then
                SESSION_PATH="$1"
            else
                echo "[sync-session] too many positional args" >&2
                exit 1
            fi
            shift ;;
    esac
done

if [[ -z "$SESSION_PATH" ]]; then
    echo "[sync-session] ERROR: session path required" >&2
    echo "Usage: $0 <session-ndjson> [--output-dir DIR] [--no-commit]" >&2
    exit 1
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATASET_ROOT="${GSE_DATASET:-$REPO_ROOT/../gse-dataset}"
PID="${GSE_PID:-P000}"

if [[ ! -d "$DATASET_ROOT" ]]; then
    echo "[sync-session] ERROR: gse-dataset not found at $DATASET_ROOT" >&2
    echo "  set GSE_DATASET env or clone the repo beside gse-prototype" >&2
    exit 1
fi

OS_NAME="macos"
if [[ "$(uname -s)" == "Linux" ]]; then
    OS_NAME="linux"
fi

if [[ -z "$OUTPUT_DIR" ]]; then
    OUTPUT_DIR="$DATASET_ROOT/metrics/$PID/$OS_NAME"
fi
mkdir -p "$OUTPUT_DIR"

BASENAME="$(basename "$SESSION_PATH" .ndjson)"
METRICS_JSON="$OUTPUT_DIR/$BASENAME.metrics.json"

echo "[sync-session] Step 1/3: generating metrics JSON -> $METRICS_JSON"
cd "$REPO_ROOT/src-tauri"
if ! cargo run --quiet --bin gse-replay -- "$SESSION_PATH" --metrics --json > "$METRICS_JSON"; then
    echo "[sync-session] cargo run failed" >&2
    exit 1
fi
echo "[sync-session] Step 1/3 OK ($(wc -c < "$METRICS_JSON") bytes)"

echo "[sync-session] Step 2/3: validating NDJSON against schema"
VALIDATE_SCRIPT="$DATASET_ROOT/scripts/validate_schema.py"
if [[ -f "$VALIDATE_SCRIPT" ]]; then
    if ! python3 "$VALIDATE_SCRIPT" "$SESSION_PATH"; then
        echo "[sync-session] schema validation failed — commit skipped" >&2
        exit 2
    fi
    echo "[sync-session] Step 2/3 OK"
else
    echo "[sync-session] WARN: validate_schema.py not found at $VALIDATE_SCRIPT — skipping"
fi

if [[ "$NO_COMMIT" -eq 1 ]]; then
    echo "[sync-session] Step 3/3 skipped (--no-commit)"
    echo "[sync-session] done (dry-run): $METRICS_JSON"
    exit 0
fi

echo "[sync-session] Step 3/3: committing to $DATASET_ROOT"
cd "$DATASET_ROOT"
git add "metrics/$PID/"
DATE="$(date +%Y-%m-%d)"
PID_LOWER="$(echo "$PID" | tr '[:upper:]' '[:lower:]')"
if ! git commit -m "data($PID_LOWER-$OS_NAME): session $DATE"; then
    echo "[sync-session] git commit failed (maybe nothing to commit?)" >&2
    exit 3
fi
if ! git push origin main; then
    echo "[sync-session] git push failed. Try: cd $DATASET_ROOT && git push origin main" >&2
    exit 3
fi
echo "[sync-session] done: $METRICS_JSON committed and pushed"
