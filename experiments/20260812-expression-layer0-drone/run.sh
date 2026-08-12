#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Step 3 — 層 0（基層）試聴の 1 コマンド再現（reproducibility-discipline ルール 4）
#
#   bash run.sh check          静的検査 + 平滑器の回帰 + git 混入検査（★ 既定）
#   bash run.sh data <dir>     Phase1 NDJSON から smoothed CSV を作る（★ 出力は repo 外）
#   bash run.sh serve [port]   player を配る（file:// の同一オリジン制約を回避）
#   bash run.sh all <dir>      check → data → serve
#
# ⚠️ 実データ (<dir>) は **リポジトリにも このスクリプトにも書かない**。
#    引数か環境変数 GSE_PHASE1_DIR で渡す（data.md に hash だけを固定してある）。
# ⚠️ Windows では git-bash で実行する（PowerShell では動かない）。
# ---------------------------------------------------------------------------
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
S0="$REPO/.steering/20260811-expression-prototype-step0/scripts"
OUT="${GSE_LAYER0_OUT:-$HERE/../../../gse-layer0-out}"   # ★ 既定で repo の外へ出す

# ★ cp932 コンソールでも本文が読めるようにする（U+2014 等で落ちない）
export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"

PY="${PYTHON:-python}"
rc_total=0
say() { printf '\n\033[1m== %s ==\033[0m\n' "$*"; }
note() { printf '   %s\n' "$*"; }

# ---------------------------------------------------------------------------
cmd_check() {
  say "1. 層 0 の静的検査（+ 検査自体を壊して赤くなることの確認）"
  "$PY" "$HERE/scripts/layer0_selftest.py" --selftest
  local rc=$?
  [ $rc -ne 0 ] && rc_total=1
  note "exit=$rc"

  say "2. 平滑器の回帰（既存 51 検査・EXPR_VERSION bump の影響を見る）"
  "$PY" "$S0/expr_smooth.py" --selftest | tail -3
  local rc2=${PIPESTATUS[0]}
  [ $rc2 -ne 0 ] && rc_total=1
  note "exit=$rc2"

  say "3. 実データ・派生物が git に載らないことの実測（data-privacy / S0-D9）"
  # ★ 「.gitignore に書いたから大丈夫」で済ませない。git 自身に聞く
  # ⚠️★★★ 2026-08-12 (Step 4) に false green を実測で発見して直した。
  #   `cmd_data` が実際に書くのは `$OUT/<tag>.snap.json` と `$OUT/<tag>.csv` なのに、
  #   probe は `out.csv` / `snapshot1.json` という **スクリプトが作らない名前**しか試していなかった。
  #   ★ 検査は「実際に書かれる名前」を試さなければ何も守っていない。
  # ⚠️ probe のファイル名は架空にする（実セッション名は擬似 ID ＋ 打鍵開始日時を含む）。
  local D="experiments/20260812-expression-layer0-drone"
  local probes=(
    "$D/results/P000.snap.json"        # ★ cmd_data が実際に書く
    "$D/results/P000.csv"              # ★ cmd_data が実際に書く
    "$D/player/P000.csv"
    "$D/results/P000.smooth.csv"
    "$D/P000_gse_00000000_000000.ndjson"
    "$D/out.csv"
    "$D/snapshot1.json"
    "$D/x.age"
  )
  local must_track=(
    "experiments/20260812-expression-layer0-drone/layer0.config.json"
    "experiments/20260812-expression-layer0-drone/player/layer0.html"
    "experiments/20260812-expression-layer0-drone/scripts/layer0_selftest.py"
    "experiments/20260812-expression-layer0-drone/run.sh"
  )
  local bad=0
  for p in "${probes[@]}"; do
    if git -C "$REPO" check-ignore -q "$p"; then
      note "ignored  OK   $p"
    else
      note "TRACKED  NG   $p   <- ★ 実データ/派生物が追跡候補になっている"
      bad=1
    fi
  done
  for p in "${must_track[@]}"; do
    if git -C "$REPO" check-ignore -q "$p"; then
      note "ignored  NG   $p   <- ★ 成果物が黙って追跡外になっている"
      bad=1
    else
      note "tracked  OK   $p"
    fi
  done
  [ $bad -ne 0 ] && rc_total=1
  note "混入検査 exit=$bad"
  return 0
}

# ---------------------------------------------------------------------------
cmd_data() {
  local dir="${1:-${GSE_PHASE1_DIR:-}}"
  if [ -z "$dir" ] || [ ! -d "$dir" ]; then
    echo "error: Phase1 NDJSON のディレクトリを渡してください（引数 または GSE_PHASE1_DIR）" >&2
    echo "       ⚠️ パスはリポジトリに書きません（data.md には hash だけ固定してあります）" >&2
    return 2
  fi
  local replay="$REPO/src-tauri/target/release/gse-replay.exe"
  [ -x "$replay" ] || replay="$REPO/src-tauri/target/release/gse-replay"
  if [ ! -x "$replay" ]; then
    say "gse-replay を build する"
    ( cd "$REPO/src-tauri" && cargo build --release --bin gse-replay ) || return 2
  fi

  mkdir -p "$OUT"
  say "smoothed CSV を作る（出力先: $OUT ★ repo の外）"
  local n=0
  for f in "$dir"/*.ndjson; do
    [ -e "$f" ] || continue
    local b tag
    b="$(basename "$f" .ndjson)"; tag="${b%%_*}"
    note "--- $tag ---"
    # ⚠️ S0-D6: --snapshot は「既存ゴールデンとの比較」モードで出力しない。既定出力を使う
    "$replay" "$f" > "$OUT/$tag.snap.json" || { rc_total=1; continue; }
    "$PY" "$S0/snapshot_to_csv.py" "$OUT/$tag.snap.json" "$OUT/$tag.csv" || { rc_total=1; continue; }
    "$PY" "$S0/expr_smooth.py" "$OUT/$tag.csv" "$OUT/$tag.smooth.csv" --tau 60 --fps 60 \
      || { rc_total=1; continue; }
    n=$((n + 1))
  done
  note "作った smoothed CSV: $n 本"
  note "★ player の「データ」欄でこの中の *.smooth.csv を選ぶ（外部へは送られない）"
  [ "$n" -eq 0 ] && rc_total=1
  return 0
}

# ---------------------------------------------------------------------------
cmd_serve() {
  local port="${1:-8731}"
  say "player を配る（Ctrl-C で停止）"
  note "→ http://127.0.0.1:$port/player/layer0.html"
  note "★ ローカルのみ。外部には出しません（bind は 127.0.0.1）"
  "$PY" -m http.server "$port" --bind 127.0.0.1 --directory "$HERE"
}

# ---------------------------------------------------------------------------
case "${1:-check}" in
  check) cmd_check ;;
  data)  shift; cmd_data "${1:-}" ;;
  serve) shift; cmd_serve "${1:-}" ;;
  all)   shift; cmd_check; cmd_data "${1:-}"; cmd_serve ;;
  *)     sed -n '2,14p' "${BASH_SOURCE[0]}"; exit 2 ;;
esac

if [ "$rc_total" -ne 0 ]; then
  printf '\n\033[31m★ 失敗がある。Step 4 へ進まない。\033[0m\n'
  exit 2
fi
printf '\n\033[32m★ 機械検査はすべて緑。\033[0m'
printf ' ⚠️ ただしこれは「危険でないと言えない」ことしか示さない。良い音かは耳が決める。\n'
exit 0
