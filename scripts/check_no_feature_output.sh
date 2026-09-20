#!/usr/bin/env bash
# ★ 「`gse-replay --features` の出力を共有しない」の**機械的な門**（起票 5・判断 5 / 6）。
#
# ⚠️★★★ **何を止めるためにあるのか**:
#   ★ 規約は前から在った —— `docs/glossary.md` の「特徴行」に逐語
#     「**中間成果物であり `gse-dataset` へは共有しない**」。
#   ⚠️ しかし **門が無かった**（2026-09-15 実測・2026-09-20 再確認）:
#     `git check-ignore` の結果は `feat.json` / `features.json` / `src-tauri/rows.json` /
#     `experiments/x/feat.json` が **4 つとも NOT ignored**、`out.ndjson` も NOT ignored。
#   ⚠️★★★ **`.gitignore` に慣用ファイル名を足すのは名前依存なので代替にならない**
#     （★ 起票 5 の逐語）。→ **中身を見る。**
#
# ⚠️ なぜ中身が機微なのか（★ 起票 5 が挙げた実体）:
#   - `t_ms` は**絶対 epoch ms** で、**`anonymize.rs` を一度も通っていない**。
#   - `T1a` 以後は **ms 粒度の pause 長** ＋ **セッション全体を横断する個人統計 (`surprise`)** が載る。
#   ★ これは `gse-dataset` へ出してよい唯一の共有物と定めた `metrics.json`（集計値・約 1KB）
#     より遥かに粒度が高い。
#
# ★ 判定は 2 本立てで、**どちらか 1 つでも当たれば赤**（fail-closed・判断 6）:
#   (a) **マーカー**: `"gse_dataset"` が `"prohibited"` の JSON（= 封筒つきの出力そのもの）
#   (b) **行の形**: `t_ms` / `activity` / `boundary` / `dispersion` / `stall_onset` の
#       **5 キーすべて**を持つオブジェクトの配列（= ⚠️ `jq '.rows'` で**封筒を剥がされた**形）
#   ⚠️ (a) だけだと剥がされた瞬間にすり抜ける。(b) だけだと将来 `rows` のキーが変わったとき
#     **黙って緑になる**（★ 本プロジェクトが 3 回踏んだ型）。→ 両方見る。
#
# ⚠️★★★ **この検査が見ていないもの**（★ 隠さずに書く）:
#   - **リポジトリの外**（Slack / メール / USB / クラウド共有）。★ ここは門を置けない。
#   - **圧縮・暗号化された中身**（`.zip` / `.age` / `.gz`）。★ git は中身を見ない。
#   - **CSV や NDJSON に変換された行**。★ JSON の形だけを見ている。
#   - ⚠️★★★ **キーを間引いた射影**。★ `is_feature_row` は 5 キー**すべて**を要求するので、
#     `jq '[.rows[] | {t_ms, dispersion}]'` のような抜き出しは**緑になる**。
#     ⚠️ `t_ms`（絶対 epoch）と `dispersion`（ms 粒度の pause 長）だけでも機微はそのまま出る。
#     ★ 5 キーを緩めると偽陽性が増えて門ごと外されるので、**検知は諦めている**
#     （⚠️ 諦めたことを隠さない・2026-09-20 code-reviewer MEDIUM）。
#   - **`gse-dataset` 側のコミット**。⚠️ 向こうには `.github` が無く CI が存在しない
#     （2026-09-20 実測）。★ 本スクリプトは `--root` で向こうのクローンにも向けられるが、
#     **自動では走らない**。→ 手順は `docs/verification-runbook.md`。
#
# Usage:
#   bash scripts/check_no_feature_output.sh              # 本リポの追跡ファイルを走査
#   bash scripts/check_no_feature_output.sh --root DIR   # 任意のツリーを走査（gse-dataset のクローン等）
#   bash scripts/check_no_feature_output.sh --self-test  # ⚠️ 検査が空振りしていないかを見る
#
# Exit: 0 = 緑 / 1 = 違反あり / 2 = ⚠️★ **検査できなかった**（★ 違反 0 件と区別する）
#
# 関連: .steering/20260920-envelope-issues/ ／ docs/glossary.md「特徴行」「共有の門」

set -uo pipefail

ROOT=""
ROOT_GIVEN=0
SELF_TEST=0
while [ $# -gt 0 ]; do
  case "$1" in
    --root) ROOT="${2:-}"; ROOT_GIVEN=1; shift 2 || { echo "[gate] --root に値がありません" >&2; exit 2; } ;;
    --self-test) SELF_TEST=1; shift ;;
    -h|--help) sed -n '1,52p' "$0"; exit 0 ;;
    *) echo "[gate] 不明な引数: $1" >&2; exit 2 ;;
  esac
done

# ⚠️★★★ `--root ""` を黙って「本リポの走査」に落とさない（2026-09-20・security-checker M4）。
#   ★ 実測: `--root "$DATASET"` で `DATASET` が空文字だと `shift 2` は成功し `ROOT=""` になり、
#     gse-dataset ではなく GSE-prototype を走査して `[gate] OK`（走査 121 件）を返していた。
#   ⚠️ gse-dataset 側は CI が無く**この手動手順が唯一の門**なので、そこが fail-open になる。
if [ "$ROOT_GIVEN" -eq 1 ] && [ -z "$ROOT" ]; then
  echo "[gate] ⚠️ --root に空の値が渡された（★ 変数が未設定のまま展開されていないか）" >&2
  exit 2
fi

command -v jq >/dev/null 2>&1 || { echo "[gate] ⚠️ jq が無いので検査できない" >&2; exit 2; }

# ---------- 走査対象の決め方 ----------
# ★ 既定（--root 無し）は **git の追跡ファイル** —— 「コミットされたら赤」が守りたい線であり、
#   作業ツリーの一時ファイルまで赤にすると門が鬱陶しくなって外される。
# ★ `--root` を与えたときは **ツリー内の全ファイル** を見る（⚠️ 向こうが git とは限らない）。
# ⚠️★★★ **出力は必ず絶対パス・NUL 区切り**にする（2026-09-20・security-checker M3 / LOW）。
#   ★ 本関数は `< <(list_candidates)` のプロセス置換、つまり**サブシェル**で走るので、
#     ここでの `cd` は呼び出し元の `$PWD` を変えない（実測）。
#     ⚠️ 旧版は `git ls-files` の repo ルート相対パスをそのまま返しており、
#     `run_scan` の `[ -f "$f" ]` は**呼び出し元の cwd** に対して解決していた。
#     → ★ repo ルート以外から起動すると候補が黙って落ちる（実測: `src-tauri/` から起動で走査 0 件）。
#   ⚠️ 旧版の `git ls-files -z | tr '\0' '\n'` は `-z` を打ち消していた ——
#     改行を含むパスは 2 つに割れ、`[ -f ]` で落ちて**黙って消える**。→ NUL のまま渡す。
list_candidates() {
  if [ -n "$ROOT" ]; then
    [ -d "$ROOT" ] || { echo "[gate] ⚠️ --root のディレクトリが無い: $ROOT" >&2; exit 2; }
    find "$ROOT" -type f \
      \( -name '*.json' -o -name '*.txt' -o -name '*.out' -o -name '*.log' \) \
      -not -path '*/.git/*' -print0
  else
    cd "$(dirname "$0")/.." || { echo "[gate] ⚠️ repo 直下へ移動できない" >&2; exit 2; }
    local top
    top="$(git rev-parse --show-toplevel 2>/dev/null)" \
      || { echo "[gate] ⚠️ git リポジトリでないので追跡ファイルを列挙できない" >&2; exit 2; }
    [ -n "$top" ] || { echo "[gate] ⚠️ repo ルートを特定できない" >&2; exit 2; }
    # ⚠️ 拡張子で**対象を絞る**が、判定そのものは中身で行う（★ 名前で「これは安全」と決めない）。
    #   ★ `.json` 以外も見るのは、`> feat.txt` のようにリダイレクト先を変えただけの持ち出しを拾うため。
    git ls-files -z -- '*.json' '*.txt' '*.out' '*.log' \
      | while IFS= read -r -d '' f; do printf '%s/%s\0' "$top" "$f"; done
  fi
}

# ---------- 判定 ----------
# ★ jq に 2 本の条件を渡し、どちらかが true なら違反。
#   ⚠️ `..` で再帰的に潜る —— 封筒が別の JSON の一部として埋め込まれても拾う。
#   ⚠️ JSON として読めないファイルは **違反なし**として扱う（★ 見ていないものの一つ）。
# ⚠️★★★ **2 本の条件は必ず `def` に包んで呼ぶこと。**
#   ★ 2026-09-20 に実測で踏んだ穴: `[ .. | select(A) ] | length > 0 or ([ .. | select(B) ] | ...)`
#     と書くと、jq は `|` を `or` より**弱く**結び、
#     `[ .. | select(A) ] | ( length > 0 or ([ .. | select(B) ] | length > 0) )` と解釈する。
#     → ⚠️ **2 本目が元の文書ではなく「1 本目の結果の配列」を入力に取る**ので、
#       封筒を剥がした行の配列が**黙って緑**になっていた（★ 突然変異 M-b が赤にならなかった）。
#   ★ `def` にすると各呼び出しが `.`（= その時点の入力 = 文書全体）を受ける。
JQ_PROG='
  def is_marker:
    (type == "object") and (.gse_dataset? == "prohibited");
  def is_feature_row:
    (type == "object")
    and has("t_ms") and has("activity") and has("boundary")
    and has("dispersion") and has("stall_onset");
  def is_row_array:
    (type == "array") and (length > 0) and all(.[]; is_feature_row);
  def has_marker: [ .. | select(is_marker) ] | length > 0;
  def has_row_array: [ .. | select(is_row_array) ] | length > 0;
  has_marker or has_row_array
'

run_scan() {
  local violations=0 scanned=0 f hit rc
  while IFS= read -r -d '' f; do
    [ -n "$f" ] || continue
    [ -f "$f" ] || continue
    scanned=$((scanned + 1))
    # ⚠️ jq の失敗 (JSON でない) と「true が返った」を区別する。
    hit="$(jq -e "$JQ_PROG" "$f" 2>/dev/null)"
    rc=$?
    # ⚠️★★★ **1 ファイルに JSON 文書が複数入っていると jq は文書ごとに 1 行出す**
    #   (2026-09-20・code-reviewer / security-checker が独立に指摘・実測で確認)。
    #   ★ 旧版は `[ "$hit" = "true" ]` だったので、`"true\ntrue"` と一致せず
    #     ⚠️ **2 文書以上なら必ず緑**になっていた（= 違反が大きいほど通る逆向きの挙動）。
    #   ⚠️ 封筒を入れた動機そのもの（複数セッションの結合）に沿って
    #     `cat feat_a.json feat_b.json > all.json` とされると素通りしていた。
    #   → ★ 「**1 行でも true があるか**」で判定する。
    if [ $rc -eq 0 ] && printf '%s\n' "$hit" | grep -qx true; then
      echo "[gate] NG: $f は gse-replay --features の出力に見える" >&2
      echo "       ★ これは中間成果物であり gse-dataset へ共有しない（docs/glossary.md「特徴行」）。" >&2
      echo "       ⚠️ t_ms は絶対 epoch ms で anonymize.rs を通っていない。" >&2
      violations=$((violations + 1))
    fi
  done < <(list_candidates)

  if [ "$scanned" -eq 0 ]; then
    echo "[gate] ⚠️ 走査対象が 0 件だった（★ 「違反なし」ではなく「検査できなかった」）" >&2
    return 2
  fi
  if [ "$violations" -gt 0 ]; then
    echo "[gate] NG: $violations 件（走査 $scanned 件）" >&2
    return 1
  fi
  echo "[gate] OK: --features 出力は見つからなかった（走査 $scanned 件）"
  return 0
}

# ---------- --self-test: 陽性対照 3 件 ＋ 陰性対照 2 件 ----------
# ⚠️★★★ **「門がある」と「門が閉まる」は別である。**
#   ★ 本プロジェクトは「検査があるつもりで検査していない」を 3 回踏んでいる。
#   ★ 実際、この検査器自身が 2026-09-20 の初版で **陽性対照 P2 を通していた**
#     （jq の `|` が `or` より弱く、2 本目の条件が元の文書を受けていなかった）。
#     → ⚠️ 手で 1 回試すだけでは足りない。対照を**この script の中に**置く。
# ★ 検体は本物の `--features` 出力ではなく**最小の合成 JSON** にする
#   （⚠️ cargo build を self-test の依存にしない。CI のどのジョブからでも 1 秒で回る）。
self_test() {
  local d rc failed=0
  d="$(mktemp -d)" || { echo "[gate] ⚠️ 一時ディレクトリを作れない" >&2; return 2; }
  # shellcheck disable=SC2064
  trap "rm -rf '$d'" RETURN

  local row='{"t_ms":1,"activity":{},"boundary":{},"dispersion":{},"stall_onset":{},"quality":{}}'

  report() { # report <名前> <期待 rc> <実測 rc>
    if [ "$3" -eq "$2" ]; then
      printf '  ✅ %-36s rc=%s\n' "$1" "$3"
    else
      printf '  ❌ %-36s rc=%s（期待 %s）\n' "$1" "$3" "$2"
      failed=$((failed + 1))
    fi
  }

  probe() { # probe <名前> <期待 rc> <ファイル名> <中身>
    local name="$1" want="$2" fname="$3" body="$4" got
    rm -rf "${d:?}/tree"; mkdir -p "$d/tree"
    printf '%s' "$body" > "$d/tree/$fname"
    # ⚠️ 関数呼び出しへの前置代入 (`ROOT=x run_scan`) は bash の posix モードで
    #   呼び出し後も残りうる。★ 代入と呼び出しを分ける（本リポは移植性ゲートを持つほど
    #   この手の版差を気にする・2026-09-20 code-reviewer LOW）。
    ROOT="$d/tree"
    run_scan >/dev/null 2>&1
    got=$?
    ROOT=""
    report "$name" "$want" "$got"
  }

  echo "[gate] --self-test: 陽性 4 / 陰性 3（★ 既定枝の対照を含む）"
  # ★ 陽性対照: 赤 (rc=1) にならなければ検査は空振りしている。
  probe "P1 封筒つき（マーカー）" 1 feat.json \
    "{\"provenance\":{\"sharing\":{\"gse_dataset\":\"prohibited\"}},\"config\":{},\"rows\":[$row]}"
  probe "P2 封筒を剥がした行の配列" 1 rows.json "[$row]"
  probe "P3 拡張子だけ変えた持ち出し" 1 notes.txt "[$row]"
  # ⚠️★★★ P4: **多文書 JSON**（★ 2026-09-20 に 2 レビューが独立に見つけた偽陰性）。
  #   ★ 封筒を入れた動機そのもの（複数セッションの結合）に沿う形なので、
  #     ここが緑だと「違反が大きいほど通る」という逆向きの門になる。
  probe "P4 封筒を 2 つ連結した多文書" 1 all.json \
    "{\"provenance\":{\"sharing\":{\"gse_dataset\":\"prohibited\"}},\"config\":{},\"rows\":[$row]}
{\"provenance\":{\"sharing\":{\"gse_dataset\":\"prohibited\"}},\"config\":{},\"rows\":[$row]}"
  # ★ 陰性対照: 緑 (rc=0) にならなければ偽陽性で、門はいずれ外される。
  probe "N1 metrics.json 形（共有物）" 0 m.json \
    '{"session_id":"P001","f1":0.83,"median_ms":120}'
  probe "N2 t_ms だけを持つ別物" 0 other.json '[{"t_ms":1,"note":"x"},{"t_ms":2,"note":"y"}]'

  # ⚠️★ 「走査 0 件」を緑と取り違えないこと（★ exit 2 と 0 を分けている理由）。
  rm -rf "${d:?}/tree"; mkdir -p "$d/tree"
  ROOT="$d/tree"
  run_scan >/dev/null 2>&1
  rc=$?
  ROOT=""
  report "N3 空ツリーは「検査できなかった」" 2 "$rc"

  # ⚠️★★★ **既定枝（`git ls-files`）の対照**（2026-09-20・security-checker M3）。
  #   ★ 上の 7 件はすべて `ROOT` を立てるので `--root` 枝しか通らない ——
  #     ⚠️ **既定枝は対照で 1 度も検査されていなかった**。
  #     ★ 本 script 自身が冒頭で警告している「検査があるつもりで検査していない」型そのもの。
  #   ★ 使い捨ての git repo を作り、検体を追跡させて既定枝を通す。
  if command -v git >/dev/null 2>&1; then
    local r="$d/repo"
    mkdir -p "$r/scripts"
    cp "$0" "$r/scripts/$(basename "$0")"
    (
      cd "$r" || exit 2
      git init -q . >/dev/null 2>&1 || exit 2
      git config user.email selftest@example.invalid
      git config user.name selftest
      printf '%s' "[$row]" > rows.json
      git add scripts/"$(basename "$0")" rows.json >/dev/null 2>&1 || exit 2
      # ★ 別ディレクトリから起動して、cwd 依存でないことも同時に見る。
      cd / || exit 2
      bash "$r/scripts/$(basename "$0")" >/dev/null 2>&1
    )
    report "P5 既定枝（追跡ファイル・別 cwd）" 1 $?
  else
    printf '  ⚠️ %-36s（git が無いので既定枝を検査できない）\n' "P5 既定枝"
    failed=$((failed + 1))
  fi

  if [ "$failed" -gt 0 ]; then
    echo "[gate] --self-test NG: $failed 件（⚠️ 検査器が壊れている。本検査の緑を信用しないこと）" >&2
    return 1
  fi
  echo "[gate] --self-test OK"
  return 0
}

if [ "$SELF_TEST" -eq 1 ]; then
  self_test
  exit $?
fi

run_scan
exit $?
