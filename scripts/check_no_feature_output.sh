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
SELF_TEST=0
while [ $# -gt 0 ]; do
  case "$1" in
    --root) ROOT="${2:-}"; shift 2 || { echo "[gate] --root に値がありません" >&2; exit 2; } ;;
    --self-test) SELF_TEST=1; shift ;;
    -h|--help) sed -n '1,46p' "$0"; exit 0 ;;
    *) echo "[gate] 不明な引数: $1" >&2; exit 2 ;;
  esac
done

command -v jq >/dev/null 2>&1 || { echo "[gate] ⚠️ jq が無いので検査できない" >&2; exit 2; }

# ---------- 走査対象の決め方 ----------
# ★ 既定（--root 無し）は **git の追跡ファイル** —— 「コミットされたら赤」が守りたい線であり、
#   作業ツリーの一時ファイルまで赤にすると門が鬱陶しくなって外される。
# ★ `--root` を与えたときは **ツリー内の全ファイル** を見る（⚠️ 向こうが git とは限らない）。
list_candidates() {
  if [ -n "$ROOT" ]; then
    [ -d "$ROOT" ] || { echo "[gate] ⚠️ --root のディレクトリが無い: $ROOT" >&2; exit 2; }
    find "$ROOT" -type f \
      \( -name '*.json' -o -name '*.txt' -o -name '*.out' -o -name '*.log' \) \
      -not -path '*/.git/*' -print
  else
    cd "$(dirname "$0")/.." || { echo "[gate] ⚠️ repo 直下へ移動できない" >&2; exit 2; }
    git rev-parse --git-dir >/dev/null 2>&1 \
      || { echo "[gate] ⚠️ git リポジトリでないので追跡ファイルを列挙できない" >&2; exit 2; }
    # ⚠️ 拡張子で**対象を絞る**が、判定そのものは中身で行う（★ 名前で「これは安全」と決めない）。
    #   ★ `.json` 以外も見るのは、`> feat.txt` のようにリダイレクト先を変えただけの持ち出しを拾うため。
    git ls-files -z -- '*.json' '*.txt' '*.out' '*.log' | tr '\0' '\n'
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
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    [ -f "$f" ] || continue
    scanned=$((scanned + 1))
    # ⚠️ jq の失敗 (JSON でない) と「true が返った」を区別する。
    hit="$(jq -e "$JQ_PROG" "$f" 2>/dev/null)"
    rc=$?
    if [ $rc -eq 0 ] && [ "$hit" = "true" ]; then
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

  probe() { # probe <名前> <期待 rc> <ファイル名> <中身>
    local name="$1" want="$2" fname="$3" body="$4" got
    rm -rf "${d:?}/tree"; mkdir -p "$d/tree"
    printf '%s' "$body" > "$d/tree/$fname"
    ROOT="$d/tree" run_scan >/dev/null 2>&1
    got=$?
    if [ "$got" -eq "$want" ]; then
      printf '  ✅ %-34s rc=%s\n' "$name" "$got"
    else
      printf '  ❌ %-34s rc=%s（期待 %s）\n' "$name" "$got" "$want"
      failed=$((failed + 1))
    fi
  }

  echo "[gate] --self-test: 陽性 3 / 陰性 2"
  # ★ 陽性対照: 赤 (rc=1) にならなければ検査は空振りしている。
  probe "P1 封筒つき（マーカー）" 1 feat.json \
    "{\"provenance\":{\"sharing\":{\"gse_dataset\":\"prohibited\"}},\"config\":{},\"rows\":[$row]}"
  probe "P2 封筒を剥がした行の配列" 1 rows.json "[$row]"
  probe "P3 拡張子だけ変えた持ち出し" 1 notes.txt "[$row]"
  # ★ 陰性対照: 緑 (rc=0) にならなければ偽陽性で、門はいずれ外される。
  probe "N1 metrics.json 形（共有物）" 0 m.json \
    '{"session_id":"P001","f1":0.83,"median_ms":120}'
  probe "N2 t_ms だけを持つ別物" 0 other.json '[{"t_ms":1,"note":"x"},{"t_ms":2,"note":"y"}]'

  # ⚠️★ 「走査 0 件」を緑と取り違えないこと（★ exit 2 と 0 を分けている理由）。
  rm -rf "${d:?}/tree"; mkdir -p "$d/tree"
  ROOT="$d/tree" run_scan >/dev/null 2>&1
  rc=$?
  if [ "$rc" -eq 2 ]; then
    printf '  ✅ %-34s rc=2\n' "N3 空ツリーは「検査できなかった」"
  else
    printf '  ❌ %-34s rc=%s（期待 2）\n' "N3 空ツリーは「検査できなかった」" "$rc"
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
