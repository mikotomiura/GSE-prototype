#!/bin/bash
# PreToolUse hook - GSE 固有の禁止パターン検出
# CLAUDE.md 制約 (1) winapi 禁止 / (8) println!/eprintln! 禁止 / 禁止事項: analysis/ に OS API

INPUT=$(cat)
TARGET_FILE=$(echo "$INPUT" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)

# Edit の new_string / Write の content を抽出
NEW_CONTENT=$(echo "$INPUT" | sed -n 's/.*"new_string"[[:space:]]*:[[:space:]]*"\(.*\)".*/\1/p' | head -1)
[ -z "$NEW_CONTENT" ] && NEW_CONTENT=$(echo "$INPUT" | sed -n 's/.*"content"[[:space:]]*:[[:space:]]*"\(.*\)".*/\1/p' | head -1)

if [ -z "$TARGET_FILE" ] || [ -z "$NEW_CONTENT" ]; then
    exit 0
fi

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
REPO_ROOT_REAL=$(cd "$REPO_ROOT" 2>/dev/null && pwd -P)
TARGET_REAL=$(python3 -c "import os,sys; print(os.path.realpath(sys.argv[1]))" "$TARGET_FILE" 2>/dev/null || echo "$TARGET_FILE")
REL=${TARGET_REAL#${REPO_ROOT_REAL}/}
[ "$REL" = "$TARGET_REAL" ] && REL=${TARGET_FILE#${REPO_ROOT}/}

# .rs ファイル: println!/eprintln! 禁止 (tests/ は許容)
if echo "$REL" | grep -qE '\.rs$' && ! echo "$REL" | grep -qE '(^src-tauri/tests/|test.*\.rs$|tests\.rs$)'; then
    if echo "$NEW_CONTENT" | grep -qE '(^|[^a-zA-Z_])(println!|eprintln!)'; then
        echo "BLOCKED ($REL): println!/eprintln! は禁止です (CLAUDE.md 制約8)。tracing::{info,warn,error,debug} を使ってください。" >&2
        exit 2
    fi
fi

# Cargo.toml: winapi crate 禁止
if echo "$REL" | grep -qE 'Cargo\.toml$'; then
    if echo "$NEW_CONTENT" | grep -qE '^\s*winapi\s*=' || echo "$NEW_CONTENT" | grep -qE '"winapi"'; then
        echo "BLOCKED ($REL): winapi crate は禁止です (CLAUDE.md 制約1)。windows crate (v0.58+) を使ってください。" >&2
        exit 2
    fi
fi

# analysis/ 配下: OS 依存 API のインポート禁止 (CLAUDE.md 禁止事項)
if echo "$REL" | grep -qE '^src-tauri/src/analysis/.*\.rs$'; then
    if echo "$NEW_CONTENT" | grep -qE '^\s*use\s+(windows|core_graphics|core_foundation|objc2|cocoa)(::|;)'; then
        echo "BLOCKED ($REL): analysis/ 内で OS 依存 API (windows/core_graphics/core_foundation/objc2/cocoa) の使用は禁止です。OS 依存は input/ または sensors*.rs に閉じてください。" >&2
        exit 2
    fi
fi

echo "[guard] PASS: banned patterns ($REL)"
exit 0
