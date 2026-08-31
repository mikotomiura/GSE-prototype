#!/bin/bash
# 週次 cargo ビルド成果物の自動掃除 (launchd: local.gse.cargo-sweep)
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
# ⚠️ CI 側の同等ガードは `.github/actions/disk-guard/action.yml`。
#   ★ 役割が違う: こちらは**予防**(週次・実機全体)、あちらは**直前の救命**(ジョブごと・workspace のみ)。
set -u

KEEP_DAYS="${GSE_SWEEP_KEEP_DAYS:-14}"
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
#   以後この週次ジョブは毎回ここで exit 1 していた (ログを見に行くまで誰も気づかない)。
#   ★ ログに ERROR を書くだけでなく **非 0 で終える**ことで、launchd の
#   `launchctl list local.gse.cargo-sweep` の最終終了コードにも現れるようにしてある。
if ! command -v cargo-sweep >/dev/null 2>&1; then
  echo "ERROR: cargo-sweep 未導入。scripts/maintenance/install-cargo-sweep-launchd.sh を実行してください"
  exit 1
fi

echo "before: $(df -Pk / | awk 'NR==2 { printf "%.1fGi", $4/1024/1024 }') free"

swept=0
for dir in \
  "$HOME/GSE-prototype" \
  "$HOME/actions-runner/_work/GSE-prototype/GSE-prototype"
do
  [ -d "$dir" ] || { echo "--- skip (不在): $dir"; continue; }
  echo "--- sweep: $dir"
  if cargo-sweep sweep --time "$KEEP_DAYS" --recursive "$dir"; then
    swept=$((swept + 1))
  else
    echo "  (失敗・続行)"
  fi
done

echo "after:  $(df -Pk / | awk 'NR==2 { printf "%.1fGi", $4/1024/1024 }') free"
echo "=== $(date '+%F %T') done (swept_dirs=${swept}) ==="

# ★ 掃除対象が 1 つも見つからなかったのは異常 (パスの前提が崩れている)。黙って緑にしない。
[ "$swept" -gt 0 ] || { echo "ERROR: 掃除できたディレクトリが 0 件です (上の skip 理由を確認)"; exit 1; }
