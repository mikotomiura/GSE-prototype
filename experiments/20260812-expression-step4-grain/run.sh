#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Step 4 — 層 2（粒子）＋ 混同テストの 1 コマンド再現（reproducibility-discipline ルール 4）
#
#   bash run.sh check          静的検査 + meta 検査 + 平滑器の回帰 + git 混入検査（★ 既定）
#   bash run.sh data <dir>     Phase1 NDJSON から smoothed CSV を作る（★ 出力は repo 外）
#   bash run.sh serve [port]   player を配る（file:// では AudioWorklet も fetch も動かない）
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
  say "1. Step 4 の静的検査（+ 検査自体を壊して赤くなることの確認）"
  "$PY" "$HERE/scripts/step4_selftest.py" --selftest
  local rc=$?
  [ $rc -ne 0 ] && rc_total=1
  note "exit=$rc"

  say "2. 平滑器の回帰（既存 51 検査・EXPR_VERSION bump の影響を見る）"
  "$PY" "$S0/expr_smooth.py" --selftest | tail -3
  local rc2=${PIPESTATUS[0]}
  [ $rc2 -ne 0 ] && rc_total=1
  note "exit=$rc2"

  say "3. Step 3 の検査が緑のままであること（★ EXPR_VERSION を上げても壊していない）"
  # ⚠️ S4-D3: SSOT を上げたので Step 3 の config も追随させた。★ 追随できているかを実測する
  "$PY" "$REPO/experiments/20260812-expression-layer0-drone/scripts/layer0_selftest.py" | tail -3
  local rc3=${PIPESTATUS[0]}
  [ $rc3 -ne 0 ] && rc_total=1
  note "exit=$rc3"

  say "3b. ★ run.sh 自身の不変条件（S4-D13: 同一参加者の別セッションが上書きされない）"
  # ⚠️★★★ 2026-08-13: `tag="${b%%_*}"` は最初の `_` までしか取らず、P010 の 17 セッションが
  #   すべて同じ tag になって**互いを上書きしていた**（エラーも出ない）。
  #   ★ 壊れた形が戻っていないことを、run.sh 自身に対して実測する。
  # ⚠️★★ **検査対象を `cmd_data` の本体だけに絞り、さらにコメントを剥がす。**
  #   理由を 2 つとも実測で踏んだ（2026-08-13）:
  #     (1) 本節の説明文に壊れた形が literal で書いてある → コメントに反応して赤くなる（notes §3.3-1）
  #     (2) ★ 下の逆検査の `sed` 置換文字列**そのもの**が壊れた形を含む → 自己参照で必ず赤くなる
  #   ★ 「検査が自分自身に反応していないか」を、検査を書くたびに確かめる。
  local rc3b=0 self="${BASH_SOURCE[0]}" code
  code="$(sed -n '/^cmd_data()/,/^}/p' "$self" | grep -v '^[[:space:]]*#')"
  [ -n "$code" ] || { printf '\033[31m  ✗ cmd_data の本体を切り出せない（検査が空回りする）\033[0m\n'; rc3b=1; }
  if printf '%s' "$code" | grep -q 'tag="\${b%%_\*}"'; then
    printf '\033[31m  ✗ tag が擬似 ID だけになっている（別セッションを上書きする形に戻っている）\033[0m\n'
    rc3b=1
  fi
  printf '%s' "$code" | grep -q 'tag="\${b%%_\*}_\${h16:0:8}"' || {
    printf '\033[31m  ✗ tag に hash が入っていない（一意性が無い）\033[0m\n'; rc3b=1; }
  printf '%s' "$code" | grep -q 'mode="pinned"' || {
    printf '\033[31m  ✗ 既定が pinned でない（hash 固定の外を黙って処理する）\033[0m\n'; rc3b=1; }
  printf '%s' "$code" | grep -q '\[ "\$n" -ne 3 \]' || {
    printf '\033[31m  ✗ 固定 3 本がそろわない場合に赤くする検査が無い\033[0m\n'; rc3b=1; }
  # ★ 逆検査: 壊した写し（コメント剥がし済み）で、上の検査が本当に発火することを実測する
  if printf '%s' "$code" | sed 's/tag="\${b%%_\*}_\${h16:0:8}"/tag="${b%%_*}"/' \
       | grep -q 'tag="\${b%%_\*}"'; then
    note "  逆検査 OK（壊した写しでは検査が発火する）"
  else
    printf '\033[31m  ✗ 逆検査が成立しない（検査が空回りしている）\033[0m\n'; rc3b=1
  fi
  [ $rc3b -ne 0 ] && rc_total=1
  note "exit=$rc3b"

  say "4. 実データ・派生物が git に載らないことの実測（data-privacy / S0-D9）"
  # ★ 「.gitignore に書いたから大丈夫」で済ませない。git 自身に聞く
  # ⚠️★★★ 2026-08-12: ここに **false green** があった（security-checker が実測で発見）。
  #   `cmd_data` が実際に書くのは `$OUT/<tag>.snap.json` と `$OUT/<tag>.csv` なのに、
  #   probe は `out.csv` / `snapshot1.json` という **スクリプトが作らない名前**しか試していなかった。
  #   → `git check-ignore` は緑を返すが、実物の派生物は追跡候補のままだった。
  #   ★ **検査は「実際に書かれる名前」を試さなければ何も守っていない。**
  # ⚠️ probe のファイル名は **架空のもの**にする（実セッション名は擬似 ID ＋ 打鍵開始日時を含む。
  #   `data.md` は「パスをリポジトリに書かない」と宣言している）。
  local D="experiments/20260812-expression-step4-grain"
  local probes=(
    "$D/results/P000.snap.json"        # ★ cmd_data が実際に書く
    "$D/results/P000.csv"              # ★ cmd_data が実際に書く
    "$D/player/P000.csv"               # ★ player へ手で置いた場合
    "$D/results/P000.smooth.csv"
    "$D/P000_gse_00000000_000000.ndjson"
    "$D/out.csv"
    "$D/snapshot1.json"
    "$D/x.age"
  )
  # ★ 逆方向も試す —— 塞ぎすぎて成果物が黙って追跡外になっていないか
  #   （⚠️ `experiments/**/*.csv` を足したので、巻き添えを毎回実測する）
  local must_track=(
    "$D/step4.config.json"
    "$D/player/step4.html"
    "$D/player/grain-processor.js"
    "$D/scripts/step4_selftest.py"
    "$D/run.sh"
    "$D/SEED"
    "$D/notes.md"
    "$D/results/blind-plan_a.json"     # ★ 盲検の結果は追跡する（実データ由来の値を含まない）
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
  # ⚠️★★★ 2026-08-13 修正: tag が "${b%%_*}" だと `P000_gse_00000000_000000` も
  #   `P000_gse_00000000_111111` も同じ `P000` になり、**同一参加者の別セッションが互いを上書きする**。
  #   ⚠️★★ 2026-08-14: ここには **実セッション名が 2 件書いてあった**（security-checker が実測で発見）。
  #     ★ 下の 158 行目が「セッション名は repo に書かない」と宣言しているのに、
  #       **同じファイルの中で矛盾していた。** → ★ 架空名（`_00000000_` 形式）へ置き換えた。
  #   ★ 研究者から受け取った実ディレクトリは 5 名 63 セッションあり（本スクリプトは 3 本前提で書かれていた）、
  #     このままだと **data.md で hash 固定したセッションではない別の回**を「P010」として聴くことになる。
  #   → ★ tag に hash を含めて一意にする。
  # ⚠️ セッション名（擬似 ID ＋ 打鍵開始日時）は repo に書かない（data.md の宣言）ので、
  #   ★ **選択はファイル名ではなく sha256 で行う。** 既定は data.md に固定した 3 本だけ。
  # ⚠️ 呼び出し側が空文字を渡すので `${2:-pinned}` では既定が効かない（空文字は「未設定」ではない）
  local mode="${2:-}"; [ -z "$mode" ] && mode="pinned"
  local pinned="b0aa474a5717639d 518a11d2d8bc4f03 3694f1a2471ca677"   # ★ data.md と同じ値
  local n=0 skipped=0
  for f in "$dir"/*.ndjson; do
    [ -e "$f" ] || continue
    local b h16 tag
    b="$(basename "$f" .ndjson)"
    h16="$(sha256sum "$f" | cut -c1-16)"
    if [ "$mode" = "pinned" ] && ! printf '%s\n' $pinned | grep -qx "$h16"; then
      skipped=$((skipped + 1)); continue
    fi
    # ★ 擬似 ID ＋ hash 先頭 8。★ 打鍵開始日時は出力名に入れない
    tag="${b%%_*}_${h16:0:8}"
    note "--- $tag ---"
    # ⚠️ S0-D6: --snapshot は「既存ゴールデンとの比較」モードで出力しない。既定出力を使う
    "$replay" "$f" > "$OUT/$tag.snap.json" || { rc_total=1; continue; }
    "$PY" "$S0/snapshot_to_csv.py" "$OUT/$tag.snap.json" "$OUT/$tag.csv" || { rc_total=1; continue; }
    "$PY" "$S0/expr_smooth.py" "$OUT/$tag.csv" "$OUT/$tag.smooth.csv" --tau 60 --fps 60 \
      || { rc_total=1; continue; }
    n=$((n + 1))
  done
  note "作った smoothed CSV: $n 本（mode=$mode / hash 不一致で飛ばした: $skipped 本）"
  note "★ player の「smoothed CSV」欄でこの中の *.smooth.csv を選ぶ（外部へは送られない）"
  note "★ 主素材は P010（離席が経過の 71%・最大 994 秒＝ B3 の判断材料は P010 にしかない）"
  # ⚠️★ 固定した 3 本がそろわないまま「作れた」と言わない（data.md との不整合を黙らせない）
  if [ "$mode" = "pinned" ] && [ "$n" -ne 3 ]; then
    printf '\033[31m★ data.md が固定した 3 本のうち %s 本しか見つからない。データが違う可能性がある。\033[0m\n' "$n"
    rc_total=1
  fi
  note "★ 全セッションを処理するなら: run.sh data <dir> all（★ hash 固定の外なので notes に必ず書く）"
  [ "$n" -eq 0 ] && rc_total=1
  return 0
}

# ---------------------------------------------------------------------------
cmd_serve() {
  local port="${1:-8732}"
  say "player を配る（Ctrl-C で停止）"
  note "→ http://127.0.0.1:$port/player/step4.html"
  note "★ ローカルのみ。外部には出しません（bind は 127.0.0.1）"
  note "⚠️ file:// では AudioWorklet も設定 fetch も動きません。必ずこの URL で開いてください"
  "$PY" -m http.server "$port" --bind 127.0.0.1 --directory "$HERE"
}

# ---------------------------------------------------------------------------
case "${1:-check}" in
  check) cmd_check ;;
  data)  shift; cmd_data "${1:-}" "${2:-}" ;;
  serve) shift; cmd_serve "${1:-}" ;;
  all)   shift; cmd_check; cmd_data "${1:-}"; cmd_serve ;;
  *)     sed -n '2,15p' "${BASH_SOURCE[0]}"; exit 2 ;;
esac

if [ "$rc_total" -ne 0 ]; then
  printf '\n\033[31m★ 失敗がある。研究者に聴かせる前に直す。\033[0m\n'
  exit 2
fi
printf '\n\033[32m★ 機械検査はすべて緑。\033[0m'
printf ' ⚠️ ただしこれは「危険でないと言えない」ことしか示さない。良い音かは耳が決める。\n'
exit 0
