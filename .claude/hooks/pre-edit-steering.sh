#!/bin/bash
# PreToolUse hook - .steering/ 必須3ファイル未整備状態での実装ファイル編集をブロック
# 入力: stdin に Claude Code から JSON が渡される (tool_input.file_path)

# JSON から file_path を抽出（jq 無しで動くよう sed/grep で）
INPUT=$(cat)
TARGET_FILE=$(echo "$INPUT" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)

if [ -z "$TARGET_FILE" ]; then
    exit 0
fi

# プロジェクトルートからの相対パスに正規化 (macOS /tmp -> /private/tmp 対策)
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
REPO_ROOT_REAL=$(cd "$REPO_ROOT" 2>/dev/null && pwd -P)
TARGET_REAL=$(python3 -c "import os,sys; print(os.path.realpath(sys.argv[1]))" "$TARGET_FILE" 2>/dev/null || echo "$TARGET_FILE")
REL=${TARGET_REAL#${REPO_ROOT_REAL}/}
[ "$REL" = "$TARGET_REAL" ] && REL=${TARGET_FILE#${REPO_ROOT}/}

# 実装ファイルパターン: src-tauri/src/ または src/ 配下の .rs/.ts/.tsx
IMPL_PATTERN='^(src-tauri/src/.*\.rs$|src/.*\.(ts|tsx)$)'

# テスト・ドキュメント・steering 自身は対象外
EXCLUDE_PATTERN='(^src-tauri/tests/|^src-tauri/src/.*test.*\.rs$|^docs/|^\.steering/|^\.claude/)'

if ! echo "$REL" | grep -qE "$IMPL_PATTERN"; then
    exit 0
fi
if echo "$REL" | grep -qE "$EXCLUDE_PATTERN"; then
    exit 0
fi

# 直近7日以内の .steering/[YYYYMMDD]-*/ を探す
TASK_DIR=""
for i in 0 1 2 3 4 5 6 7; do
    DATE=$(date -v-${i}d +%Y%m%d 2>/dev/null || date -d "$i days ago" +%Y%m%d 2>/dev/null)
    [ -z "$DATE" ] && continue
    FOUND=$(ls -1d "${REPO_ROOT_REAL}/.steering/${DATE}-"* 2>/dev/null | tail -1)
    if [ -n "$FOUND" ]; then
        TASK_DIR="$FOUND"
        break
    fi
done

if [ -z "$TASK_DIR" ]; then
    echo "BLOCKED: 実装ファイル ($REL) を編集する前に /start-task でタスクを開始してください。" >&2
    echo "直近7日内に .steering/[YYYYMMDD]-*/ が見つかりません。" >&2
    exit 2
fi

# 必須3ファイル
MISSING=""
[ ! -f "$TASK_DIR/requirement.md" ] && MISSING="$MISSING requirement.md"
[ ! -f "$TASK_DIR/design.md" ] && MISSING="$MISSING design.md"
[ ! -f "$TASK_DIR/tasklist.md" ] && MISSING="$MISSING tasklist.md"

if [ -n "$MISSING" ]; then
    echo "BLOCKED: $TASK_DIR に以下の必須ファイルがありません:$MISSING" >&2
    echo "/start-task のテンプレートに従って作成してから実装に入ってください。" >&2
    exit 2
fi

exit 0
