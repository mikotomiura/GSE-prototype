#!/usr/bin/env bash
# GSE セッション NDJSON を一括で gse-dataset に同期する (macOS/Linux)。
#
# 処理:
#   1. fallback ディレクトリの未同期 NDJSON を raw/<local-pid>/ にコピー
#      (local-pid = GSE_PID → ~/.gse/participant_id → P000。fallback dir は端末ローカル)
#   2. raw/*/ を participant ごとに反復し、metrics 未生成のファイルに sync-session.sh
#      --no-commit を実行 (PID は raw のディレクトリ名 = パス導出で解決)
#   3. まとめて 1 commit + push (全 participant を一括 add)
#
# Usage:
#   ./scripts/sync-all.sh [--no-commit] [--fallback DIR]
#
# Env vars:
#   GSE_DATASET — gse-dataset ルート (default: ../gse-dataset from repo root)
#   GSE_PID     — fallback コピー先の被験者 ID 明示指定 (任意)。raw 配下の既存ファイルは
#                 ディレクトリ名から PID を導出するため GSE_PID に依存しない。
#
# Exit codes: 0=OK, 1=cargo fail, 2=schema fail, 3=git fail, 4=precondition

set -euo pipefail

# === 参加者 ID ヘルパー (logger is_valid_participant_id と一致。sync-session.sh と同一実装) ===
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

# logger の永続化先 ~/.gse/participant_id を読む (基点 USERPROFILE → HOME)。
read_persisted_pid() {
    local base="${USERPROFILE:-${HOME:-}}"
    [[ -n "$base" ]] || return 1
    local f="$base/.gse/participant_id"
    [[ -f "$f" ]] || return 1
    local id
    # logger load_id_from (logger.rs:988) と同じく全文を読んで trim+検証する。
    id="$(cat "$f" 2>/dev/null || true)"
    id="${id#"${id%%[![:space:]]*}"}"  # ltrim
    id="${id%"${id##*[![:space:]]}"}"  # rtrim
    is_valid_pid "$id" || return 1
    printf '%s' "$id"
}

NO_COMMIT=0
FALLBACK_DIR=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-commit)
            NO_COMMIT=1; shift ;;
        --fallback)
            [[ $# -ge 2 ]] || { echo "[sync-all] --fallback requires a value" >&2; exit 1; }
            FALLBACK_DIR="$2"; shift 2 ;;
        --help|-h)
            sed -n '2,16p' "$0"; exit 0 ;;
        *)
            echo "[sync-all] unknown option: $1" >&2; exit 1 ;;
    esac
done

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATASET_ROOT="${GSE_DATASET:-$REPO_ROOT/../gse-dataset}"

OS_NAME="macos"
if [[ "$(uname -s)" == "Linux" ]]; then
    OS_NAME="linux"
fi

if [[ -z "$FALLBACK_DIR" ]]; then
    FALLBACK_DIR="$HOME/Documents/GSE-sessions"
fi

if [[ ! -d "$DATASET_ROOT" ]]; then
    echo "[sync-all] ERROR: gse-dataset not found at $DATASET_ROOT" >&2
    echo "  set GSE_DATASET env or clone the repo beside gse-prototype" >&2
    exit 1
fi

# ローカル PID (fallback dir のファイル帰属先): GSE_PID → 永続化 → P000 (パス導出は使わない、D4)
LOCAL_PID=""
if [[ -n "${GSE_PID:-}" ]] && is_valid_pid "${GSE_PID}"; then
    LOCAL_PID="${GSE_PID}"
elif LOCAL_PID="$(read_persisted_pid)"; then
    :
else
    LOCAL_PID="P000"
fi
LOCAL_RAW_DIR="$DATASET_ROOT/raw/$LOCAL_PID"
echo "[sync-all] local participant id (fallback copy target): $LOCAL_PID"

mkdir -p "$LOCAL_RAW_DIR"

# === Step 0: schema parity pre-flight (gse-prototype vs gse-dataset) ===
# Python helper に実ロジックを集約 (scripts/check_schema_parity.py)。
# 詳細は .steering/20260417-schema-drift-guard/design.md を参照。
PARITY_SCRIPT="$REPO_ROOT/scripts/check_schema_parity.py"
if [[ ! -f "$PARITY_SCRIPT" ]]; then
    echo "[sync-all] ERROR: check_schema_parity.py not found at $PARITY_SCRIPT" >&2
    exit 4
fi
PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "[sync-all] ERROR: neither python3 nor python found on PATH" >&2
    exit 4
fi
echo "[sync-all] Step 0/3: verifying schema parity (gse-prototype <-> gse-dataset)"
# set -e 環境下では `if ! cmd; then rc=$?` が 0 を拾うため、|| で rc を保全する
parity_rc=0
"$PYTHON_BIN" "$PARITY_SCRIPT" --dataset "$DATASET_ROOT" || parity_rc=$?
if [[ "$parity_rc" -ne 0 ]]; then
    echo "[sync-all] schema parity check failed (exit $parity_rc) — aborting before any file copy." >&2
    exit "$parity_rc"
fi

# === Step 1: fallback → raw コピー (重複スキップ) ===
COPIED=0
if [[ -d "$FALLBACK_DIR" ]]; then
    echo "[sync-all] Step 1/3: copying unsynced NDJSON from $FALLBACK_DIR -> raw/$LOCAL_PID/"
    for f in "$FALLBACK_DIR"/gse_*.ndjson; do
        [[ -f "$f" ]] || continue
        BASENAME="$(basename "$f")"
        if [[ ! -f "$LOCAL_RAW_DIR/$BASENAME" ]]; then
            cp "$f" "$LOCAL_RAW_DIR/$BASENAME"
            echo "  copied: $BASENAME"
            COPIED=$((COPIED + 1))
        fi
    done
    echo "[sync-all] Step 1/3 OK ($COPIED files copied)"
else
    echo "[sync-all] Step 1/3: fallback dir not found ($FALLBACK_DIR) — skipping"
fi

# === Step 2: metrics 未生成ファイルを検出して sync-session 実行 ===
# set -e 下での rc 取得パターンに注意:
#   OK: `cmd || rc=$?`          (||/else 経由なら $? は cmd 自身の exit code)
#   NG: `if ! cmd; then rc=$?`  (if! の形は then 内 $? が 0 化する事象あり)
# 以降の `if GSE_DATASET=... cmd; then ... else rc=$?` は if/else の else 側で
# $? を取る形なので正常動作する (Step 0 の || パターンと等価安全)。
PROCESSED=0
FAILED=0
TOUCHED_PIDS=""   # 改行区切りの処理済み PID (bash 3.2 互換のため配列は使わない)
echo "[sync-all] Step 2/3: generating metrics for unprocessed sessions (per participant)"
for pdir in "$DATASET_ROOT"/raw/*/; do
    [[ -d "$pdir" ]] || continue
    pid="$(basename "$pdir")"
    if ! is_valid_pid "$pid"; then
        echo "  WARN: skipping raw dir with invalid participant id: $pid" >&2
        continue
    fi
    metrics_dir="$DATASET_ROOT/metrics/$pid/$OS_NAME"
    mkdir -p "$metrics_dir"
    for f in "$pdir"gse_*.ndjson; do
        [[ -f "$f" ]] || continue
        BASENAME="$(basename "$f" .ndjson)"
        METRICS_FILE="$metrics_dir/$BASENAME.metrics.json"
        if [[ -f "$METRICS_FILE" ]]; then
            echo "  skip (already has metrics): $pid/$BASENAME"
            continue
        fi
        echo "  processing: $pid/$BASENAME"
        # sync-session.sh は <session> パス (.../raw/<pid>/) から PID を導出する。
        # GSE_PID は明示せず、raw のディレクトリ名を真実源とする (raw と metrics を一致させる)。
        if GSE_DATASET="$DATASET_ROOT" "$REPO_ROOT/scripts/sync-session.sh" "$f" --no-commit; then
            PROCESSED=$((PROCESSED + 1))
            TOUCHED_PIDS="${TOUCHED_PIDS}${pid}"$'\n'
        else
            rc=$?
            echo "  FAILED: $pid/$BASENAME (exit $rc)" >&2
            FAILED=$((FAILED + 1))
        fi
    done
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
DATE="$(date +%Y-%m-%d)"
TOTAL=$((COPIED + PROCESSED))
# 触れた PID (処理済み + コピー先) のみ stage する。不正名でスキップした raw dir は commit
# しない (構造ガードの趣旨)。`--` で先頭ハイフン PID のオプション誤認も防ぐ。
if [[ "$COPIED" -gt 0 ]]; then
    TOUCHED_PIDS="${TOUCHED_PIDS}${LOCAL_PID}"$'\n'
fi
UNIQUE_PIDS="$(printf '%s' "$TOUCHED_PIDS" | sed '/^$/d' | sort -u)"
while IFS= read -r p; do
    [[ -n "$p" ]] || continue
    git add -- "raw/$p/" "metrics/$p/"
done <<< "$UNIQUE_PIDS"
PID_COUNT="$(printf '%s\n' "$UNIQUE_PIDS" | sed '/^$/d' | wc -l | tr -d ' ')"
if [[ "$PID_COUNT" -le 1 ]]; then
    SCOPE_PID="${UNIQUE_PIDS:-$LOCAL_PID}"
    SCOPE="$(printf '%s' "$SCOPE_PID" | tr '[:upper:]' '[:lower:]')"
else
    SCOPE="multi"
fi
if ! git commit -m "data($SCOPE-$OS_NAME): batch sync $DATE ($TOTAL files)"; then
    echo "[sync-all] git commit failed (maybe nothing to commit?)" >&2
    exit 3
fi
if ! git push origin main; then
    echo "[sync-all] git push failed. Try: cd $DATASET_ROOT && git push origin main" >&2
    exit 3
fi
echo "[sync-all] done: $PROCESSED metrics generated, $COPIED files copied, committed and pushed"
