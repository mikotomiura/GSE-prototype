#!/usr/bin/env bash
# loop-spawn-cleanup-test.sh — `scripts/loop-spawn.sh --cleanup` の検査 (★ 起票 18 の回帰)。
#
# ⚠️★★★ **何を止めるためにあるのか** (2026-09-20 の実測・起票 18):
#   ★ 旧実装は worktree を **ブランチ名だけ**で引いていたので、`loop/<id>-*` から逸脱した
#     worktree を 1 件も撤去できないまま **`cleanup 完了` / exit 0** を返していた。
#   ⚠️ 実害: (1) 同じ id の再実行が恒久的に死ぬ (2) main checkout が `main` を取れなくなる
#     (3) ★★★ **失敗が誰にも見えない** (`verify-before-claiming` の型)。
#
# ⚠️★★★ **「正常なら緑」だけ試さない** (★ `loop-worktree-deny-test.sh` と同じ規約)。
#   ★ **陰性対照** (＝ 実装を殺したら赤くなるか) まで見る。ここでは一致規則の
#     **path 系統を sed で潰した変異版**を作り、逸脱 worktree が残ることを確認する。
#   ★ 検査が空振りしていたら、「cleanup は動く」という緑は何の保証にもならない。
#
# ★ 対象:
#   1. 正常系 / ⚠️ 逸脱 (★ 本丸) / 冪等
#   2. ⚠️ 撤去不能 (lock) のとき「完了」と書かず **非 0** で止まるか
#   3. ⚠️ 別 id を巻き込まないか (★ 旧実装は正規表現の部分一致で `loop/zzz2-*` を巻き込んだ)
#   4. ⚠️★★★ **main checkout を撤去しない**か
#   5. ⚠️ 残存ディレクトリを **消さずに**報告し、非 0 で止まるか
#   6. ⚠️★★★ 変異テスト (★ この検査が空振りしていないこと)
#
# Usage: bash scripts/loop-spawn-cleanup-test.sh
# Exit:  0 = 全件合格 / 1 = 不合格あり / 2 = ⚠️ 検査できなかった
#
# ⚠️ **実 repo には 1 バイトも触れない** (★ すべて mktemp 配下の使い捨て git repo で行う)。
#
# 関連: .steering/20260921-loop-spawn-cleanup-fix/ ／
#       .steering/20260914-mhd-feature-offline-tiers/blockers.md 起票 18
set -uo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"
SPAWN_SH="${REPO_ROOT}/scripts/loop-spawn.sh"

# ⚠️ 実行者の global / system git 設定を継承しない (★ `commit.gpgsign=true` /
#   `core.hooksPath` / `init.templateDir` が設定された環境で**環境由来の赤**になるのを避ける)。
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null

PASS=0; FAIL=0
ok() { echo "  OK   $1"; PASS=$((PASS + 1)); }
ng() { echo "  NG   $1"; FAIL=$((FAIL + 1)); }

[ -f "${SPAWN_SH}" ] || { echo "loop-spawn.sh が無い"; exit 2; }

TMP="$(mktemp -d)" || { echo "mktemp に失敗 (★ 判定しない)"; exit 2; }
FINISHED=0
cleanup_tmp() {
  local rc=$?
  rm -rf "${TMP}" 2>/dev/null || true
  if [ "${FINISHED}" -eq 0 ]; then
    echo "  NG   ⚠️★ 検査自身が途中で終了した (rc=${rc})。★ 緑として扱わないこと。"
  fi
}
trap cleanup_tmp EXIT

# ── ヘルパ ──────────────────────────────────────────────
setup_fake_repo() { # setup_fake_repo <repo-dir> [spawn-script-src]
  local r="$1" src="${2:-${SPAWN_SH}}"
  mkdir -p "${r}/scripts" || return 1
  cp "${src}" "${r}/scripts/loop-spawn.sh" || return 1
  # ★ deny 注入は **この検査の対象ではない** (★ 対象は loop-worktree-deny-test.sh)。
  #   ⚠️ 本物を使うと jq 必須になり、jq の無い環境で「判定できない」が増えるだけなので stub にする。
  printf '#!/usr/bin/env bash\nexit 0\n' > "${r}/scripts/loop-worktree-deny.sh" || return 1
  (
    cd "${r}" || exit 1
    git -c init.defaultBranch=main -c init.templateDir= init -q . || exit 1
    git config user.email loop-test@example.invalid || exit 1
    git config user.name loop-test || exit 1
    git config commit.gpgsign false || exit 1
    git config core.hooksPath /dev/null || exit 1
    git add scripts || exit 1
    git commit -q -m init || exit 1
  ) >/dev/null 2>&1
}

do_spawn() { # do_spawn <repo-dir> <id> <short>
  ( cd "$1" && bash scripts/loop-spawn.sh --no-exec "$2" "$3" ) >/dev/null 2>&1
}

OUT=""; RC=0
do_cleanup() { # do_cleanup <repo-dir> <id>  → OUT / RC に入れる
  OUT="$( (cd "$1" && bash scripts/loop-spawn.sh --cleanup "$2") 2>&1 )"
  RC=$?
}

# ⚠️ `grep -q` を使わない —— `set -o pipefail` 下では grep の早期終了が上流に SIGPIPE を投げ、
#   ★ **一致したのに非 0** になりうる (＝ 検査が静かに反転する)。→ `grep -c` で全部読ませる。
wt_has() { # wt_has <repo-dir> <basename> → 0 なら登録に在る
  local n
  n="$( (cd "$1" && git worktree list --porcelain 2>/dev/null) \
        | awk '/^worktree /{p=substr($0,10); gsub(/\\/,"/",p); k=split(p,s,"/"); print s[k]}' \
        | grep -cxF "$2" )" || true
  [ "${n:-0}" -gt 0 ]
}

branch_exists() { # branch_exists <repo-dir> <branch>
  ( cd "$1" && git show-ref --verify --quiet "refs/heads/$2" )
}

has_text() { # has_text <haystack> <needle>
  case "$1" in *"$2"*) return 0 ;; esac
  return 1
}

# ── 1. 正常系 / 逸脱 / 冪等 ─────────────────────────────
echo "════════════════════════════════════════"
echo "1. 正常系 / ⚠️ 逸脱 (★ 起票 18 の本丸) / 冪等"

R1="${TMP}/r1/repo"; mkdir -p "${R1}"
if ! setup_fake_repo "${R1}"; then
  ng "一時 git repo を用意できなかった (★ 判定できない)"
else
  # --- 1a: 正常系 (loop/<id>-<short> のまま) ---
  if do_spawn "${R1}" 001 t; then
    do_cleanup "${R1}" 001
    if [ "${RC}" -eq 0 ] && ! wt_has "${R1}" "repo-001-t" && ! branch_exists "${R1}" "loop/001-t"; then
      ok "正常系: worktree と branch を撤去し exit 0"
    else
      ng "正常系: rc=${RC} / worktree 残=$(wt_has "${R1}" "repo-001-t" && echo yes || echo no) / branch 残=$(branch_exists "${R1}" "loop/001-t" && echo yes || echo no)"
    fi
  else
    ng "正常系: worktree を作れなかった (★ 判定できない)"
  fi

  # --- 1b: ⚠️★★★ 逸脱 (worktree が loop/<id>-* 以外を指す) = 起票 18 そのもの ---
  if do_spawn "${R1}" 002 t; then
    ( cd "${TMP}/r1/wt/repo-002-t" && git switch -c deviated-002 ) >/dev/null 2>&1
    do_cleanup "${R1}" 002
    if [ "${RC}" -eq 0 ] && ! wt_has "${R1}" "repo-002-t"; then
      ok "⚠️★ 逸脱: ブランチが loop/002-* から外れていても撤去できた (★ 起票 18 の回帰)"
    else
      ng "⚠️★ 逸脱: 撤去できていない (rc=${RC}) —— ★ 起票 18 が再発している"
    fi
    if [ -d "${TMP}/r1/wt/repo-002-t" ]; then
      ng "⚠️ 逸脱: ディレクトリが残っている (★ 同じ id の再実行が死ぬ)"
    else
      ok "⚠️ 逸脱: ディレクトリも残っていない"
    fi
  else
    ng "逸脱: worktree を作れなかった (★ 判定できない)"
  fi

  # --- 1c: 冪等 (対象 0 件は緑) ---
  do_cleanup "${R1}" 001
  if [ "${RC}" -eq 0 ] && has_text "${OUT}" "対象なし"; then
    ok "冪等: 2 回目は「対象なし」で exit 0"
  else
    ng "冪等: rc=${RC} / 出力=[${OUT}]"
  fi
fi

# ── 2. 撤去不能のとき「完了」と書かない ─────────────────
echo "2. ⚠️ 撤去不能 (lock) のとき「完了」と書かず非 0 で止まるか"

R2="${TMP}/r2/repo"; mkdir -p "${R2}"
if ! setup_fake_repo "${R2}" || ! do_spawn "${R2}" 004 t; then
  ng "撤去不能: 準備できなかった (★ 判定できない)"
else
  ( cd "${R2}" && git worktree lock "${TMP}/r2/wt/repo-004-t" ) >/dev/null 2>&1
  do_cleanup "${R2}" 004
  if [ "${RC}" -ne 0 ]; then
    ok "撤去不能: 非 0 で止まった"
  else
    ng "撤去不能: exit 0 を返した (⚠️★ 起票 18 の再来)"
  fi
  if has_text "${OUT}" "cleanup 完了"; then
    ng "撤去不能: 「完了」と書いた (⚠️★★★ 事実と報告が食い違っている)"
  else
    ok "撤去不能: 「完了」と書かなかった"
  fi
  if wt_has "${R2}" "repo-004-t"; then
    ok "撤去不能: worktree は実際に残っている (★ 報告と事実が一致)"
  else
    ng "撤去不能: worktree は消えているのに失敗と報告した (★ 検査の前提が崩れている)"
  fi
  ( cd "${R2}" && git worktree unlock "${TMP}/r2/wt/repo-004-t" ) >/dev/null 2>&1 || true
fi

# ── 3. 別 id を巻き込まない ─────────────────────────────
echo "3. ⚠️ 別 id を巻き込まないか (★ 旧実装は部分一致で巻き込んだ)"

R3="${TMP}/r3/repo"; mkdir -p "${R3}"
if ! setup_fake_repo "${R3}" || ! do_spawn "${R3}" 005 t || ! do_spawn "${R3}" 0055 t; then
  ng "別 id: 準備できなかった (★ 判定できない)"
else
  do_cleanup "${R3}" 005
  if [ "${RC}" -eq 0 ] && ! wt_has "${R3}" "repo-005-t"; then
    ok "別 id: 対象 (005) は撤去できた"
  else
    ng "別 id: 対象 (005) を撤去できなかった (rc=${RC})"
  fi
  if wt_has "${R3}" "repo-0055-t" && branch_exists "${R3}" "loop/0055-t"; then
    ok "別 id: ⚠️ 0055 を巻き込んでいない (worktree も branch も健在)"
  else
    ng "別 id: ⚠️★★★ 0055 を巻き込んだ (★ 前方一致の区切りが効いていない)"
  fi
fi

# ── 4. main checkout を撤去しない ───────────────────────
echo "4. ⚠️★★★ main checkout を撤去しないか"

R4="${TMP}/r4/repo"; mkdir -p "${R4}"
if ! setup_fake_repo "${R4}"; then
  ng "main 保護: 準備できなかった (★ 判定できない)"
else
  # ★ main checkout 自身に `loop/006-t` を掴ませる (＝ ブランチ一致が本体に当たる形)。
  ( cd "${R4}" && git switch -c loop/006-t ) >/dev/null 2>&1
  do_cleanup "${R4}" 006
  if [ -d "${R4}/.git" ] && [ -f "${R4}/scripts/loop-spawn.sh" ] && wt_has "${R4}" "repo"; then
    ok "main 保護: ⚠️★★★ main checkout を撤去していない"
  else
    ng "main 保護: ⚠️★★★ main checkout を壊した (★ 最悪の事故)"
  fi
  if has_text "${OUT}" "main checkout"; then
    ok "main 保護: 撤去対象から外したことを明示した"
  else
    ng "main 保護: 何も言わずに素通りした (★ 人が気づけない)"
  fi
  if [ "${RC}" -ne 0 ]; then
    ok "main 保護: 掴んだままの branch を消せないので非 0 で止まった"
  else
    ng "main 保護: branch が残っているのに exit 0 を返した"
  fi
fi

# ── 5. 残存ディレクトリを消さずに報告する ───────────────
echo "5. ⚠️ 残存ディレクトリを **消さずに** 報告し、非 0 で止まるか"

R5="${TMP}/r5/repo"; mkdir -p "${R5}"
if ! setup_fake_repo "${R5}"; then
  ng "残存 dir: 準備できなかった (★ 判定できない)"
else
  mkdir -p "${TMP}/r5/wt/repo-007-x"
  echo "do-not-delete-me" > "${TMP}/r5/wt/repo-007-x/keep.txt"
  do_cleanup "${R5}" 007
  if [ "${RC}" -ne 0 ]; then
    ok "残存 dir: 非 0 で止まった (★ 再実行を殺す状態を「完了」と書かない)"
  else
    ng "残存 dir: exit 0 を返した (⚠️ 次の spawn が『ディレクトリが残存』で死ぬ)"
  fi
  if [ -f "${TMP}/r5/wt/repo-007-x/keep.txt" ]; then
    ok "残存 dir: ⚠️ 中身を消していない (★ rm -rf しない)"
  else
    ng "残存 dir: ⚠️★★★ 人のディレクトリを黙って消した"
  fi
fi

# ── 6. 変異テスト (★ この検査が空振りしていないこと) ────
echo "6. ⚠️★★★ 変異テスト —— path 系統を潰したら赤くなるか"

R6="${TMP}/r6/repo"; mkdir -p "${R6}"
MUT="${TMP}/mutated-loop-spawn.sh"
sed 's/if (bn == exa_p || index(bn, pfx_p) == 1) hitp = 1/hitp = hitp/' "${SPAWN_SH}" > "${MUT}"
if grep -c 'index(bn, pfx_p)' "${MUT}" 2>/dev/null | grep -qv '^0$'; then
  ng "変異テスト: 変異が当たらなかった (★ 一致規則の書き方が変わった → 検査不能)"
elif ! setup_fake_repo "${R6}" "${MUT}" || ! do_spawn "${R6}" 008 t; then
  ng "変異テスト: 準備できなかった (★ 判定できない)"
else
  ( cd "${TMP}/r6/wt/repo-008-t" && git switch -c deviated-008 ) >/dev/null 2>&1
  do_cleanup "${R6}" 008
  if wt_has "${R6}" "repo-008-t"; then
    ok "変異テスト: path 系統を潰すと逸脱 worktree が残った (★ 検査は空振りしていない)"
  else
    ng "変異テスト: 潰しても撤去できた (⚠️★★★ この検査は何も見ていない)"
  fi
  # ★ 併せて「最後の網」も見る —— ⚠️ 一致規則が退行しても **「完了」とは書かせない**。
  if [ "${RC}" -ne 0 ] && ! has_text "${OUT}" "cleanup 完了"; then
    ok "変異テスト: 一致規則が退行しても「完了」とは書かなかった (★ 残存 dir の網が効いた)"
  else
    ng "変異テスト: 退行しているのに「完了」と書いた (⚠️★ 起票 18 と同じ嘘に戻る)"
  fi
fi

echo "════════════════════════════════════════"
echo "PASS=${PASS}  FAIL=${FAIL}"
FINISHED=1
[ "${FAIL}" -eq 0 ] || exit 1
exit 0
