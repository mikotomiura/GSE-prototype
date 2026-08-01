#!/usr/bin/env bash
# secrets-pre-filter.sh
# PreToolUse on Bash — codex の外部呼び出しのコマンド文字列に
# 機密ファイル参照 / proprietary 拡張子が含まれていないかを検査。
# 含まれていればブロック (exit 2)。
#
# 設計原則: **判定できないなら通さない (fail-closed)**。

set -uo pipefail

INPUT_JSON=$(cat)

# 高速早期 exit: raw JSON に codex の文字列が無ければ parse すらしない (Bash 全発火対策)
case "$INPUT_JSON" in
  *codex*) ;;
  *) exit 0 ;;
esac

# JSON パースは python (jq 非依存)。パース不能を空文字へ縮退させると
# case が *) にマッチして **素通り (fail-open)** するため、判定不能なら通さない。
PYTHON=$(command -v python3 || command -v python || true)
if [ -z "$PYTHON" ]; then
    echo "[guard] BLOCKED: python not found — codex コマンドを検査できないため通さない (fail-closed)" >&2
    exit 2
fi

# Windows git-bash の日本語ロケール (cp932) で UnicodeDecodeError にならないよう UTF-8 を強制
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8

if ! COMMAND=$(printf '%s' "$INPUT_JSON" | "$PYTHON" -c \
    "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null); then
    echo "[guard] BLOCKED: hook 入力 JSON を parse できない — fail-closed" >&2
    exit 2
fi

# codex の**サブコマンドを限定しない**。`codex exec` 決め打ちだと
# `codex e` (alias) / `codex review` / `codex --cd . exec` / 行継続 がすべて素通りする。
# ただし判定は**コマンド位置** (行頭 / パイプ / `;` / `&&` / `||` / `(` の直後) に限る。
# 単に「codex という語を含むか」にすると、ヒアドキュメント内で codex に言及しただけの
# 無関係な Bash 呼び出しまでブロックしてしまう (実際に踏んだ)。
# 判定は python で行う。`grep` に頼ると **grep 不在・regex エラーでも exit 0 = 素通り**
# になり、外部コマンド不在で静かに壊れるという本件と同じ穴が残る。
CODEX_HIT=$(printf '%s' "$COMMAND" | "$PYTHON" -c \
    "import re,sys; print('1' if re.search(r'(?m)(^|[|;&(]|&&|\|\|)[ \t]*(\S*/)?codex([ \t]|$)', sys.stdin.read()) else '0')" 2>/dev/null)
if [ "$CODEX_HIT" != "1" ] && [ "$CODEX_HIT" != "0" ]; then
    echo "[guard] BLOCKED: codex 判定に失敗 — fail-closed" >&2
    exit 2
fi
[ "$CODEX_HIT" = "0" ] && exit 0

# 機密パターン (external-skills.md が単一真実源: document-skills 未導入のため拡張子フィルタ不要)
# credential 系 + GSE 固有 (NDJSON/キーストローク) のみ。
# 終端は「英数字・アンダースコアでない文字 or 行末」にする。空白と `"` だけに限ると
# `codex exec "$(cat .env)"` のような**最も自然な書き方**が素通りする。
DENY_PATTERN='\.env([^A-Za-z0-9_]|$)|\.envrc([^A-Za-z0-9_]|$)|\.pem([^A-Za-z0-9_]|$)|\.key([^A-Za-z0-9_]|$)|credentials([^A-Za-z0-9_]|$)|/secrets/|\.ndjson([^A-Za-z0-9_]|$)|NDJSON([^A-Za-z0-9_]|$)'

if printf '%s' "$COMMAND" | grep -qiE "$DENY_PATTERN"; then
    echo "[guard] BLOCKED: codex exec command references secrets or proprietary file" >&2
    echo "[guard]          Refusing to send sensitive content to external LLM." >&2
    echo "[guard]          Command surface (truncated): $(printf '%s' "$COMMAND" | head -c 200)" >&2
    exit 2
fi

echo "[guard] PASS: codex exec command surface clean"
exit 0
