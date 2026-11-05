#!/usr/bin/env bash
# 確認（凍結の後に 1 回だけ）: CS1 2019 年版の取り置きの書き手だけの中間を作り、確認の解析を回す。
# 事前登録 v5 の P2・P10。凍結の前には走らせない。
# 使い方: run-confirm-holdout.sh <OSF の登録の URL> <登録に書いた confirm-manifest.sha256 の SHA-256>
# 照合（全部、計算の前）: manifest の SHA-256 が登録の値と同じ → manifest に並べた全てのファイル（この手順自身・
# 確認と変換のスクリプトと、それが読み込むスクリプト・環境の一覧）の SHA-256 → 入力・取り置きの一覧・gse-replay の
# SHA-256 → Python の版と pip freeze → 作業ツリーがきれい → 前の開始の記録が無い。
# 開始の前に、照合した値と時刻を results_holdout/start.json に書いてコミットする（1 回だけの記録）。
# 途中で止まったら results_holdout/failed.json を書いて止める。直した後の再実行は逸脱で、CONFIRM_RERUN_REASON に
# 理由を書いたときだけ通す（前の dir は results_holdout.failed.<時刻> に移す。結果は照合を通った最初の完走だけを使う）。
set -euo pipefail
OSF_URL="${1:?OSF の凍結の URL を渡す（凍結の前に走らせない）}"
MANIFEST_SHA="${2:?登録に書いた confirm-manifest.sha256 の SHA-256 を渡す}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXP_REL="experiments/20261105-findings-paper1-prefreeze"
: "${DATA_DIR:=$HOME/gse-public-data}"
PY="${CONFIRM_PY:-$DATA_DIR/venv-findings1/bin/python}"
CS1="$DATA_DIR/cs1"
K19="$CS1/raw/2019/keystrokes.csv"
BIN="${GSE_REPLAY:-$DATA_DIR/klicke/bin/gse-replay}"
WORK="$CS1/work2019_holdout"
OUT="$EXP_DIR/results_holdout"
sha() { shasum -a 256 "$1" | cut -d' ' -f1; }
die() { echo "$1" >&2; exit 1; }

# 1. 照合（計算の前）
[ "$(sha "$EXP_DIR/confirm-manifest.sha256")" = "$MANIFEST_SHA" ] || die "confirm-manifest.sha256 が登録の値と違う"
(cd "$REPO_ROOT" && shasum -a 256 -c "$EXP_REL/confirm-manifest.sha256" >/dev/null) || die "manifest のファイルが登録の版と違う"
[ "$(sha "$K19")" = b54d8cf56b7719ae0ec9ecf19e5b3788168f087bd4a50238dca1e06f6bfe7955 ] || die "2019 年版の SHA-256 が違う"
[ "$(sha "$CS1/holdout.json")" = a5a32fcefeb97b038afd170e2672262fd5a71230d5e851319eaa076b606bdc47 ] || die "取り置きの一覧が違う"
[ "$(sha "$BIN")" = 26cae610383fb6de01651cc904895efa72a691c3dd1e27689a14a4ca51c33bb3 ] || die "gse-replay が違う"
[ "$("$PY" -I -c 'import sys;print(sys.version.split()[0])')" = 3.14.4 ] || die "Python の版が違う"
[ "$("$PY" -m pip freeze)" = "$(cat "$EXP_DIR/requirements-confirm.txt")" ] || die "環境が requirements-confirm.txt と違う"
[ -z "$(git -C "$REPO_ROOT" status --porcelain)" ] || die "作業ツリーがきれいでない（コミットしてから走らせる）"
# パイプにしない（pipefail の下では grep -q が先に抜けると git log が SIGPIPE で終わり、一致があっても偽になる）
# 完走の記録があれば、理由があっても止める（結果は最初の完走だけ・P10）
[ -z "$(git -C "$REPO_ROOT" log --all --format=%H --grep='^取り置きの確認の完走' -n 1)" ] || die "完走の記録がある（2 回目は回さない・P10）"
if [ -n "$(git -C "$REPO_ROOT" log --all --format=%H --grep='^取り置きの確認の開始' -n 1)" ]; then
  [ -n "${CONFIRM_RERUN_REASON:-}" ] || die "前の開始の記録がある（最初の完走だけを使う・P10。再実行は CONFIRM_RERUN_REASON に理由を書いて逸脱として）"
fi
if [ -e "$OUT" ]; then
  [ ! -e "$OUT/confirm_holdout.json" ] || die "取り置きの結果が既にある（最初の完走だけを使う・P10）"
  [ -n "${CONFIRM_RERUN_REASON:-}" ] || die "途中で止まった前の走りがある。直した後の再実行は CONFIRM_RERUN_REASON に理由を書く（逸脱）"
  FAILED_DIR="$OUT.failed.$(date -u +%Y%m%dT%H%M%SZ)"
  mv "$OUT" "$FAILED_DIR"
  git -C "$REPO_ROOT" add -A "$EXP_REL/$(basename "$OUT")" "$EXP_REL/$(basename "$FAILED_DIR")"
  git -C "$REPO_ROOT" commit -q -m "取り置きの確認の前の走りを退避（$EXP_REL/$(basename "$FAILED_DIR")・理由: $CONFIRM_RERUN_REASON）[skip ci]"
fi

# 2. 開始の記録（コミットしてから計算に入る）
mkdir -p "$OUT"
"$PY" -I -c "import json,sys,datetime;json.dump({'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'osf_url':sys.argv[1],'manifest_sha256':sys.argv[2],'git_head':sys.argv[3],'rerun_reason':sys.argv[4] or None},open(sys.argv[5],'w'),indent=1)" \
  "$OSF_URL" "$MANIFEST_SHA" "$(git -C "$REPO_ROOT" rev-parse HEAD)" "${CONFIRM_RERUN_REASON:-}" "$OUT/start.json"
git -C "$REPO_ROOT" add "$EXP_REL/results_holdout/start.json"
git -C "$REPO_ROOT" commit -q -m "取り置きの確認の開始（$EXP_REL/results_holdout/start.json）[skip ci]" -- "$EXP_REL/results_holdout/start.json"
STEP=start
# 止まったら、止まった段を failed.json に書いて、そのままコミットする（中断の記録・P10）
record_failure() {
  "$PY" -I -c "import json,sys,datetime;json.dump({'failed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'step':sys.argv[1],'kind':sys.argv[2]},open(sys.argv[3],'w'),indent=1)" "$STEP" "$1" "$OUT/failed.json" || true
  git -C "$REPO_ROOT" add "$EXP_REL/results_holdout" || true
  git -C "$REPO_ROOT" commit -q -m "取り置きの確認の中断（段: $STEP・$1）[skip ci]" -- "$EXP_REL/results_holdout" || true
  echo "途中で止まった（$STEP）。直さずに記録し、研究者に聞く（P10）" >&2
}
trap 'record_failure error' ERR
trap 'record_failure interrupted; exit 130' INT TERM

export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
unset CONFIRM_SMOKE
STEP=selftest
"$PY" -I "$EXP_DIR/scripts/confirm_p1.py" --selftest
# 3. 取り置きの書き手だけの中間（見た書き手を読み飛ばす一覧を渡す。ID は repo の外にだけ置く）
STEP=build
SKIP="$CS1/skip_seen_2019.json"
"$PY" -I -c "import csv,json,sys;csv.field_size_limit(10**9);r=csv.reader(open(sys.argv[1],newline=''));i=next(r).index('SubjectID');s={x[i] for x in r};h=set(json.load(open(sys.argv[2]))['2019']);assert h<=s;json.dump({'2019':sorted(s-h)},open(sys.argv[3],'w'))" "$K19" "$CS1/holdout.json" "$SKIP"
rm -rf "$WORK"
"$PY" -I "$REPO_ROOT/experiments/20261104-cs1-landscape/scripts/build_cs1.py" 2019 "$K19" "$BIN" "$SKIP" "$WORK" "${JOBS:-6}"
cp "$WORK/build_summary.json" "$OUT/build_summary_holdout.json"
# 取り置きの書き手が全員読まれたか（変換で読んだ書き手の数 = 取り置きの一覧の人数）
"$PY" -I -c "import json,sys;b=json.load(open(sys.argv[1]));h=json.load(open(sys.argv[2]))['2019'];sys.exit(0 if b['writers_read']==len(h) else '取り置きの書き手の数が合わない: %d / %d'%(b['writers_read'],len(h)))" "$WORK/build_summary.json" "$CS1/holdout.json"
# 4. 感度の中間（陽性対照つき）
STEP=build_variants
bash "$EXP_DIR/build-variants.sh" "$WORK" "$PY" "$BIN" "${JOBS:-6}"
cp "${WORK}_control_summary.json" "$OUT/rebuild_control_summary_holdout.json"
for v in q995 w15 w60; do cp "${WORK}_$v/rebuild_summary.json" "$OUT/rebuild_summary_${v}_holdout.json"; done
# 5. 確認の解析
STEP=confirm
"$PY" -I "$EXP_DIR/scripts/confirm_p1.py" holdout "$WORK" "$CS1/holdout.json" 20261106 "$OUT"
STEP=provenance
"$PY" -I -c "import json,sys,datetime,hashlib;h=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest();json.dump({'git_head':sys.argv[1],'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'confirm_holdout_sha256':h(sys.argv[2]),'manifest_sha256':h(sys.argv[3])},open(sys.argv[4],'w'),indent=1)" \
  "$(git -C "$REPO_ROOT" rev-parse HEAD)" "$OUT/confirm_holdout.json" "$EXP_DIR/confirm-manifest.sha256" "$OUT/provenance_holdout.json"
# 完走の記録（手順がコミットする。結果は集計値だけで、書き手ごとの値を含まない）
STEP=commit
git -C "$REPO_ROOT" add "$EXP_REL/results_holdout"
git -C "$REPO_ROOT" commit -q -m "取り置きの確認の完走（$EXP_REL/results_holdout）[skip ci]" -- "$EXP_REL/results_holdout"
trap - ERR INT TERM
echo "完走した。results_holdout/ をコミットした。"
