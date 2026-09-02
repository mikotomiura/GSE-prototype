#!/usr/bin/env bash
# run.sh — experiments/20260902-expression-layerA-visual
#
# 使い方:
#   bash run.sh check          設定の自己検査（★ 実験を回す前に必ず通す）
#   bash run.sh serve [port]   player を配る（★ file:// では fetch が落ちる）
#   bash run.sh all [port]     check → serve
#
# ⚠️★★★ 本実験は「音」ではなく「視覚」の層 A である。
#    音側（experiments/20260812-expression-*）とは別系統であり、混ぜない。

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${PYTHON:-python}"
CFG="$HERE/layerA.config.json"

note() { printf '%s\n' "$*" >&2; }
die()  { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

cmd_check() {
  note "== check =="
  [ -f "$CFG" ] || die "layerA.config.json が無い"
  [ -f "$HERE/player/layerA.html" ] || die "player/layerA.html が無い"

  # ★ JSON として妥当か（★ 壊れた config で黙って走らせない）
  "$PY" -c "import json,sys; json.load(open(sys.argv[1], encoding='utf-8'))" "$CFG" \
    || die "layerA.config.json が JSON として壊れている"

  "$PY" "$HERE/scripts/selftest.py" "$CFG" "$HERE/player/layerA.html"
  note "check: OK"
}

cmd_serve() {
  local port="${1:-8931}"
  note "== serve =="
  note "★ 開く URL: http://127.0.0.1:${port}/player/layerA.html"
  note "⚠️ file:// では設定 fetch が落ちます。必ずこの URL で開いてください。"
  "$PY" -m http.server "$port" --bind 127.0.0.1 --directory "$HERE"
}

case "${1:-}" in
  check) cmd_check ;;
  serve) shift; cmd_serve "${1:-}" ;;
  all)   shift; cmd_check; cmd_serve "${1:-}" ;;
  *) note "usage: bash run.sh {check|serve [port]|all [port]}"; exit 2 ;;
esac
