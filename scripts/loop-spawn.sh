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
# ⚠️★★★ **撤去できたことを確かめてから「完了」と書く**（★ 起票 18・2026-09-20 の実測で発見）。
#   ★ 旧実装は worktree を **ブランチ名だけ**で引いていたので、
#     ⚠️ 起票 10 の形で `loop/<id>-*` から逸脱した worktree が **1 件もヒットせず**、
#     **branch だけ消して worktree を残したまま `cleanup 完了` / exit 0** を返していた。
#     ★ 実害: 同じ id の再実行が恒久的に死に (下の `:同名 worktree が既に存在`)、
#       ⚠️ main checkout が `main` を取れなくなり、**失敗が誰にも見えない**。
#   → ★ 直し方は 3 つ: **(1) パスでも引く (2) 撤去できたか再確認してから報告する
#     (3) 1 つでも残ったら非 0 で止まる**。
#
# ★ 一致規則は **branch と path の 2 系統**（どちらかに当たれば対象）:
#     branch: `loop/<id>` 完全一致 / `loop/<id>-` 前方一致
#     path  : basename が `<repo>-<id>` 完全一致 / `<repo>-<id>-` 前方一致
#   ⚠️ 前方一致には区切り `-` を要求する —— ★ 旧実装の `$0 ~ ("loop/" id)` は
#     **正規表現の部分一致**なので `--cleanup zzz` が `loop/zzz2-issue` にも当たった。
#   ★ `<id>-<short>` を丸ごと渡す運用 (`--cleanup 001-issue`) が実在するので**完全一致も許す**。
if [ "${1:-}" = "--cleanup" ]; then
  id="${2:?--cleanup には issue-id が必要です}"
  left=0; n_wt=0; n_br=0; processed_bn=""

  # ★ 登録済み worktree の **basename** 集合を返す。
  #   ⚠️ フルパスで突き合わせない —— git は `C:/wt/...` を、bash の `pwd` は `/c/wt/...` を返すため
  #     (2026-09-21 に git-bash で実測)。★ 既存の stale 検出 (下方) も basename で比較している。
  registered_bn() {
    git worktree list --porcelain 2>/dev/null \
      | awk '/^worktree /{p=substr($0,10); gsub(/\\/,"/",p); n=split(p,seg,"/"); print seg[n]}'
  }
  # ★ 改行を番兵にした完全一致判定（⚠️ `grep -q` を使わない —— `set -o pipefail` 下では
  #   grep の早期終了が上流に SIGPIPE を投げ、**一致したのに非 0** になりうるため）。
  contains_line() { # contains_line <candidates> <needle>
    case "
$1
" in
      *"
$2
"*) return 0 ;;
    esac
    return 1
  }

  # porcelain の worktree 行はプレフィックス除去で取得 (空白入りパスに耐える)
  wts="$(git worktree list --porcelain | awk -v id="${id}" -v rn="${repo_name}" '
    BEGIN { exa_p = rn "-" id; pfx_p = rn "-" id "-"; exa_b = "loop/" id; pfx_b = "loop/" id "-" }
    function flush() {
      if (p != "" && (hitb || hitp)) print p
      p = ""; hitb = 0; hitp = 0
    }
    /^worktree /{
      flush()
      p = substr($0, 10)
      q = p; gsub(/\\/, "/", q); n = split(q, seg, "/"); bn = seg[n]
      if (bn == exa_p || index(bn, pfx_p) == 1) hitp = 1
    }
    /^branch /{
      b = substr($0, 8); sub(/^refs\/heads\//, "", b)
      if (b == exa_b || index(b, pfx_b) == 1) hitb = 1
    }
    END { flush() }
  ')"

  if [ -n "${wts}" ]; then
    while IFS= read -r wt; do
      [ -n "${wt}" ] || continue
      # ⚠️★★★ main checkout は**絶対に**撤去しない（★ 明示ガード。basename 規則上は届かないが置く）。
      if [ "${wt}" = "${repo_root}" ]; then
        echo "loop-spawn: ⚠️ main checkout (${wt}) は撤去対象にしません" >&2
        continue
      fi
      wt_bn="$(basename "${wt}")"
      processed_bn="${processed_bn}
${wt_bn}"
      git worktree remove "${wt}" >/dev/null 2>&1 \
        || git worktree remove --force "${wt}" >/dev/null 2>&1 || true
      # ★ remove の exit code を信じず、**登録とディレクトリを引き直して**確かめる。
      if contains_line "$(registered_bn)" "${wt_bn}" || [ -e "${wt}" ]; then
        echo "loop-spawn: ⚠️ worktree 撤去失敗 (dirty/locked?): ${wt}" >&2
        echo "            ★ 手で:  git worktree remove --force \"${wt}\"" >&2
        left=$((left + 1))
      else
        echo "loop-spawn: ★ worktree 撤去: ${wt}"
        n_wt=$((n_wt + 1))
      fi
    done <<EOF
${wts}
EOF
  fi

  # 同一 id の branch を 1 つずつ削除 (複数一致でも壊れない)
  # ⚠️ `-D` は使わない（★ 未 merge の作業を黙って捨てない。★ `abort_worktree` と同じ判断）。
  # ★ `--format` で取る —— ⚠️ `git branch --list` の素の出力は別 worktree が掴む枝に `+` を付ける。
  brs="$(git branch --list "loop/${id}" "loop/${id}-*" --format='%(refname:short)')"
  if [ -n "${brs}" ]; then
    while IFS= read -r b; do
      [ -n "${b}" ] || continue
      git branch -d "${b}" >/dev/null 2>&1 || true
      # ★ 削除できたかを **show-ref で**確かめてから書く。
      if git show-ref --verify --quiet "refs/heads/${b}"; then
        echo "loop-spawn: ⚠️ branch ${b} を削除できませんでした (未 merge か worktree が掴んでいる)" >&2
        echo "            ★ 内容を確認のうえ:  git branch -D ${b}" >&2
        left=$((left + 1))
      else
        echo "loop-spawn: ★ branch 撤去: ${b}"
        n_br=$((n_br + 1))
      fi
    done <<EOF
${brs}
EOF
  fi

  git worktree prune

  # ★ 撤去しきれずに**ディレクトリが残っている**形（下方の `ディレクトリ … が残存` が die する状態）。
  #   ⚠️ **自動削除はしない** —— `rm -rf` は破壊的で、中に何が入っているか分からない。
  #   ★ ただし同じ id の再実行を殺すので、**「完了」とは書かない**（left に数える）。
  #   ⚠️★★★ **上のループで触ったものだけを除外する**（★ 「登録にあるなら除外」にしない）——
  #     ★ 一致規則が退行して worktree を拾えなくなったとき、**ここが最後の網**になる。
  #     ⚠️ 登録の有無で除外すると、拾えなかった worktree が黙って「完了」に化ける（＝ 起票 18 の再来）。
  for d in "../wt/${repo_name}-${id}" "../wt/${repo_name}-${id}-"*; do
    [ -d "${d}" ] || continue
    d_bn="$(basename "${d}")"
    if contains_line "${processed_bn}" "${d_bn}"; then continue; fi   # ★ 上で報告済み
    if contains_line "$(registered_bn)" "${d_bn}"; then
      echo "loop-spawn: ⚠️ worktree 登録に残っているのに id と結び付けられませんでした: ${d}" >&2
      echo "            ★ 手で:  git worktree remove --force \"${d}\"" >&2
    else
      echo "loop-spawn: ⚠️ worktree 登録に無いディレクトリが残存: ${d}" >&2
      echo "            ★ 中身を確認のうえ手で削除してください (★ 残ると同じ id の再実行が死にます)" >&2
    fi
    left=$((left + 1))
  done

  if [ "${left}" -gt 0 ]; then
    echo "loop-spawn: ⚠️ cleanup 未完了 issue ${id} — 撤去できなかったものが ${left} 件あります" >&2
    echo "            (★ 撤去できたのは worktree ${n_wt} 件 / branch ${n_br} 件)" >&2
    exit 1
  fi
  if [ "$((n_wt + n_br))" -eq 0 ]; then
    echo "loop-spawn: cleanup 対象なし issue ${id} (★ 既に撤去済み)"
  else
    echo "loop-spawn: cleanup 完了 issue ${id} (worktree ${n_wt} 件 / branch ${n_br} 件 を撤去)"
  fi
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
# ★ 撤去判定に使う「作成時の commit」を控えておく (★ abort_worktree の注記を参照)。
start_sha="$(git rev-parse --verify --quiet "$start" 2>/dev/null || true)"
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
  local left_wt="" left_br="" tip=""
  cd "$repo_root" 2>/dev/null || true
  # ⚠️ 撤去できたかを**確かめてから**「撤去しました」と書く（★ Codex /cross-review 2 巡目）。
  git worktree remove --force "$wtdir" >/dev/null 2>&1 || left_wt="$wtdir"
  # ⚠️★★★ **`-D` を無条件で使わない**（★ Codex /cross-review 1 巡目 MEDIUM）。
  #   ★ ただし `-d` の merged 判定は **現在の HEAD 依存**なので、作業ブランチに居ると
  #     ⚠️ 空のブランチでも拒否されて残骸になる（★ Codex 2 巡目）。
  #   → ★ 判定を HEAD に依存させない: **作成時の commit から 1 mm も動いていないときだけ**消す。
  tip="$(git rev-parse --verify --quiet "refs/heads/$branch" 2>/dev/null || true)"
  if [ -n "$tip" ] && [ "$tip" = "${start_sha:-}" ]; then
    git branch -D "$branch" >/dev/null 2>&1 || left_br="$branch"
  elif [ -n "$tip" ]; then
    # ⚠️ 何かがコミットされている ＝ 作りたてではない。★ 消さずに残して人に渡す。
    left_br="$branch"
  fi
  git worktree prune >/dev/null 2>&1 || true
  die "$1
            ${left_wt:+⚠️ worktree ($left_wt) を撤去できませんでした。手で確認してください。}${left_wt:+
            }${left_wt:-★ worktree ($wtdir) は撤去しました。}
            ${left_br:+⚠️ branch $left_br は作成時から動いているため残しました (手で確認してください)。}
            ★ 原因を直してから再実行してください。
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
