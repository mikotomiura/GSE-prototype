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
#   GSE_PID     — 被験者 ID の明示指定 (任意)。下記の解決順で使われる。
#
# 参加者 ID 解決順 (raw 構造を真実源とする。logger Part 2 の自動生成 ID に追従):
#   1. パス導出: <session> が .../raw/<PID>/gse_*.ndjson なら親ディレクトリ名 <PID>
#   2. $GSE_PID (allowlist 通過時)
#   3. ~/.gse/participant_id (logger の永続化先、allowlist 通過時)
#   4. P000 (最終 fallback)
#   詳細: .steering/20260619-sync-auto-participant-id/decisions.md
#
# Exit codes (scripts/sync-session.ps1 と整合):
#   0  OK
#   1  cargo 失敗
#   2  schema 失敗
#   3  git 失敗
#
# 関連: docs/development-guidelines.md §10.2、.steering/20260415-windows-onboarding/ Stage E

set -euo pipefail

# === 参加者 ID ヘルパー (logger is_valid_participant_id と挙動を一致させる) ===
# allowlist: ASCII 英数字 + _ + - のみ・長さ 1..=64、かつ Windows 予約デバイス名を拒否
# (大小無視)。logger.rs:918-942 と完全一致。前後空白は呼び出し側で trim 済み前提。
GSE_RESERVED_IDS=" CON PRN AUX NUL COM1 COM2 COM3 COM4 COM5 COM6 COM7 COM8 COM9 LPT1 LPT2 LPT3 LPT4 LPT5 LPT6 LPT7 LPT8 LPT9 "
is_valid_pid() {
    local id="$1"
    if ! [[ "$id" =~ ^[A-Za-z0-9_-]{1,64}$ ]]; then
        return 1
    fi
    local upper
    upper="$(printf '%s' "$id" | tr '[:lower:]' '[:upper:]')"
    if [[ "$GSE_RESERVED_IDS" == *" $upper "* ]]; then
        return 1
    fi
    return 0
}

# セッションパスが .../raw/<PID>/gse_*.ndjson の形なら親ディレクトリ名 (PID) を stdout に返す。
# 祖父ディレクトリ名が厳密に "raw" のときのみ成立 (fallback dir 等を誤導出しないため)。
derive_pid_from_path() {
    local sp="$1"
    local parent grand
    parent="$(basename "$(dirname "$sp")")"
    grand="$(basename "$(dirname "$(dirname "$sp")")")"
    if [[ "$grand" == "raw" ]] && is_valid_pid "$parent"; then
        printf '%s' "$parent"
        return 0
    fi
    return 1
}

# logger の永続化先 ~/.gse/participant_id を読む (基点 USERPROFILE → HOME)。
# 値は trim + allowlist 検証。無い/不正なら非ゼロ。
read_persisted_pid() {
    local base="${USERPROFILE:-${HOME:-}}"
    [[ -n "$base" ]] || return 1
    local f="$base/.gse/participant_id"
    [[ -f "$f" ]] || return 1
    local id
    # logger load_id_from (logger.rs:988) と同じく全文を読んで trim+検証する
    # (先頭行だけ読むと複数行ファイルの 2 行目以降を見逃し、logger より緩くなるため)。
    id="$(cat "$f" 2>/dev/null || true)"
    id="${id#"${id%%[![:space:]]*}"}"  # ltrim
    id="${id%"${id##*[![:space:]]}"}"  # rtrim
    is_valid_pid "$id" || return 1
    printf '%s' "$id"
}

SESSION_PATH=""
OUTPUT_DIR=""
NO_COMMIT=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --output-dir)
            [[ $# -ge 2 ]] || { echo "[sync-session] --output-dir requires a value" >&2; exit 1; }
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

# 参加者 ID 解決: パス導出 → GSE_PID → 永続化値 → P000 (上記ヘッダ参照)
PID=""
PID_SOURCE=""
if PID="$(derive_pid_from_path "$SESSION_PATH")"; then
    PID_SOURCE="raw-path"
elif [[ -n "${GSE_PID:-}" ]] && is_valid_pid "${GSE_PID}"; then
    PID="${GSE_PID}"; PID_SOURCE="GSE_PID"
elif PID="$(read_persisted_pid)"; then
    PID_SOURCE="persisted"
else
    PID="P000"; PID_SOURCE="default"
fi
echo "[sync-session] participant id: $PID (source: $PID_SOURCE)"

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
