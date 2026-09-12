#!/usr/bin/env bash
# ⚠️★★★ **「テストは書いたが CI で走らない」を捕まえる。**
#
# ★ なぜ要るか（2026-09-10 の実測）:
#   ⚠️ `scripts/secrets-filter-test.sh` は **対照つきの立派なテストなのに CI 登録が 0 件**で、
#     ★ 手で叩かない限り走らなかった。⚠️ その裏で filter には**実在の穴が 20 件以上**あった。
#   ⚠️ 調べたら **secrets-filter だけではなかった** —— ★ 同じ状態のテストが **8 本**あった。
#   → ★ 人が「配線を忘れない」話ではないので、**機械で見張る**。
#
# ★ 使い方:
#   bash scripts/check-tests-are-wired.sh              # 検査
#   bash scripts/check-tests-are-wired.sh --self-test  # ⚠️ 検査が空振りしていないかを見る
#
# ★ 意図的に CI から外すものは、**理由つきで** 下の除外表に書く（⚠️ 理由なしは通さない）。
set -euo pipefail

# ⚠️★★★ **workflow は 1 枚ではない** (2026-09-12・security-checker HIGH)。
#   ★ `supply-chain.yml` を足した時、ここが `ci.yml` だけを見ていたため、
#   そちらに配線した 2 本が「CI で 1 度も走らない」と誤判定された。
#   ⚠️ **この番人が workflow 1 枚ぶん構造的に盲目だった**ということであり、
#   赤を消す最短経路が「除外表に足す」= 検査器の変異テストを黙って無効化することだった。
#   → ★ **全 workflow を見る。** ⚠️ 0 件マッチだと `grep` が stdin を読んで固まるので
#   本数を先に検算する (下記 `CI_FILE_COUNT`)。
#   ⚠️ 本数はスカラで数える。★ macOS 既定の **bash 3.2 では `set -u` 下で空配列に
#   `${#arr[@]}` を当てると "unbound variable" で落ちる** ので、空になりうる配列を
#   参照する前に**カウンタで弾く**（★ 参照そのものが起きない形にする）。
CI_FILES=()
CI_FILE_COUNT=0
while IFS= read -r _wf; do
  [ -n "$_wf" ] || continue
  CI_FILES+=("$_wf")
  CI_FILE_COUNT=$((CI_FILE_COUNT+1))
done <<< "$(git ls-files '.github/workflows/*.yml' '.github/workflows/*.yaml')"
if [ "$CI_FILE_COUNT" -lt 1 ]; then
  echo "⚠️ .github/workflows/ に workflow が 1 枚も無い → 判定しない" >&2
  exit 2
fi

# ⚠️★★ 除外は「名前<TAB>理由」。★ 理由が空なら**未達として扱う**（⚠️ 黙って外させない）。
read -r -d '' EXCLUDES <<'EX' || true
run-codex-review-test.sh	Codex CLI と .codex/budget.json に依存し、CI ランナーに Codex が無い
EX

is_excluded() {
  printf '%s\n' "$EXCLUDES" | while IFS=$'\t' read -r name reason; do
    [ -n "${name:-}" ] || continue
    if [ "$name" = "$1" ]; then
      [ -n "${reason:-}" ] && printf 'yes\t%s' "$reason" || printf 'no-reason'
      break
    fi
  done
}

# ★ テストとみなすもの: scripts/ 配下の test_*.py / *_test.sh / *-test.sh
list_tests() {
  git ls-files scripts/ \
    | grep -E '(^|/)(test_[^/]*\.(py|sh)|[^/]*[-_]test\.(py|sh))$' \
    | grep -v '__init__' || true
}

# ★ CI から参照されているか（★ ファイル名 **または** python のモジュールパス）。
#   ⚠️ ファイル名だけを見ると `python3 -m unittest scripts.tests.foo` を**見落とす**
#   （★ 2026-09-10 に実際に見落として誤報告しかけた）。
wired() {
  local f="$1" base mod
  base="$(basename "$f")"
  mod="$(printf '%s' "${f%.py}" | tr '/' '.')"
  grep -qF "$base" "${CI_FILES[@]}" >/dev/null && return 0
  [ "${f##*.}" = "py" ] && grep -qF "$mod" "${CI_FILES[@]}" >/dev/null && return 0
  return 1
}

if [ "${1:-}" = "--self-test" ]; then
  echo "── ⚠️ 自己検査（★ この検査が空振りしていないか）"
  ok=0; n=0
  # ★ 陽性対照: CI に確実に書いてある名前は wired と判定されること
  n=$((n+1)); if wired "scripts/secrets-filter-test.sh"; then
    echo "  ✅ 陽性対照: CI 登録済みの .sh を wired と判定した"; ok=$((ok+1))
  else echo "  ⚠️ 陽性対照が落ちた（★ CI か検査が変わった）"; fi
  # ★ 陽性対照 2: **モジュールパスでしか書かれていない** py も wired と判定すること
  n=$((n+1)); if wired "scripts/tests/test_capabilities_gate.py"; then
    echo "  ✅ 陽性対照: モジュールパス指定の .py も拾えた（⚠️ ここを落とすと誤報告する）"; ok=$((ok+1))
  else echo "  ⚠️ モジュールパス指定を拾えていない"; fi
  # ⚠️★★★ 陽性対照 3: **ci.yml 以外の workflow にしか無い**名前も拾うこと。
  #   ★ これが無いと「workflow を 1 枚しか見ていない」盲点が**また素通りする**
  #   (⚠️ 2026-09-12 の実際の見落としが、まさに陽性対照 2 件とも ci.yml 内だったこと由来)。
  n=$((n+1)); if wired "scripts/tests/test_check_dependency_audit.py"; then
    echo "  ✅ 陽性対照: ci.yml 以外の workflow に配線された .py も拾えた"; ok=$((ok+1))
  else echo "  ⚠️ ci.yml 以外の workflow を見ていない（★ CI_FILES の列挙が壊れた）"; fi
  # ★ 列挙した workflow が 2 枚以上あること（⚠️ 1 枚に戻ったら上の対照が意味を失う）
  n=$((n+1)); if [ "$CI_FILE_COUNT" -ge 2 ]; then
    echo "  ✅ workflow を $CI_FILE_COUNT 枚見ている"; ok=$((ok+1))
  else echo "  ⚠️ workflow を $CI_FILE_COUNT 枚しか見ていない"; fi
  # ★ 陰性対照: 存在しない名前は wired ではないこと
  n=$((n+1)); if wired "scripts/tests/test_this_does_not_exist_$$.py"; then
    echo "  ⚠️ 陰性対照が失敗（★ 何でも wired と言っている）"
  else echo "  ✅ 陰性対照: 未登録の名前は wired ではないと判定した"; ok=$((ok+1)); fi
  # ★ 列挙が空でないこと（⚠️ 0 件マッチは緑になる）
  n=$((n+1)); c="$(list_tests | grep -c . || true)"
  if [ "${c:-0}" -ge 5 ]; then echo "  ✅ 列挙: $c 本（★ 0 件マッチで空振りしていない）"; ok=$((ok+1));
  else echo "  ⚠️ 列挙が $c 本しかない（★ パターンが壊れた可能性）"; fi
  echo "  → $ok / $n"
  [ "$ok" -eq "$n" ] || exit 1
  exit 0
fi

echo "════════════════════════════════════════"
echo "★ scripts/ のテストが CI から呼ばれているか (workflow $CI_FILE_COUNT 枚を走査)"
miss=0; total=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
  total=$((total+1))
  base="$(basename "$f")"
  if wired "$f"; then
    printf '  ★ %-44s CI で走る\n' "$f"
  else
    ex="$(is_excluded "$base")"
    case "$ex" in
      yes*) printf '  ☐ %-44s 除外（%s）\n' "$f" "${ex#yes	}" ;;
      no-reason) printf '  ⚠️ %-44s **除外に理由が無い**\n' "$f"; miss=$((miss+1)) ;;
      *) printf '  ⚠️ %-44s **CI で 1 度も走らない**\n' "$f"; miss=$((miss+1)) ;;
    esac
  fi
done <<< "$(list_tests)"

echo "────────────────────────────────────────"
if [ "$total" -lt 5 ]; then
  echo "⚠️★★★ 列挙が $total 本しかない。★ **検査が空振りしている可能性** → 判定しない。"
  exit 2
fi
if [ "$miss" -eq 0 ]; then
  echo "✅ ★ $total 本すべて CI から呼ばれている（★ 除外は理由つき）"
else
  echo "⚠️★★★ **$total 本中 $miss 本が CI で走らない。**"
  echo "   → ★ **いずれかの workflow** に足すか、⚠️ **理由つきで**本スクリプトの除外表に書くこと。"
  exit 3
fi
