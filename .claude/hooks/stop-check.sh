#!/bin/bash
# Stop hook (Report 層) - セッション終了時の静的解析
# 問題があった時のみ [stop] WARN を 1 行出す。詳細はユーザーが手動で実行する前提。

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
MANIFEST="${REPO_ROOT}/src-tauri/Cargo.toml"

# 変更ファイルが無ければスキップ
CHANGED=$(git diff --name-only HEAD 2>/dev/null | wc -l | tr -d ' ')
if [ "$CHANGED" -eq 0 ]; then
    exit 0
fi

# Rust: cargo clippy (変更された .rs ファイルがある場合のみ)
#
# ⚠️★★★ --all-targets を付けること (2026-09-12)。
#   ★ 既定のターゲット (lib + bin) だけだと **#[cfg(test)] のコードが一切解析されない**。
#   ⚠️ しかも clippy は lib が落ちた時点で止まるので、lib を緑にするまで bin の指摘も見えない。
#     → 実際にこの穴で 1.94 の lint が 33 + 12 件たまり、片付けるまで存在に気づけなかった。
if git diff --name-only HEAD 2>/dev/null | grep -q '\.rs$'; then
    if [ -f "$MANIFEST" ]; then
        if ! cargo clippy --manifest-path "$MANIFEST" --quiet --all-targets -- -D warnings >/dev/null 2>&1; then
            echo "[stop] WARN: cargo clippy reported issues. Run 'cargo clippy --all-targets' to inspect."
        fi
    fi
fi

# TypeScript: tsc --noEmit (変更された .ts/.tsx ファイルがある場合のみ)
if git diff --name-only HEAD 2>/dev/null | grep -qE '\.(ts|tsx)$'; then
    if [ -f "${REPO_ROOT}/tsconfig.json" ] && command -v npx >/dev/null 2>&1; then
        if ! (cd "$REPO_ROOT" && npx --no-install tsc --noEmit >/dev/null 2>&1); then
            echo "[stop] WARN: tsc reported type errors. Run 'npx tsc --noEmit' to inspect."
        fi
    fi
fi

exit 0
