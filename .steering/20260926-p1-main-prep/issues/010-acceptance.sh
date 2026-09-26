#!/usr/bin/env bash
# issue 010（ADR-030 補訂 3）の AC 検査
set -uo pipefail
fail() { echo "[acceptance 010] NG: $*" >&2; exit 1; }
REPO_ROOT="$(pwd)"
[ -f "$REPO_ROOT/src-tauri/Cargo.toml" ] || fail "cwd が repo root ではない: $REPO_ROOT"
PY="${PYTHON:-python}"; command -v "$PY" >/dev/null 2>&1 || PY=python3
export PYTHONUTF8=1
A=docs/adr/ADR-030-stall-onset-and-decision-episode.md
R=docs/adr/README.md
B="$(git rev-parse --verify -q feat/p1-main-prep || echo main)"

del="$(git diff --numstat "$B" -- "$A" | awk '{print $2}')"
[ "${del:-0}" -eq 0 ] || fail "AC1: ADR-030 に削除行がある（本文を書き換えない）"
[ "$(grep -c '^## 補訂 3（2026-09-26）' "$A")" -eq 1 ] || fail "AC1: 補訂 3 の見出しが 1 つではない"

sec="$(awk '/^## 補訂 3（2026-09-26）/{f=1} f' "$A")"
[ -n "$sec" ] || fail "AC2: 補訂 3 の節を取り出せない"
for w in "補訂 2 項目 6" "補訂 2 項目 2" "null" "iki_cv" "P1-F" "0.995" "200" "1000" "Proposed" "実データ"; do
  printf '%s' "$sec" | grep -q -- "$w" || fail "AC2/3: 補訂 3 に '$w' が無い"
done

rdel="$(git diff --numstat "$B" -- "$R" | awk '{print $2}')"
radd="$(git diff --numstat "$B" -- "$R" | awk '{print $1}')"
# ★ README は表の 1 行に句を足すので「1 行削除 1 行追加」になる。変わった行が ADR-030 の行だけで、長くなっただけであることを見る
if [ "${rdel:-0}" -ne 0 ]; then
  [ "$rdel" -eq 1 ] && [ "$radd" -eq 1 ] || fail "AC4: README の差分が 1 行の書き足しではない"
  git diff -U0 "$B" -- "$R" | grep -E '^[-+]\|' | grep -vq 'ADR-030' && fail "AC4: ADR-030 以外の行が変わっている"
  old="$(git show "$B:$R" | grep '^| \[\*\*ADR-030\*\*\]')"
  new="$(grep '^| \[\*\*ADR-030\*\*\]' "$R")"
  [ "${#new}" -gt "${#old}" ] || fail "AC4: ADR-030 の行が伸びていない（書き足しではない）"
  case "$new" in "${old:0:400}"*) : ;; *) fail "AC4: ADR-030 の行の先頭 400 字が書き換わっている" ;; esac
fi
grep '^| \[\*\*ADR-030\*\*\]' "$R" | grep -q "補訂 3" || fail "AC4: README の ADR-030 行に補訂 3 が無い"

"$PY" scripts/check_doc_lexicon.py >/dev/null 2>&1 || fail "AC5: check_doc_lexicon が赤"
"$PY" scripts/check_citations.py >/dev/null 2>&1 || fail "AC5: check_citations が赤"
echo "[acceptance 010] OK"
