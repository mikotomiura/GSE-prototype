#!/bin/bash
# PostToolUse hook - cargo fmt を実行し、変更があれば報告
# Edit/Write 後に発火。.rs 以外のファイルでは cargo fmt は無影響（静かに終了）

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
MANIFEST="${REPO_ROOT}/src-tauri/Cargo.toml"

if [ ! -f "$MANIFEST" ]; then
    exit 0
fi

# フォーマットが必要か先にチェック
if cargo fmt --manifest-path "$MANIFEST" -- --check >/dev/null 2>&1; then
    exit 0
fi

# フォーマット実行
cargo fmt --manifest-path "$MANIFEST" --quiet 2>/dev/null || true
echo "[fmt] cargo fmt applied"
exit 0
