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
#   8. ⚠️★★★ 変異テスト (★ **群 7 が** 空振りしていないこと)
#      8a fail-closed を潰す / 8b 抽出器の**深さ 1 だけ**規則を潰す / 8c `valid_refname` を潰す
#
# ⚠️★★★ **7k には変異対照が無い** (★ 2026-09-21 の書き直し後) ——
#   ★ 抽出器を文字ステートマシンへ書き直した結果、**行の位置に依存しなくなった**ので、
#   「1 行同居を取り逸す」形を sed で作れない。★ 7k は **行ベースへ戻したときに
#   捕まえるための構造的な回帰テスト**として残してある（⚠️ 「対照がある」とは書かない）。
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
  # ⚠️ ブランチ名に `/` が入る形 (`RELEASE/2026-09`) を渡されるので、
  #   ★ マーカーのファイル名は平坦化する。
  #   ⚠️ さもなければ存在しないディレクトリへの書き込みになり、
  #   **「準備できなかった」で群がまるごと飛ぶ** (2026-09-21 に実測)。
  local mk
  mk="marker-$(printf '%s' "$2" | tr '/' '_')"
  ( cd "$1" && git switch -q -c "$2" \
    && printf 'x
' > "${mk}" && git add "${mk}" \
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
  # ⚠️★★★ **「コミット後ろ」だけで見ない** (★ `code-reviewer` MEDIUM・2026-09-21) ——
  #   ★ その語は「0 コミット後ろ」にも一致するので、**警告経路を検査できない**。
  #   ⚠️ fake repo の構成を少し変えると乖離が 0 になり、★★★ **起票 23 の 2 つ目の視点が
  #   黙って無検査になる**。→ ★ 警告の印まで固定し、乖離 0 の陰性対照を置く。
  if [ "${SRC}" -eq 0 ] \
     && has_text "${SERR}" "provenance" \
     && has_text "${SERR}" "⚠️★★★ 乖離" \
     && has_text "${SERR}" "コミット後ろ" \
     && has_text "${SERR}" "20260101-zzz-task"; then
    ok "7s: provenance と ★★★付きの乖離警告を stderr に出した"
  else
    ng "7s: rc=${SRC} / provenance または ★★★付きの乖離警告が stderr に出ていない"
  fi
  s_last_7s="$(printf '%s\n' "${SOUT}" | tail -1)"
  # ★ 陰性対照: 乖離が無いときは ★★★警告を出さない
  #   (⚠️ 常に出ていたら上の 7s は何も見ていない)
  SPAWN_ENV="LOOP_BASE_BRANCH=main"; do_spawn_x "${R7}" --no-exec 7s2 t
  if [ "${SRC}" -eq 0 ] && ! has_text "${SERR}" "⚠️★★★ 乖離"; then
    ok "7s の陰性対照: 乖離が無いときは ★★★警告を出さない"
  else
    ng "7s の陰性対照: rc=${SRC} —— ⚠️ 乖離が無いのに警告が出た (★ 上の 7s が何も見ていない)"
  fi
  if [ -n "${s_last_7s}" ] && [ -d "${s_last_7s}" ]; then
    ok "7t: ★ stdout の最終行が worktree の絶対パスのまま (--no-exec の契約)"
  else
    ng "7t: ⚠️★★★ stdout 契約が壊れた (最終行=[${s_last_7s}]) —— loop-run.sh が worktree を掴めない"
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

# --- 7n..7ab: ⚠️ 読めない / 不正な値 / 危険な参照 → 止まる (★ 黙って main へ落ちない) ---
# ⚠️★★★ **期待する stderr の語まで見る。**
#   ★ `code-reviewer` MEDIUM・2026-09-21: 旧 7p / 7q は「非 0 なら緑」だったので、
#     `valid_refname` を外しても **後段の `git fetch` / `worktree add` が落ちて緑のまま通った**
#     (＝ 依頼文が警告した「偶然一致で緑」型)。→ ★ **どの関門で止まったか**を語で固定する。
echo "7n-7ab. ⚠️★★★ 読めない値・不正な値・危険な参照で **黙って main へ落ちない**か"
i=0
for spec in \
  '7n|VAL:123|数値|値を読めません' \
  '7o|RAW_NESTED_BOTH|深さ 1 と入れ子の両方|深さ 1 (トップレベル) 以外' \
  '7p|VAL:"-foo"|先頭が - (オプション混入)|ブランチ名として妥当ではありません' \
  '7q|VAL:"a b"|空白入り|ブランチ名として妥当ではありません' \
  '7r|VAL:"no-such-branch"|存在しないブランチ|' \
  '7u|RAW_NESTED_ONLY|⚠️★★★ 入れ子のみ (両系統 HIGH)|深さ 1 (トップレベル) 以外' \
  '7v|RAW_BROKEN|壊れた JSON (書き込み途中)|JSON が壊れています' \
  '7w|VAL:""|空文字列 (= 打ち間違い)|空文字列です' \
  '7x|RAW_DUP_TOP|深さ 1 に 2 回|2 回出てきます' \
  '7z|VAL:"FETCH_HEAD"|予約名 FETCH_HEAD|ブランチ名として妥当ではありません' \
  '7aa|VAL:"0123456789012345678901234567890123456789"|40 桁 hex (= commit sha)|ブランチ名として妥当ではありません' \
  '7ab|VAL:"refs/heads/main"|refs/ 始まり|ブランチ名として妥当ではありません'
do
  i=$((i + 1))
  cid="${spec%%|*}"; rest="${spec#*|}"; val="${rest%%|*}"
  rest="${rest#*|}"; label="${rest%%|*}"; want="${rest#*|}"
  RX="${TMP}/rx${i}/repo"; mkdir -p "${RX}"
  if ! setup_fake_repo "${RX}"; then
    ng "${cid}: 準備できなかった (★ 判定できない)"
    continue
  fi
  case "${val}" in
    RAW_NESTED_BOTH)
      add_cfg_raw "${RX}" 20260101-bad '{
  "task": "bad",
  "base_branch": "main",
  "headless": { "base_branch": "other" }
}' ;;
    RAW_NESTED_ONLY)
      # ⚠️★★★ 両系統が HIGH で挙げた形 —— ★ template に `headless` が実在するので、
      #   base_branch をその中に書き間違えるだけで踏める。
      add_cfg_raw "${RX}" 20260101-bad '{
  "task": "bad",
  "headless": { "base_branch": "sneaky" }
}' ;;
    RAW_BROKEN)  mkdir -p "${RX}/.steering/20260101-bad"
                 printf '%s' '{"task": "bad", "base_bra' > "${RX}/.steering/20260101-bad/_loop-config.json" ;;
    RAW_DUP_TOP) add_cfg_raw "${RX}" 20260101-bad '{
  "task": "bad",
  "base_branch": "main",
  "base_branch": "other"
}' ;;
    VAL:*)       add_cfg "${RX}" 20260101-bad "${val#VAL:}" ;;
  esac
  commit_cfgs "${RX}"
  SPAWN_ENV=""; do_spawn_x "${RX}" --no-exec --task 20260101-bad "${cid}" t
  if [ "${SRC}" -eq 0 ] || wt_has "${RX}" "repo-${cid}-t"; then
    ng "${cid}: ${label} → rc=${SRC} / worktree 残=$(wt_has "${RX}" "repo-${cid}-t" && echo yes || echo no) (⚠️ 黙って進んだ)"
  elif [ -n "${want}" ] && ! has_text "${SERR}" "${want}"; then
    # ⚠️ 非 0 ではあるが **別の理由**で落ちている (★ 意図した関門を通っていない)
    ng "${cid}: ${label} → 非 0 だが期待した語が出ていない (欲しい語=[${want}])"
  else
    ok "${cid}: ${label} → 非 0 で止まり worktree を作らなかった${want:+ (★ 関門を語で確認)}"
  fi
done

# --- 7y: ⚠️ config でない既存ファイルを --task に渡す (★ security-checker MEDIUM) ---
R7Y="${TMP}/r7y/repo"; mkdir -p "${R7Y}"
if ! setup_fake_repo "${R7Y}"; then
  ng "7y: 準備できなかった (★ 判定できない)"
else
  add_cfg "${R7Y}" 20260101-ok 'null'
  printf 'not a config\n' > "${R7Y}/.steering/20260101-ok/requirement.md"
  commit_cfgs "${R7Y}"
  SPAWN_ENV=""; do_spawn_x "${R7Y}" --no-exec --task .steering/20260101-ok/requirement.md 7y t
  if [ "${SRC}" -ne 0 ] && has_text "${SERR}" "_loop-config.json を指定してください" \
     && ! wt_has "${R7Y}" "repo-7y-t"; then
    ok "7y: config でないファイルを --task に渡すと止まる (⚠️ キー 0 件で黙って main へ落ちない)"
  else
    ng "7y: rc=${SRC} —— ⚠️ 任意のファイルを config として受けている"
  fi
fi

# --- 7ac: ⚠️★★★ config の制御バイトが provenance を汚さない (★ security-checker MEDIUM) ---
# ⚠️ 生で出すと `\x1b[8m` (conceal) や `\r` で **この後に続く乖離の警告行を隠せる**。
R7AC="${TMP}/r7ac/repo"; mkdir -p "${R7AC}"
if ! setup_fake_repo "${R7AC}" || ! make_branch "${R7AC}" pinned-a; then
  ng "7ac: 準備できなかった (★ 判定できない)"
else
  mkdir -p "${R7AC}/.steering/20260101-esc"
  printf '{\n  "task": "t\033[8m EVIL",\n  "base_branch": "pinned-a"\n}\n' \
    > "${R7AC}/.steering/20260101-esc/_loop-config.json"
  commit_cfgs "${R7AC}"
  SPAWN_ENV=""; do_spawn_x "${R7AC}" --no-exec --task 20260101-esc 7ac t
  esc_left="$(printf '%s' "${SERR}" | LC_ALL=C tr -dc '\033' | wc -c)"
  esc_left="${esc_left//[[:space:]]/}"
  if [ "${SRC}" -eq 0 ] && [ "${esc_left:-1}" -eq 0 ] && has_text "${SERR}" "EVIL"; then
    ok "7ac: ★★★ config の ESC バイトを落として出した (⚠️ 乖離の警告行を隠せない)"
  else
    ng "7ac: rc=${SRC} / 残った ESC=${esc_left} —— ⚠️★★★ 端末エスケープで警告を隠せる"
  fi
fi

# --- 7x2: ⚠️ 素名の日付接頭辞が「数字 8 桁」に限られているか (★ code-reviewer MEDIUM) ---
# ⚠️ 旧実装の `${bn#????????-}` は **任意の 8 文字**を剥がしたので、
#   `fix-loop-spawn` が `--task spawn` に当たった (★ 誤った base に pin)。
R7X="${TMP}/r7x/repo"; mkdir -p "${R7X}"
if ! setup_fake_repo "${R7X}"; then
  ng "7x2: 準備できなかった (★ 判定できない)"
else
  add_cfg "${R7X}" fix-loop-spawn 'null'
  commit_cfgs "${R7X}"
  SPAWN_ENV=""; do_spawn_x "${R7X}" --no-exec --task spawn 7x2 t
  if [ "${SRC}" -ne 0 ] && ! wt_has "${R7X}" "repo-7x2-t"; then
    ok "7x2: 日付でない 8 文字＋- を素名として剥がさない (⚠️ fix-loop-spawn が spawn に当たらない)"
  else
    ng "7x2: rc=${SRC} —— ⚠️ 任意の 8 文字を日付として剥がしている"
  fi
  # ★ 陽性対照: 同じ dir 名は basename でちゃんと引ける
  SPAWN_ENV=""; do_spawn_x "${R7X}" --no-exec --task fix-loop-spawn 7x3 t
  if [ "${SRC}" -eq 0 ] && cut_from "${R7X}" "${TMP}/r7x/wt" 7x3 t main; then
    ok "7x2 の陽性対照: basename 完全一致なら日付が無くても引ける"
  else
    ng "7x2 の陽性対照: rc=${SRC} —— ⚠️ 日付の無い task dir を引けなくなった"
  fi
fi
# --- 7ad-7af: ⚠️ Codex `/cross-review` 1 巡目が「薄い」と指摘した経路 ---
echo "7ad-7af. ⚠️ LOOP_BASE_BRANCH の不正値 / 大文字ブランチの過剰拒否 / 制御文字入り selector"

R7Z="${TMP}/r7z/repo"; mkdir -p "${R7Z}"
if ! setup_fake_repo "${R7Z}" || ! make_branch "${R7Z}" RELEASE/2026-09; then
  ng "7ad-7af: 準備できなかった (★ 判定できない)"
else
  # --- 7ad: LOOP_BASE_BRANCH の不正値も検証されるか ---
  # ⚠️ env 経路は config を読まずに即 return するので、**検証が別経路**になっている。
  SPAWN_ENV="LOOP_BASE_BRANCH=--upload-pack=echo"; do_spawn_x "${R7Z}" --no-exec 7ad t
  # ⚠️★★★ **「LOOP_BASE_BRANCH」の語で見てはならない** —— ★ 2026-09-21 に実測:
  #   provenance 行が `provenance = env:LOOP_BASE_BRANCH` を出すので、
  #   ⚠️ **検証を外しても語が一致し、`git worktree add` が落ちて非 0 になり、
  #   ★★★ 緑のまま通っていた** (★ 本タスクで狩ってきた「偶然一致で緑」型そのもの)。
  #   → ★ **関門の die メッセージで固定する。**
  if [ "${SRC}" -ne 0 ]      && has_text "${SERR}" "LOOP_BASE_BRANCH の値がブランチ名として妥当ではありません"      && ! wt_has "${R7Z}" "repo-7ad-t"; then
    ok "7ad: LOOP_BASE_BRANCH の不正値を **env 経路の関門**で止めた (★ 語で確認)"
  else
    ng "7ad: rc=${SRC} —— ⚠️ env 経路の関門を通っていない (★ --upload-pack= は git fetch が受理する)"
  fi

  # --- 7ae: ⚠️★★★ 大文字ブランチを **過剰に拒否していない**か (★ 過剰拒否の陰性対照) ---
  # ⚠️ 2026-09-21 の実測: 「先頭コンポーネントが全部大文字なら拒否」にしていたため
  #   `RELEASE/2026-09` / `FEATURE/foo` / `HOTFIX/x` まで**誤って拒否**していた。
  #   → ★ pseudo-ref は `HEAD` / `*_HEAD` / `AUTO_MERGE` だけなので、そこだけ拒む。
  add_cfg "${R7Z}" 20260101-upper '"RELEASE/2026-09"'
  commit_cfgs "${R7Z}"
  SPAWN_ENV=""; do_spawn_x "${R7Z}" --no-exec --task 20260101-upper 7ae t
  if [ "${SRC}" -eq 0 ] && cut_from "${R7Z}" "${TMP}/r7z/wt" 7ae t "RELEASE/2026-09"; then
    ok "7ae: ★★★ 大文字の運用ブランチ (RELEASE/2026-09) を過剰に拒否していない"
  else
    ng "7ae: rc=${SRC} —— ⚠️★★★ 正当な大文字ブランチを拒否している (★ 予約名の規則が広すぎる)"
  fi

  # --- 7af: 制御文字・CRLF 入りの --task を渡す ---
  SPAWN_ENV=""; do_spawn_x "${R7Z}" --no-exec --task "$(printf '20260101-upper\r')" 7af t
  if [ "${SRC}" -ne 0 ] && ! wt_has "${R7Z}" "repo-7af-t"; then
    ok "7af: 制御文字入りの --task は一致せず止まる"
  else
    ng "7af: rc=${SRC} —— ⚠️ CR 付きの selector が通った"
  fi
fi

# --- 7ag: ✖ **削除した** (2026-09-21・Codex `/cross-review` 2 巡目) ---
# ⚠️★★★ **完全な空振りだったので消した。「緑だが何も見ていないテスト」は残さない。**
#   ★ 理由: `loop-run.sh:756` は `--dry-run` のとき **`run_issue` に到達しない**ので、
#     一時ファイルを数えても **spawn の経路を 1 行も通っていなかった**。
#   ⚠️ かつコメントには「(a) run が止まる (b) 一時ファイルが残らない」と書いていたが、
#     **(a) は一切検査していなかった**（`ag_rc` も `r7ag.out` も未使用）。
#   ★ 代わりに何が守っているか:
#     - モードC の配線（`--task` を渡すこと）は **`loop-worktree-deny-test.sh` と
#       `loop-run-guard-test.sh` が stub 付きで本番の `loop-run.sh` を回して守っている**。
#       ★ 実測の陰性対照: `--task` を外すと **34/0 → 30/4** と **35/0 → 19/16** になる。
#     - `trap ... RETURN` が bash で発火することは **別途 2026-09-21 に直接実測**している。
#   ⚠️ ここで stub ハーネスを組み直すのは `loop-run-guard-test.sh` の重複になるのでしない。

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

# --- 8b: 抽出器の「深さ 1 だけ」規則を殺す ---
# ⚠️★★★ **両系統 (code-reviewer / security-checker) が HIGH で挙げた穴の対照である。**
#   ★ 殺すと入れ子の同名キーを深さ 1 として数えるので、
#   `{"headless":{"base_branch":"sneaky"}}` が **正当な pin として採られる**。
#   ⚠️ template には `headless` が実在するので、書き間違えるだけで踏める形である。
MUT8B="${TMP}/mut8b-loop-spawn.sh"
sed 's/if (depth != 1) { i = k + 1; continue }/if (0) { i = k + 1; continue }/' "${SPAWN_SH}" > "${MUT8B}"
mut8b_src="$(grep -c 'if (depth != 1) { i = k + 1; continue }' "${SPAWN_SH}" 2>/dev/null)" || mut8b_src=0
mut8b_left="$(grep -c 'if (depth != 1) { i = k + 1; continue }' "${MUT8B}" 2>/dev/null)" || mut8b_left=0
if [ "${mut8b_src:-0}" -ne 1 ] || [ "${mut8b_left:-0}" -ne 0 ]; then
  ng "8b: 変異を当てられない (src=${mut8b_src} / mut=${mut8b_left}) —— ★ 深さ規則の書き方が変わった → ⚠️ **検査不能**。sed を直せ"
else
  R8B="${TMP}/r8b/repo"; mkdir -p "${R8B}"
  if ! setup_fake_repo "${R8B}" "${MUT8B}" || ! make_branch "${R8B}" sneaky; then
    ng "8b: 準備できなかった (★ 判定できない)"
  else
    add_cfg_raw "${R8B}" 20260101-nested '{
  "task": "nested",
  "headless": { "base_branch": "sneaky" }
}'
    commit_cfgs "${R8B}"
    SPAWN_ENV=""; do_spawn_x "${R8B}" --no-exec --task 20260101-nested 8b t
    if [ "${SRC}" -eq 0 ] && cut_from "${R8B}" "${TMP}/r8b/wt" 8b t sneaky; then
      ok "8b: ★★★ 深さ規則を潰すと入れ子の base_branch が採られた (★ 7u は空振りしていない)"
    else
      ng "8b: 潰しても入れ子が採られなかった (⚠️★★★ 7u は深さの穴を見ていない可能性)"
    fi
  fi
fi

# --- 8c: valid_refname を殺す ---
# ⚠️★★★ **7p / 7q / 7z / 7aa / 7ab の対照である。**
#   ★ `code-reviewer` MEDIUM・2026-09-21: これらは `valid_refname` を外しても
#   **後段の `git fetch` / `worktree add` が落ちて非 0 になる**ので、
#   ⚠️ 「非 0 なら緑」の判定では **関門を 1 つも検査できていなかった**。
#   → ★ 7 群側は期待する語まで固定したので、ここで「語が出なくなる」ことを確認する。
MUT8C="${TMP}/mut8c-loop-spawn.sh"
sed 's/^valid_refname() {/valid_refname() { return 0;/' "${SPAWN_SH}" > "${MUT8C}"
mut8c_src="$(grep -c '^valid_refname() {$' "${SPAWN_SH}" 2>/dev/null)" || mut8c_src=0
mut8c_left="$(grep -c '^valid_refname() {$' "${MUT8C}" 2>/dev/null)" || mut8c_left=0
if [ "${mut8c_src:-0}" -ne 1 ] || [ "${mut8c_left:-0}" -ne 0 ]; then
  ng "8c: 変異を当てられない (src=${mut8c_src} / mut=${mut8c_left}) —— ★ valid_refname の宣言が変わった → ⚠️ **検査不能**"
else
  R8C="${TMP}/r8c/repo"; mkdir -p "${R8C}"
  if ! setup_fake_repo "${R8C}" "${MUT8C}"; then
    ng "8c: 準備できなかった (★ 判定できない)"
  else
    add_cfg "${R8C}" 20260101-bad '"FETCH_HEAD"'
    commit_cfgs "${R8C}"
    SPAWN_ENV=""; do_spawn_x "${R8C}" --no-exec --task 20260101-bad 8c t
    if ! has_text "${SERR}" "ブランチ名として妥当ではありません"; then
      ok "8c: ★★★ valid_refname を潰すと関門の語が出なくなった (★ 7p/7q/7z/7aa/7ab は語で見ている)"
    else
      ng "8c: 潰しても関門の語が出た (⚠️★★★ 変異が効いていない → 検査不能)"
    fi
    # ⚠️★★★ **ここで rc を見ない。**
    #   ★ 潰しても `git worktree add ... FETCH_HEAD` が別の理由で落ちるので、
    #   「rc が 0 でも非 0 でも ok」と書くと **常に真 = それ自体が空振り**になる
    #   (★ 2026-09-21 に実際にそう書いてしまい、rc=128 で緑になっていた)。
    #   → ★ **対照は「関門の語が消えること」だけ**で成立する。
  fi
fi

# ── 9. ⚠️★★★ 起票 A: spawn 経路 (id / short) の検証 ──────
# ⚠️★★★ **何を止めるためにあるのか** (2026-09-26 の実測・design.md 起票 A):
#   ★ 旧実装は `--cleanup` 経路にしか id 検証が無く、spawn 経路 (`id="${1:?…}"` /
#     `short="${2:-issue}"`) は無検証のまま `branch=` / `wtdir=` へ直接埋め込んでいた。
#   ⚠️ 実測: id に `-x` (leading dash) や `a/b` (スラッシュ) を渡しても
#     `git worktree add -b "loop/-x-t" ...` / `git worktree add -b "loop/a/b-t" "../wt/repo-a/b-t" ...`
#     は **成功する** (git 自身は拒まない)。★ すると `--cleanup` 側は同じ id を validate_name で
#     弾くため、**spawn では作れるのに --cleanup では永久に撤去できない worktree** が生まれる。
echo "════════════════════════════════════════"
echo "9. ⚠️★★★ 起票 A: spawn 経路 (id / short) の検証 (--cleanup 専用だった検証を通す)"

R9="${TMP}/r9/repo"; mkdir -p "${R9}"
if ! setup_fake_repo "${R9}"; then
  ng "起票 A: 準備できなかった (★ 判定できない)"
else
  wt_count() { ( cd "$1" && git worktree list --porcelain 2>/dev/null | grep -c '^worktree ' ) || true; }
  br_count() { ( cd "$1" && git branch --list 'loop/*' 2>/dev/null | wc -l | tr -d '[:space:]' ); }

  base_wt="$(wt_count "${R9}")"; base_br="$(br_count "${R9}")"

  # --- 9a: id が不正なら非 0 で die し、worktree/branch を 1 件も増やさない ---
  for bad in '-x' 'a/b' 'a..b'; do
    SPAWN_ENV=""; do_spawn_x "${R9}" --no-exec "${bad}" t
    now_wt="$(wt_count "${R9}")"; now_br="$(br_count "${R9}")"
    if [ "${SRC}" -ne 0 ] && [ "${now_wt}" = "${base_wt}" ] && [ "${now_br}" = "${base_br}" ]; then
      ok "9a: id=[${bad}] は非 0 で die し worktree/branch を作らなかった"
    else
      ng "9a: id=[${bad}] rc=${SRC} / worktree ${base_wt}→${now_wt} / branch ${base_br}→${now_br}"
    fi
  done

  # --- 9b: short が不正でも同様 (id は有効値 900 を使う) ---
  for bad in '-x' 'a/b' 'a..b'; do
    SPAWN_ENV=""; do_spawn_x "${R9}" --no-exec 900 "${bad}"
    now_wt="$(wt_count "${R9}")"; now_br="$(br_count "${R9}")"
    if [ "${SRC}" -ne 0 ] && [ "${now_wt}" = "${base_wt}" ] && [ "${now_br}" = "${base_br}" ]; then
      ok "9b: short=[${bad}] は非 0 で die し worktree/branch を作らなかった"
    else
      ng "9b: short=[${bad}] rc=${SRC} / worktree ${base_wt}→${now_wt} / branch ${base_br}→${now_br}"
    fi
  done

  # --- 9m: ⚠️★★★ 変異テスト —— validate_name を no-op にすると spawn 経路が素通りするか ---
  MUT9="${TMP}/mut9-loop-spawn.sh"
  sed 's/^validate_name() {/validate_name() { return 0;/' "${SPAWN_SH}" > "${MUT9}"
  mut9_src="$(grep -c '^validate_name() {$' "${SPAWN_SH}" 2>/dev/null)" || mut9_src=0
  mut9_left="$(grep -c '^validate_name() {$' "${MUT9}" 2>/dev/null)" || mut9_left=0
  if [ "${mut9_src:-0}" -ne 1 ] || [ "${mut9_left:-0}" -ne 0 ]; then
    ng "9m: 変異を当てられない (src=${mut9_src} / mut=${mut9_left}) —— ★ validate_name の宣言が変わった → ⚠️ 検査不能"
  else
    R9M="${TMP}/r9m/repo"; mkdir -p "${R9M}"
    if ! setup_fake_repo "${R9M}" "${MUT9}"; then
      ng "9m: 準備できなかった (★ 判定できない)"
    else
      # ★ id=-x は git 自身が拒まない (実測済み) ので、潰せば通ってしまうはず。
      SPAWN_ENV=""; do_spawn_x "${R9M}" --no-exec '-x' t
      if [ "${SRC}" -eq 0 ] && wt_has "${R9M}" "repo--x-t"; then
        ok "9m: ★★★ validate_name を潰すと id=[-x] が通ってしまった (★ 9a/9b は空振りしていない)"
      else
        ng "9m: 潰しても rc=${SRC} で止まった (⚠️★★★ 9a/9b が検証したい経路を通っていない可能性)"
      fi
    fi
  fi
fi

# ── 10. ⚠️★★★ P1-J: base の祖先関係で start を決める (判断 3) ────
# ⚠️★★★ **何を止めるためにあるのか** (design.md P1-J・decisions.md 判断 3):
#   ★ 旧実装は `git fetch origin "$base"` が成功すると**無条件で** `origin/$base` を採用し、
#     ローカル `$base` が先行していても無視していた。→ push 前にローカルで merge した pin が
#     古い origin から切られる事故になる。
echo "10. ⚠️★★★ P1-J: base の祖先関係で start を決める (equal/ahead/behind/diverge/no-local/fetch 失敗)"

setup_origin_repo() { # setup_origin_repo <repo-dir> <bare-dir> [spawn-script-src]
  local r="$1" bare="$2" src="${3:-${SPAWN_SH}}"
  # ⚠️★★★ `setup_fake_repo` へ `src` を転送し忘れると、群 10g/10h の変異版
  #   (`${MUT10G}` / `${MUT10H}`) が使われず **常に無傷の loop-spawn.sh を検査してしまう**
  #   (＝ 変異テストが空振りする)。★ 2026-09-26 に実測で踏んだ。
  setup_fake_repo "${r}" "${src}" || return 1
  git init --bare -q "${bare}" >/dev/null 2>&1 || return 1
  ( cd "${r}" && git remote add origin "${bare}" && git push -q origin main ) >/dev/null 2>&1
}
make_pushed_branch() { # make_pushed_branch <repo-dir> <branch> → ★ local と origin を同じ sha に揃える
  local r="$1" b="$2"
  ( cd "${r}" && git switch -q -c "${b}" \
      && printf 'x\n' > "m-$(printf '%s' "${b}" | tr '/' '_')" \
      && git add -A -- . && git commit -q -m "on ${b}" \
      && git push -q origin "${b}" && git switch -q main ) >/dev/null 2>&1
}
add_local_commit() { # add_local_commit <repo-dir> <branch> → ★ ローカルだけ 1 コミット進める (未 push)
  local r="$1" b="$2"
  ( cd "${r}" && git switch -q "${b}" \
      && printf 'y\n' > "l-$(printf '%s' "${b}" | tr '/' '_')" \
      && git add -A -- . && git commit -q -m "local extra on ${b}" && git switch -q main ) >/dev/null 2>&1
}
add_origin_commit() { # add_origin_commit <bare-dir> <branch> → ★ origin だけ (別クローン経由で) 1 コミット進める
  local bare="$1" b="$2" tmp rc
  tmp="$(mktemp -d)" || return 1
  ( cd "${tmp}" && git clone -q "${bare}" c \
      && cd c && git -c user.email=x@x.invalid -c user.name=x checkout -q "${b}" \
      && printf 'z\n' > "o-$(printf '%s' "${b}" | tr '/' '_')" && git add -A -- . \
      && git -c user.email=x@x.invalid -c user.name=x commit -q -m "origin extra on ${b}" \
      && git push -q origin "${b}" ) >/dev/null 2>&1
  rc=$?
  rm -rf "${tmp}"
  return ${rc}
}
create_origin_only_branch() { # create_origin_only_branch <bare-dir> <branch> → ★ ローカルには一切存在しない
  local bare="$1" b="$2" tmp rc
  tmp="$(mktemp -d)" || return 1
  ( cd "${tmp}" && git clone -q "${bare}" c \
      && cd c && git -c user.email=x@x.invalid -c user.name=x switch -q -c "${b}" \
      && printf 'n\n' > "n-$(printf '%s' "${b}" | tr '/' '_')" && git add -A -- . \
      && git -c user.email=x@x.invalid -c user.name=x commit -q -m "on ${b}" \
      && git push -q origin "${b}" ) >/dev/null 2>&1
  rc=$?
  rm -rf "${tmp}"
  return ${rc}
}
origin_tip() { ( cd "$1" && git rev-parse --verify --quiet "refs/remotes/origin/$2" ) 2>/dev/null; }
# ★ `tip_of` / `wt_head` は群 7 で定義済み (このファイル内で以後も使い回せる)。

R10="${TMP}/r10/repo"; O10="${TMP}/r10/origin.git"
if ! setup_origin_repo "${R10}" "${O10}"; then
  ng "P1-J: origin 付き一時 repo を用意できなかった (★ 判定できない)"
else
  # --- 10a: 一致 → origin/$base ---
  make_pushed_branch "${R10}" feat-eq
  SPAWN_ENV="LOOP_BASE_BRANCH=feat-eq"; do_spawn_x "${R10}" --no-exec 10a t
  if [ "${SRC}" -eq 0 ] && has_text "${SERR}" "start-choice = equal" \
     && [ "$(wt_head "${TMP}/r10/wt/repo-10a-t")" = "$(origin_tip "${R10}" feat-eq)" ]; then
    ok "10a: 一致 → origin/base から切り、start-choice=equal を出した"
  else
    ng "10a: rc=${SRC} —— 一致状態で期待どおりに切れていない"
  fi

  # --- 10b: ローカル先行 → ローカルから切り、未 push 件数の WARN を出す ---
  make_pushed_branch "${R10}" feat-ahead
  add_local_commit "${R10}" feat-ahead
  SPAWN_ENV="LOOP_BASE_BRANCH=feat-ahead"; do_spawn_x "${R10}" --no-exec 10b t
  if [ "${SRC}" -eq 0 ] && has_text "${SERR}" "start-choice = local-ahead" && has_text "${SERR}" "未 push" \
     && [ "$(wt_head "${TMP}/r10/wt/repo-10b-t")" = "$(tip_of "${R10}" feat-ahead)" ]; then
    ok "10b: ★★★ ローカル先行 → ローカルから切り、未 push の WARN を出した (旧実装は origin から切っていた)"
  else
    ng "10b: rc=${SRC} —— ローカル先行なのに期待どおりに切れていない"
  fi

  # --- 10c: ローカル遅れ → origin/$base (現行どおり) ---
  make_pushed_branch "${R10}" feat-behind
  add_origin_commit "${O10}" feat-behind
  SPAWN_ENV="LOOP_BASE_BRANCH=feat-behind"; do_spawn_x "${R10}" --no-exec 10c t
  if [ "${SRC}" -eq 0 ] && has_text "${SERR}" "start-choice = local-behind" \
     && [ "$(wt_head "${TMP}/r10/wt/repo-10c-t")" = "$(origin_tip "${R10}" feat-behind)" ]; then
    ok "10c: ローカル遅れ → origin/base から切った"
  else
    ng "10c: rc=${SRC} —— ローカル遅れなのに期待どおりに切れていない"
  fi

  # --- 10d: 分岐 → die (worktree も branch も作らない) ---
  make_pushed_branch "${R10}" feat-div
  add_local_commit "${R10}" feat-div
  add_origin_commit "${O10}" feat-div
  SPAWN_ENV="LOOP_BASE_BRANCH=feat-div"; do_spawn_x "${R10}" --no-exec 10d t
  if [ "${SRC}" -ne 0 ] && ! wt_has "${R10}" "repo-10d-t" && ! branch_exists "${R10}" "loop/10d-t"; then
    ok "10d: ★★★ 分岐は die し、worktree も branch も作らなかった (fail-closed)"
  else
    ng "10d: rc=${SRC} —— 分岐なのに進んだ、または残骸がある"
  fi

  # --- 10e: ローカルに base が無い → origin/$base (現行どおり) ---
  create_origin_only_branch "${O10}" feat-nolocal
  SPAWN_ENV="LOOP_BASE_BRANCH=feat-nolocal"; do_spawn_x "${R10}" --no-exec 10e t
  if [ "${SRC}" -eq 0 ] && has_text "${SERR}" "start-choice = no-local" \
     && [ "$(wt_head "${TMP}/r10/wt/repo-10e-t")" = "$(origin_tip "${R10}" feat-nolocal)" ]; then
    ok "10e: ローカル無し → origin/base から切った"
  else
    ng "10e: rc=${SRC} —— ローカル無しなのに期待どおりに切れていない"
  fi
fi

# --- 10f: fetch 失敗 → ローカル base で続行 (★ 別 repo。origin URL を壊すため使い捨てる) ---
R10F="${TMP}/r10f/repo"; O10F="${TMP}/r10f/origin.git"
if ! setup_origin_repo "${R10F}" "${O10F}" || ! make_pushed_branch "${R10F}" feat-eq; then
  ng "10f: 準備できなかった (★ 判定できない)"
else
  ( cd "${R10F}" && git remote set-url origin "${TMP}/r10f/no-such-origin.git" ) >/dev/null 2>&1
  SPAWN_ENV="LOOP_BASE_BRANCH=feat-eq"; do_spawn_x "${R10F}" --no-exec 10f t
  if [ "${SRC}" -eq 0 ] && has_text "${SERR}" "start-choice = fetch-failed" && has_text "${SERR}" "fetch 失敗" \
     && [ "$(wt_head "${TMP}/r10f/wt/repo-10f-t")" = "$(tip_of "${R10F}" feat-eq)" ]; then
    ok "10f: fetch 失敗 → ローカル base で続行し、start-choice=fetch-failed を出した"
  else
    ng "10f: rc=${SRC} —— fetch 失敗時の挙動が期待と違う"
  fi
fi

# --- 10g/10h: ⚠️★★★ 変異テスト (★ 群 10 が空振りしていないこと) ---
echo "10g-10h. ⚠️★★★ 変異テスト —— 祖先関係の分岐を潰したら赤くなるか"

# 10g: local-ahead の判定を潰す (常に false = rc 1 扱い) → 10b は分岐 (die) に落ちるはず
#   ⚠️★★★ P1-K のロック直列化に伴い判定を `elif git merge-base …; then` から
#   `git merge-base … || ahead_rc=$?` (★ `set -e` 下で bare command の rc を直接読むため) へ
#   書き換えた。sed の当て先もこの形に追随させる (★ 2026-09-26 レビュー対応時に実測で踏んだ)。
MUT10G="${TMP}/mut10g-loop-spawn.sh"
sed 's#git merge-base --is-ancestor "refs/remotes/origin/\$base" "refs/heads/\$base" 2>/dev/null || ahead_rc=\$?#ahead_rc=1#' \
  "${SPAWN_SH}" > "${MUT10G}"
mut10g_src="$(grep -cF 'git merge-base --is-ancestor "refs/remotes/origin/$base" "refs/heads/$base" 2>/dev/null || ahead_rc=$?' "${SPAWN_SH}" 2>/dev/null)" || mut10g_src=0
mut10g_left="$(grep -cF 'git merge-base --is-ancestor "refs/remotes/origin/$base" "refs/heads/$base" 2>/dev/null || ahead_rc=$?' "${MUT10G}" 2>/dev/null)" || mut10g_left=0
if [ "${mut10g_src:-0}" -ne 1 ] || [ "${mut10g_left:-0}" -ne 0 ]; then
  ng "10g: 変異を当てられない (src=${mut10g_src} / mut=${mut10g_left}) —— ★ 判定式の書き方が変わった → ⚠️ 検査不能"
else
  R10G="${TMP}/r10g/repo"; O10G="${TMP}/r10g/origin.git"
  if ! setup_origin_repo "${R10G}" "${O10G}" "${MUT10G}"; then
    ng "10g: 準備できなかった (★ 判定できない)"
  else
    make_pushed_branch "${R10G}" feat-ahead
    add_local_commit "${R10G}" feat-ahead
    SPAWN_ENV="LOOP_BASE_BRANCH=feat-ahead"; do_spawn_x "${R10G}" --no-exec 10g t
    if [ "${SRC}" -ne 0 ]; then
      ok "10g: ★★★ local-ahead 判定を潰すと分岐扱いで die した (★ 10b は空振りしていない)"
    else
      ng "10g: 潰しても rc=0 で進んだ (⚠️★★★ 10b が判定式を見ていない可能性)"
    fi
  fi
fi

# 10h: local-behind の判定を潰す (常に true = rc 0 扱い) → 10d (分岐) が die せず進んでしまうはず
#   ⚠️★★★ 10g と同じ理由で sed の当て先を `behind_rc=$?` の形へ追随させる。
MUT10H="${TMP}/mut10h-loop-spawn.sh"
sed 's#git merge-base --is-ancestor "refs/heads/\$base" "refs/remotes/origin/\$base" 2>/dev/null || behind_rc=\$?#behind_rc=0#' \
  "${SPAWN_SH}" > "${MUT10H}"
mut10h_src="$(grep -cF 'git merge-base --is-ancestor "refs/heads/$base" "refs/remotes/origin/$base" 2>/dev/null || behind_rc=$?' "${SPAWN_SH}" 2>/dev/null)" || mut10h_src=0
mut10h_left="$(grep -cF 'git merge-base --is-ancestor "refs/heads/$base" "refs/remotes/origin/$base" 2>/dev/null || behind_rc=$?' "${MUT10H}" 2>/dev/null)" || mut10h_left=0
if [ "${mut10h_src:-0}" -ne 1 ] || [ "${mut10h_left:-0}" -ne 0 ]; then
  ng "10h: 変異を当てられない (src=${mut10h_src} / mut=${mut10h_left}) —— ★ 判定式の書き方が変わった → ⚠️ 検査不能"
else
  R10H="${TMP}/r10h/repo"; O10H="${TMP}/r10h/origin.git"
  if ! setup_origin_repo "${R10H}" "${O10H}" "${MUT10H}"; then
    ng "10h: 準備できなかった (★ 判定できない)"
  else
    make_pushed_branch "${R10H}" feat-div
    add_local_commit "${R10H}" feat-div
    add_origin_commit "${O10H}" feat-div
    SPAWN_ENV="LOOP_BASE_BRANCH=feat-div"; do_spawn_x "${R10H}" --no-exec 10h t
    if [ "${SRC}" -eq 0 ] && wt_has "${R10H}" "repo-10h-t"; then
      ok "10h: ★★★ local-behind 判定を潰すと分岐なのに死なず進んでしまった (★ 10d は空振りしていない)"
    else
      ng "10h: 潰しても rc=${SRC} で止まった (⚠️★★★ 10d が判定式を見ていない可能性)"
    fi
  fi
fi

# ── 11. ⚠️★★★ P1-K: spawn の直列化ロックと失敗時の残骸片づけ ────
# ⚠️★★★ **何を止めるためにあるのか** (design.md P1-K・decisions.md 判断 6):
#   ★ `git worktree add -b` は upstream 設定で `.git/config` を書くため、2 本同時だと
#     git 自身のロックで片方が落ち、旧実装は `set -e` で **ブランチだけ作られた状態で die**
#     し、片づけないまま終わっていた。
echo "11. ⚠️★★★ P1-K: spawn の同時実行と、worktree add 失敗時の残骸片づけ"

# --- 11a: 同じ repo で別 id の spawn を 2 本 & で同時に起動し、両方 exit 0 / 両方 worktree あり ---
R11="${TMP}/r11/repo"; mkdir -p "${R11}"
if ! setup_fake_repo "${R11}"; then
  ng "11a: 準備できなかった (★ 判定できない)"
else
  round=1
  all_ok=1
  while [ "${round}" -le 3 ]; do
    ida="c${round}a"; idb="c${round}b"
    ( cd "${R11}" && bash scripts/loop-spawn.sh --no-exec "${ida}" t ) >"${TMP}/r11-${round}a.log" 2>&1 &
    pa=$!
    ( cd "${R11}" && bash scripts/loop-spawn.sh --no-exec "${idb}" t ) >"${TMP}/r11-${round}b.log" 2>&1 &
    pb=$!
    wait "${pa}"; rca=$?
    wait "${pb}"; rcb=$?
    if [ "${rca}" -ne 0 ] || [ "${rcb}" -ne 0 ] \
       || ! wt_has "${R11}" "repo-${ida}-t" || ! wt_has "${R11}" "repo-${idb}-t"; then
      all_ok=0
      ng "11a: round ${round} 失敗 (rca=${rca} rcb=${rcb})"
    fi
    round=$((round + 1))
  done
  if [ "${all_ok}" -eq 1 ]; then
    ok "11a: 別 id の同時 spawn を 3 ラウンド、毎回両方 exit 0・両方 worktree あり"
  fi
fi

# --- 11a2: ⚠️★★★ mkdir が不可分でない環境でも、同時 spawn の両方が成功すること (2026-11-06) ---
#   ★ ubuntu 26.04 の既定の mkdir (uutils coreutils 0.10.0) は、同時に呼ばれると既にある
#     ディレクトリにも 0 を返す (CI の対照で 300 回中 258 回、両方が成功した。python の os.mkdir・
#     bash の noclobber・GNU の mkdir は 0 回)。mkdir の成否だけをロックにすると、2 本が同時に
#     ロックを取ったと思い込み、pid の読み戻しで片方が fail-closed で止まっていた (11a が赤)。
#   → 「既にあっても 0 を返す mkdir」(mkdir -p) に差し替え、macOS でも同じ状況を再現する。
#     直す前は片方が落ち、直した後は片方が待って両方とも成功する。
R11U="${TMP}/r11u/repo"; mkdir -p "${R11U}"
if ! setup_fake_repo "${R11U}"; then
  ng "11a2: 準備できなかった (★ 判定できない)"
else
  round=1
  all_ok=1
  while [ "${round}" -le 3 ]; do
    ida="u${round}a"; idb="u${round}b"
    (
      mkdir() { command mkdir -p "$@"; }
      export -f mkdir
      cd "${R11U}" && bash scripts/loop-spawn.sh --no-exec "${ida}" t
    ) >"${TMP}/r11u-${round}a.log" 2>&1 &
    pa=$!
    (
      mkdir() { command mkdir -p "$@"; }
      export -f mkdir
      cd "${R11U}" && bash scripts/loop-spawn.sh --no-exec "${idb}" t
    ) >"${TMP}/r11u-${round}b.log" 2>&1 &
    pb=$!
    rca=0; wait "${pa}" || rca=$?
    rcb=0; wait "${pb}" || rcb=$?
    if [ "${rca}" -ne 0 ] || [ "${rcb}" -ne 0 ] \
       || ! wt_has "${R11U}" "repo-${ida}-t" || ! wt_has "${R11U}" "repo-${idb}-t"; then
      all_ok=0
      ng "11a2: round ${round} 失敗 (rca=${rca} rcb=${rcb})"
      sed 's/^/         | /' "${TMP}/r11u-${round}a.log" "${TMP}/r11u-${round}b.log" | grep -i 'lock' | head -4
    fi
    round=$((round + 1))
  done
  if [ "${all_ok}" -eq 1 ]; then
    ok "11a2: 既にあっても 0 を返す mkdir の下でも、同時 spawn を 3 ラウンド、毎回両方 exit 0・両方 worktree あり"
  fi
fi

# --- 11b: ⚠️★★★ git worktree add を失敗させたとき、branch が残らないこと ---
#   ★ 失敗のさせ方: 作成先パスに **同名の実ファイル**を事前に置く (★ Windows もファイル名で
#     衝突させられるので両 OS で同じ fixture を作れる。パーミッションでの再現は移植性が無い)。
R11B="${TMP}/r11b/repo"; mkdir -p "${R11B}"
if ! setup_fake_repo "${R11B}"; then
  ng "11b: 準備できなかった (★ 判定できない)"
else
  mkdir -p "${TMP}/r11b/wt"
  echo "blocker" > "${TMP}/r11b/wt/repo-fx-t"   # ★ worktree の作成先を実ファイルで塞ぐ
  SPAWN_ENV=""; do_spawn_x "${R11B}" --no-exec fx t
  if [ "${SRC}" -ne 0 ] && ! branch_exists "${R11B}" "loop/fx-t"; then
    ok "11b: ★★★ git worktree add 失敗時に branch loop/fx-t を残さなかった (旧実装は残していた)"
  else
    ng "11b: rc=${SRC} / branch 残=$(branch_exists "${R11B}" "loop/fx-t" && echo yes || echo no)"
  fi
fi

# --- 11c: ⚠️★★★ 変異テスト —— abort_worktree の cleanup 条件を潰すと branch が残るか ---
MUT11C="${TMP}/mut11c-loop-spawn.sh"
sed 's/if \[ -n "\$tip" \] && \[ "\$tip" = "\${start_sha:-}" \]; then/if false; then/' "${SPAWN_SH}" > "${MUT11C}"
mut11c_src="$(grep -cF 'if [ -n "$tip" ] && [ "$tip" = "${start_sha:-}" ]; then' "${SPAWN_SH}" 2>/dev/null)" || mut11c_src=0
mut11c_left="$(grep -cF 'if [ -n "$tip" ] && [ "$tip" = "${start_sha:-}" ]; then' "${MUT11C}" 2>/dev/null)" || mut11c_left=0
if [ "${mut11c_src:-0}" -ne 1 ] || [ "${mut11c_left:-0}" -ne 0 ]; then
  ng "11c: 変異を当てられない (src=${mut11c_src} / mut=${mut11c_left}) —— ★ abort_worktree の書き方が変わった → ⚠️ 検査不能"
else
  R11C="${TMP}/r11c/repo"; mkdir -p "${R11C}"
  if ! setup_fake_repo "${R11C}" "${MUT11C}"; then
    ng "11c: 準備できなかった (★ 判定できない)"
  else
    mkdir -p "${TMP}/r11c/wt"
    echo "blocker" > "${TMP}/r11c/wt/repo-fx-t"
    SPAWN_ENV=""; do_spawn_x "${R11C}" --no-exec fx t
    if [ "${SRC}" -ne 0 ] && branch_exists "${R11C}" "loop/fx-t"; then
      ok "11c: ★★★ cleanup 条件を潰すと branch が残った (★ 11b は空振りしていない)"
    else
      ng "11c: 潰しても branch が残らなかった (⚠️★★★ 11b が cleanup 条件を見ていない可能性)"
    fi
  fi
fi

# --- 11d-11f: ⚠️★★★ ロックそのものを決定論的に検査する (★ 2026-09-26 メインのレビューで追加) ---
#   ★ 同時実行の競合は再現できなかった (下の注記) ので、**ロックを先に置いて**振る舞いを見る:
#     11d: 生きている pid のロック → 待ち切って非 0・branch も worktree も作らない
#     11e: 死んだ pid のロック     → stale として除去し、spawn が通る
#     11f: 変異 —— `acquire_spawn_lock` の呼び出しを消すと 11d の状況で spawn が通ってしまう (★ 11d が空振りしていない)
echo "11d-11f. ⚠️★★★ P1-K: ロックを先に置いたときの待ち・stale 除去・変異"
LOCK_ENV="LOOP_SPAWN_LOCK_TIMEOUT=2 LOOP_SPAWN_LOCK_POLL=0.2"
sleep 60 &
LIVE_PID=$!
R11D="${TMP}/r11d/repo"; mkdir -p "${R11D}"
if ! setup_fake_repo "${R11D}"; then
  ng "11d: 準備できなかった (★ 判定できない)"
else
  mkdir -p "${R11D}/.git/loop-spawn.lock" && printf '%s' "${LIVE_PID}" > "${R11D}/.git/loop-spawn.lock/pid"
  SPAWN_ENV="${LOCK_ENV}"; do_spawn_x "${R11D}" --no-exec lk t
  if [ "${SRC}" -ne 0 ] && ! branch_exists "${R11D}" "loop/lk-t" && ! wt_has "${R11D}" "repo-lk-t" \
     && [ -d "${R11D}/.git/loop-spawn.lock" ]; then
    ok "11d: 生きている pid のロックでは待ち切って非 0・branch/worktree を作らず・他人のロックを消さない"
  else
    ng "11d: rc=${SRC} / branch 残=$(branch_exists "${R11D}" "loop/lk-t" && echo yes || echo no) / lock 残=$([ -d "${R11D}/.git/loop-spawn.lock" ] && echo yes || echo no)"
  fi
fi
R11E="${TMP}/r11e/repo"; mkdir -p "${R11E}"
if ! setup_fake_repo "${R11E}"; then
  ng "11e: 準備できなかった (★ 判定できない)"
else
  true & DEAD_PID=$!; wait "${DEAD_PID}" 2>/dev/null || true
  mkdir -p "${R11E}/.git/loop-spawn.lock" && printf '%s' "${DEAD_PID}" > "${R11E}/.git/loop-spawn.lock/pid"
  SPAWN_ENV="${LOCK_ENV}"; do_spawn_x "${R11E}" --no-exec st t
  if [ "${SRC}" -eq 0 ] && wt_has "${R11E}" "repo-st-t" && [ ! -d "${R11E}/.git/loop-spawn.lock" ]; then
    ok "11e: 死んだ pid のロックは stale として除去し、spawn が通り、終了時にロックを残さない"
  else
    ng "11e: rc=${SRC} / wt=$(wt_has "${R11E}" "repo-st-t" && echo yes || echo no) / lock 残=$([ -d "${R11E}/.git/loop-spawn.lock" ] && echo yes || echo no)"
  fi
fi
MUT11F="${TMP}/mut11f-loop-spawn.sh"
sed '/^acquire_spawn_lock$/d' "${SPAWN_SH}" > "${MUT11F}"
mut11f_src="$(grep -c '^acquire_spawn_lock$' "${SPAWN_SH}" 2>/dev/null)" || mut11f_src=0
mut11f_left="$(grep -c '^acquire_spawn_lock$' "${MUT11F}" 2>/dev/null)" || mut11f_left=0
if [ "${mut11f_src:-0}" -ne 1 ] || [ "${mut11f_left:-0}" -ne 0 ]; then
  ng "11f: 変異を当てられない (src=${mut11f_src} / mut=${mut11f_left}) —— ★ ロック取得の書き方が変わった → ⚠️ 検査不能"
else
  R11F="${TMP}/r11f/repo"; mkdir -p "${R11F}"
  if ! setup_fake_repo "${R11F}" "${MUT11F}"; then
    ng "11f: 準備できなかった (★ 判定できない)"
  else
    mkdir -p "${R11F}/.git/loop-spawn.lock" && printf '%s' "${LIVE_PID}" > "${R11F}/.git/loop-spawn.lock/pid"
    SPAWN_ENV="${LOCK_ENV}"; do_spawn_x "${R11F}" --no-exec lk t
    if [ "${SRC}" -eq 0 ]; then
      ok "11f: ★★★ ロック取得を消すと、生きているロックを無視して spawn が通った (★ 11d は空振りしていない)"
    else
      ng "11f: 取得を消しても止まった (⚠️★★★ 11d がロック以外の理由で止まっている可能性) rc=${SRC}"
    fi
  fi
fi
kill "${LIVE_PID}" 2>/dev/null || true

# --- 11g/11h: ⚠️★★★ C-M1 (レビュー): rm -rf が失敗し続けてもタイムアウトが必ず効くか ────
#   ⚠️★★★ 何を止めるためにあるのか (2026-09-26 のレビュー・C-M1):
#     ★ 旧実装の stale 分岐は `rm -rf … || true; continue` で、i の加算も sleep も飛ばしていた。
#     rm が失敗し続けると (★ Windows のハンドル保持など) タイムアウトが一切効かないまま
#     CPU を回し続ける。
#   ★ `rm` を bash 関数で shadow し `export -f` で子プロセス (`bash scripts/loop-spawn.sh`) に
#     引き継がせ、「rm が常に失敗する」状況を **決定論的に**作る (★ 実ファイルは一切消えない)。
#   ⚠️ 旧実装だとこの状況で無限ループになるため、**外側の壁時計タイムアウト**で検出する
#     (バックグラウンド起動＋経過秒数のポーリング。`timeout` コマンドの有無に依存しない)。
echo "11g-11h. ⚠️★★★ C-M1: rm -rf が失敗し続けても LOCK_TIMEOUT 内に非 0 で止まるか (スピンしない)"

run_fakerm_scenario() { # run_fakerm_scenario <repo-dir> <spawn-src> <id> <out-prefix>
  local r="$1" src="$2" id="$3" pfx="$4" gpid waited grc
  setup_fake_repo "${r}" "${src}" || return 2
  true & DPID=$!; wait "${DPID}" 2>/dev/null || true   # ★ 確実に死んでいる pid (11e と同じ作法)
  mkdir -p "${r}/.git/loop-spawn.lock" && printf '%s' "${DPID}" > "${r}/.git/loop-spawn.lock/pid"
  (
    cd "${r}" || exit 1
    rm() { return 1; }
    export -f rm
    # ⚠️★★★ 起票 (2026-09-26 の裁定・項目 7): **exec を明示する。**
    #   ★ exec 最適化の保証が無い bash (macOS 3.2) では、`(...)` サブシェルの最後のコマンドが
    #     単純な `env ... bash ...` でも新たな子プロセスへ fork されうる。
    #   ⚠️ すると `$!` (＝ gpid) はサブシェル自身の pid のままで、実際に走る
    #     `bash scripts/loop-spawn.sh` はその**孫プロセス**になる。下の `kill -9 "${gpid}"` は
    #     孫まで届かないため、ハング検出後も loop-spawn.sh が孤児として残りうる。
    #   → ★ `exec` でサブシェル自身を置き換え、`gpid` が実プロセスの pid と一致するようにする。
    exec env LOOP_SPAWN_LOCK_TIMEOUT=3 LOOP_SPAWN_LOCK_POLL=0.2 bash scripts/loop-spawn.sh --no-exec "${id}" t
  ) >"${TMP}/${pfx}.out" 2>"${TMP}/${pfx}.err" &
  gpid=$!
  waited=0
  while kill -0 "${gpid}" 2>/dev/null && [ "${waited}" -lt 15 ]; do
    sleep 1; waited=$((waited + 1))
  done
  if kill -0 "${gpid}" 2>/dev/null; then
    kill -9 "${gpid}" 2>/dev/null || true
    wait "${gpid}" 2>/dev/null || true
    FAKERM_HUNG=1; FAKERM_RC=""; FAKERM_WAITED="${waited}"
  else
    wait "${gpid}"; grc=$?
    FAKERM_HUNG=0; FAKERM_RC="${grc}"; FAKERM_WAITED="${waited}"
  fi
  FAKERM_ERR="$(cat "${TMP}/${pfx}.err" 2>/dev/null || true)"
}

R11G="${TMP}/r11g/repo"; mkdir -p "${R11G}"
if ! run_fakerm_scenario "${R11G}" "${SPAWN_SH}" gg 11g; then
  ng "11g: 準備できなかった (★ 判定できない)"
else
  if [ "${FAKERM_HUNG}" -eq 1 ]; then
    ng "11g: ⚠️★★★ ${FAKERM_WAITED} 秒待ってもプロセスが終わらなかった (★ C-M1 のスピンが再発している)"
  elif [ "${FAKERM_RC}" -ne 0 ] && has_text "${FAKERM_ERR}" "loop-spawn.lock を"; then
    ok "11g: ★★★ rm が失敗し続けても LOCK_TIMEOUT (3秒) 内に非 0 で止まった (${FAKERM_WAITED} 秒で終了)"
  else
    ng "11g: rc=${FAKERM_RC} / ${FAKERM_WAITED} 秒で終了したが期待した die メッセージが無い"
  fi
fi

# --- 11h: ⚠️★★★ 変異テスト —— i の加算を潰すと 11g の状況でハングするか ---
MUT11H="${TMP}/mut11h-loop-spawn.sh"
sed 's/i=\$((i + 1))/i=\$((i + 0))/' "${SPAWN_SH}" > "${MUT11H}"
mut11h_src="$(grep -cF 'i=$((i + 1))' "${SPAWN_SH}" 2>/dev/null)" || mut11h_src=0
mut11h_left="$(grep -cF 'i=$((i + 1))' "${MUT11H}" 2>/dev/null)" || mut11h_left=0
if [ "${mut11h_src:-0}" -ne 1 ] || [ "${mut11h_left:-0}" -ne 0 ]; then
  ng "11h: 変異を当てられない (src=${mut11h_src} / mut=${mut11h_left}) —— ★ i の加算の書き方が変わった → ⚠️ 検査不能"
else
  R11H="${TMP}/r11h/repo"; mkdir -p "${R11H}"
  if ! run_fakerm_scenario "${R11H}" "${MUT11H}" hh 11h; then
    ng "11h: 準備できなかった (★ 判定できない)"
  else
    if [ "${FAKERM_HUNG}" -eq 1 ]; then
      ok "11h: ★★★ i の加算を潰すと rm 失敗が続く状況でハングした (★ 11g は空振りしていない)"
    else
      ng "11h: 潰しても ${FAKERM_WAITED} 秒で終了した (rc=${FAKERM_RC}) (⚠️★★★ 11g が i の加算を見ていない可能性)"
    fi
  fi
fi

# --- 11i/11j: ⚠️★★★ C-M2 (レビュー): stale 除去の TOCTOU —— 読み直しが効いているか ────
#   ⚠️★★★ 何を止めるためにあるのか (2026-09-26 のレビュー・C-M2):
#     ★ 待ち手 A と B が同じ死んだ pid を読み、A が除去して取り直した直後に B が
#     **古い判断のまま** A の新しいロックを消すと、2 本が同時にクリティカルセクションへ入る。
#   ⚠️ 実際の 2 プロセス競合はタイミング依存で確定再現できないため、`cat` を bash 関数で
#     shadow して「1 回目の読み取りは死んだ pid・2 回目以降は生きている pid」を**決定論的に**
#     作る (★ reap 直後の読み直しが「観測した死んだ pid と同じ場合に限り消す」を検査する)。
echo "11i-11j. ⚠️★★★ C-M2: stale 除去の TOCTOU —— reap 内の pid 読み直しが効いているか"

run_fakecat_scenario() { # run_fakecat_scenario <repo-dir> <spawn-src> <id> <out-prefix>
  local r="$1" src="$2" id="$3" pfx="$4" dpid apid ipid waited irc
  setup_fake_repo "${r}" "${src}" || return 2
  true & dpid=$!; wait "${dpid}" 2>/dev/null || true   # ★ 1 回目の読み取りに使う「死んだ pid」
  sleep 20 & apid=$!                                    # ★ 2 回目以降の読み取りに使う「生きている pid」
  mkdir -p "${r}/.git/loop-spawn.lock" && printf '%s' "${dpid}" > "${r}/.git/loop-spawn.lock/pid"
  (
    cd "${r}" || exit 1
    export FAKECAT_COUNT="${TMP}/${pfx}-count"
    export FAKECAT_DEAD="${dpid}"
    export FAKECAT_ALIVE="${apid}"
    printf '0' > "${FAKECAT_COUNT}"
    cat() {
      case "$1" in
        */loop-spawn.lock/pid)
          local real
          real="$(command cat "$1" 2>/dev/null || true)"
          if [ "${real}" = "$$" ]; then
            # ⚠️★★★ CR MEDIUM (2026-09-26 2巡目) の副作用: acquire_spawn_lock 自身が pid を
            #   書いた直後に読み戻して確認するようになった。★ 実ファイルの中身が既に自分の
            #   $$ (＝ 自分がこの直前に書いた値) なら、それは TOCTOU シナリオの対象
            #   (他プロセスの死んだ/生きたロック) ではないので偽装せず素通しする
            #   (⚠️ さもないと acquire 自身が自分の pid を読み戻せず誤って die する)。
            command cat "$1"
            return 0
          fi
          local n
          n="$(command cat "${FAKECAT_COUNT}" 2>/dev/null || echo 0)"
          n=$((n + 1))
          printf '%s' "${n}" > "${FAKECAT_COUNT}"
          if [ "${n}" -eq 1 ]; then printf '%s' "${FAKECAT_DEAD}"; else printf '%s' "${FAKECAT_ALIVE}"; fi
          return 0 ;;
      esac
      command cat "$@"
    }
    export -f cat
    # ⚠️★★★ 起票 (2026-09-26 の裁定・項目 7): `run_fakerm_scenario` と同じ理由で exec を明示する
    #   (★ サブシェルの pid ($!) と実プロセスをずらさない。詳細はそちらのコメント参照)。
    exec env LOOP_SPAWN_LOCK_TIMEOUT=3 LOOP_SPAWN_LOCK_POLL=0.2 bash scripts/loop-spawn.sh --no-exec "${id}" t
  ) >"${TMP}/${pfx}.out" 2>"${TMP}/${pfx}.err" &
  ipid=$!
  waited=0
  while kill -0 "${ipid}" 2>/dev/null && [ "${waited}" -lt 15 ]; do
    sleep 1; waited=$((waited + 1))
  done
  if kill -0 "${ipid}" 2>/dev/null; then
    kill -9 "${ipid}" 2>/dev/null || true
    wait "${ipid}" 2>/dev/null || true
    FAKECAT_HUNG=1; FAKECAT_RC=""
  else
    wait "${ipid}"; irc=$?
    FAKECAT_HUNG=0; FAKECAT_RC="${irc}"
  fi
  FAKECAT_WAITED="${waited}"
  kill "${apid}" 2>/dev/null || true
}

R11I="${TMP}/r11i/repo"; mkdir -p "${R11I}"
if ! run_fakecat_scenario "${R11I}" "${SPAWN_SH}" ii 11i; then
  ng "11i: 準備できなかった (★ 判定できない)"
else
  if [ "${FAKECAT_HUNG}" -eq 1 ]; then
    ng "11i: ⚠️ ${FAKECAT_WAITED} 秒待ってもプロセスが終わらなかった (★ 判定できない)"
  elif [ "${FAKECAT_RC}" -ne 0 ] && ! wt_has "${R11I}" "repo-ii-t"; then
    ok "11i: ★★★ 読み直した pid が生きていたので他人のロックを消さず、待ち切って非 0 で止まった"
  else
    ng "11i: rc=${FAKECAT_RC} / worktree 作成=$(wt_has "${R11I}" "repo-ii-t" && echo yes || echo no) (⚠️ 読み直しが効いていない?)"
  fi
fi

# --- 11j: ⚠️★★★ 変異テスト —— reap 内の再検査 (読み直し一致 + kill -0) を潰すと
#   11i と同じ状況で「生きているロック」を消して通ってしまうか ---
MUT11J="${TMP}/mut11j-loop-spawn.sh"
sed 's/if \[ "\${reap_pid:-}" = "\${lock_pid}" \] \&\& ! kill -0 "\${lock_pid}" 2>\/dev\/null; then/if true; then/' \
  "${SPAWN_SH}" > "${MUT11J}"
mut11j_src="$(grep -cF 'if [ "${reap_pid:-}" = "${lock_pid}" ] && ! kill -0 "${lock_pid}" 2>/dev/null; then' "${SPAWN_SH}" 2>/dev/null)" || mut11j_src=0
mut11j_left="$(grep -cF 'if [ "${reap_pid:-}" = "${lock_pid}" ] && ! kill -0 "${lock_pid}" 2>/dev/null; then' "${MUT11J}" 2>/dev/null)" || mut11j_left=0
if [ "${mut11j_src:-0}" -ne 1 ] || [ "${mut11j_left:-0}" -ne 0 ]; then
  ng "11j: 変異を当てられない (src=${mut11j_src} / mut=${mut11j_left}) —— ★ reap の再検査の書き方が変わった → ⚠️ 検査不能"
else
  R11J="${TMP}/r11j/repo"; mkdir -p "${R11J}"
  if ! run_fakecat_scenario "${R11J}" "${MUT11J}" jj 11j; then
    ng "11j: 準備できなかった (★ 判定できない)"
  else
    if [ "${FAKECAT_HUNG}" -eq 0 ] && [ "${FAKECAT_RC}" -eq 0 ] && wt_has "${R11J}" "repo-jj-t"; then
      ok "11j: ★★★ 再検査を潰すと『生きているロック』を消して通ってしまった (★ 11i は空振りしていない)"
    else
      ng "11j: 潰しても hung=${FAKECAT_HUNG} / rc=${FAKECAT_RC} で止まった (⚠️★★★ 11i が再検査を見ていない可能性)"
    fi
  fi
fi

# ⚠️ **やっていないこと** (★ 隠さない):
#   - P1-K のロック自体を外す変異による「同時実行で本当に失敗する」直接の再現は
#     この環境 (Windows/git-bash・ローカル NTFS) では **12 並列まで手で確認しても再現しなかった**
#     (★ git 自身の内部ロックが十分速いため、この規模の同時実行では衝突しなかったと見られる)。
#     → 上の 11b/11c は「同時実行で起きた事故と *同じ形* (worktree add 失敗時にブランチが
#     残る)」を **決定論的なファイル衝突**で再現し、その修正 (`abort_worktree` 経由の片づけ)
#     が効いていることを検査する。ロック自体は 11d-11f (先に置いたロックでの待ち・stale 除去・変異) が守る。
#   - ⚠️★★★ C-M1 (11g/11h) は `rm` を、C-M2 (11i/11j) は `cat` を bash 関数で shadow して
#     決定論的に再現した。★ 2 プロセスの実競合そのもの (真の TOCTOU タイミング) は
#     この環境でも直接には再現していない —— 11i/11j は「reap 内の読み直しという **コードの経路**」
#     を検査しているのであって、「2 プロセスが同時に mkdir を試みる」瞬間そのものではない
#     (★ 隠さない。できなかったことはできなかったと書く)。

# ── 12. ⚠️★★★ 起票 A の LOW 項目 (レビュー) ──────────────
echo "════════════════════════════════════════"
echo "12. ⚠️ LOW: LOCK_POLL/TIMEOUT の検証・validate_name の sanitize・rev-list の refs 明示化"

R12="${TMP}/r12/repo"; mkdir -p "${R12}"
if ! setup_fake_repo "${R12}"; then
  ng "12: 準備できなかった (★ 判定できない)"
else
  # --- 12a/12b: LOOP_SPAWN_LOCK_POLL が 0 / 非数値なら die (メッセージつき) ---
  SPAWN_ENV="LOOP_SPAWN_LOCK_POLL=0"; do_spawn_x "${R12}" --no-exec p0 t
  if [ "${SRC}" -ne 0 ] && has_text "${SERR}" "LOOP_SPAWN_LOCK_POLL" && ! wt_has "${R12}" "repo-p0-t"; then
    ok "12a: LOOP_SPAWN_LOCK_POLL=0 は die した (★ 0 除算での無言終了ではない)"
  else
    ng "12a: rc=${SRC} —— ⚠️ POLL=0 が素通りした (0 除算で無言終了している可能性)"
  fi
  SPAWN_ENV="LOOP_SPAWN_LOCK_POLL=abc"; do_spawn_x "${R12}" --no-exec pn t
  if [ "${SRC}" -ne 0 ] && has_text "${SERR}" "LOOP_SPAWN_LOCK_POLL" && ! wt_has "${R12}" "repo-pn-t"; then
    ok "12b: LOOP_SPAWN_LOCK_POLL=abc (非数値) は die した"
  else
    ng "12b: rc=${SRC} —— ⚠️ 非数値の POLL が素通りした"
  fi

  # --- 12c/12d: LOOP_SPAWN_LOCK_TIMEOUT も同様 ---
  SPAWN_ENV="LOOP_SPAWN_LOCK_TIMEOUT=0"; do_spawn_x "${R12}" --no-exec t0 t
  if [ "${SRC}" -ne 0 ] && has_text "${SERR}" "LOOP_SPAWN_LOCK_TIMEOUT" && ! wt_has "${R12}" "repo-t0-t"; then
    ok "12c: LOOP_SPAWN_LOCK_TIMEOUT=0 は die した"
  else
    ng "12c: rc=${SRC} —— ⚠️ TIMEOUT=0 が素通りした"
  fi
  SPAWN_ENV="LOOP_SPAWN_LOCK_TIMEOUT=-1"; do_spawn_x "${R12}" --no-exec tn t
  if [ "${SRC}" -ne 0 ] && has_text "${SERR}" "LOOP_SPAWN_LOCK_TIMEOUT" && ! wt_has "${R12}" "repo-tn-t"; then
    ok "12d: LOOP_SPAWN_LOCK_TIMEOUT=-1 (負値) は die した"
  else
    ng "12d: rc=${SRC} —— ⚠️ 負値の TIMEOUT が素通りした"
  fi

  # ★ 陽性対照: 正常な値では変わらず動く (⚠️ 検証を厳しくしすぎて通常系まで壊していないか)
  SPAWN_ENV="LOOP_SPAWN_LOCK_POLL=0.1 LOOP_SPAWN_LOCK_TIMEOUT=5"; do_spawn_x "${R12}" --no-exec pok t
  if [ "${SRC}" -eq 0 ] && wt_has "${R12}" "repo-pok-t"; then
    ok "12e: 正常な POLL/TIMEOUT では従来どおり動く (★ 過剰拒否の陰性対照)"
  else
    ng "12e: rc=${SRC} —— ⚠️ 正常値まで拒否している"
  fi
fi

# --- 12f: ⚠️★★★ validate_name の die メッセージが制御文字を生で出さないか ---
#   ★ 7ac と同じ作法 (ESC バイトが残らないこと)。id に ESC を混ぜても英数字以外を弾く
#   `*[!A-Za-z0-9._-]*` の分岐で die するので、そのメッセージが sanitize_disp を通っているか見る。
R12B="${TMP}/r12b/repo"; mkdir -p "${R12B}"
if ! setup_fake_repo "${R12B}"; then
  ng "12f: 準備できなかった (★ 判定できない)"
else
  SPAWN_ENV=""; do_spawn_x "${R12B}" --no-exec "$(printf 'x\033[8mEVIL')" t
  esc_left="$(printf '%s' "${SERR}" | LC_ALL=C tr -dc '\033' | wc -c)"
  esc_left="${esc_left//[[:space:]]/}"
  if [ "${SRC}" -ne 0 ] && [ "${esc_left:-1}" -eq 0 ] && has_text "${SERR}" "EVIL"; then
    ok "12f: ★★★ validate_name の die メッセージから ESC バイトを落とした (sanitize_disp 適用済み)"
  else
    ng "12f: rc=${SRC} / 残った ESC=${esc_left} —— ⚠️ id の値を生で出している"
  fi
fi

# --- 12g: ⚠️★★★ rev-list の refs 明示化 (同名 tag との曖昧さ回避) ---
#   ★ 旧実装は `git rev-list --count "origin/${base}..${base}"` で、同名 tag があると
#   `origin/<base>` 側 (tag と衝突しうる短縮形) の解決が曖昧になり、**未 push 件数を誤って数える**
#   (★ 一次実測: 本来 1 コミットのところ、旧形は warning を出しつつ "0 コミット" と報告した)。
#   ⚠️★★★ 同じシナリオで、local-ahead の `start` を無修飾の `$base` にしていると
#   `git worktree add ... "$start"` が `fatal: ambiguous object name` で落ちた (★ 一次実測)。
#   ★ この経路は P1-J で新設したものなので本タスクで直した (`start="refs/heads/$base"`)。
#   → ★ 件数の診断に加えて、**worktree が作られ HEAD がローカルの sha であること**も見る。
R12C="${TMP}/r12c/repo"; O12C="${TMP}/r12c/origin.git"
if ! setup_origin_repo "${R12C}" "${O12C}"; then
  ng "12g: 準備できなかった (★ 判定できない)"
else
  make_pushed_branch "${R12C}" amb
  add_local_commit "${R12C}" amb
  # ★ ブランチと同名の tag を作る (★ `origin/amb` という短縮参照の解決を曖昧にしうる形)。
  ( cd "${R12C}" && git tag amb main ) >/dev/null 2>&1
  SPAWN_ENV="LOOP_BASE_BRANCH=amb"; do_spawn_x "${R12C}" --no-exec 12g t
  if has_text "${SERR}" "start-choice = local-ahead" && has_text "${SERR}" "未 push の 1 コミット"; then
    ok "12g: ★★★ 同名 tag があっても未 push の件数を正しく (1件) 数えた (refs/heads・refs/remotes 明示の効果)"
  else
    ng "12g: ⚠️ 未 push の件数表示が正しくない (同名 tag で曖昧解決している可能性) / stderr=[${SERR}]"
  fi
  loc12g="$(git -C "${R12C}" rev-parse refs/heads/amb 2>/dev/null || true)"
  head12g="$(git -C "${TMP}/r12c/wt/repo-12g-t" rev-parse HEAD 2>/dev/null || true)"
  if [ "${SRC}" -eq 0 ] && [ -n "${loc12g}" ] && [ "${head12g}" = "${loc12g}" ]; then
    ok "12g: ★★★ 同名 tag があっても local-ahead の worktree を作れ、HEAD がローカルの sha (start を refs/heads で修飾した効果)"
  else
    ng "12g: ⚠️ 同名 tag で worktree を作れない / HEAD がずれている (rc=${SRC} head=${head12g:-なし} local=${loc12g:-なし})"
  fi
fi

# ⚠️ **やっていないこと (LOW・★ 隠さない)**:
#   - origin_sha が「fetch 成功なのに空」になる状態、および `merge-base --is-ancestor` が
#     rc 128 (shallow clone 等) を返す状態は、この一時 repo ハーネスでは**再現できなかった**
#     (rc 128 は shallow clone の追加配線が要り、既存ハーネス (bare origin + full push) の
#     延長では作れない)。★ die メッセージはコードレビューで固定した文言を実装した
#     (このファイル群にある「分岐とは別の異常です」「rc=128・shallow clone 等の可能性」)。

# ── 13. ⚠️★★★ 2026-09-26 Codex /cross-review (P1・LOW 群) の個別対応 ──────
# ⚠️★★★ **何を止めるためにあるのか** (decisions.md 判断 9/10):
#   ★ Codex P1: `git worktree add` 失敗経路が「ロック解放 → abort_worktree」の順だったため、
#     解放直後に**並行する別 spawn**が同じ id/short の worktree/branch を作ると、
#     abort_worktree の後始末がその**他人の worktree/branch**を消しうる。
#   ★ ref の修飾: `start="origin/$base"`（equal/local-behind/no-local）と
#     fetch 失敗・origin 無しの `start="$base"` が無修飾のままだった
#     (⚠️ 後者は同名 tag があると `fatal: ambiguous object name` で実際に落ちる。下の 13a-fetchfail で実測)。
#   ★ CDPATH: LOCK の絶対化 `cd "$d" && pwd` が CDPATH の影響を受ける (下の 13b で実測)。
#   ★ release: 自分のロックか確かめずに `rm -rf` していた (13c)。
#   ★ 巨大な TIMEOUT: awk の `max_i` が数値比較を壊す桁数でも通っていた (13d)。
echo "════════════════════════════════════════"
echo "13. ⚠️★★★ Codex /cross-review 由来の個別対応 (ロック保持順序 / ref 修飾 / CDPATH / release pid 一致 / 巨大 TIMEOUT)"

# --- 13a: ref の修飾 —— base 名と同名の tag があっても各経路が worktree を作れる ---
echo "13a. ⚠️★★★ base 名と同名の tag があっても equal/local-behind/no-local/fetch-失敗 が worktree を作れる"

R13="${TMP}/r13/repo"; O13="${TMP}/r13/origin.git"
if ! setup_origin_repo "${R13}" "${O13}"; then
  ng "13a: origin 付き一時 repo を用意できなかった (★ 判定できない)"
else
  # 13a-eq: 一致 + 同名 tag
  make_pushed_branch "${R13}" tag-eq
  ( cd "${R13}" && git tag tag-eq main ) >/dev/null 2>&1
  SPAWN_ENV="LOOP_BASE_BRANCH=tag-eq"; do_spawn_x "${R13}" --no-exec 13aeq t
  if [ "${SRC}" -eq 0 ] && [ "$(wt_head "${TMP}/r13/wt/repo-13aeq-t")" = "$(origin_tip "${R13}" tag-eq)" ]; then
    ok "13a-eq: 一致 + 同名 tag でも worktree を作れた (HEAD が origin/base と一致)"
  else
    ng "13a-eq: rc=${SRC} —— 同名 tag があると一致状態で worktree を作れない"
  fi

  # 13a-behind: ローカル遅れ + 同名 tag
  make_pushed_branch "${R13}" tag-behind
  add_origin_commit "${O13}" tag-behind
  ( cd "${R13}" && git tag tag-behind main ) >/dev/null 2>&1
  SPAWN_ENV="LOOP_BASE_BRANCH=tag-behind"; do_spawn_x "${R13}" --no-exec 13abehind t
  if [ "${SRC}" -eq 0 ] && [ "$(wt_head "${TMP}/r13/wt/repo-13abehind-t")" = "$(origin_tip "${R13}" tag-behind)" ]; then
    ok "13a-behind: ローカル遅れ + 同名 tag でも worktree を作れた"
  else
    ng "13a-behind: rc=${SRC} —— 同名 tag があるとローカル遅れで worktree を作れない"
  fi

  # 13a-nolocal: ローカルに無い (origin 限定ブランチ) + ローカルにある同名 tag
  ( cd "${R13}" && git tag tag-nolocal main ) >/dev/null 2>&1
  create_origin_only_branch "${O13}" tag-nolocal
  SPAWN_ENV="LOOP_BASE_BRANCH=tag-nolocal"; do_spawn_x "${R13}" --no-exec 13anolocal t
  if [ "${SRC}" -eq 0 ] && [ "$(wt_head "${TMP}/r13/wt/repo-13anolocal-t")" = "$(origin_tip "${R13}" tag-nolocal)" ]; then
    ok "13a-nolocal: ローカルに同名 tag があっても origin 限定ブランチから worktree を作れた"
  else
    ng "13a-nolocal: rc=${SRC} —— 同名 tag があるとローカル無しで worktree を作れない"
  fi
fi

# 13a-fetchfail: ⚠️★★★ fetch 失敗 (無修飾 $base) + 同名 tag —— ★ これは実際に ambiguous で落ちる経路
R13F="${TMP}/r13f/repo"; O13F="${TMP}/r13f/origin.git"
if ! setup_origin_repo "${R13F}" "${O13F}" || ! make_pushed_branch "${R13F}" tag-ff; then
  ng "13a-fetchfail: 準備できなかった (★ 判定できない)"
else
  ( cd "${R13F}" && git tag tag-ff main ) >/dev/null 2>&1
  ( cd "${R13F}" && git remote set-url origin "${TMP}/r13f/no-such-origin.git" ) >/dev/null 2>&1
  SPAWN_ENV="LOOP_BASE_BRANCH=tag-ff"; do_spawn_x "${R13F}" --no-exec 13aff t
  if [ "${SRC}" -eq 0 ] && [ "$(wt_head "${TMP}/r13f/wt/repo-13aff-t")" = "$(tip_of "${R13F}" tag-ff)" ]; then
    ok "13a-fetchfail: ★★★ fetch 失敗 + 同名 tag でもローカル base から worktree を作れた (旧実装は ambiguous で落ちる)"
  else
    ng "13a-fetchfail: rc=${SRC} —— ⚠️★★★ 同名 tag があると fetch 失敗時に worktree を作れない (無修飾 \$base の危険)"
  fi
fi

# --- 13b: ⚠️★★★ CDPATH が一致しうる値でも spawn が正常に完了するか ---
# ⚠️★★★ **なぜ「ロックの待ち」ではなく「正常完了」で見るか** (2026-09-26 に一次実測で発見):
#   ★ CDPATH の一致で `cd` が使われると、bash は **解決したパスを cd 自身が stdout にも書く**
#     (`cd -` と同じ副作用)。→ `$(cd "$dir" && pwd)` は **同じ行が 2 回**入った値になり、
#     ⚠️ 素朴に「待ち切って die したか」で見ると、**この 2 行入り (改行混入) の不正な値のせいで
#     `mkdir` が常に失敗し続けてタイムアウト待ちに落ちる**(原因は CDPATH だが症状は同じ「die」)。
#     ★ 実測: `mkdir "<decoy>/.git\n<decoy>/.git/loop-spawn.lock"` は
#     `mkdir: cannot create directory … No such file or directory` で rc=1。
#   → ★ **正常完了 (rc=0・worktree 作成) するかどうか**で見る: 旧実装は改行混入で `mkdir` が
#     恒久的に失敗し続け待ち切って die する。★ 修正後は `CDPATH=` で無効化しているので
#     普通に (競合なしで) 一発で `mkdir` が成功し、正常完了する。
echo "13b. ⚠️★★★ CDPATH が一致しうる値でも spawn が正常に完了するか (改行混入で mkdir が壊れて die しないか)"

R13B="${TMP}/r13b/repo"; mkdir -p "${R13B}"
DECOY13B="${TMP}/r13b-decoy"; mkdir -p "${DECOY13B}/.git"
if ! setup_fake_repo "${R13B}"; then
  ng "13b: 準備できなかった (★ 判定できない)"
else
  # ⚠️★★★ CDPATH には **デコイ自身** を列挙する (★ bash は "CDPATH エントリ + / + 引数" で探すため、
  #   `cd .git` は `${DECOY13B}/.git` と一致しうる)。
  SPAWN_ENV="CDPATH=${DECOY13B} LOOP_SPAWN_LOCK_TIMEOUT=3 LOOP_SPAWN_LOCK_POLL=0.2"
  do_spawn_x "${R13B}" --no-exec cdp t
  if [ "${SRC}" -eq 0 ] && wt_has "${R13B}" "repo-cdp-t"; then
    ok "13b: ★★★ CDPATH があっても spawn が正常に完了した (★ CDPATH= での無効化が効いている)"
  else
    ng "13b: rc=${SRC} / worktree=$(wt_has "${R13B}" "repo-cdp-t" && echo yes || echo no) —— ⚠️★★★ CDPATH で LOCK の絶対化が壊れている疑い"
  fi
fi

# --- 13c: ⚠️★★★ release_spawn_lock は pid が自分と一致しないロックを消さない ---
echo "13c. ⚠️★★★ release_spawn_lock は pid が自分と一致しないロックを消さないか"

R13C="${TMP}/r13c/repo"; mkdir -p "${R13C}"
if ! setup_fake_repo "${R13C}"; then
  ng "13c: 準備できなかった (★ 判定できない)"
else
  (
    cd "${R13C}" || exit 1
    # ⚠️ `${LOCK}/pid` の読み取りだけを偽装する —— 実ファイルには自分の $$ が書かれているが、
    #   release 時の確認読み取りだけ **別の pid** を返させ、「一致しない」状況を決定論的に作る。
    # ⚠️★★★ CR MEDIUM (2026-09-26 2巡目) の副作用: acquire_spawn_lock 自身が pid を書いた直後に
    #   読み戻して確認するようになったため、成功系路での「${LOCK}/pid」読み取りは
    #   1 回 (release 時) から 2 回 (acquire 直後の自己確認 + release 時) に増えた。
    #   ⚠️ 無条件に偽装すると **acquire 自身の自己確認**まで偽の値を受け取り、
    #   「自分が書いた pid を読み戻せない」と誤って die してしまう (13c が試したい release 側の
    #   分岐に到達できなくなる)。→ ★ 1 回目 (acquire 直後) は本物を素通しし、
    #   2 回目以降 (release) だけ偽装する。
    export FAKECAT13C_N="${TMP}/13c-n"
    printf '0' > "${FAKECAT13C_N}"
    cat() {
      case "$1" in
        */loop-spawn.lock/pid)
          local n
          n="$(command cat "${FAKECAT13C_N}" 2>/dev/null || echo 0)"
          n=$((n + 1))
          printf '%s' "${n}" > "${FAKECAT13C_N}"
          if [ "${n}" -eq 1 ]; then
            command cat "$1"
          else
            printf '424242'
          fi
          return 0 ;;
      esac
      command cat "$@"
    }
    export -f cat
    exec env LOOP_SPAWN_LOCK_TIMEOUT=5 LOOP_SPAWN_LOCK_POLL=0.2 bash scripts/loop-spawn.sh --no-exec 13c t
  ) >"${TMP}/13c.out" 2>"${TMP}/13c.err"
  RC13C=$?
  ERR13C="$(cat "${TMP}/13c.err" 2>/dev/null || true)"
  if [ "${RC13C}" -eq 0 ] && has_text "${ERR13C}" "解放しません" && [ -d "${R13C}/.git/loop-spawn.lock" ]; then
    ok "13c: ★★★ pid 不一致のロックを release が消さず、警告を出した (ロックは残存)"
  else
    ng "13c: rc=${RC13C} / lock 残=$([ -d "${R13C}/.git/loop-spawn.lock" ] && echo yes || echo no) / stderr=[${ERR13C}]"
  fi
  rm -rf "${R13C}/.git/loop-spawn.lock" 2>/dev/null || true
fi

# --- 13d: ⚠️★★★ 巨大な LOOP_SPAWN_LOCK_TIMEOUT は die する (無限待ちに落ちない) ---
# ⚠️★★★ **なぜ競合 (先に置いたロック) を用意するか**: `[ -gt ]` の数値比較が壊れて無効化される
#   バグは `acquire_spawn_lock` の **while ループの中**にしか無い。★ 競合が無いと 1 回目の
#   `mkdir` がそのまま成功してループ本体が 1 度も実行されず、TIMEOUT の値に関係なく
#   一瞬で正常終了してしまう (＝ 検査が何も見ない)。→ ★ 11d と同じ「生きている pid」の
#   ロックを先に置き、実際にループへ入らせてから検証する。
echo "13d. ⚠️★★★ ロックが競合している状況で LOOP_SPAWN_LOCK_TIMEOUT=20 桁でも die するか (待ちが無効化されないか)"

R13D="${TMP}/r13d/repo"; mkdir -p "${R13D}"
if ! setup_fake_repo "${R13D}"; then
  ng "13d: 準備できなかった (★ 判定できない)"
else
  sleep 60 & D13_LIVE_PID=$!
  mkdir -p "${R13D}/.git/loop-spawn.lock" && printf '%s' "${D13_LIVE_PID}" > "${R13D}/.git/loop-spawn.lock/pid"
  # ⚠️★★★ **壁時計タイムアウトで包む** (★ 11g/11h と同じ理由) —— 検査対象そのものが
  #   「無限待ちに落ちる」バグなので、素の呼び出しだと**この検査自身がハングしうる**。
  (
    cd "${R13D}" || exit 1
    exec env LOOP_SPAWN_LOCK_TIMEOUT=12345678901234567890 LOOP_SPAWN_LOCK_POLL=0.2 bash scripts/loop-spawn.sh --no-exec 13d t
  ) >"${TMP}/13d.out" 2>"${TMP}/13d.err" &
  d13pid=$!
  waited=0
  while kill -0 "${d13pid}" 2>/dev/null && [ "${waited}" -lt 10 ]; do
    sleep 1; waited=$((waited + 1))
  done
  if kill -0 "${d13pid}" 2>/dev/null; then
    kill -9 "${d13pid}" 2>/dev/null || true
    wait "${d13pid}" 2>/dev/null || true
    ng "13d: ⚠️★★★ ${waited} 秒待ってもプロセスが終わらなかった (★ 巨大な TIMEOUT で無限待ちに落ちている疑い)"
  else
    wait "${d13pid}"; d13rc=$?
    d13err="$(cat "${TMP}/13d.err" 2>/dev/null || true)"
    if [ "${d13rc}" -ne 0 ] && has_text "${d13err}" "待ち回数" && [ "${waited}" -le 3 ] && ! wt_has "${R13D}" "repo-13d-t"; then
      ok "13d: ★★★ 競合下でも 20 桁の LOCK_TIMEOUT は (待たずに) 即 die した (${waited} 秒で終了)"
    else
      ng "13d: rc=${d13rc} / ${waited} 秒で終了 —— 期待した die メッセージが無い、または待ってしまっている"
    fi
  fi
  kill "${D13_LIVE_PID}" 2>/dev/null || true
fi

# --- 13e: ⚠️★★★ Codex P1: worktree add 失敗の後始末中もロックを保持しているか ---
echo "13e. ⚠️★★★ Codex P1: worktree add 失敗の後始末 (abort_worktree) 中もロックを保持しているか"

R13E="${TMP}/r13e/repo"; mkdir -p "${R13E}"
if ! setup_fake_repo "${R13E}"; then
  ng "13e: 準備できなかった (★ 判定できない)"
else
  mkdir -p "${TMP}/r13e/wt"
  echo "blocker" > "${TMP}/r13e/wt/repo-fy-t"   # ★ worktree の作成先を実ファイルで塞ぎ git worktree add を失敗させる (11b と同じ作法)
  (
    cd "${R13E}" || exit 1
    OBS="${TMP}/13e-observed.txt"
    export OBS
    # ⚠️ `git worktree remove --force <wtdir>` (＝ abort_worktree の最初の一手) だけを横取りし、
    #   その時点での LOCK の状態を観測してから、実際の git へ渡す。
    git() {
      if [ "$1" = "worktree" ] && [ "$2" = "remove" ] && [ "$3" = "--force" ]; then
        local gcd gcd_abs lockdir pidval
        gcd="$(command git rev-parse --git-common-dir 2>/dev/null)"
        gcd_abs="$(CDPATH= cd -P -- "${gcd}" 2>/dev/null && pwd -P)"
        lockdir="${gcd_abs}/loop-spawn.lock"
        if [ -d "${lockdir}" ]; then
          pidval="$(command cat "${lockdir}/pid" 2>/dev/null || true)"
          if [ "${pidval}" = "$$" ]; then
            printf 'held-self' > "${OBS}"
          else
            printf 'held-other:%s' "${pidval}" > "${OBS}"
          fi
        else
          printf 'absent' > "${OBS}"
        fi
      fi
      command git "$@"
    }
    export -f git
    exec env bash scripts/loop-spawn.sh --no-exec fy t
  ) >"${TMP}/13e.out" 2>"${TMP}/13e.err"
  RC13E=$?
  OBS13E="$(cat "${TMP}/13e-observed.txt" 2>/dev/null || echo "(観測なし)")"
  if [ "${RC13E}" -ne 0 ] && [ "${OBS13E}" = "held-self" ]; then
    ok "13e: ★★★ abort_worktree の最初の一手の時点でロックは自分保持のまま (観測=${OBS13E})"
  else
    ng "13e: rc=${RC13E} / 観測=[${OBS13E}] —— ⚠️★★★ 後始末の前にロックが解放されている疑い (Codex P1 の再発)"
  fi
fi

# --- 13f: ⚠️ reap 用ロックの残骸 (mkdir(.reap) と rmdir(.reap) の間の中断) を EXIT trap が片づけるか ---
echo "13f. ⚠️ reap 用ロックの残骸を EXIT trap が片づけるか (中断を SIGTERM の自己送信で模す)"

R13G="${TMP}/r13g/repo"; mkdir -p "${R13G}"
if ! setup_fake_repo "${R13G}"; then
  ng "13f: 準備できなかった (★ 判定できない)"
else
  true & dpid13f=$!; wait "${dpid13f}" 2>/dev/null || true   # ★ 確実に死んでいる pid (11e と同じ作法)
  mkdir -p "${R13G}/.git/loop-spawn.lock" && printf '%s' "${dpid13f}" > "${R13G}/.git/loop-spawn.lock/pid"
  (
    cd "${R13G}" || exit 1
    export FAKECAT13F_N="${TMP}/13f-n"
    printf '0' > "${FAKECAT13F_N}"
    # ⚠️ `${LOCK}/pid` の 2 回目の読み取り (＝ reap 内の `reap_pid=...`。mkdir(.reap) は既に成功済みで
    #   rmdir(.reap) 前) のタイミングで自分自身へ SIGTERM を送り「中断」を模す。
    #   ⚠️ **本当の 2 プロセス競合ではない** (★ 隠さない。11i/11j と同じ限界)。
    cat() {
      case "$1" in
        */loop-spawn.lock/pid)
          local n
          n="$(command cat "${FAKECAT13F_N}" 2>/dev/null || echo 0)"
          n=$((n + 1))
          printf '%s' "${n}" > "${FAKECAT13F_N}"
          if [ "${n}" -eq 2 ]; then
            kill -TERM $$
          fi
          command cat "$@"
          return 0 ;;
      esac
      command cat "$@"
    }
    export -f cat
    exec env LOOP_SPAWN_LOCK_TIMEOUT=3 LOOP_SPAWN_LOCK_POLL=0.2 bash scripts/loop-spawn.sh --no-exec 13f t
  ) >"${TMP}/13f.out" 2>"${TMP}/13f.err"
  RC13F=$?
  # ⚠️★★★ CR MEDIUM (2026-09-26 2巡目): 「.reap が残っていない」だけでは、SIGTERM が
  #   mkdir(.reap)/rmdir(.reap) の間に間に合わず、**ただ正常終了しただけ**の場合も同じ結果になり
  #   空振りしうる (★ 正常終了でも通常の `rmdir "${LOCK}.reap" 2>/dev/null && REAP_HELD=0` が
  #   .reap を消すため、「残っていない」は中断の証拠にならない)。
  #   → ★ 「本当に中断されたこと」も見る: 中断されたなら非 0 (SIGTERM なら 143 等) で終了し、
  #     worktree もまだ作られていないはず (mkdir(.reap) の時点では git worktree add に未到達)。
  if [ "${RC13F}" -ne 0 ] && ! wt_has "${R13G}" "repo-13f-t" \
     && [ ! -d "${R13G}/.git/loop-spawn.lock.reap" ]; then
    ok "13f: ★★★ 中断 (rc=${RC13F}・worktree 未作成) の状況で .reap の残骸も残らなかった"
  else
    ng "13f: rc=${RC13F} / worktree=$(wt_has "${R13G}" "repo-13f-t" && echo yes || echo no) / .reap 残=$([ -d "${R13G}/.git/loop-spawn.lock.reap" ] && echo yes || echo no) —— ⚠️ 中断が実際に起きた証拠が無い (空振りの疑い)"
  fi
fi
# ⚠️ **やっていないこと** (★ 隠さない): 13f は **本当の 2 プロセス競合による中断を再現していない**
#   (★ SIGTERM の自己送信という決定論的な代替。11i/11j の限界と同じ)。

# --- 13f2: ⚠️★★★ 変異テスト —— release_spawn_lock の REAP_HELD 片づけを潰すと 13f が赤くなるか ---
#   ★ 13f と同じ中断シナリオを再生し、EXIT trap 側の後始末 (`if [ "${REAP_HELD}" -eq 1 ]; then rmdir …`)
#   を no-op にする。★ 中断が実際に起きているなら、この変異で .reap の残骸が残るはず。
echo "13f2. ⚠️★★★ 変異テスト —— release_spawn_lock の REAP_HELD 片づけを潰すと 13f の状況で .reap が残るか"

MUT13F2="${TMP}/mut13f2-loop-spawn.sh"
sed 's/if \[ "\${REAP_HELD}" -eq 1 \]; then/if false; then/' "${SPAWN_SH}" > "${MUT13F2}"
mut13f2_src="$(grep -cF 'if [ "${REAP_HELD}" -eq 1 ]; then' "${SPAWN_SH}" 2>/dev/null)" || mut13f2_src=0
mut13f2_left="$(grep -cF 'if [ "${REAP_HELD}" -eq 1 ]; then' "${MUT13F2}" 2>/dev/null)" || mut13f2_left=0
if [ "${mut13f2_src:-0}" -ne 1 ] || [ "${mut13f2_left:-0}" -ne 0 ]; then
  ng "13f2: 変異を当てられない (src=${mut13f2_src} / mut=${mut13f2_left}) —— ★ REAP_HELD 片づけの書き方が変わった → ⚠️ 検査不能"
else
  R13G2="${TMP}/r13g2/repo"; mkdir -p "${R13G2}"
  if ! setup_fake_repo "${R13G2}" "${MUT13F2}"; then
    ng "13f2: 準備できなかった (★ 判定できない)"
  else
    true & dpid13f2=$!; wait "${dpid13f2}" 2>/dev/null || true
    mkdir -p "${R13G2}/.git/loop-spawn.lock" && printf '%s' "${dpid13f2}" > "${R13G2}/.git/loop-spawn.lock/pid"
    (
      cd "${R13G2}" || exit 1
      export FAKECAT13F2_N="${TMP}/13f2-n"
      printf '0' > "${FAKECAT13F2_N}"
      cat() {
        case "$1" in
          */loop-spawn.lock/pid)
            local n
            n="$(command cat "${FAKECAT13F2_N}" 2>/dev/null || echo 0)"
            n=$((n + 1))
            printf '%s' "${n}" > "${FAKECAT13F2_N}"
            if [ "${n}" -eq 2 ]; then
              kill -TERM $$
            fi
            command cat "$@"
            return 0 ;;
        esac
        command cat "$@"
      }
      export -f cat
      exec env LOOP_SPAWN_LOCK_TIMEOUT=3 LOOP_SPAWN_LOCK_POLL=0.2 bash scripts/loop-spawn.sh --no-exec 13f2 t
    ) >"${TMP}/13f2.out" 2>"${TMP}/13f2.err"
    if [ -d "${R13G2}/.git/loop-spawn.lock.reap" ]; then
      ok "13f2: ★★★ REAP_HELD の片づけを潰すと .reap の残骸が残った (★ 13f は空振りしていない)"
    else
      ng "13f2: 潰しても .reap の残骸が残らなかった (⚠️★★★ 13f が REAP_HELD 片づけ以外の理由で緑になっている可能性、または中断自体が起きていない可能性)"
    fi
  fi
fi

# --- 13g-13i: ⚠️★★★ 変異テスト —— 13e/13c/13d の心臓部を潰したら赤くなるか ---
echo "13g-13i. ⚠️★★★ 変異テスト —— ロック保持順序 / release pid 一致 / max_i 桁数上限を潰したら赤くなるか"

# 13g: item 1 の心臓部 (worktree add 失敗時に abort_worktree の前で明示解放しない) を潰す
#   → 旧実装のとおり abort_worktree の直前に release_spawn_lock を戻すと、13e が観測する時点で
#   ロックは既に解放されているはず (観測=absent になる)。
MUT13G="${TMP}/mut13g-loop-spawn.sh"
sed 's/  abort_worktree "git worktree add に失敗しました: branch=\$branch \/ worktree=\$wtdir \/ start=\$start"/  release_spawn_lock\n  abort_worktree "git worktree add に失敗しました: branch=$branch \/ worktree=$wtdir \/ start=$start"/' \
  "${SPAWN_SH}" > "${MUT13G}"
mut13g_src="$(grep -cF 'abort_worktree "git worktree add に失敗しました: branch=$branch / worktree=$wtdir / start=$start"' "${SPAWN_SH}" 2>/dev/null)" || mut13g_src=0
mut13g_mutlines="$(grep -c 'release_spawn_lock' "${MUT13G}" 2>/dev/null)" || mut13g_mutlines=0
mut13g_srclines="$(grep -c 'release_spawn_lock' "${SPAWN_SH}" 2>/dev/null)" || mut13g_srclines=0
if [ "${mut13g_src:-0}" -ne 1 ] || [ "${mut13g_mutlines}" -le "${mut13g_srclines}" ]; then
  ng "13g: 変異を当てられない (src 一致=${mut13g_src} / release_spawn_lock 行数 src=${mut13g_srclines} mut=${mut13g_mutlines}) —— ★ 書き方が変わった → ⚠️ 検査不能"
else
  R13H="${TMP}/r13h/repo"; mkdir -p "${R13H}"
  if ! setup_fake_repo "${R13H}" "${MUT13G}"; then
    ng "13g: 準備できなかった (★ 判定できない)"
  else
    mkdir -p "${TMP}/r13h/wt"
    echo "blocker" > "${TMP}/r13h/wt/repo-fz-t"
    (
      cd "${R13H}" || exit 1
      OBS="${TMP}/13g-observed.txt"; export OBS
      git() {
        if [ "$1" = "worktree" ] && [ "$2" = "remove" ] && [ "$3" = "--force" ]; then
          local gcd gcd_abs lockdir
          gcd="$(command git rev-parse --git-common-dir 2>/dev/null)"
          gcd_abs="$(CDPATH= cd -P -- "${gcd}" 2>/dev/null && pwd -P)"
          lockdir="${gcd_abs}/loop-spawn.lock"
          if [ -d "${lockdir}" ]; then printf 'held' > "${OBS}"; else printf 'absent' > "${OBS}"; fi
        fi
        command git "$@"
      }
      export -f git
      exec env bash scripts/loop-spawn.sh --no-exec fz t
    ) >"${TMP}/13g.out" 2>"${TMP}/13g.err"
    OBS13G="$(cat "${TMP}/13g-observed.txt" 2>/dev/null || echo "(観測なし)")"
    if [ "${OBS13G}" = "absent" ]; then
      ok "13g: ★★★ 明示解放を戻すと後始末の時点でロックが既に無かった (★ 13e は空振りしていない)"
    else
      ng "13g: 観測=[${OBS13G}] —— ⚠️★★★ 変異を当てても held のままだった (13e が見ている経路と違う可能性)"
    fi
  fi
fi

# 13h: item 4 の心臓部 (release 時の pid 一致確認) を潰す —— 常に消す形に戻す
MUT13H="${TMP}/mut13h-loop-spawn.sh"
sed 's/if \[ "\${held_pid:-}" = "\$\$" \]; then/if true; then/' "${SPAWN_SH}" > "${MUT13H}"
mut13h_src="$(grep -cF 'if [ "${held_pid:-}" = "$$" ]; then' "${SPAWN_SH}" 2>/dev/null)" || mut13h_src=0
mut13h_left="$(grep -cF 'if [ "${held_pid:-}" = "$$" ]; then' "${MUT13H}" 2>/dev/null)" || mut13h_left=0
if [ "${mut13h_src:-0}" -ne 1 ] || [ "${mut13h_left:-0}" -ne 0 ]; then
  ng "13h: 変異を当てられない (src=${mut13h_src} / mut=${mut13h_left}) —— ★ pid 一致確認の書き方が変わった → ⚠️ 検査不能"
else
  R13I="${TMP}/r13i/repo"; mkdir -p "${R13I}"
  if ! setup_fake_repo "${R13I}" "${MUT13H}"; then
    ng "13h: 準備できなかった (★ 判定できない)"
  else
    (
      cd "${R13I}" || exit 1
      # ⚠️★★★ CR MEDIUM (2026-09-26 2巡目) の副作用: 13c と同じ理由で、acquire 直後の
      #   自己確認 (1 回目) は本物を素通しし、release 時 (2 回目以降) だけ偽装する。
      export FAKECAT13H_N="${TMP}/13h-n"
      printf '0' > "${FAKECAT13H_N}"
      cat() {
        case "$1" in
          */loop-spawn.lock/pid)
            local n
            n="$(command cat "${FAKECAT13H_N}" 2>/dev/null || echo 0)"
            n=$((n + 1))
            printf '%s' "${n}" > "${FAKECAT13H_N}"
            if [ "${n}" -eq 1 ]; then
              command cat "$1"
            else
              printf '424242'
            fi
            return 0 ;;
        esac
        command cat "$@"
      }
      export -f cat
      exec env LOOP_SPAWN_LOCK_TIMEOUT=5 LOOP_SPAWN_LOCK_POLL=0.2 bash scripts/loop-spawn.sh --no-exec 13h t
    ) >"${TMP}/13h.out" 2>"${TMP}/13h.err"
    if [ ! -d "${R13I}/.git/loop-spawn.lock" ]; then
      ok "13h: ★★★ pid 一致確認を潰すと、pid 不一致でもロックを消してしまった (★ 13c は空振りしていない)"
    else
      ng "13h: 潰してもロックが残った (⚠️★★★ 13c が pid 一致確認以外の理由で残っている可能性)"
    fi
  fi
fi

# 13i: item 6 の心臓部 (max_i の桁数上限) を潰す —— 20 桁でも die しなくなるはず
MUT13I="${TMP}/mut13i-loop-spawn.sh"
sed 's/if \[ "\${#max_i}" -gt 9 \]; then/if false; then/' "${SPAWN_SH}" > "${MUT13I}"
mut13i_src="$(grep -cF 'if [ "${#max_i}" -gt 9 ]; then' "${SPAWN_SH}" 2>/dev/null)" || mut13i_src=0
mut13i_left="$(grep -cF 'if [ "${#max_i}" -gt 9 ]; then' "${MUT13I}" 2>/dev/null)" || mut13i_left=0
if [ "${mut13i_src:-0}" -ne 1 ] || [ "${mut13i_left:-0}" -ne 0 ]; then
  ng "13i: 変異を当てられない (src=${mut13i_src} / mut=${mut13i_left}) —— ★ 桁数上限の書き方が変わった → ⚠️ 検査不能"
else
  R13J="${TMP}/r13j/repo"; mkdir -p "${R13J}"
  if ! setup_fake_repo "${R13J}" "${MUT13I}"; then
    ng "13i: 準備できなかった (★ 判定できない)"
  else
    # ⚠️★★★ 13d と同じ理由で **競合 (先に置いたロック) が無いとループ本体に入らず、
    #   潰した行を一度も通らないまま一瞬で正常終了する** (＝ 検査が何も見ない)。
    sleep 60 & I13_LIVE_PID=$!
    mkdir -p "${R13J}/.git/loop-spawn.lock" && printf '%s' "${I13_LIVE_PID}" > "${R13J}/.git/loop-spawn.lock/pid"
    (
      cd "${R13J}" || exit 1
      exec env LOOP_SPAWN_LOCK_TIMEOUT=12345678901234567890 LOOP_SPAWN_LOCK_POLL=0.2 bash scripts/loop-spawn.sh --no-exec 13i t
    ) >"${TMP}/13i.out" 2>"${TMP}/13i.err" &
    i13pid=$!
    waited=0
    while kill -0 "${i13pid}" 2>/dev/null && [ "${waited}" -lt 8 ]; do
      sleep 1; waited=$((waited + 1))
    done
    if kill -0 "${i13pid}" 2>/dev/null; then
      kill -9 "${i13pid}" 2>/dev/null || true
      wait "${i13pid}" 2>/dev/null || true
      ok "13i: ★★★ 桁数上限を潰すと 20 桁の TIMEOUT + 競合下で ${waited} 秒待ってもプロセスが終わらなかった (★ 13d は空振りしていない)"
    else
      wait "${i13pid}"; i13rc=$?
      ng "13i: 潰しても ${waited} 秒で終了した (rc=${i13rc}) (⚠️★★★ 13d が桁数上限以外の理由で die している可能性)"
    fi
    kill "${I13_LIVE_PID}" 2>/dev/null || true
  fi
fi

# ── 14. ⚠️★★★ 2026-09-26 Codex /cross-review (2巡目) の個別対応 ──────
# ⚠️★★★ **何を止めるためにあるのか**:
#   ★ CR MEDIUM: acquire_spawn_lock が pid の書き込み失敗を確かめずに LOCK_HELD=1 にしていた。
#     release_spawn_lock は「pid が自分と一致するときだけ解放する」ので、書き込みに失敗すると
#     ロックが永久に残り、以後の spawn が全部タイムアウトで死ぬ。
#   ★ CR LOW: `local_ref_or_raw` は、ローカルに base が無いとき無修飾の値をそのまま返していた。
#     fetch 失敗・origin 無しの経路でこれが使われると、同名の tag があれば worktree add が
#     **黙って** tag を start にする (branch が無いので ambiguous エラーにもならない)。
echo "════════════════════════════════════════"
echo "14. ⚠️★★★ Codex /cross-review 2巡目: pid 書き込み確認 / 無修飾 base の die"

# --- 14a: pid の書き込みに失敗すると die し、ロックディレクトリが残らない ---
echo "14a. ⚠️★★★ CR MEDIUM: pid を書き込めない状況では die し、ロックディレクトリを残さないか"

R14A="${TMP}/r14a/repo"; mkdir -p "${R14A}"
if ! setup_fake_repo "${R14A}"; then
  ng "14a: 準備できなかった (★ 判定できない)"
else
  (
    cd "${R14A}" || exit 1
    # ⚠️ mkdir を shadow し、loop-spawn.lock の mkdir が成功した直後に
    #   pid の位置へ **ディレクトリ**を先回りして置く (★ 以後の `> .../pid` は
    #   EISDIR で必ず失敗する)。
    #   ⚠️ 実測: Windows/git-bash では umask/chmod によるパーミッション遮断が
    #   所有者に対して効かない (umask 0200 で mkdir しても drwxr-xr-x のままだった) ので、
    #   パーミッションではなくこの形で決定論的に再現する。
    mkdir() {
      case "$1" in
        */loop-spawn.lock)
          command mkdir "$1" || return $?
          command mkdir "$1/pid"
          return 0
          ;;
      esac
      command mkdir "$@"
    }
    export -f mkdir
    exec env bash scripts/loop-spawn.sh --no-exec 14a t
  ) >"${TMP}/14a.out" 2>"${TMP}/14a.err"
  RC14A=$?
  ERR14A="$(cat "${TMP}/14a.err" 2>/dev/null || true)"
  if [ "${RC14A}" -ne 0 ] && ! wt_has "${R14A}" "repo-14a-t" \
     && [ ! -d "${R14A}/.git/loop-spawn.lock" ] && has_text "${ERR14A}" "pid を書き込めませんでした"; then
    ok "14a: ★★★ pid を書き込めない状況で die し、ロックディレクトリを残さなかった"
  else
    ng "14a: rc=${RC14A} / worktree 残=$(wt_has "${R14A}" "repo-14a-t" && echo yes || echo no) / lock 残=$([ -d "${R14A}/.git/loop-spawn.lock" ] && echo yes || echo no) / stderr=[${ERR14A}]"
  fi
fi

# --- 14b: ⚠️★★★ 変異テスト —— 読み戻し確認を消すと 14a の状況でロックが残ってしまうか ---
MUT14B="${TMP}/mut14b-loop-spawn.sh"
sed 's/if \[ "\${written_pid:-}" != "\$\$" \]; then/if false; then/' "${SPAWN_SH}" > "${MUT14B}"
mut14b_src="$(grep -cF 'if [ "${written_pid:-}" != "$$" ]; then' "${SPAWN_SH}" 2>/dev/null)" || mut14b_src=0
mut14b_left="$(grep -cF 'if [ "${written_pid:-}" != "$$" ]; then' "${MUT14B}" 2>/dev/null)" || mut14b_left=0
if [ "${mut14b_src:-0}" -ne 1 ] || [ "${mut14b_left:-0}" -ne 0 ]; then
  ng "14b: 変異を当てられない (src=${mut14b_src} / mut=${mut14b_left}) —— ★ 読み戻し確認の書き方が変わった → ⚠️ 検査不能"
else
  R14B="${TMP}/r14b/repo"; mkdir -p "${R14B}"
  if ! setup_fake_repo "${R14B}" "${MUT14B}"; then
    ng "14b: 準備できなかった (★ 判定できない)"
  else
    (
      cd "${R14B}" || exit 1
      mkdir() {
        case "$1" in
          */loop-spawn.lock)
            command mkdir "$1" || return $?
            command mkdir "$1/pid"
            return 0
            ;;
        esac
        command mkdir "$@"
      }
      export -f mkdir
      exec env bash scripts/loop-spawn.sh --no-exec 14b t
    ) >"${TMP}/14b.out" 2>"${TMP}/14b.err"
    if [ -d "${R14B}/.git/loop-spawn.lock" ]; then
      ok "14b: ★★★ 読み戻し確認を消すと pid を書けなくてもロックが残った (★ 14a は空振りしていない)"
    else
      ng "14b: 潰してもロックが残らなかった (⚠️★★★ 14a が読み戻し確認以外の理由で残っている可能性)"
    fi
  fi
fi

# --- 14c: ⚠️★★★ CR LOW: origin 無し + base と同名の tag だけ → die し worktree/branch を作らない ---
echo "14c-14d. ⚠️★★★ CR LOW: ローカルに base が無く origin も無い/fetch 失敗 + 同名 tag → die するか"

R14C="${TMP}/r14c/repo"; mkdir -p "${R14C}"
if ! setup_fake_repo "${R14C}"; then
  ng "14c: 準備できなかった (★ 判定できない)"
else
  # ★ base と同名の tag だけを作る (★ branch は作らない —— これが起票の危険な経路)。
  ( cd "${R14C}" && git tag only-tag main ) >/dev/null 2>&1
  SPAWN_ENV="LOOP_BASE_BRANCH=only-tag"; do_spawn_x "${R14C}" --no-exec 14c t
  if [ "${SRC}" -ne 0 ] && ! wt_has "${R14C}" "repo-14c-t" && ! branch_exists "${R14C}" "loop/14c-t" \
     && has_text "${SERR}" "remote からも取得できません"; then
    ok "14c: ★★★ origin 無し + 同名 tag のみで die し、worktree も branch も作らなかった"
  else
    ng "14c: rc=${SRC} / worktree=$(wt_has "${R14C}" "repo-14c-t" && echo yes || echo no) —— ⚠️★★★ 同名 tag から黙って worktree を切った疑い"
  fi
fi

# --- 14d: fetch 失敗 + 同名 tag (origin はあるが取得できない) → die ---
R14D="${TMP}/r14d/repo"; O14D="${TMP}/r14d/origin.git"
if ! setup_origin_repo "${R14D}" "${O14D}"; then
  ng "14d: 準備できなかった (★ 判定できない)"
else
  ( cd "${R14D}" && git tag only-tag-2 main ) >/dev/null 2>&1
  ( cd "${R14D}" && git remote set-url origin "${TMP}/r14d/no-such-origin.git" ) >/dev/null 2>&1
  SPAWN_ENV="LOOP_BASE_BRANCH=only-tag-2"; do_spawn_x "${R14D}" --no-exec 14d t
  if [ "${SRC}" -ne 0 ] && ! wt_has "${R14D}" "repo-14d-t" && ! branch_exists "${R14D}" "loop/14d-t" \
     && has_text "${SERR}" "remote からも取得できません"; then
    ok "14d: ★★★ fetch 失敗 + 同名 tag のみで die し、worktree も branch も作らなかった"
  else
    ng "14d: rc=${SRC} / worktree=$(wt_has "${R14D}" "repo-14d-t" && echo yes || echo no) —— ⚠️★★★ 同名 tag から黙って worktree を切った疑い"
  fi
fi

# --- 14e: ⚠️★★★ 変異テスト —— local_ref_or_raw_die を無修飾値に戻すと 14c/14d が危険な成功をするか ---
MUT14E="${TMP}/mut14e-loop-spawn.sh"
sed 's/local_ref_or_raw_die "\$1"/printf '"'"'%s'"'"' "$1"/' "${SPAWN_SH}" > "${MUT14E}"
mut14e_src="$(grep -cF 'local_ref_or_raw_die "$1"' "${SPAWN_SH}" 2>/dev/null)" || mut14e_src=0
mut14e_left="$(grep -cF 'local_ref_or_raw_die "$1"' "${MUT14E}" 2>/dev/null)" || mut14e_left=0
if [ "${mut14e_src:-0}" -ne 1 ] || [ "${mut14e_left:-0}" -ne 0 ]; then
  ng "14e: 変異を当てられない (src=${mut14e_src} / mut=${mut14e_left}) —— ★ die 呼び出しの書き方が変わった → ⚠️ 検査不能"
else
  R14E="${TMP}/r14e/repo"; mkdir -p "${R14E}"
  if ! setup_fake_repo "${R14E}" "${MUT14E}"; then
    ng "14e: 準備できなかった (★ 判定できない)"
  else
    ( cd "${R14E}" && git tag only-tag main ) >/dev/null 2>&1
    SPAWN_ENV="LOOP_BASE_BRANCH=only-tag"; do_spawn_x "${R14E}" --no-exec 14e t
    if [ "${SRC}" -eq 0 ] && wt_has "${R14E}" "repo-14e-t"; then
      ok "14e: ★★★ die を無修飾値に戻すと、同名 tag から黙って worktree を切ってしまった (★ 14c/14d は空振りしていない)"
    else
      ng "14e: 潰しても rc=${SRC} で止まった (⚠️★★★ 14c/14d が die 呼び出し以外の理由で止まっている可能性)"
    fi
  fi
fi

echo "════════════════════════════════════════"
echo "PASS=${PASS}  FAIL=${FAIL}"
FINISHED=1
[ "${FAIL}" -eq 0 ] || exit 1
exit 0
