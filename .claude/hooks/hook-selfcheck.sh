#!/usr/bin/env bash
# hook-selfcheck.sh — SessionStart hook。settings.json の全 command hook を毎セッション検証。
# 目的: hook のパス崩れ/権限落ち/構文ミス/依存欠如を、実害が出る前に検知する。常に exit 0。
set -uo pipefail
P="[hookcheck]"
command -v jq >/dev/null 2>&1 || { echo "$P SKIP: jq 無し"; exit 0; }

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SET="$ROOT/.claude/settings.json"
[ -f "$SET" ] || { echo "$P SKIP: settings.json 無し"; exit 0; }

TO="timeout 8"; command -v timeout >/dev/null 2>&1 || TO=""   # timeout 無ければ素で走らせる

# 全イベント配下の type=command の command 文字列 (重複排除)
CMDS="$(jq -r '(.hooks // {}) | to_entries[] | .value[]? | (.hooks // [])[]?
              | select(.type=="command") | .command' "$SET" 2>/dev/null | sort -u)"
[ -z "$CMDS" ] && { echo "$P OK: 登録 hook 0 件"; exit 0; }

total=0; bad=0; warn=""
while IFS= read -r cmd; do
  [ -z "$cmd" ] && continue
  total=$((total+1))
  # command 文字列から最初の .sh パスを抽出。無ければ先頭トークン。
  script="$(printf '%s' "$cmd" | grep -oE '[^[:space:]]+\.sh' | head -n1)"
  [ -z "$script" ] && script="$(printf '%s' "$cmd" | awk '{print $1}')"
  # 正規化: `bash "$(git rev-parse --show-toplevel ...)/.claude/hooks/x.sh"` のような
  # shell 展開ラッパー由来の先頭ゴミ (例 ".)/") を、既知の hook ルートから切り出して除去する。
  script="$(printf '%s' "$script" | sed -E 's#.*(\.claude/hooks/|\.claude/commands/|scripts/)#\1#')"
  name="${script##*/}"
  case "$script" in /*|[A-Za-z]:*) path="$script" ;; *) path="$ROOT/$script" ;; esac

  if [ ! -e "$path" ]; then bad=$((bad+1)); warn="$warn ${name}:missing"; continue; fi
  case "$script" in
    *.sh)
      if ! bash -n "$path" 2>/dev/null; then bad=$((bad+1)); warn="$warn ${name}:syntax"; continue; fi
      if [ ! -x "$path" ] && ! head -n1 "$path" | grep -q '^#!'; then
        bad=$((bad+1)); warn="$warn ${name}:not-exec"; continue; fi
      # 安全 smoke: fail-safe 印のある hook のみ空 stdin で実走。exit 0 を期待。
      # 自分自身 ($0) は smoke しない (marker 文字列が自スクリプトにも出現し再帰するため)。
      if grep -q '# selfcheck: safe' "$path" && ! [ "$path" -ef "$0" ]; then
        if ! printf '' | $TO bash "$path" >/dev/null 2>&1; then
          bad=$((bad+1)); warn="$warn ${name}:runtime"; continue; fi
      fi
      ;;
    *) : ;;   # 非 .sh (node/python 等) は存在のみ確認
  esac
done <<< "$CMDS"

if [ "$bad" -eq 0 ]; then
  echo "$P OK: $total hooks healthy"
else
  echo "$P WARN: $bad/$total hooks に問題 ->$warn" >&2   # 該当 hook を確認
fi
exit 0
