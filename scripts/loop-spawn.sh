#!/usr/bin/env bash
# loop-spawn.sh — 1 issue 用の worktree を切り、その中で Claude セッションを起動する人間用ヘルパ。
#   使い方:  bash scripts/loop-spawn.sh <issue-id> [short-slug]
#            bash scripts/loop-spawn.sh --cleanup <issue-id>
#            bash scripts/loop-spawn.sh --no-exec <issue-id> [short-slug]   # worktree 生成のみ (モードC 用)
# worktree は main checkout の隣 (../wt/) に作る。events は main checkout の絶対パスに集約されるため
# 各 worker が同じ _loop-events.jsonl に append できる。
set -euo pipefail

BASE_DEFAULT="${LOOP_BASE_BRANCH:-}"   # 未指定なら下で解決

die() { echo "loop-spawn: $*" >&2; exit 1; }

# ⚠️ このスクリプトは後段で repo_root → worktree と 2 回 cd するので、
#   ★ 兄弟スクリプトの場所は **cd する前に絶対パスで固定**する
#   (⚠️ `dirname "$0"` を後段で評価すると worktree 側の存在しないパスを指す)。
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || die "git リポジトリ内で実行してください"
cd "$repo_root"
repo_name="$(basename "$repo_root")"

# --no-exec: worktree 生成のみで Claude を起動しない (先頭で処理し、以降の分岐に影響させる)
if [ "${1:-}" = "--no-exec" ]; then LOOP_NO_EXEC=1; shift; fi

# --- base branch の解決 (pin) ---
# 優先順: LOOP_BASE_BRANCH → _loop-config.json の base_branch → origin/HEAD → main → master
#
# ⚠ 未 merge の作業ブランチで作業している場合は必ず pin すること。
#    pin し忘れると main から worktree が切られ、実装がそこに存在しないため
#    **全 issue が即死する**。
resolve_base() {
  if [ -n "$BASE_DEFAULT" ]; then echo "$BASE_DEFAULT"; return; fi
  local b=""
  # _loop-config.json の base_branch を見る (config が見つかる場合のみ)
  local cfg
  cfg="$(ls -1 .steering/*/_loop-config.json 2>/dev/null | tail -1 || true)"
  if [ -n "${cfg:-}" ] && [ -f "$cfg" ]; then
    b="$(jq -r '.base_branch // empty' "$cfg" 2>/dev/null || true)"
  fi
  if [ -z "${b:-}" ]; then
    # origin/HEAD が指す既定ブランチ → 無ければ main → master の順
    b="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')" || true
  fi
  if [ -z "${b:-}" ]; then
    if git show-ref --verify --quiet refs/heads/main; then b=main
    elif git show-ref --verify --quiet refs/heads/master; then b=master
    else b="$(git rev-parse --abbrev-ref HEAD)"; fi
  fi
  echo "$b"
}

# --- cleanup モード (merge 後の撤去) ---
if [ "${1:-}" = "--cleanup" ]; then
  id="${2:?--cleanup には issue-id が必要です}"
  # porcelain の worktree 行はプレフィックス除去で取得 (空白入りパスに耐える)
  wt="$(git worktree list --porcelain | awk -v id="$id" '/^worktree /{p=substr($0,10)} /^branch /&&$0 ~ ("loop/" id){print p}')"
  if [ -n "$wt" ]; then
    git worktree remove "$wt" 2>/dev/null || git worktree remove --force "$wt" \
      || echo "loop-spawn: worktree 撤去失敗 (dirty/locked?) — 手動確認を"
  else
    echo "loop-spawn: worktree 見つからず (既に撤去?)"
  fi
  # 同一 id の branch を 1 つずつ削除 (複数一致でも壊れない)
  git branch --list "loop/${id}-*" | sed 's/^[ *]*//' | while read -r b; do
    [ -n "$b" ] && { git branch -d "$b" 2>/dev/null || echo "loop-spawn: branch $b 未 merge か既に削除"; }
  done
  git worktree prune
  echo "loop-spawn: cleanup 完了 issue ${id}"
  exit 0
fi

id="${1:?issue-id を指定してください}"
short="${2:-issue}"
base="$(resolve_base)"
branch="loop/${id}-${short}"
wtdir="../wt/${repo_name}-${id}-${short}"

# --- dirty tree ハンドリング ---
if [ -n "$(git status --porcelain)" ]; then
  echo "loop-spawn: 作業ツリーに未コミット変更があります。worktree add は index を共有しません" >&2
  echo "            が、混乱を避けるため commit / stash を推奨します。続行するには LOOP_FORCE=1。" >&2
  [ "${LOOP_FORCE:-0}" = "1" ] || die "中断 (LOOP_FORCE=1 で強行可)"
fi

# --- stale worktree 検出 (basename 一致・空白入りパスに耐える) ---
target_bn="$(basename "$wtdir")"
if git worktree list --porcelain | awk '/^worktree /{print substr($0,10)}' \
     | while read -r p; do [ "$(basename "$p")" = "$target_bn" ] && echo HIT; done | grep -q HIT; then
  die "同名 worktree が既に存在: $wtdir  (完了済みなら --cleanup $id を先に)"
fi
if [ -d "$wtdir" ]; then die "ディレクトリ $wtdir が残存。手動で確認/削除してください"; fi
if git show-ref --verify --quiet "refs/heads/$branch"; then
  die "ブランチ $branch が既存。--cleanup $id で撤去してから再実行"
fi
git worktree prune   # 消えたパスの登録を掃除

# --- base を remote と同期し、可能なら remote-tracking から分岐 (stale local base を避ける) ---
start="$base"
if git remote get-url origin >/dev/null 2>&1; then
  if git fetch --quiet origin "$base"; then
    start="origin/$base"          # fetch 成功時は最新の remote から分岐
  else
    echo "loop-spawn: fetch 失敗 (オフライン?) ローカル base で続行"
  fi
fi

echo "loop-spawn: base=$base (start=$start) → branch=$branch / worktree=$wtdir"
git worktree add -b "$branch" "$wtdir" "$start"
cd "$wtdir"

# --- ⚠️★★★ 必須 `permissions.deny` の注入（★ worktree 作成直後・失敗したら使わせない） ---
#   ★ モードC (`loop-run.sh:275`) は worktree 生成を **このスクリプトへ委譲している**ので、
#     ここに 1 か所置けば **モードA（人が spawn）とモードC（無人）の両方**が通る。
#   ⚠️ 逆に `loop-run.sh` 側に置くと **モードA が素通りする**。
#   ⚠️★★★ 出力は **stderr** へ流す —— ★ `--no-exec` の
#     「**stdout の最終行 = worktree の絶対パス**」という契約 (`loop-run.sh:275` の `tail -1`) を壊さないため。
#   ⚠️ 失敗しても続行する経路は作らない (fail-closed)。理由は loop-worktree-deny.sh 冒頭。
#   ⚠️★★★ 失敗したら **worktree と branch ごと撤去する**（★ code-reviewer / security-checker
#     MEDIUM・2026-09-14）。★ 残すと (a) 人が手で `cd` して deny 無しで起動できてしまい、
#     (b) 同じ id の再実行が「同名 worktree が既に存在」で**恒久的に死ぬ**。
#     ★ 作りたてで中身が無いので、撤去して失うものは無い。
deny_script="${SCRIPT_DIR}/loop-worktree-deny.sh"
abort_worktree() { # abort_worktree <理由>
  local left=""
  cd "$repo_root" 2>/dev/null || true
  git worktree remove --force "$wtdir" >/dev/null 2>&1 || true
  # ⚠️★★★ **`-D` を使わない**（★ Codex /cross-review MEDIUM・2026-09-14）。
  #   ★ ここへ来るのは上の `git show-ref --verify` で「同名ブランチが無い」ことを確かめた直後に
  #     `git worktree add -b` で**作ったばかりのブランチ**だけなので、base から進んでいない。
  #   → ★ `-d` なら「未 merge の作業を持つブランチ」は**拒否される** ＝ 想定外の削除が起きない。
  #     ⚠️ 拒否されたらブランチを残し、そのことを人に伝える（★ 黙って force しない）。
  git branch -d "$branch" >/dev/null 2>&1 || left="$branch"
  git worktree prune      >/dev/null 2>&1 || true
  die "$1
            ★ worktree ($wtdir) は撤去しました。原因を直して再実行してください。
            ${left:+⚠️ branch $left は未 merge の作業を持つため残しました (手で確認してください)。}
            (既存 worktree を手で点検するなら  bash scripts/loop-worktree-deny.sh --verify <worktree>)"
}
[ -f "${deny_script}" ] || abort_worktree "必須 deny の注入スクリプトが見つかりません: ${deny_script}"
bash "${deny_script}" "$(pwd)" >&2 \
  || abort_worktree "worktree への必須 deny 注入に失敗しました。★ deny 無しの worktree は渡しません。"

echo "loop-spawn: worktree 準備完了。"

# --no-exec / NO_EXEC: worktree を作るだけで Claude を起動しない (モードC の loop-run.sh から再利用する)。
# worktree の絶対パスを stdout に 1 行だけ出す (呼び出し側が読む契約)。
if [ "${LOOP_NO_EXEC:-0}" = "1" ] || [ "${NO_EXEC:-0}" = "1" ]; then
  pwd
  exit 0
fi

echo "loop-spawn: Claude を起動します → /loop-issue $id を実行してください"
# Windows(Git Bash) では claude が .cmd/.ps1 shim のことがあり exec が滑る。見つからなければ手順を案内。
if command -v claude >/dev/null 2>&1; then
  exec claude
else
  echo "loop-spawn: 'claude' が PATH に見つかりません。手動で:  cd \"$wtdir\" && claude"
  exit 0
fi
