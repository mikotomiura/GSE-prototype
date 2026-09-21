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
#   6. ⚠️★★★ 変異テスト (★ --cleanup の検査が空振りしていないこと)
#   7. ★★★ **base の解決** (★ 起票 23・2026-09-21 追加) —— config を task で選ぶ /
#      ⚠️ 特定できなければ **1 件でも止まる** / ⚠️ 読めない値で **黙って main へ落ちない** /
#      ★ provenance と乖離を stderr へ出す / ★ stdout の最終行の契約を壊さない
#   8. ⚠️★★★ 変異テスト (★ **群 7 が** 空振りしていないこと) —— fail-closed と抽出器を潰す
#
# Usage: bash scripts/loop-spawn-cleanup-test.sh
# Exit:  0 = 全件合格 / 1 = 不合格あり / 2 = ⚠️ 検査できなかった
#
# ⚠️ **実 repo には 1 バイトも触れない** (★ すべて mktemp 配下の使い捨て git repo で行う)。
#
# 関連: .steering/20260921-loop-spawn-cleanup-fix/ (起票 18) ／
#       .steering/20260921-loop-spawn-resolve-base/ (★ 起票 23・群 7 / 8) ／
#       .steering/20260914-mhd-feature-offline-tiers/blockers.md 起票 18 / 23
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

  # --- 1d: ⚠️ **完全一致**の経路 (`<id>-<short>` を丸ごと渡す) ---
  # ★ `--cleanup 001-issue` という渡し方が実在する
  #   (`.steering/_handoff/next-session-issue001-pause-const-arbitration.md:123` 逐語)。
  # ⚠️ これが無いと `bn == exa_p` / `b == exa_b` を消しても緑のままになる (★ code-reviewer 指摘)。
  if do_spawn "${R1}" 003 t; then
    do_cleanup "${R1}" 003-t
    if [ "${RC}" -eq 0 ] && ! wt_has "${R1}" "repo-003-t" && ! branch_exists "${R1}" "loop/003-t"; then
      ok "完全一致: <id>-<short> を丸ごと渡しても撤去できた"
    else
      ng "完全一致: rc=${RC} —— ★ 前方一致しか効いていない (⚠️ --cleanup 001-issue の形が死ぬ)"
    fi
  else
    ng "完全一致: worktree を作れなかった (★ 判定できない)"
  fi

  # --- 1e: ⚠️★★★ **linked worktree の中から叩く** (★ code-reviewer HIGH・2026-09-21 実測) ---
  # ★ `git rev-parse --show-toplevel` は worktree 自身を返すので、repo_name が
  #   `repo-00N-t` に化け、⚠️ **path 系統 / main ガード / 残存 dir の網が同時に無効化**されていた。
  if do_spawn "${R1}" 009 t; then
    ( cd "${TMP}/r1/wt/repo-009-t" && git switch -c deviated-009 ) >/dev/null 2>&1
    OUT="$( (cd "${TMP}/r1/wt/repo-009-t" && bash "${R1}/scripts/loop-spawn.sh" --cleanup 009) 2>&1 )"
    RC=$?
    if ! wt_has "${R1}" "repo-009-t"; then
      ok "⚠️★ worktree 内から: main checkout を解決して撤去できた"
    else
      ng "⚠️★★★ worktree 内から: 撤去できていない (★ 起票 18 と同じ嘘が戻っている)"
    fi
    if wt_has "${R1}" "repo"; then
      ok "⚠️★ worktree 内から: main checkout は無傷"
    else
      ng "⚠️★★★ worktree 内から: main checkout を壊した"
    fi
    if [ "${RC}" -eq 0 ] && wt_has "${R1}" "repo-009-t"; then
      ng "⚠️★★★ worktree 内から: 残っているのに exit 0 を返した"
    else
      ok "⚠️★ worktree 内から: 事実と報告が一致している (rc=${RC})"
    fi
  else
    ng "worktree 内から: worktree を作れなかった (★ 判定できない)"
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

  # --- 2b: ⚠️★★★ **未コミット変更を黙って捨てない** (★ security-checker MEDIUM) ---
  # ★ 旧版は `remove --force` を無条件に撃っていた。⚠️ 逸脱 worktree は作業が載っている
  #   可能性が最も高い対象なので、★ **捨てずに人へ渡す**（branch 側で -D を避けたのと同じ理屈）。
  if do_spawn "${R2}" 010 t; then
    echo "work-in-progress" > "${TMP}/r2/wt/repo-010-t/WIP.txt"
    do_cleanup "${R2}" 010
    if [ -f "${TMP}/r2/wt/repo-010-t/WIP.txt" ]; then
      ok "未コミット変更: ⚠️ 黙って捨てていない (★ ファイルが残っている)"
    else
      ng "未コミット変更: ⚠️★★★ 作業を復旧不能に捨てた"
    fi
    if [ "${RC}" -ne 0 ] && ! has_text "${OUT}" "cleanup 完了"; then
      ok "未コミット変更: 「完了」と書かず非 0 で止まった"
    else
      ng "未コミット変更: rc=${RC} で「完了」と書いた"
    fi
  else
    ng "未コミット変更: worktree を作れなかった (★ 判定できない)"
  fi
fi

# ── 2c. id の検証 ───────────────────────────────────────
echo "2c. ⚠️★★★ id の glob メタ文字で削除対象が広がらないか"

R2B="${TMP}/r2b/repo"; mkdir -p "${R2B}"
if ! setup_fake_repo "${R2B}" || ! do_spawn "${R2B}" 011 t || ! do_spawn "${R2B}" 012 t; then
  ng "id 検証: 準備できなかった (★ 判定できない)"
else
  # ★ `git branch --list` の引数は **fnmatch パターン**なので、素通しだと
  #   `--cleanup '*'` が `loop/*` に化け、⚠️ **全 loop ブランチが -d の対象**になる。
  do_cleanup "${R2B}" '*'
  if [ "${RC}" -ne 0 ]; then
    ok "id 検証: '*' を拒否した"
  else
    ng "id 検証: '*' を受け付けた (⚠️ branch 側だけ全部消えうる)"
  fi
  if branch_exists "${R2B}" "loop/011-t" && branch_exists "${R2B}" "loop/012-t"; then
    ok "id 検証: ⚠️★★★ 無関係な loop ブランチを 1 本も消していない"
  else
    ng "id 検証: ⚠️★★★ 無関係な loop ブランチを消した"
  fi
  do_cleanup "${R2B}" '../../x'
  if [ "${RC}" -ne 0 ]; then
    ok "id 検証: '../../x' を拒否した (★ ../wt/ の外を指させない)"
  else
    ng "id 検証: '../../x' を受け付けた"
  fi
  # ★ `.` / `..` は文字集合だけでは通る（⚠️ Codex /cross-review 1 巡目）。
  do_cleanup "${R2B}" '..'
  if [ "${RC}" -ne 0 ]; then
    ok "id 検証: '..' を拒否した"
  else
    ng "id 検証: '..' を受け付けた"
  fi
fi

# ── 2d. 同じ basename の別 worktree に誤爆しないか ──────
echo "2d. ⚠️ 別パスに同じ basename の worktree があっても誤判定しないか"

R2C="${TMP}/r2c/repo"; mkdir -p "${R2C}"
if ! setup_fake_repo "${R2C}" || ! do_spawn "${R2C}" 013 t; then
  ng "同 basename: 準備できなかった (★ 判定できない)"
else
  # ★ `../wt/repo-013-t` と **同じ basename** の worktree を別の場所にも作る。
  #   ⚠️ 撤去確認を basename で行うと、対象が消えているのに「撤去失敗」と誤判定する。
  mkdir -p "${TMP}/r2c/other"
  ( cd "${R2C}" && git worktree add -b decoy-013 "${TMP}/r2c/other/repo-013-t" main ) >/dev/null 2>&1
  decoy_ok=0
  [ -d "${TMP}/r2c/other/repo-013-t" ] && decoy_ok=1
  if [ "${decoy_ok}" -eq 0 ]; then
    ng "同 basename: 囮 worktree を作れなかった (★ 判定できない)"
  else
    do_cleanup "${R2C}" 013
    if [ "${RC}" -eq 0 ] && ! has_text "${OUT}" "撤去失敗"; then
      ok "同 basename: 誤って「撤去失敗」と言わない (★ パスで見ている)"
    else
      ng "同 basename: 撤去できたのに失敗と報告した (rc=${RC}) —— ★ basename 照合に戻っている"
    fi
    if [ -d "${TMP}/r2c/other/repo-013-t" ]; then
      ok "同 basename: ⚠️ 別パスの worktree を巻き込んでいない"
    else
      ng "同 basename: ⚠️★★★ 別パスの worktree を撤去した"
    fi
  fi
fi

# ── 2e. パスに空白が混じっても壊れないか ────────────────
echo "2e. ⚠️ repo のパスに空白が混じっても一致規則が効くか"

R2D="${TMP}/r2d with space/repo"; mkdir -p "${R2D}"
if ! setup_fake_repo "${R2D}" || ! do_spawn "${R2D}" 014 t; then
  ng "空白パス: 準備できなかった (★ 判定できない)"
else
  ( cd "${TMP}/r2d with space/wt/repo-014-t" && git switch -c deviated-014 ) >/dev/null 2>&1
  do_cleanup "${R2D}" 014
  if [ "${RC}" -eq 0 ] && ! wt_has "${R2D}" "repo-014-t"; then
    ok "空白パス: 逸脱 worktree を撤去できた (★ wt_home の前方一致が空白で壊れない)"
  else
    ng "空白パス: 撤去できていない (rc=${RC}) —— ★ 空白入りパスで一致規則が壊れている"
  fi
fi
# ⚠️ **やっていないこと**（★ 隠さない）: パスに `*` / `?` / `[` を含む形と、
#   `git -C <wt> status` が失敗する形の回帰は**置いていない**。
#   ★ 前者は Windows がファイル名に `*` `?` を許さず**両 OS で同じ fixture を作れない**ため。
#     （⚠️ `contains_line` が literal であることは 2026-09-21 に `*` / `?` で別途実測した）
#   ★ 後者は権限・I/O エラーを**移植的に再現する手段が無い**ため。
#   → ⚠️ どちらも「検査していない」のであって「通っている」ではない。

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
sed 's/if (index(q, home) == 1 \&\& (bn == exa_p || index(bn, pfx_p) == 1)) hitp = 1/hitp = hitp/' "${SPAWN_SH}" > "${MUT}"
# ⚠️ ここでも `grep -q` をパイプ終端に置かない (★ 上の `wt_has` と同じ理屈)。
mut_left="$(grep -c 'index(bn, pfx_p)' "${MUT}" 2>/dev/null)" || mut_left=0
if [ "${mut_left:-0}" -ne 0 ]; then
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

# ── 7. base の解決 (★ 起票 23 の回帰) ───────────────────
# ⚠️★★★ **何を止めるためにあるのか** (2026-09-21 の実測・起票 23):
#   ★ 旧 `resolve_base` は逐語 `cfg="$(ls -1 .steering/*/_loop-config.json ... | tail -1 || true)"` で、
#     ⚠️ **いま回そうとしている task と無関係に** config を **黙って 1 つ**拾っていた。
#   ★ 実害の実測: `LOOP_FORCE=1 bash scripts/loop-spawn.sh --no-exec zzz` が
#     **完了済みタスクの枝**から worktree を切り、⚠️ **main より 38 コミット前**になった。
#   ⚠️ 併せて `jq -r ... 2>/dev/null || true` が **jq 不在 / 壊れた JSON / 不正な値**を
#     すべて「空」に潰し、★ **pin が無言で消える**形もあった。
#
# ⚠️★★★ **判定は「どの枝から切られたか」を *中身* で見る。**
#   ★ 各ブランチに `marker-<branch>` を 1 つ置き、worktree の HEAD sha と突き合わせる。
#   ⚠️ 「base=main と表示されたか」で見てはならない —— ★ 使い捨て repo の既定は `main` なので、
#     **取り逃がして fallback に落ちても偶然一致し、緑のまま穴が生きる**。
echo "7. ⚠️★★★ base の解決 —— task で選ぶ / 特定できなければ止まる (★ 起票 23)"

make_branch() { # make_branch <repo-dir> <branch>   ★ マーカー付きの実在ブランチを足す
  ( cd "$1" && git switch -q -c "$2" \
    && printf 'x\n' > "marker-$2" && git add "marker-$2" \
    && git commit -q -m "on $2" && git switch -q main ) >/dev/null 2>&1
}

add_cfg_raw() { # add_cfg_raw <repo-dir> <task-dir> <JSON 本文>
  local r="$1" t="$2"
  mkdir -p "${r}/.steering/${t}" || return 1
  printf '%s\n' "$3" > "${r}/.steering/${t}/_loop-config.json"
}

add_cfg() { # add_cfg <repo-dir> <task-dir> <base_branch の JSON 値そのまま>
  add_cfg_raw "$1" "$2" "{
  \"task\": \"$2\",
  \"mode\": \"C\",
  \"base_branch\": $3,
  \"budget\": { \"max_attempts\": 2 }
}"
}

# ⚠️ config を足したら commit する —— ★ さもないと `loop-spawn.sh` の dirty-tree 判定に当たる。
#   ★ pathspec を `.steering` に限っているので、repo 全体を無条件に stage しているのではない。
commit_cfgs() { ( cd "$1" && git add -A -- .steering && git commit -q -m cfg ) >/dev/null 2>&1; }
reset_cfgs()  { ( cd "$1" && rm -rf .steering && git add -A -- .steering && git commit -q -m nocfg ) >/dev/null 2>&1; }

SOUT=""; SERR=""; SRC=0; SPAWN_ENV=""
do_spawn_x() { # do_spawn_x <repo-dir> <args...>   ★ 環境は SPAWN_ENV="K=V ..." で渡す
  local r="$1"; shift
  # ⚠️ `$SPAWN_ENV` は意図して非引用 (★ 語分割させて env に渡す)。本検査の値に空白は無い。
  # shellcheck disable=SC2086
  SOUT="$( (cd "$r" && env ${SPAWN_ENV} bash scripts/loop-spawn.sh "$@") 2>"${TMP}/serr.txt" )"
  SRC=$?
  SERR="$(cat "${TMP}/serr.txt" 2>/dev/null || true)"
}

tip_of()  { ( cd "$1" && git rev-parse --verify --quiet "refs/heads/$2" ) 2>/dev/null; }
wt_head() { ( cd "$1" && git rev-parse HEAD ) 2>/dev/null; }

# ★ 「id <id> の worktree が branch <b> の先端から切られたか」
cut_from() { # cut_from <repo-dir> <wt-root> <id> <short> <branch>
  local r="$1" wtroot="$2" id="$3" short="$4" b="$5" wt
  wt="${wtroot}/repo-${id}-${short}"
  [ -d "$wt" ] || return 1
  [ "$(wt_head "$wt")" = "$(tip_of "$r" "$b")" ]
}

R7="${TMP}/r7/repo"; mkdir -p "${R7}"
if ! setup_fake_repo "${R7}" || ! make_branch "${R7}" pinned-a || ! make_branch "${R7}" pinned-b; then
  ng "群 7: 一時 git repo を用意できなかった (★ 判定できない)"
else
  MAIN_TIP="$(tip_of "${R7}" main)"

  # --- 7a: config 0 件 + --task なし → 従来どおり main ---
  SPAWN_ENV=""; do_spawn_x "${R7}" --no-exec 7a t
  if [ "${SRC}" -eq 0 ] && cut_from "${R7}" "${TMP}/r7/wt" 7a t main; then
    ok "7a: config 0 件なら従来どおり既定 (main) から切る"
  else
    ng "7a: rc=${SRC} / worktree が main から切られていない"
  fi

  # --- 7b: config 1 件 + --task なし → ⚠️★★★ 止まる (本丸) ---
  add_cfg "${R7}" 20260101-zzz-task '"pinned-a"' && commit_cfgs "${R7}"
  SPAWN_ENV=""; do_spawn_x "${R7}" --no-exec 7b t
  if [ "${SRC}" -ne 0 ] \
     && has_text "${SERR}" "20260101-zzz-task" \
     && has_text "${SERR}" "--task" \
     && has_text "${SERR}" "LOOP_BASE_BRANCH" \
     && ! wt_has "${R7}" "repo-7b-t"; then
    ok "7b: ★★★ config 1 件でも --task 無しなら止まり、候補と逃がし口を出した"
  else
    ng "7b: rc=${SRC} / 候補=$(has_text "${SERR}" "20260101-zzz-task" && echo yes || echo no) / worktree 残=$(wt_has "${R7}" "repo-7b-t" && echo yes || echo no)"
  fi

  # --- 7c: config 2 件 + --task なし → 止まり、両方を挙げる ---
  add_cfg "${R7}" 20260101-aaa-task '"pinned-b"' && commit_cfgs "${R7}"
  SPAWN_ENV=""; do_spawn_x "${R7}" --no-exec 7c t
  if [ "${SRC}" -ne 0 ] && has_text "${SERR}" "20260101-zzz-task" && has_text "${SERR}" "20260101-aaa-task"; then
    ok "7c: config 2 件なら止まり、候補を 2 件とも挙げた"
  else
    ng "7c: rc=${SRC} / 候補の列挙が不足"
  fi

  # --- 7d: --task で「tail -1 が選ぶ方ではない」方を選べる ---
  # ⚠️ zzz が名前順で最後 (= 旧実装が拾う方) で pinned-a。aaa を指定して pinned-b を取る。
  SPAWN_ENV=""; do_spawn_x "${R7}" --no-exec --task 20260101-aaa-task 7d t
  if [ "${SRC}" -eq 0 ] && cut_from "${R7}" "${TMP}/r7/wt" 7d t pinned-b; then
    ok "7d: ★ --task が tail -1 とは別の config を選び、その base から切った"
  else
    ng "7d: rc=${SRC} / pinned-b から切られていない (⚠️ tail -1 に退行?)"
  fi

  # --- 7e: LOOP_TASK (env) でも選べる ---
  SPAWN_ENV="LOOP_TASK=20260101-aaa-task"; do_spawn_x "${R7}" --no-exec 7e t
  if [ "${SRC}" -eq 0 ] && cut_from "${R7}" "${TMP}/r7/wt" 7e t pinned-b; then
    ok "7e: LOOP_TASK (env) でも task を選べる"
  else
    ng "7e: rc=${SRC} / pinned-b から切られていない"
  fi

  # --- 7f: --task が LOOP_TASK に勝つ ---
  SPAWN_ENV="LOOP_TASK=20260101-zzz-task"; do_spawn_x "${R7}" --no-exec --task 20260101-aaa-task 7f t
  if [ "${SRC}" -eq 0 ] && cut_from "${R7}" "${TMP}/r7/wt" 7f t pinned-b; then
    ok "7f: --task が LOOP_TASK より優先される"
  else
    ng "7f: rc=${SRC} / --task が勝っていない"
  fi

  # --- 7g: 日付接頭辞を落とした素名でも当たる ---
  SPAWN_ENV=""; do_spawn_x "${R7}" --no-exec --task aaa-task 7g t
  if [ "${SRC}" -eq 0 ] && cut_from "${R7}" "${TMP}/r7/wt" 7g t pinned-b; then
    ok "7g: 素名 (日付接頭辞なし) でも task を引ける"
  else
    ng "7g: rc=${SRC} / 素名で引けていない"
  fi

  # --- 7h: 存在しない task → 止まる ---
  SPAWN_ENV=""; do_spawn_x "${R7}" --no-exec --task no-such-task 7h t
  if [ "${SRC}" -ne 0 ] && ! wt_has "${R7}" "repo-7h-t"; then
    ok "7h: 存在しない --task で止まった"
  else
    ng "7h: rc=${SRC} / 存在しない task で進んだ"
  fi

  # --- 7j: LOOP_BASE_BRANCH は config を読まずに勝つ ---
  SPAWN_ENV="LOOP_BASE_BRANCH=pinned-a"; do_spawn_x "${R7}" --no-exec 7j t
  if [ "${SRC}" -eq 0 ] && cut_from "${R7}" "${TMP}/r7/wt" 7j t pinned-a; then
    ok "7j: LOOP_BASE_BRANCH が config を読まずに最優先で効く"
  else
    ng "7j: rc=${SRC} / pinned-a から切られていない"
  fi

  # --- 7s / 7t: provenance と乖離 (stderr) / stdout 契約 ---
  SPAWN_ENV=""; do_spawn_x "${R7}" --no-exec --task 20260101-zzz-task 7s t
  if [ "${SRC}" -eq 0 ] \
     && has_text "${SERR}" "provenance" \
     && has_text "${SERR}" "コミット後ろ" \
     && has_text "${SERR}" "20260101-zzz-task"; then
    ok "7s: 解決した base の provenance と既定からの乖離を stderr に出した"
  else
    ng "7s: rc=${SRC} / provenance/乖離 が stderr に出ていない"
  fi
  s_last="$(printf '%s\n' "${SOUT}" | tail -1)"
  if [ -n "${s_last}" ] && [ -d "${s_last}" ]; then
    ok "7t: ★ stdout の最終行が worktree の絶対パスのまま (--no-exec の契約)"
  else
    ng "7t: ⚠️★★★ stdout 契約が壊れた (最終行=[${s_last}]) —— loop-run.sh が worktree を掴めない"
  fi
fi

# --- 7i: --task が 2 つの dir に一致 → 止まる ---
R7I="${TMP}/r7i/repo"; mkdir -p "${R7I}"
if ! setup_fake_repo "${R7I}"; then
  ng "7i: 準備できなかった (★ 判定できない)"
else
  add_cfg "${R7I}" 20260101-dup 'null'
  add_cfg "${R7I}" 20260202-dup 'null'
  commit_cfgs "${R7I}"
  SPAWN_ENV=""; do_spawn_x "${R7I}" --no-exec --task dup 7i t
  if [ "${SRC}" -ne 0 ] && has_text "${SERR}" "20260101-dup" && has_text "${SERR}" "20260202-dup"; then
    ok "7i: 素名が 2 件に一致したら止まり、両方を挙げた"
  else
    ng "7i: rc=${SRC} / 曖昧な --task で進んだ or 候補が出ない"
  fi
fi

# --- 7k: ⚠️★★★ 1 行に 3 キーが同居した config (★ 既存テストと同じ形) ---
# ⚠️ **pinned-a に pin する** —— ★ main 以外にしないと、行頭アンカーへ退行しても
#   fallback の main と偶然一致し、**この検査が何も見ないことになる** (→ 群 8b が対照)。
R7K="${TMP}/r7k/repo"; mkdir -p "${R7K}"
if ! setup_fake_repo "${R7K}" || ! make_branch "${R7K}" pinned-a; then
  ng "7k: 準備できなかった (★ 判定できない)"
else
  add_cfg_raw "${R7K}" 20260101-oneline '{
  "task": "oneline", "mode": "C", "base_branch": "pinned-a",
  "budget": { "max_attempts": 2 }
}'
  commit_cfgs "${R7K}"
  SPAWN_ENV=""; do_spawn_x "${R7K}" --no-exec --task 20260101-oneline 7k t
  if [ "${SRC}" -eq 0 ] && cut_from "${R7K}" "${TMP}/r7k/wt" 7k t pinned-a; then
    ok "7k: ★★★ 1 行に複数キーが同居した config でも base_branch が効く (行頭アンカー禁止)"
  else
    ng "7k: rc=${SRC} / pinned-a から切られていない (⚠️ 行頭アンカーに退行?)"
  fi
fi

# --- 7l / 7m: null / キー無し → die せず fallback ---
R7L="${TMP}/r7l/repo"; mkdir -p "${R7L}"
if ! setup_fake_repo "${R7L}"; then
  ng "7l/7m: 準備できなかった (★ 判定できない)"
else
  add_cfg "${R7L}" 20260101-nullbase 'null' && commit_cfgs "${R7L}"
  SPAWN_ENV=""; do_spawn_x "${R7L}" --no-exec --task 20260101-nullbase 7l t
  if [ "${SRC}" -eq 0 ] && cut_from "${R7L}" "${TMP}/r7l/wt" 7l t main; then
    ok "7l: base_branch が null なら fallback (main) へ落ちる"
  else
    ng "7l: rc=${SRC} / null で main へ落ちていない"
  fi

  reset_cfgs "${R7L}"
  add_cfg_raw "${R7L}" 20260101-nokey '{
  "task": "nokey",
  "mode": "C",
  "budget": { "max_attempts": 2 }
}'
  commit_cfgs "${R7L}"
  SPAWN_ENV=""; do_spawn_x "${R7L}" --no-exec --task 20260101-nokey 7m t
  if [ "${SRC}" -eq 0 ] && cut_from "${R7L}" "${TMP}/r7l/wt" 7m t main; then
    ok "7m: base_branch キーが無ければ fallback (⚠️ die しない)"
  else
    ng "7m: rc=${SRC} / キー無しで止まった or main へ落ちていない"
  fi
fi

# --- 7n..7r: ⚠️ 読めない / 不正な値 / 存在しない枝 → 止まる (★ 黙って main へ落ちない) ---
echo "7n-7r. ⚠️★★★ 読めない値・不正な値・存在しない枝で **黙って main へ落ちない**か"
i=0
for spec in \
  '7n|123|数値' \
  '7o|DUPKEY|base_branch が 2 回' \
  '7p|"-foo"|先頭が - (オプション混入)' \
  '7q|"a b"|空白入り' \
  '7r|"no-such-branch"|存在しないブランチ'
do
  i=$((i + 1))
  cid="${spec%%|*}"; rest="${spec#*|}"; val="${rest%%|*}"; label="${rest#*|}"
  RX="${TMP}/rx${i}/repo"; mkdir -p "${RX}"
  if ! setup_fake_repo "${RX}"; then
    ng "${cid}: 準備できなかった (★ 判定できない)"
    continue
  fi
  if [ "${val}" = "DUPKEY" ]; then
    add_cfg_raw "${RX}" 20260101-bad '{
  "task": "bad",
  "base_branch": "main",
  "headless": { "base_branch": "other" }
}'
  else
    add_cfg "${RX}" 20260101-bad "${val}"
  fi
  commit_cfgs "${RX}"
  SPAWN_ENV=""; do_spawn_x "${RX}" --no-exec --task 20260101-bad "${cid}" t
  if [ "${SRC}" -ne 0 ] && ! wt_has "${RX}" "repo-${cid}-t"; then
    ok "${cid}: ${label} → 非 0 で止まり worktree を作らなかった"
  else
    ng "${cid}: ${label} → rc=${SRC} / worktree 残=$(wt_has "${RX}" "repo-${cid}-t" && echo yes || echo no) (⚠️ 黙って進んだ)"
  fi
done

# ── 8. 変異テスト (★ 群 7 が空振りしていないこと) ────────
echo "8. ⚠️★★★ 変異テスト —— fail-closed / 抽出器を潰したら赤くなるか"

# --- 8a: fail-closed を殺す (--task 無しの die を素通りさせる) ---
MUT8A="${TMP}/mut8a-loop-spawn.sh"
sed 's/elif \[ "\${n_cfg:-0}" -gt 0 \]; then/elif false; then/' "${SPAWN_SH}" > "${MUT8A}"
# ⚠️★★★ **`|| echo 0` を使わない。**
#   ★ `grep -c` は **0 件でも "0" を出力しつつ exit 1** するので、`|| echo 0` を付けると
#     **"0" が 2 行**出る。⚠️ すると `[` が integer expression エラーを出し、
#     ★★★ **`if` が偽になってガードが素通りする** (＝ 変異が当たっていなくても
#     「検査不能」と報告せずに本体へ進む ＝ **検査が空振りしていることに気づけない**)。
#   ★ 群 6 の `mut_left` と同じ形 (`... 2>/dev/null)" || var=0`) に揃える。
#   ⚠️ 2026-09-21 に実測で踏んだ: 当て先の書き方を変える実験をしたら
#     `[: missing ']'` を出して **NG の理由を間違えた**。
#   ★★★ **両側で数える** —— ⚠️★★★ 「元の形が消えた」だけでは
#     **「sed が置換した」と「そもそも存在しなかった」を区別できない**。
#     ★ 2026-09-21 に実測: 当て先の書き方を変えたところ、ガードは「成功」と見なして
#     本体へ進み、⚠️ **NG の理由を間違えた**（「潰しても止まった」と報告した）。
#   → ★ 元は **SPAWN_SH に 1 件あり**、**MUT で 0 件になっている**ことを両方確かめる。
mut8a_src="$(grep -c 'elif \[ "\${n_cfg:-0}" -gt 0 \]; then' "${SPAWN_SH}" 2>/dev/null)" || mut8a_src=0
mut8a_left="$(grep -c 'elif \[ "\${n_cfg:-0}" -gt 0 \]; then' "${MUT8A}" 2>/dev/null)" || mut8a_left=0
if [ "${mut8a_src:-0}" -ne 1 ] || [ "${mut8a_left:-0}" -ne 0 ]; then
  ng "8a: 変異を当てられない (src=${mut8a_src} / mut=${mut8a_left}) —— ★ fail-closed の書き方が変わった → ⚠️ **検査不能**。sed を直せ"
else
  R8A="${TMP}/r8a/repo"; mkdir -p "${R8A}"
  if ! setup_fake_repo "${R8A}" "${MUT8A}"; then
    ng "8a: 準備できなかった (★ 判定できない)"
  else
    add_cfg "${R8A}" 20260101-zzz-task '"main"' && commit_cfgs "${R8A}"
    SPAWN_ENV=""; do_spawn_x "${R8A}" --no-exec 8a t
    if [ "${SRC}" -eq 0 ]; then
      ok "8a: fail-closed を潰すと --task 無しで通ってしまった (★ 7b は空振りしていない)"
    else
      ng "8a: 潰しても止まった (⚠️★★★ 7b は fail-closed を見ていない可能性)"
    fi
  fi
fi

# --- 8b: 抽出器を行頭アンカーへ退行させる ---
# ⚠️★★★ **これが最も重要である** —— ★ 7k だけでは「fake repo の既定が偶然 main」で
#   緑のまま通る恐れがある。★ 8b が赤くならなければ 7k は何も見ていない。
MUT8B="${TMP}/mut8b-loop-spawn.sh"
sed 's/anchor = ""/anchor = "^"/' "${SPAWN_SH}" > "${MUT8B}"
# ⚠️ 変異後の形を数えない —— ★ `loop-spawn.sh` の**注記に逐語で** `anchor = "^"` が入っているので
#   2 件数えてしまう。★ 群 6 と同じく「**元の形が消えたか**」で判定する。
mut8b_src="$(grep -c 'anchor = ""' "${SPAWN_SH}" 2>/dev/null)" || mut8b_src=0
mut8b_left="$(grep -c 'anchor = ""' "${MUT8B}" 2>/dev/null)" || mut8b_left=0
if [ "${mut8b_src:-0}" -ne 1 ] || [ "${mut8b_left:-0}" -ne 0 ]; then
  # ⚠️ メッセージにバッククォートを入れない —— ★ 二重引用符の中では **コマンド置換**として
  #   実行される (2026-09-21 に実測: `anchor: command not found` を出し、語が消えた)。
  ng "8b: 変異を当てられない (src=${mut8b_src} / mut=${mut8b_left}) —— ★ 抽出器の注入点 [anchor = \"\"] が変わった → ⚠️ **検査不能**。sed を直せ"
else
  R8B="${TMP}/r8b/repo"; mkdir -p "${R8B}"
  if ! setup_fake_repo "${R8B}" "${MUT8B}" || ! make_branch "${R8B}" pinned-a; then
    ng "8b: 準備できなかった (★ 判定できない)"
  else
    add_cfg_raw "${R8B}" 20260101-oneline '{
  "task": "oneline", "mode": "C", "base_branch": "pinned-a",
  "budget": { "max_attempts": 2 }
}'
    commit_cfgs "${R8B}"
    SPAWN_ENV=""; do_spawn_x "${R8B}" --no-exec --task 20260101-oneline 8b t
    if cut_from "${R8B}" "${TMP}/r8b/wt" 8b t main; then
      ok "8b: ★★★ 行頭アンカーへ退行させると pin を取り逃がし main へ落ちた (★ 7k は空振りしていない)"
    else
      ng "8b: 退行させても pinned-a から切れた (⚠️★★★ 7k は行頭アンカーの穴を見ていない)"
    fi
  fi
fi

echo "════════════════════════════════════════"
echo "PASS=${PASS}  FAIL=${FAIL}"
FINISHED=1
[ "${FAIL}" -eq 0 ] || exit 1
exit 0
