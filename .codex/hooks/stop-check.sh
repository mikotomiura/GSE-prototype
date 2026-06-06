#!/bin/bash
# Stop hook - 完了前品質チェック (cargo clippy + tsc)
# 変更ファイルがある場合のみ実行し、問題があれば Claude に通知する

CHANGED=$(git diff --name-only HEAD 2>/dev/null | wc -l | tr -d ' ')
if [ "$CHANGED" -eq 0 ]; then
  exit 0
fi

OUTPUT=""

# Rust: cargo clippy (変更された .rs ファイルがある場合)
if git diff --name-only HEAD 2>/dev/null | grep -q '\.rs$'; then
  CLIPPY=$(cargo clippy --manifest-path src-tauri/Cargo.toml --quiet 2>&1 | grep -E "^error|^warning\[" | head -15)
  if [ -n "$CLIPPY" ]; then
    OUTPUT="${OUTPUT}[cargo clippy]\n${CLIPPY}\n"
  fi
fi

# TypeScript: tsc --noEmit (変更された .ts/.tsx ファイルがある場合)
if git diff --name-only HEAD 2>/dev/null | grep -qE '\.(ts|tsx)$'; then
  TSC=$(npx tsc --noEmit --pretty false 2>&1 | grep -E "error TS" | head -10)
  if [ -n "$TSC" ]; then
    OUTPUT="${OUTPUT}[tsc]\n${TSC}\n"
  fi
fi

if [ -n "$OUTPUT" ]; then
  echo "=== 品質チェック結果 ==="
  printf "%b" "$OUTPUT"
  echo "上記の問題を修正してから完了としてください。"
fi
