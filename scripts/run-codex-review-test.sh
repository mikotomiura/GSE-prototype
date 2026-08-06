#!/usr/bin/env bash
# scripts/run-codex-review-test.sh
# run-codex-review.sh の **codex を呼ぶ手前の分岐**を実測する。
#
# ⚠️★ なぜ要るか: このラッパは「Codex に何を送るか」を決める唯一の場所であり、
#   2026-08-07 に ★ 引数素通し (`--no-index` で repo 外のファイルを送れる) と
#   ★ `--ack-filtered` (fail-closed の逃がし口) を足した。⚠️ **足した本人が壊しても
#   気づけない**ので、ここで測る (cross-review 指摘)。
#
# ⚠️ ★ codex を実際に呼ぶ経路 (--ack-filtered で最後まで進む) は **ここでは測らない**。
#   課金と予算ファイルの書き換えが起きるため。★ その経路は人が 1 回ずつ実走して確かめる。
#
# 使い方: bash scripts/run-codex-review-test.sh   (rc=0 なら全ケース期待どおり)

set -uo pipefail
cd "$(dirname "$0")/.."
W=scripts/run-codex-review.sh

ng=0
total=0

# rc と、stderr に出るべき文言を測る。
expect() {
  local label="$1" want_rc="$2" want_msg="$3"
  shift 3
  local err rc
  err=$("$W" "$@" 2>&1 >/dev/null)
  rc=$?
  total=$((total + 1))
  if [ "$rc" -ne "$want_rc" ]; then
    echo "NG   $label → rc=$rc (${want_rc} を期待)  err=${err}"
    ng=$((ng + 1))
  elif ! printf '%s' "$err" | grep -qF -- "$want_msg"; then
    echo "NG   $label → rc=$rc は合っているが文言が違う: ${err}"
    ng=$((ng + 1))
  else
    echo "OK   $label → rc=$rc / 文言も期待どおり"
  fi
}

echo "--- 1. ★ 引数は <range> [-- <paths>] だけ (repo 外へ届く経路を塞ぐ) ---"
# ⚠️ --no-index は index も .gitignore も無視するので、通すと g1-submit.json
#   (endpoint + SHARED_SECRET) のような追跡外ファイルを Codex に送れてしまう。
expect "--no-index を拒否する"        1 "オプションは受け付けません" --no-index /etc/hosts /etc/passwd
expect "ack つきでも拒否する"          1 "オプションは受け付けません" --ack-filtered --no-index /etc/hosts /etc/passwd
expect "その他のオプションも拒否する"  1 "オプションは受け付けません" --cached
expect "range は 1 個まで"             1 "range は 1 個までです"      HEAD HEAD~1

echo "--- 2. ★ 明示した範囲が空なら rc=0 で帰らない (走ったと誤読させない) ---"
expect "空の範囲は exit 1"             1 "指定した差分が空です"       HEAD..HEAD -- scripts/run-codex-review.sh
# `--` の後ろは pathspec なので、`-` で始まっても引数検証は通す (空判定まで進む)。
expect "-- の後ろは通る"               1 "指定した差分が空です"       HEAD..HEAD -- ./no-such-file

echo "--- 3. ★ secrets-filter が止めたら既定は fail-closed ---"
# ⚠️ 「secret」の語を必ず含む差分を動的に選ぶ (固定ハッシュを埋め込まない)。
SF_COMMIT=$(git log -1 --format=%H -- scripts/secrets-filter.sh)
if [ -z "$SF_COMMIT" ]; then
  echo "NG   secrets-filter.sh に触れたコミットが見つからない (検査不能)"
  ng=$((ng + 1)); total=$((total + 1))
else
  expect "ack 無しは exit 2 で止まる" 2 "BLOCKED" "$SF_COMMIT^..$SF_COMMIT" -- scripts/secrets-filter.sh
fi

echo
if [ "$ng" -eq 0 ]; then
  echo "全 $total ケース期待どおり"
else
  echo "$ng 件が期待と違う（全 $total ケース）"
fi
exit $((ng == 0 ? 0 : 1))
