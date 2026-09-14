#!/usr/bin/env bash
# loop-worktree-deny-test.sh — `scripts/loop-worktree-deny.sh` と loop-spawn.sh への配線の検査。
#
# ⚠️★★★ **「正常なら緑」だけ試さない**（★ `verify-before-claiming` ルール 5b / 6）。
#   ★ 3 状態（**不在 / 正常 / 壊れている**）を実際に作って通し、
#   ⚠️ **陰性対照**（1 件抜いたら検査が赤になるか）まで見る。
#   ★ 検査が空振りしていたら、「deny が入っている」という緑は何の保証にもならない。
#
# ★ 対象:
#   1. 3 状態 ＋ 冪等性
#   2. ⚠️ 陰性対照（検査が空振りしていないこと）
#   3. ⚠️★★★ **契約の二重定義** —— スクリプトの 7 件 ⇄ `loop-config.README.md` の逐語 7 件
#   4. ★ `loop-spawn.sh` への配線を **実際に worktree を作って** 検査する（一時 git repo 内）
#      ⚠️ 併せて「**stdout の最終行 = worktree の絶対パス**」という
#      `loop-run.sh:275` (`tail -1`) の契約が壊れていないことを見る。
#
# Usage: bash scripts/loop-worktree-deny-test.sh
# Exit:  0 = 全件合格 / 1 = 不合格あり / 2 = ⚠️ 検査できなかった
#
# 関連: .steering/20260914-loop-foundation-worktree-deny/
set -uo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"
DENY_SH="${REPO_ROOT}/scripts/loop-worktree-deny.sh"
SPAWN_SH="${REPO_ROOT}/scripts/loop-spawn.sh"
README="${REPO_ROOT}/.steering/_template/loop-config.README.md"

PASS=0; FAIL=0
ok() { echo "  OK   $1"; PASS=$((PASS + 1)); }
ng() { echo "  NG   $1"; FAIL=$((FAIL + 1)); }

command -v jq >/dev/null 2>&1 || { echo "jq が無いので検査できない (★ 判定しない)"; exit 2; }
[ -f "${DENY_SH}" ]  || { echo "loop-worktree-deny.sh が無い"; exit 2; }
[ -f "${SPAWN_SH}" ] || { echo "loop-spawn.sh が無い"; exit 2; }
[ -f "${README}" ]   || { echo "loop-config.README.md が無い"; exit 2; }

TMP="$(mktemp -d)"
FINISHED=0
cleanup() {
  local rc=$?
  # ⚠️ 一時 git repo と worktree ごと消す（★ 実 repo には 1 バイトも触れていない）
  rm -rf "${TMP}" 2>/dev/null || true
  if [ "${FINISHED}" -eq 0 ]; then
    echo "  NG   ⚠️★ 検査自身が途中で終了した (rc=${rc})。★ 緑として扱わないこと。"
  fi
}
trap cleanup EXIT

# ⚠️ Windows(git-bash) の jq は CRLF で出力するので、行の突き合わせ前に CR を落とす。
deny_of() { jq -r '.permissions.deny // [] | .[]' "$1" 2>/dev/null | tr -d '\r' | sort; }
count_of() { printf '%s\n' "$1" | grep -c . || true; }

echo "════════════════════════════════════════"
echo "1. --print と 契約の二重定義 (スクリプト ⇄ loop-config.README.md)"

printed="$(bash "${DENY_SH}" --print | sort)"
n_printed="$(count_of "${printed}")"
if [ "${n_printed}" -eq 7 ]; then
  ok "--print が 7 件を返した"
else
  ng "--print が ${n_printed} 件 (★ 7 件のはず)"
fi

# ★ README のコードブロックから逐語で抜く。
# ⚠️ 抽出が空なら「一致」ではなく **検査不能** として不合格にする（★ 0 件マッチは緑になる）。
# ⚠️ 抽出は **`deny` 配列だけ**に限る（★ 同じブロックに `allow` / `ask` の例が足されても壊れないため）。
from_readme="$(awk '/"deny": \[/,/\]/' "${README}" | grep -oE '"Bash\([^"]*\)"' | tr -d '"' | sort -u)"
n_readme="$(count_of "${from_readme}")"
if [ "${n_readme}" -lt 7 ]; then
  ng "README から deny を ${n_readme} 件しか抽出できない (★ 抽出が壊れている → 判定できない)"
elif [ "${printed}" = "${from_readme}" ]; then
  ok "契約の二重定義なし: スクリプトの 7 件と README の 7 件が集合一致"
else
  ng "スクリプトと README の deny が食い違う (★ 片方だけ増えた)"
  diff <(printf '%s\n' "${printed}") <(printf '%s\n' "${from_readme}") || true
fi

echo "2. 3 状態 (不在 / 正常 / 壊れている)"

# --- 不在 ---
WT_A="${TMP}/absent"; mkdir -p "${WT_A}"
if bash "${DENY_SH}" "${WT_A}" >/dev/null 2>&1; then
  f_a="${WT_A}/.claude/settings.local.json"
  got_a="$(deny_of "${f_a}")"
  if [ "$(count_of "${got_a}")" -eq 7 ] && [ "${got_a}" = "${printed}" ]; then
    ok "不在: 必須 7 件ちょうどを持つ有効な JSON を新規作成した"
  else
    ng "不在: 生成された deny が必須 7 件と一致しない"
  fi
else
  ng "不在: 注入が失敗した"
fi

# --- 正常 (他のキーあり) ---
WT_B="${TMP}/existing"; mkdir -p "${WT_B}/.claude"
cat > "${WT_B}/.claude/settings.local.json" <<'EXISTING_JSON'
{
  "env": {"FOO": "bar"},
  "permissions": {
    "allow": ["Bash(cargo test:*)"],
    "deny": ["Bash(sudo:*)", "Bash(curl:*)"],
    "ask": ["Bash(npm publish:*)"]
  }
}
EXISTING_JSON
if bash "${DENY_SH}" "${WT_B}" >/dev/null 2>&1; then
  f_b="${WT_B}/.claude/settings.local.json"
  kept_env="$(jq -r '.env.FOO // ""' "${f_b}")"
  kept_allow="$(jq -r '.permissions.allow[0] // ""' "${f_b}")"
  kept_ask="$(jq -r '.permissions.ask[0] // ""' "${f_b}")"
  kept_extra="$(jq -r 'if (.permissions.deny | index("Bash(curl:*)")) == null then "gone" else "kept" end' "${f_b}")"
  n_deny="$(jq -r '.permissions.deny | length' "${f_b}")"
  n_uniq="$(jq -r '.permissions.deny | unique | length' "${f_b}")"
  got_b="$(deny_of "${f_b}")"
  n_missing=0
  while IFS= read -r req; do
    [ -n "${req}" ] || continue
    printf '%s\n' "${got_b}" | grep -qxF "${req}" || n_missing=$((n_missing + 1))
  done <<< "${printed}"
  if [ "${kept_env}" = "bar" ] && [ "${kept_allow}" = "Bash(cargo test:*)" ] \
     && [ "${kept_ask}" = "Bash(npm publish:*)" ] && [ "${kept_extra}" = "kept" ]; then
    ok "正常: 他のキー (env / allow / ask) と既存 deny を保持した"
  else
    ng "正常: 既存のキーが失われた (env=${kept_env} allow=${kept_allow} ask=${kept_ask} curl=${kept_extra})"
  fi
  if [ "${n_missing}" -eq 0 ]; then
    ok "正常: 必須 7 件がすべてマージされた"
  else
    ng "正常: 必須 deny が ${n_missing} 件欠けている"
  fi
  if [ "${n_deny}" = "${n_uniq}" ] && [ "${n_deny}" = "8" ]; then
    ok "正常: 重複なし (既存 2 ∪ 必須 7 = 8 件。★ sudo が重複していない)"
  else
    ng "正常: deny の件数が想定外 (len=${n_deny} uniq=${n_uniq}。★ 8 件のはず)"
  fi
else
  ng "正常: 既存ファイルがあるときの注入が失敗した"
fi

# --- 壊れている ---
WT_C="${TMP}/broken"; mkdir -p "${WT_C}/.claude"
printf '{ this is not json' > "${WT_C}/.claude/settings.local.json"
before="$(cat "${WT_C}/.claude/settings.local.json")"
bash "${DENY_SH}" "${WT_C}" >/dev/null 2>&1; rc_broken=$?
after="$(cat "${WT_C}/.claude/settings.local.json")"
if [ "${rc_broken}" -ne 0 ]; then
  ok "壊れている: 非 0 で停止した (fail-closed)"
else
  ng "壊れている: 素通りした (⚠️★ 危険)"
fi
if [ "${before}" = "${after}" ]; then
  ok "壊れている: ファイルを 1 バイトも書き換えていない"
else
  ng "壊れている: ファイルを書き換えた (★ 人の設定を黙って捨てた)"
fi
leftover="$(ls -a "${WT_C}/.claude" | grep -c '^\.settings\.local\.json\.' || true)"
if [ "${leftover}" -eq 0 ]; then
  ok "壊れている: 一時ファイルを残していない"
else
  ng "壊れている: 一時ファイルが ${leftover} 個残った"
fi

# --- オブジェクトでない JSON (配列) ---
WT_D="${TMP}/array"; mkdir -p "${WT_D}/.claude"
printf '["not", "an", "object"]' > "${WT_D}/.claude/settings.local.json"
bash "${DENY_SH}" "${WT_D}" >/dev/null 2>&1; rc_arr=$?
if [ "${rc_arr}" -ne 0 ]; then
  ok "配列 JSON: 非 0 で停止した"
else
  ng "配列 JSON: 素通りした"
fi

echo "3. 冪等性"
bash "${DENY_SH}" "${WT_B}" >/dev/null 2>&1
n2="$(jq -r '.permissions.deny | length' "${WT_B}/.claude/settings.local.json")"
if [ "${n2}" = "8" ]; then
  ok "冪等: 2 回目でも deny が増えない (8 件のまま)"
else
  ng "冪等: 2 回目で ${n2} 件に増えた"
fi

echo "4. 検査 (--verify) の陽性対照 / 陰性対照"

if bash "${DENY_SH}" --verify "${WT_A}" >/dev/null 2>&1; then
  ok "陽性対照: 正しい状態を OK と判定した"
else
  ng "陽性対照: 正しい状態を NG と判定した (★ 検査が厳しすぎる)"
fi

# ⚠️★★★ 陰性対照 —— ★ これが緑だと、上の全部が「何も見ていない緑」になる。
WT_E="${TMP}/tampered"; mkdir -p "${WT_E}/.claude"
jq 'del(.permissions.deny[] | select(. == "Bash(git push:*)"))' \
   "${WT_A}/.claude/settings.local.json" > "${WT_E}/.claude/settings.local.json"
if bash "${DENY_SH}" --verify "${WT_E}" >/dev/null 2>&1; then
  ng "陰性対照: 1 件抜いたのに OK と言った (⚠️★ 検査が空振りしている)"
else
  ok "陰性対照: 1 件抜いたら NG と判定した"
fi

# ⚠️★★★ **fail-open の回帰テスト**（★ 2026-09-14 に code-reviewer / security-checker が
#   **両方 HIGH** で指摘し、実測で再現した形）。
#   ★ 旧実装は jq の実行時エラーを `2>/dev/null || true` で握りつぶし、
#     ⚠️ **deny が 1 件も無いのに「検査 OK」**と報告していた。
#   → ★ 下の 6 形はすべて **NG でなければならない**（⚠️ 1 つでも緑なら安全装置の検査系が嘘をつく）。
fo_fail=0; fo_n=0
for shape in \
  '{"permissions":"nope"}' \
  '["not","an","object"]' \
  '{"permissions":["a"]}' \
  '{"permissions":42}' \
  '{"permissions":{}}' \
  '{}' ; do
  fo_n=$((fo_n + 1))
  WT_FO="${TMP}/failopen-${fo_n}"; mkdir -p "${WT_FO}/.claude"
  printf '%s' "${shape}" > "${WT_FO}/.claude/settings.local.json"
  if bash "${DENY_SH}" --verify "${WT_FO}" >/dev/null 2>&1; then
    ng "陰性対照(fail-open 回帰): ${shape} を OK と言った"
    fo_fail=$((fo_fail + 1))
  fi
done
if [ "${fo_fail}" -eq 0 ]; then
  ok "陰性対照(fail-open 回帰): deny を持たない ${fo_n} 形すべてを NG と判定した"
fi

# ⚠️ 型が違う (deny が配列でない) 場合
WT_F="${TMP}/wrongtype"; mkdir -p "${WT_F}/.claude"
printf '{"permissions": {"deny": "Bash(git push:*)"}}' > "${WT_F}/.claude/settings.local.json"
if bash "${DENY_SH}" --verify "${WT_F}" >/dev/null 2>&1; then
  ng "陰性対照: deny が配列でないのに OK と言った"
else
  ok "陰性対照: deny が配列でなければ NG と判定した"
fi

# ⚠️ 1 件だけ欠けている形も NG か（★ 部分適用を緑にしない）
WT_H="${TMP}/partial"; mkdir -p "${WT_H}/.claude"
printf '{"permissions": {"deny": ["Bash(sudo:*)"]}}' > "${WT_H}/.claude/settings.local.json"
if bash "${DENY_SH}" --verify "${WT_H}" >/dev/null 2>&1; then
  ng "陰性対照: 部分適用 (1 件だけ) を OK と言った"
else
  ok "陰性対照: 部分適用を NG と判定した"
fi

# ⚠️ ファイルが無い場合
WT_G="${TMP}/nofile"; mkdir -p "${WT_G}"
if bash "${DENY_SH}" --verify "${WT_G}" >/dev/null 2>&1; then
  ng "陰性対照: settings.local.json が無いのに OK と言った"
else
  ok "陰性対照: settings.local.json が無ければ NG と判定した"
fi

# ⚠️ 存在しないディレクトリ
if bash "${DENY_SH}" "${TMP}/does-not-exist" >/dev/null 2>&1; then
  ng "存在しないディレクトリを受け付けた"
else
  ok "存在しないディレクトリを拒否した"
fi

echo "5. loop-spawn.sh への配線 (⚠️ 実際に一時 git repo で worktree を作る)"

setup_fake_repo() { # setup_fake_repo <repo-dir>
  local r="$1"
  mkdir -p "${r}/scripts"
  cp "${SPAWN_SH}" "${r}/scripts/loop-spawn.sh"
  cp "${DENY_SH}"  "${r}/scripts/loop-worktree-deny.sh"
  # ⚠️ 実行者の global git 設定を継承しない（★ `commit.gpgsign=true` / `core.hooksPath` /
  #   `init.templateDir` が設定された環境で **環境由来の赤**になるのを避ける。code-reviewer MEDIUM）。
  (
    cd "${r}" || exit 1
    export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
    git -c init.defaultBranch=main -c init.templateDir= init -q . || exit 1
    git config user.email loop-test@example.invalid || exit 1
    git config user.name loop-test || exit 1
    git config commit.gpgsign false || exit 1
    git config core.hooksPath /dev/null || exit 1
    git add scripts || exit 1
    git commit -q -m init || exit 1
  ) >/dev/null 2>&1
}

FAKE="${TMP}/fake/repo"; mkdir -p "${FAKE}"
if setup_fake_repo "${FAKE}"; then
  spawn_out="$( (cd "${FAKE}" && bash scripts/loop-spawn.sh --no-exec 001 t) 2>/dev/null )"
  rc_spawn=$?
  last_line="$(printf '%s\n' "${spawn_out}" | tail -1)"
  if [ "${rc_spawn}" -eq 0 ]; then
    ok "配線: loop-spawn.sh --no-exec が成功した"
  else
    ng "配線: loop-spawn.sh --no-exec が失敗した (rc=${rc_spawn})"
  fi
  if [ -n "${last_line}" ] && [ -d "${last_line}" ]; then
    ok "契約: stdout の最終行が worktree のディレクトリである (★ loop-run.sh の tail -1)"
  else
    ng "契約: stdout の最終行がディレクトリでない → [${last_line}] (⚠️ loop-run.sh が worktree を掴めなくなる)"
  fi
  if [ -n "${last_line}" ] && [ -d "${last_line}" ] \
     && [ "$(count_of "$(deny_of "${last_line}/.claude/settings.local.json")")" -eq 7 ]; then
    ok "配線: 作られた worktree に必須 deny 7 件が入っている"
  else
    ng "配線: 作られた worktree に必須 deny が入っていない"
  fi
else
  ng "配線: 一時 git repo を用意できなかった (★ 判定できない)"
fi

# ⚠️★★★ 配線の陰性対照 —— ★ 注入が失敗したら **worktree を渡してはならない**。
FAKE2="${TMP}/fake2/repo"; mkdir -p "${FAKE2}"
if setup_fake_repo "${FAKE2}"; then
  printf '#!/usr/bin/env bash\nexit 1\n' > "${FAKE2}/scripts/loop-worktree-deny.sh"
  out2="$( (cd "${FAKE2}" && bash scripts/loop-spawn.sh --no-exec 002 t) 2>/dev/null )"
  rc2=$?
  last2="$(printf '%s\n' "${out2}" | tail -1)"
  if [ "${rc2}" -ne 0 ]; then
    ok "配線の陰性対照: 注入が失敗したら loop-spawn.sh も非 0 で止まる"
  else
    ng "配線の陰性対照: 注入が失敗したのに成功した (⚠️★ deny 無しの worktree を渡す)"
  fi
  if [ -n "${last2}" ] && [ -d "${last2}" ]; then
    ng "配線の陰性対照: 失敗したのに worktree パスを stdout 最終行に出した (⚠️ loop-run.sh が掴んでしまう)"
  else
    ok "配線の陰性対照: worktree パスを渡していない"
  fi
  # ⚠️★★★ 失敗した worktree / branch が残らないこと（★ 残すと人が手で入って deny 無しで起動できる。
  #   ★ かつ同じ id の再実行が「同名 worktree が既に存在」で恒久的に死ぬ）。
  left_wt="$( (cd "${FAKE2}" && git worktree list --porcelain 2>/dev/null | grep -c '^worktree ') || true)"
  left_br="$( (cd "${FAKE2}" && git branch --list 'loop/*' 2>/dev/null | grep -c .) || true)"
  if [ "${left_wt}" = "1" ] && [ "${left_br}" = "0" ]; then
    ok "配線の陰性対照: 失敗した worktree と branch を撤去した (残 worktree=1 本体のみ / loop ブランチ 0)"
  else
    ng "配線の陰性対照: worktree/branch が残った (worktree=${left_wt} loopブランチ=${left_br})"
  fi
else
  ng "配線の陰性対照: 一時 git repo を用意できなかった (★ 判定できない)"
fi

echo "────────────────────────────────────────"
FINISHED=1
echo "合格 ${PASS} / 不合格 ${FAIL}"
[ "${FAIL}" -eq 0 ] || exit 1
echo "全件合格"
