#!/bin/bash
# 毎日の cargo ビルド成果物の自動掃除 (launchd: local.gse.cargo-sweep)
#
# ⚠️★★★ このファイルが**正本**である。`~/.local/bin/gse-cargo-sweep.sh` は
#   `install-cargo-sweep-launchd.sh` がここからコピーした複製にすぎない。
#   ★ 直すときはここを直してインストーラを流し直すこと (複製側を直すと次回上書きされる)。
#
# 背景: 2026-08-31、self-hosted ランナー gse-mac のディスクが枯渇し
#   PR #135 の check が `No space left on device (os error 28)` で落ちた。
#   self-hosted は workspace が永続するため target が減らない。
#   実測で runner 側 2.7G / ローカルクローン側 31G。
#
# 方針: --time N で「N 日以上触られていない」成果物だけを消す。
#   活きているビルドキャッシュは残るのでフルビルドにはならない。
#
# ⚠️★★★ 2026-10-18 に「週次・14 日」→「毎日・3 日」へ改めた。
#   ★ 実測: 週次・14 日でも空きは 8.8Gi まで落ちていた。溜まっていたのは
#   (1) ワークツリー 5 本がそれぞれ持つ target (sweep 対象がメインクローンだけだった)、
#   (2) incremental の古いセッション (`gse_next_lib` だけで 36 個・1 個 100〜200MB)。
#   → 対象を全ワークツリーへ広げ、incremental の古いセッションも消す。
#   ⚠️ target をワークツリー間で共有 (CARGO_TARGET_DIR) する案は**採らない**:
#   `release/gse-replay` が最後にビルドしたワークツリーの物で上書きされ、実験が別ブランチの
#   バイナリで走りうる (`resource_isolation: per-worktree` の前提を壊す)。
#
# ⚠️ CI 側の同等ガードは `.github/actions/disk-guard/action.yml`。
#   ★ 役割が違う: こちらは**予防**(毎日・実機全体)、あちらは**直前の救命**(ジョブごと・workspace のみ)。
set -u

KEEP_DAYS="${GSE_SWEEP_KEEP_DAYS:-3}"
LOG="$HOME/Library/Logs/gse-cargo-sweep.log"
PATH="$HOME/.cargo/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export PATH

exec >>"$LOG" 2>&1
echo "=== $(date '+%F %T') start (keep=${KEEP_DAYS}d) ==="

# ⚠️ 走行中のビルドの成果物を消すとジョブ/ビルドが壊れる。必ず先に確認する。
# ★ `Runner.Listener` (常駐サービス) ではなく `Runner.Worker` (ジョブ実行中のみ) を見る。
if pgrep -f "Runner.Worker" >/dev/null 2>&1; then
  echo "SKIP: CI ジョブ実行中 (Runner.Worker)"
  exit 0
fi
if pgrep -x cargo >/dev/null 2>&1 || pgrep -x rustc >/dev/null 2>&1; then
  echo "SKIP: ローカルビルド実行中 (cargo/rustc)"
  exit 0
fi

# ⚠️★★★ 2026-08-31 の実測: この分岐が**実際に踏まれていた**。
#   11:54 に 1 度成功した後、いつの間にか cargo-sweep が消えており、
#   以後この定期ジョブは毎回ここで exit 1 していた (ログを見に行くまで誰も気づかない)。
#   ★ ログに ERROR を書くだけでなく **非 0 で終える**ことで、launchd の
#   `launchctl list local.gse.cargo-sweep` の最終終了コードにも現れるようにしてある。
if ! command -v cargo-sweep >/dev/null 2>&1; then
  echo "ERROR: cargo-sweep 未導入。scripts/maintenance/install-cargo-sweep-launchd.sh を実行してください"
  exit 1
fi

echo "before: $(df -Pk / | awk 'NR==2 { printf "%.1fGi", $4/1024/1024 }') free"

# ⚠️★★★ ランナー workspace の場所は**ハードコードしない** (code-reviewer HIGH, 2026-08-31)。
#   ★ 理由: 初版は `$HOME/actions-runner/_work/GSE-prototype/GSE-prototype` を直書きしていた。
#   ⚠️ repo 名変更 / runner 再セットアップ / `_work` の配置替えのどれでも**不在**になり、
#   そのとき「ローカルクローン側だけ掃除して緑」になる。★ 枯渇したのは **CI workspace 側**
#   なので、守るべき対象を守らないまま成功を報告することになる。
#   → ⚠️ runner 自身の設定 (`.runner` の `workDirectory`) から導出し、導出できなければ落ちる。
RUNNER_ROOT="$HOME/actions-runner"
RUNNER_WS=""
if [ -f "$RUNNER_ROOT/.runner" ]; then
  # ⚠️★ キー名は **`workFolder`** である。★ 2026-08-31 に実機の `.runner` のキー名を
  #   実際に読んで確かめた (agentId / agentName / poolId / poolName / serverUrl /
  #   gitHubUrl / **workFolder**)。⚠️ 私は初版で `workDirectory` と**推測で書いていた**。
  #   ★ 旧名も一応拾い、どちらも無ければ既定の `_work` に落とす。
  # ★ jq に依存しない (実機に無い実績がある)。
  # ⚠️★★★ **`sed -E` (ERE) を使う。** BSD sed (macOS 既定) は BRE の `\|` (GNU 拡張) を
  #   解さず、⚠️ **エラーも出さずに 0 件マッチ**する (2026-08-31 に実測して踏んだ)。
  #   ★ そのまま気づかなければ、常にフォールバックの `_work` が使われ「たまたま動く」
  #   —— つまり**検出しているつもりで何も検出していない**状態になっていた。
  #   (memory `macos-default-tools-break-gates` と同型)
  wd="$(sed -nE 's/.*"work(Folder|Directory)"[[:space:]]*:[[:space:]]*"([^"]*)".*/\2/p' "$RUNNER_ROOT/.runner" | head -1)"
  [ -n "$wd" ] || wd="_work"
  case "$wd" in /*) work="$wd" ;; *) work="$RUNNER_ROOT/$wd" ;; esac
  # ⚠️ repo 名を決め打ちしない。`_work/<owner-repo>/<repo>` を glob で拾う。
  for cand in "$work"/*/*; do
    [ -d "$cand/src-tauri" ] || continue
    RUNNER_WS="$cand"
    break
  done
fi

local_clone=""
[ -d "$HOME/GSE-prototype" ] && local_clone="$HOME/GSE-prototype"

# ★ incremental の古いセッションを消す (`<target>/<profile>/incremental/<crate>-<hash>/`)。
#   ⚠️ <crate>-<hash> は build/check/test/rust-analyzer などビルドの仕方ごとに別物が積まれ、
#   使われなくなった組み合わせは誰も消さない。★ mtime が KEEP_DAYS より古いものだけ消す。
prune_incremental() {
  local target="$1"
  [ -d "$target" ] || return 0
  find "$target" -maxdepth 3 -type d -name incremental -prune -print 2>/dev/null |
    while IFS= read -r inc; do
      find "$inc" -mindepth 1 -maxdepth 1 -type d -mtime +"$KEEP_DAYS" -exec rm -rf {} + 2>/dev/null
    done
}

# ★ ローカルクローンに紐づく全ワークツリー (本体を除く)。⚠️ 失敗しても必須判定には含めない
#   (ワークツリーは作っては消すので、無いこと自体は異常ではない)。
worktrees=()
if [ -n "$local_clone" ]; then
  while IFS= read -r wt; do
    [ "$wt" = "$local_clone" ] && continue
    [ -d "$wt" ] && worktrees+=("$wt")
  done < <(git -C "$local_clone" worktree list --porcelain 2>/dev/null | sed -n 's/^worktree //p')
fi

swept_local=0
swept_runner=0
for dir in "$local_clone" "$RUNNER_WS" "${worktrees[@]+"${worktrees[@]}"}"; do
  [ -n "$dir" ] || continue
  # ⚠️ TOCTOU (code-reviewer MEDIUM): 冒頭の pgrep は起動時 1 回きり。★ その直後に
  #   ジョブが割り当てられると、mtime 基準の削除が**走行中ビルドの参照ファイル**を消しうる。
  #   → 完全な排他は組めない (CI 側がロックを取らない) が、**各回の直前で測り直す**。
  if pgrep -f "Runner.Worker" >/dev/null 2>&1; then
    echo "--- SKIP (CI ジョブが開始した): $dir"
    continue
  fi
  echo "--- sweep: $dir"
  if cargo-sweep sweep --time "$KEEP_DAYS" --recursive "$dir"; then
    for t in "$dir"/target "$dir"/src-tauri/target; do prune_incremental "$t"; done
    if [ "$dir" = "$local_clone" ]; then
      swept_local=1
    elif [ "$dir" = "$RUNNER_WS" ]; then
      swept_runner=1
    fi
  else
    echo "  (失敗・続行)"
  fi
done

echo "after:  $(df -Pk / | awk 'NR==2 { printf "%.1fGi", $4/1024/1024 }') free"

# ⚠️★★★ check-then-act の競合 (security-checker LOW, 2026-08-31):
#   上の pgrep 判定と実際の sweep のあいだに CI ジョブが**始まりうる**。その場合、
#   走行中ビルドの成果物を消して `build-macos` (リリース生成) を不可解に落としうる。
#   ★ 完全な排他は launchd 側では組めない (CI 側がロックを取らないため) ので、
#   ⚠️ **少なくとも「起きたことを記録に残す」**。無言で通さない。
if pgrep -f "Runner.Worker" >/dev/null 2>&1; then
  echo "WARN: sweep 中に CI ジョブが開始しました。★ 直後の CI が不可解に失敗したらこれを疑うこと"
fi

echo "=== $(date '+%F %T') done (local=${swept_local} runner=${swept_runner}) ==="

# ⚠️★★★ **2 つを別々に判定する** (code-reviewer HIGH)。★ 初版は `swept -gt 0` で
#   「どちらか 1 本でも成功すれば緑」だった —— ⚠️ CI workspace を掃除できていないのに
#   緑を報告する型であり、本スクリプトが是正しようとしている欠陥そのものだった。
rc=0
if [ "$swept_local" -eq 0 ]; then
  echo "ERROR: ローカルクローンを掃除できませんでした (\$HOME/GSE-prototype)"
  rc=1
fi
if [ "$swept_runner" -eq 0 ]; then
  echo "ERROR: ★ CI workspace を掃除できませんでした。⚠️ 枯渇するのはこちら側です。"
  echo "       runner root=${RUNNER_ROOT} / .runner=$([ -f "$RUNNER_ROOT/.runner" ] && echo あり || echo なし) / 検出=${RUNNER_WS:-(なし)}"
  echo "       ★ runner を再セットアップした / repo 名が変わった場合はここが見つからなくなります。"
  rc=1
fi
exit "$rc"
