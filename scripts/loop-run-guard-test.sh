#!/usr/bin/env bash
# loop-run-guard-test.sh — `scripts/loop-run.sh` の 3 つのガードの検査。
#
# ★ 対象（★ 2026-09-20 追加・`.steering/20260920-loop-foundation-fixes/`）:
#   B. **ブランチ検査** (`ensure_branch`) —— ⚠️ 起票 10 の是正。worktree 隔離の**境界**。
#   S. **Status フィルタ** (`issue_status` / `ALL` の決定) —— ⚠️ 判断 26 の申し送り。
#   D. **`permission_denials` の内訳** —— ⚠️ 起票 3。
#
# ⚠️★★★ **「正常なら緑」だけ試さない**（★ `verify-before-claiming` ルール 5b / 6）。
#   ★ B2 が **陰性対照**である: ⚠️ 逸脱しない stub でも blocked になるなら、
#     B1 / B3 の「blocked になった」は**何も検査していない緑**になる。
#
# ⚠️★★★ **この検査が見ていないもの**（★ 明示する。`docs/loop-engineering.md` 逐語の裏返し）:
#   1. ★ **deny が実際に拒否するか**は 1 行も見ていない —— 権限判定は Claude Code の
#      ランタイム内にあり、**stub の `claude` では再現できない**。
#      → ★ 実測は `.steering/20260920-loop-foundation-fixes/measurements.md` (M1 / M2 / M3)。
#      ⚠️ **M3 は deny 9 件でも `git -C . checkout main` が通ることを実測している**。
#        ★ だから deny は多層防御であり、**境界は本検査 B1〜B3 が見ているブランチ検査**である。
#   2. ★ `permission_mode` を `auto` / `bypassPermissions` へ昇格させた場合。★ 測っていない。
#   3. ⚠️ **`verify_level: recheck` の `run_watchdog` セッションそのもの**は 1 度も起動していない
#      （★ stub の issue はすべて `parse`）。★ B4 が押さえているのは
#      **`issue_done` 直前の検査**であり、⚠️ watchdog が逸脱する経路は
#      「verify の最中に逸脱する」形で*代用*している（★ 同じ 1 行が両方を拾う）。
#   4. ★ 並列実行 (`parallel > 1`) での events の競合。★ 1 本でしか回していない。
#   5. ⚠️ **`git restore --source=<other> -- .` のような HEAD を動かさない内容の差し替え**。
#      ★ `ensure_branch` は原理的に拾えない（★ B5 が見ているのは HEAD が動く形だけ）。
#   6. ★ `_loop-artifacts/` の 14 日 prune と、`mkdir -p` 失敗時の「(保存できず)」経路。
#
# ⚠️★★★ **B1〜B5 / S1〜S8 / D1〜D2 は突然変異で赤くなることを確認済み**（2026-09-20・計 6 種）。
#   ★ 詳細は `.steering/20260920-loop-foundation-fixes/measurements.md`。
#
# Usage: bash scripts/loop-run-guard-test.sh
# Exit:  0 = 全件合格 / 1 = 不合格あり / 2 = ⚠️ 検査できなかった
set -uo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"
RUN_SH="${REPO_ROOT}/scripts/loop-run.sh"
SPAWN_SH="${REPO_ROOT}/scripts/loop-spawn.sh"
DENY_SH="${REPO_ROOT}/scripts/loop-worktree-deny.sh"

PASS=0; FAIL=0
ok() { echo "  OK   $1"; PASS=$((PASS + 1)); }
ng() { echo "  NG   $1"; FAIL=$((FAIL + 1)); }

command -v jq >/dev/null 2>&1 || { echo "jq が無いので検査できない (★ 判定しない)"; exit 2; }
for f in "${RUN_SH}" "${SPAWN_SH}" "${DENY_SH}"; do
  [ -f "${f}" ] || { echo "$(basename "${f}") が無い"; exit 2; }
done

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

# ---------- 一時 repo の用意 ----------
# ★ `loop-worktree-deny-test.sh` §6 の `setup_loop_repo` と同じ作法。
#   ⚠️ `claude` を stub に差し替えて `loop-run.sh` を**実際に回し**、events を読んで判定する。
#   ★ stub は **worktree を cwd として**起動されるので、
#     `git checkout` をさせれば起票 10 の実測をそのまま再現できる。
setup_repo() { # setup_repo <repo-dir> <claude-stub-の本体> [denials-json] [verify.test のコマンド]
  local r="$1" stub="$2" denials="${3:-[]}" vtest="${4:-true}"
  mkdir -p "${r}/scripts" "${r}/.steering/task/issues" "${r}/stub"
  cp "${SPAWN_SH}" "${r}/scripts/loop-spawn.sh"
  cp "${DENY_SH}"  "${r}/scripts/loop-worktree-deny.sh"
  cp "${RUN_SH}"   "${r}/scripts/loop-run.sh"
  { printf '#!/usr/bin/env bash\n'; printf '%s\n' "${stub}"
    printf 'printf "%s\\n"\n' \
      "{\\\"subtype\\\":\\\"success\\\",\\\"total_cost_usd\\\":0,\\\"usage\\\":{\\\"input_tokens\\\":1,\\\"output_tokens\\\":1},\\\"permission_denials\\\":${denials}}"
  } > "${r}/stub/claude"
  chmod +x "${r}/stub/claude"

  # ★ 001 = 通常 / 002 = Status blocked / 003 = Status 節なし / 004 = 002 に依存 (★ 回帰の予防 S4)
  cat > "${r}/.steering/task/issues/001.md" <<'I1'
# Issue 001: stub
verify_level: parse
## Goal
stub
## Dependencies
## Status

I1
  cat > "${r}/.steering/task/issues/002.md" <<'I2'
# Issue 002: stub (blocked)
verify_level: parse
## Goal
stub
## Dependencies
## Status

blocked（★ 実装フェーズの設計議論待ち。注釈が続いても前方一致で判定できること）
I2
  cat > "${r}/.steering/task/issues/003.md" <<'I3'
# Issue 003: stub (## Status 節そのものが無い)
verify_level: parse
## Goal
stub
## Dependencies
I3
  cat > "${r}/.steering/task/issues/004.md" <<'I4'
# Issue 004: stub (blocked な 002 に依存する)
verify_level: parse
## Goal
stub
## Dependencies
- 002
## Status

I4
  # ⚠️★★★ 005 = **装飾つきの blocked**（★ `code-reviewer` MEDIUM・2026-09-20）。
  #   ★ 実在する書式（`✅ **done**（…）` / `⚠️★★★ **不要（not needed）**`）と同じ形で
  #     `blocked` を書かれると、⚠️ **素の前方一致は fail-open する**。
  cat > "${r}/.steering/task/issues/005.md" <<'I5'
# Issue 005: stub (装飾つき blocked)
verify_level: parse
## Goal
stub
## Dependencies
## Status

⚠️★★★ **blocked**（★ 装飾つきでも除外されること）
I5
  cat > "${r}/.gitignore" <<'IGN'
.steering/**/_loop-events.jsonl
.steering/**/_loop-board.md
.steering/**/_loop-run-report.md
.steering/**/_loop-artifacts/
stub/
IGN
  cat > "${r}/.steering/task/_loop-config.json" <<CFG
{
  "task": "stub", "mode": "C", "base_branch": "main",
  "verify": { "test": "${vtest}" },
  "budget": { "max_attempts": 2, "no_progress_threshold": 4, "token_ceiling": 40000000, "parallel": 1 },
  "events_path": "${r}/.steering/task/_loop-events.jsonl",
  "headless": { "max_turns": 3, "permission_mode": "acceptEdits", "model": "sonnet", "watchdog_model": "haiku" }
}
CFG
  (
    cd "${r}" || exit 1
    export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
    git -c init.defaultBranch=main -c init.templateDir= init -q . || exit 1
    git config user.email loop-test@example.invalid || exit 1
    git config user.name loop-test || exit 1
    git config commit.gpgsign false || exit 1
    git config core.hooksPath /dev/null || exit 1
    git add scripts .steering .gitignore || exit 1
    git commit -q -m init || exit 1
    # ⚠️★★★ **逸脱先の空きブランチ**を用意する（★ 2026-09-20 に踏んだ落とし穴 その 1）。
    #   ★ 最初 B1 の stub は `git checkout main` にしていたが、⚠️ **git 自身が弾いて逸脱できず**、
    #     検査が「逸脱を検出していない」ではなく「逸脱が起きていない」で赤になった。
    #     （★ git は同一ブランチの二重チェックアウトを拒む。一時 repo の本体が `main` に居るため。）
    #   ★ これは起票 10 の逐語「⚠️ かつ main checkout が `main` に居たら checkout は失敗していた
    #     （★ 今回は別ブランチだったので通った）」そのものである。
    #   → ★ **どこにもチェックアウトされていないブランチ**を逸脱先にすれば、実運用の一般形を再現できる。
    #
    # ⚠️★★★ **さらに `escape-target` を main から *分岐* させる**（★ 落とし穴 その 2）。
    #   ★ 同一コミットを指したままだと、B5（履歴の入れ替え）で HEAD が 1 mm も動かず、
    #     ⚠️ 「検査が見逃した」ではなく **「入れ替えが起きていない」** で赤になる。
    #   → ★ init(C1) から escape-target に独自コミットを積み、main にも別のコミットを積んで
    #     **共通祖先が C1 になる本物の分岐**を作る。
    git branch escape-target || exit 1
    git checkout -q escape-target || exit 1
    echo decoy > decoy.txt && git add decoy.txt && git commit -q -m decoy || exit 1
    git checkout -q main || exit 1
    echo onmain > onmain.txt && git add onmain.txt && git commit -q -m onmain || exit 1
  ) >/dev/null 2>&1
}

run_loop() { # run_loop <repo-dir> [引数...] → events.jsonl のパスを stdout へ
  local r="$1"; shift
  ( cd "${r}" && PATH="${r}/stub:${PATH}" bash scripts/loop-run.sh .steering/task "$@" ) >/dev/null 2>&1
  printf '%s\n' "${r}/.steering/task/_loop-events.jsonl"
}

dry_run() { # dry_run <repo-dir> [引数...] → stdout(+stderr) をそのまま返す
  local r="$1"; shift
  ( cd "${r}" && PATH="${r}/stub:${PATH}" bash scripts/loop-run.sh .steering/task --dry-run "$@" ) 2>&1
}

echo "════════════════════════════════════════"
echo "B. ブランチ検査 (ensure_branch) — ⚠️ 起票 10 の境界"

# --- B2 (⚠️ 陰性対照を先に回す): 逸脱しない stub は issue_done になること ---
#   ★ これが赤なら、B1 / B3 の「blocked になった」は何も検査していない緑である。
B2="${TMP}/b2/repo"; mkdir -p "${B2}"
if setup_repo "${B2}" ':'; then
  ev="$(run_loop "${B2}" --issues 001)"
  if [ -s "${ev}" ] && grep -q '"event":"issue_done"' "${ev}"; then
    ok "B2 陰性対照: 逸脱しない attempt は issue_done になった (★ 検査が空振りでない)"
  else
    ng "B2 陰性対照: 逸脱していないのに issue_done が出ない (⚠️★ 以降の判定が無意味になる)"
    [ -s "${ev}" ] && sed -n '1,8p' "${ev}"
  fi
  if grep -q 'loop/001-\* から外れている' "${ev}" 2>/dev/null; then
    ng "B2 陰性対照: 逸脱していないのにブランチ検査が発火した (★ 誤検出)"
  else
    ok "B2 陰性対照: 誤検出していない"
  fi
else
  ng "B2: 一時 git repo を用意できなかった (★ 判定できない)"
fi

# --- B1: stub が `git checkout <別ブランチ>` する (★ 起票 10 の実測の再現) ---
#   ⚠️ 逸脱先は `main` にしない（★ 上の `git branch escape-target` のコメントを参照）。
B1="${TMP}/b1/repo"; mkdir -p "${B1}"
if setup_repo "${B1}" 'git checkout -q escape-target 2>/dev/null || true'; then
  ev="$(run_loop "${B1}" --issues 001)"
  if [ -s "${ev}" ]; then
    # ⚠️ まず **逸脱が実際に起きたか**を確かめる（★ 起きていない緑を「検出した」と読まないため）。
    if grep -q 'HEAD=loop/001-issue' "${ev}"; then
      ng "B1: ⚠️★ stub が逸脱できていない (★ 検査ではなく前提が壊れている)"
    fi
    if grep -q '"event":"blocked"' "${ev}" && grep -q 'loop/001-\* から外れている' "${ev}"; then
      ok "B1: git checkout で逸脱した attempt を blocked にした"
    else
      ng "B1: ⚠️★ 逸脱を検出していない (★ 別ブランチを verify する事故が残る)"
      sed -n '1,8p' "${ev}"
    fi
    if grep -q '"event":"issue_done"' "${ev}"; then
      ng "B1: ⚠️★★★ 逸脱したのに issue_done になった (★ 最も危険な形)"
    else
      ok "B1: 逸脱した issue を done にしていない"
    fi
    # ⚠️ 逸脱先のブランチ名を detail に残していること（★ 人が原因を追えるため）
    if grep -q 'HEAD=escape-target' "${ev}"; then
      ok "B1: 逸脱先のブランチ名を events に残した (HEAD=escape-target)"
    else
      ng "B1: 逸脱先が events から分からない (★ 起票 3 と同じ「件数だけ」問題になる)"
    fi
  else
    ng "B1: events.jsonl が空 (★ 判定できない)"
  fi
else
  ng "B1: 一時 git repo を用意できなかった (★ 判定できない)"
fi

# --- B3: stub が detached HEAD にする ---
#   ★ `rev-parse --abbrev-ref HEAD` は detached では `HEAD` を返すので不一致になるはず。
B3="${TMP}/b3/repo"; mkdir -p "${B3}"
if setup_repo "${B3}" 'git checkout -q --detach HEAD 2>/dev/null || true'; then
  ev="$(run_loop "${B3}" --issues 001)"
  if [ -s "${ev}" ] && grep -q 'loop/001-\* から外れている' "${ev}" \
     && ! grep -q '"event":"issue_done"' "${ev}"; then
    ok "B3: detached HEAD を逸脱として blocked にした"
  else
    ng "B3: ⚠️ detached HEAD を見逃した (★ 何を verify したか分からない緑が出る)"
    [ -s "${ev}" ] && sed -n '1,8p' "${ev}"
  fi
else
  ng "B3: 一時 git repo を用意できなかった (★ 判定できない)"
fi

# --- B4: ⚠️ verify が緑になった *後*（watchdog 経路）の逸脱を拾うこと ---
#   ★ `code-reviewer` / `security-checker` が**両方 HIGH** で指摘した穴（2026-09-20）。
#   ⚠️ stub は `claude` の代役なので、**verify が緑になる条件**で逸脱させる必要がある。
#     → ★ verify(`true`) は常に緑なので、stub がセッション末に逸脱すれば
#       verify 直前の検査に当たる。★ **issue_done 直前の検査を単独で試すには、
#       verify 自身に逸脱させる**（`verify.test` から checkout する）。
B4="${TMP}/b4/repo"; mkdir -p "${B4}"
if setup_repo "${B4}" ':' '[]' 'git checkout -q escape-target 2>/dev/null; true'; then
  ev="$(run_loop "${B4}" --issues 001)"
  if [ -s "${ev}" ]; then
    if grep -q '"event":"issue_done"' "${ev}"; then
      ng "B4: ⚠️★★★ verify の最中に逸脱したのに issue_done になった (★ 別ブランチを見て出した done)"
    else
      ok "B4: verify 後の逸脱でも issue_done を出さなかった"
    fi
    if grep -q 'loop/001-\* から外れている' "${ev}"; then
      ok "B4: issue_done 直前のブランチ検査が発火した"
    else
      ng "B4: ⚠️ issue_done 直前に HEAD を見ていない"
    fi
  else
    ng "B4: events.jsonl が空 (★ 判定できない)"
  fi
else
  ng "B4: 一時 git repo を用意できなかった (★ 判定できない)"
fi

# --- B5: ⚠️ ブランチ名を保ったままの履歴入れ替え（reset --soft / branch -f） ---
#   ★ `security-checker` MEDIUM。⚠️ `git reset --hard` だけが deny に在り、`--soft` は通る。
B5="${TMP}/b5/repo"; mkdir -p "${B5}"
if setup_repo "${B5}" 'git reset -q --soft escape-target 2>/dev/null || true'; then
  ev="$(run_loop "${B5}" --issues 001)"
  if [ -s "${ev}" ] && grep -q '履歴が入れ替わっている' "${ev}" \
     && ! grep -q '"event":"issue_done"' "${ev}"; then
    ok "B5: ブランチ名は同じでも履歴が入れ替わったら blocked にした"
  else
    ng "B5: ⚠️ reset --soft による中身の差し替えを見逃した (★ 名前しか見ていない)"
    [ -s "${ev}" ] && sed -n '1,6p' "${ev}"
  fi
else
  ng "B5: 一時 git repo を用意できなかった (★ 判定できない)"
fi

echo "S. Status フィルタ — ⚠️ 判断 26 の申し送り (★ 3 状態)"

S="${TMP}/s/repo"; mkdir -p "${S}"
if setup_repo "${S}" ':'; then
  # --- S1 (a) 既定実行: blocked の 002 が計画に出ないこと ---
  out="$(dry_run "${S}")"
  if printf '%s' "${out}" | grep -qE '^ +002 '; then
    ng "S1 (a) 既定: ⚠️★ Status=blocked の 002 が実行計画に載っている (★ 起票 9 と同型の空回り)"
  else
    ok "S1 (a) 既定: Status=blocked の 002 を実行計画から外した"
  fi
  if printf '%s' "${out}" | grep -qE '^ +001 '; then
    ok "S1 (a) 既定: 通常の 001 は実行計画に載っている (★ 外しすぎていない)"
  else
    ng "S1 (a) 既定: ⚠️ 通常の 001 まで外した (★ フィルタが広すぎる)"
  fi
  if printf '%s' "${out}" | grep -q 'Status=blocked で除外'; then
    ok "S1 (a) 既定: 除外したことを人に見せている (★ 黙って飛ばさない)"
  else
    ng "S1 (a) 既定: 除外を黙って行った (★ 人が気づけない)"
  fi

  # --- S2 (b) --issues で明示: blocked でも計画に出ること ---
  out2="$(dry_run "${S}" --issues 002)"
  if printf '%s' "${out2}" | grep -qE '^ +002 '; then
    ok "S2 (b) 明示: --issues 002 なら blocked でも実行計画に載る"
  else
    ng "S2 (b) 明示: ⚠️ --issues で指定しても回せない (★ 逃げ道が無い)"
  fi
  if printf '%s' "${out2}" | grep -q '明示指定されたので実行します'; then
    ok "S2 (b) 明示: blocked を承知で回すことを警告した"
  else
    ng "S2 (b) 明示: 警告が出ていない (★ 事故に気づけない)"
  fi

  # --- S3 (c) `## Status` 節が無い issue: 回ること ---
  if printf '%s' "${out}" | grep -qE '^ +003 '; then
    ok "S3 (c) Status 節なし: 実行計画に載る (★ 新規 issue が黙って走らなくならない)"
  else
    ng "S3 (c) Status 節なし: ⚠️ 外れた (★ テンプレの Status は見出しだけで値が空)"
  fi

  # --- S4 ⚠️ 回帰の予防: blocked な issue に依存していても preflight_dag が die しないこと ---
  if printf '%s' "${out2}" | grep -q 'issues/ に存在しません'; then
    ng "S4 回帰: ⚠️★ blocked を外したせいで依存の存在確認が誤診した (★ ALL_FILES で引くこと)"
  elif printf '%s' "${out}" | grep -qE '^ +004 '; then
    ok "S4 回帰: blocked な 002 に依存する 004 でも die しない (★ 存在確認は ALL_FILES)"
  else
    ng "S4 回帰: 004 が実行計画に出ない (★ 依存 issue を外したことで巻き添えにしている)"
    printf '%s\n' "${out}" | head -20
  fi

  # --- S5 ⚠️ 装飾つき blocked（★ 素の前方一致だと fail-open する） ---
  if printf '%s' "${out}" | grep -qE '^ +005 '; then
    ng "S5 装飾: ⚠️★ 「⚠️★★★ **blocked**（…）」が除外されず実行計画に載った (★ fail-open)"
  else
    ok "S5 装飾: 装飾つきの blocked も除外した (★ 先頭の記号を剥がして判定している)"
  fi

  # --- S6 ⚠️ **実際に回す**（★ --dry-run では通らない経路。`code-reviewer` MEDIUM） ---
  #   ★ S1〜S5 はすべて --dry-run なので、`_loop-run-report.md` の「実行しなかった issue」節と
  #     Status フィルタの**副作用の本体**（blocked に依存する issue が実際に blocked になること）を
  #     ⚠️ **1 度も通っていなかった**（★ その 2 ブロックを削除しても緑のままだった）。
  ev="$(run_loop "${S}")"
  rep="${S}/.steering/task/_loop-run-report.md"
  if [ -s "${rep}" ]; then
    if grep -q '002' "${rep}" && grep -q 'Status=blocked のため実行しなかった' "${rep}"; then
      ok "S6 レポート: 除外した issue をレポートに残した (★ ALL から外れても消えない)"
    else
      ng "S6 レポート: 除外した issue がレポートから消えた (★ 人が気づけない)"
    fi
  else
    ng "S6 レポート: _loop-run-report.md が空 (★ 判定できない)"
  fi
  if [ -s "${ev}" ] && grep '"issue":"004"' "${ev}" | grep -q '依存 issue が未完のため未実行'; then
    ok "S6 副作用: blocked な 002 に依存する 004 は blocked として events に残る (★ 黙って消えない)"
  else
    ng "S6 副作用: ⚠️ 004 の扱いが events から分からない (★ Status フィルタの副作用が不可視)"
    [ -s "${ev}" ] && grep '"issue":"004"' "${ev}" | head -3
  fi
  if [ -s "${ev}" ] && grep -q '"issue":"005"' "${ev}"; then
    ng "S6: ⚠️ 装飾つき blocked の 005 が実際に実行された"
  else
    ok "S6: 装飾つき blocked の 005 は実行されなかった"
  fi

  # --- S7 ⚠️ --issues で blocked を迂回したことが events に残ること ---
  S7="${TMP}/s7/repo"; mkdir -p "${S7}"
  if setup_repo "${S7}" ':'; then
    ev7="$(run_loop "${S7}" --issues 002)"
    if [ -s "${ev7}" ] && grep -q 'Status=blocked の issue を --issues で明示指定して実行している' "${ev7}"; then
      ok "S7 迂回: blocked を承知で回したことを events に残した (★ 後から監査できる)"
    else
      ng "S7 迂回: ⚠️ 迂回の記録が events に無い (★ 端末のスクロールバックにしか残らない)"
    fi
  else
    ng "S7: 一時 git repo を用意できなかった (★ 判定できない)"
  fi

  # --- S8 ⚠️ --issues の id 検証（★ パストラバーサル） ---
  out8="$(dry_run "${S}" --issues '../../x' 2>&1)"
  if printf '%s' "${out8}" | grep -q 'id が不正です'; then
    ok "S8 検証: --issues の不正な id を拒否した (★ _loop-artifacts の外へ書かせない)"
  else
    ng "S8 検証: ⚠️ '../../x' を受理した (★ gitignore の外へ成果物を書ける)"
  fi
else
  ng "S: 一時 git repo を用意できなかった (★ 判定できない)"
fi

echo "D. permission_denials の内訳 — ⚠️ 起票 3"

# ★ 実スキーマは 2026-09-20 に実測した (measurements.md M1b):
#   {"tool_name":"Bash","tool_use_id":"...","tool_input":{"command":"...","description":"..."}}
#   ⚠️ 拒否はすべて tool_name=="Bash" になるので、**tool_name だけ数えても何も分からない**。
D="${TMP}/d/repo"; mkdir -p "${D}"
DENIALS='[{\"tool_name\":\"Bash\",\"tool_use_id\":\"t1\",\"tool_input\":{\"command\":\"git checkout main\",\"description\":\"x\"}},{\"tool_name\":\"Bash\",\"tool_use_id\":\"t2\",\"tool_input\":{\"command\":\"git push origin\",\"description\":\"y\"}},{\"tool_name\":\"WebFetch\",\"tool_use_id\":\"t3\",\"tool_input\":{\"url\":\"http://x\"}}]'
if setup_repo "${D}" ':' "${DENIALS}"; then
  ev="$(run_loop "${D}" --issues 001)"
  if [ -s "${ev}" ]; then
    line="$(grep 'permission_denials=' "${ev}" | head -1)"
    if [ -n "${line}" ]; then
      ok "D1: permission_denials を events に記録した"
    else
      ng "D1: permission_denials の行が無い (★ 判定できない)"
    fi
    # ⚠️ 件数だけでなく**何が拒否されたか**が読めること（★ 起票 3 の本体）
    if printf '%s' "${line}" | grep -q 'Bash(git checkout)' \
       && printf '%s' "${line}" | grep -q 'Bash(git push)'; then
      ok "D1: 拒否されたコマンドの内訳が events から読める (★ tool_name だけに潰れていない)"
    else
      ng "D1: ⚠️★ 内訳が読めない (★ 起票 3 が閉じていない): ${line}"
    fi
    if printf '%s' "${line}" | grep -q 'WebFetch'; then
      ok "D1: Bash 以外の tool も内訳に出る"
    else
      ng "D1: Bash 以外の tool が落ちている"
    fi
    art="${D}/.steering/task/_loop-artifacts/001-attempt1-denials.json"
    if [ -s "${art}" ] && [ "$(jq -r 'length' "${art}" 2>/dev/null)" = "3" ]; then
      ok "D1: 生の permission_denials 配列を _loop-artifacts/ に残した (3 件)"
    else
      ng "D1: ⚠️ 生配列が残っていない (★ tool_input.command を後から追えない): ${art}"
    fi
    # ⚠️ 非致命であること（★ denials があっても verify が緑なら done になる）
    if grep -q '"event":"issue_done"' "${ev}"; then
      ok "D1: denials があっても verify が緑なら issue_done (★ 非致命の扱いを変えていない)"
    else
      ng "D1: ⚠️ denials を致命扱いにしてしまった (★ events_path は必ず 1 件拒否される)"
    fi
  else
    ng "D1: events.jsonl が空 (★ 判定できない)"
  fi
else
  ng "D: 一時 git repo を用意できなかった (★ 判定できない)"
fi

# --- D2 ⚠️★★★ 資格情報を伏せてから保存すること（★ `security-checker` HIGH・2026-09-20） ---
#   ★ `.tool_input.command` は worker が組み立てた自由文字列なので、秘密が混ざりうる。
#   ⚠️ **events（board から見える）と生配列（恒久保存）の両方**を見る。
D2="${TMP}/d2/repo"; mkdir -p "${D2}"
# ⚠️★★★ **架空値は `scripts/secrets-filter.sh` に当たらない綴りで書く**（★ 2026-09-20 に実際に踏んだ）。
#   ★ 最初は `GH_TOKEN=ghp_…` と書いたが、⚠️ フィルタの `gh_token` に直撃して
#     **`/cross-review` が fail-closed でブロックされた**。
#   ★ 本 repo の方針は逐語「**正しい解き方はフィクスチャ側を寄せること**」であり、
#     ⚠️ **フィルタを弱めたり `--ack-filtered` で迂回したりしない**
#     （★ 迂回する動機を作るのが最悪の結果 —— `secrets-filter.sh` の S5C-D8）。
#   ★ `CI_TOKEN` / `Authorization:` は **`loop-run.sh` の `DENY_REDACT` には当たり**、
#     フィルタの列には無い。→ ★ 検出力は落ちていない。
SECRET_DENIALS='[{\"tool_name\":\"Bash\",\"tool_use_id\":\"t1\",\"tool_input\":{\"command\":\"CI_TOKEN=zzzTESTVALUE1234 gh api repos/x\"}},{\"tool_name\":\"Bash\",\"tool_use_id\":\"t2\",\"tool_input\":{\"command\":\"curl -H Authorization:Bearer_ZZZTESTVALUE5678 https://x\"}}]'
if setup_repo "${D2}" ':' "${SECRET_DENIALS}"; then
  ev="$(run_loop "${D2}" --issues 001)"
  art2="${D2}/.steering/task/_loop-artifacts/001-attempt1-denials.json"
  if [ -s "${ev}" ] && ! grep -q 'ZZZTESTVALUE' "${ev}"; then
    ok "D2: events に秘密が出ていない (★ 伏せてから集計している)"
  else
    ng "D2: ⚠️★★★ events に秘密が平文で残った: $(grep -o 'ZZZTESTVALUE[0-9]*' "${ev}" | head -2 | tr '\n' ' ')"
  fi
  if [ -s "${art2}" ] && ! grep -q 'ZZZTESTVALUE' "${art2}"; then
    ok "D2: 生配列にも秘密が残っていない (★ 恒久保存される側)"
  else
    ng "D2: ⚠️★★★ 生配列に秘密が平文で残った → ${art2}"
  fi
  # ⚠️ 伏せても「何が拒否されたか」は読めること（★ 起票 3 の目的を潰していないこと）
  if [ -s "${ev}" ] && grep -q 'gh api\|CI_TOKEN=\*\*\*' "${ev}"; then
    ok "D2: 伏せたうえで、何が拒否されたかは読める (★ 起票 3 の目的を潰していない)"
  else
    ng "D2: ⚠️ 伏せた結果、内訳が読めなくなった: $(grep -o 'permission_denials=[^"]*' "${ev}" | head -1)"
  fi
else
  ng "D2: 一時 git repo を用意できなかった (★ 判定できない)"
fi

echo "────────────────────────────────────────"
FINISHED=1
echo "合格 ${PASS} / 不合格 ${FAIL}"
[ "${FAIL}" -eq 0 ] || exit 1
echo "全件合格"
