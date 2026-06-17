#!/usr/bin/env bash
# secrets-pre-filter.sh
# PreToolUse on Bash — `codex exec` 呼び出しのコマンド文字列に
# 機密ファイル参照 / proprietary 拡張子が含まれていないかを検査。
# 含まれていればブロック (exit 2)。

set -uo pipefail

INPUT_JSON=$(cat)
COMMAND=$(echo "$INPUT_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null || echo "")

# codex を含まないコマンドは即座に通過
case "$COMMAND" in
  *codex*) ;;
  *) exit 0 ;;
esac

if ! echo "$COMMAND" | grep -qE 'codex[[:space:]]+exec'; then
    exit 0
fi

# 機密パターン (external-skills.md が単一真実源: document-skills 未導入のため拡張子フィルタ不要)
# credential 系 + GSE 固有 (NDJSON/キーストローク) のみ
DENY_PATTERN='\.env([[:space:]"]|$)|\.pem([[:space:]"]|$)|\.key([[:space:]"]|$)|credentials([[:space:]"]|$)|/secrets/|\.ndjson([[:space:]"]|$)|NDJSON([[:space:]"]|$)'

if echo "$COMMAND" | grep -qiE "$DENY_PATTERN"; then
    echo "[guard] BLOCKED: codex exec command references secrets or proprietary file" >&2
    echo "[guard]          Refusing to send sensitive content to external LLM." >&2
    echo "[guard]          Command surface (truncated): $(echo "$COMMAND" | head -c 200)" >&2
    exit 2
fi

echo "[guard] PASS: codex exec command surface clean"
exit 0
