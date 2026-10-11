#!/usr/bin/env bash
# 1 コマンド再現 — experiments/20261011-g1-copy-self-trial
# reproducibility-discipline ルール 4。
#
# 使い方（このディレクトリで）:
#   G1_RECORDS=<復号した NDJSON のディレクトリ> G1_WORK=<repo の外の作業ディレクトリ> \
#   ZIPS=<前の実測の raw/zips> bash run.sh
#   bash run.sh selftest   # 自己検査だけ（記録を読まない）
#
# 記録（G1_RECORDS）と記録から作った区間の並び（G1_WORK）は repo の外に置く（data.md）。
# results/ に書くのは集計だけ。Python は .venv（requirements.txt）。-X utf8 で動かす（Windows コンソールは cp932）。
set -euo pipefail

cd "$(dirname "$0")"
if [ -x .venv/Scripts/python ]; then PY=.venv/Scripts/python; else PY=.venv/bin/python; fi
[ -x "$PY" ] || { echo "!! .venv が無い（README の手順で作る）" >&2; exit 1; }
run() { "$PY" -I -X utf8 -W ignore "$@"; }
PROCS="${PROCESSES:-4}"

selftest() {
  echo "== 自己検査（落ちたら本計算をしない）=="
  run scripts/selftest.py
}

# どの git 作業ツリー（この repo・本体の checkout・別の worktree）の中も「中」とみなす。
# 調べられない（ディレクトリが無い・cd できない）ときも「中」とみなす（fail-closed）。
# Python 側（common.assert_private_dir）でも同じ判定をする。
inside_git_tree() {
  [ -d "$1" ] || return 0
  ( cd "$1" 2>/dev/null ) || return 0
  git -C "$1" rev-parse --show-toplevel >/dev/null 2>&1 && return 0
  return 1
}

main() {
  : "${G1_RECORDS:?G1_RECORDS（復号した NDJSON のディレクトリ）を指定する}"
  : "${G1_WORK:?G1_WORK（repo の外の作業ディレクトリ）を指定する}"
  if inside_git_tree "$G1_RECORDS"; then
    echo "!! G1_RECORDS は既存の、どの git 作業ツリーの外のディレクトリにする（data.md）" >&2; exit 1
  fi
  if [ -e "$G1_WORK" ] && inside_git_tree "$G1_WORK"; then
    echo "!! G1_WORK はどの git 作業ツリーの外に置く（data.md）" >&2; exit 1
  fi
  if [ ! -e "$G1_WORK" ] && inside_git_tree "$(dirname "$G1_WORK")"; then
    echo "!! G1_WORK はどの git 作業ツリーの外に置く（data.md）" >&2; exit 1
  fi
  mkdir -p "$G1_WORK" results raw
  selftest
  if ! run scripts/build_corpus.py --check --out raw/corpus_g1.json --copy-out results/copy_segments.json \
       --stats results/corpus_g1_stats.json; then
    : "${ZIPS:?ZIPS（前の実測の raw/zips）を指定する}"
    echo "== おとりのコーパス（G1 の規則・1,500 作品）=="
    run scripts/build_corpus.py --zips "$ZIPS" --out raw/corpus_g1.json --copy-out results/copy_segments.json \
      --stats results/corpus_g1_stats.json --processes "$PROCS"
  fi
  echo "== 記録の区間（G1_WORK へ）=="
  run scripts/records.py --records "$G1_RECORDS" --work "$G1_WORK"
  echo "== 照らし合わせ =="
  run scripts/crosscheck.py --work "$G1_WORK" --copy results/copy_segments.json --out results/crosscheck.json
  echo "== 照合と診断 =="
  run scripts/matching.py --work "$G1_WORK" --copy results/copy_segments.json --corpus raw/corpus_g1.json \
    --corpus-stats results/corpus_g1_stats.json --out results/matching.json --processes "$PROCS"
  echo "== 事後の探索（区切りの乱れを許す攻撃者・notes.md 逸脱 3）=="
  run scripts/explore_align.py --work "$G1_WORK" --copy results/copy_segments.json --corpus raw/corpus_g1.json \
    --corpus-stats results/corpus_g1_stats.json --out results/explore_align.json --processes "$PROCS"
  echo "== 表 =="
  run scripts/summarize.py --crosscheck results/crosscheck.json --matching results/matching.json \
    --corpus-stats results/corpus_g1_stats.json --explore results/explore_align.json --out results/summary.md
}

case "${1:-all}" in
  selftest) selftest ;;
  all) main ;;
  *) echo "usage: bash run.sh [selftest]" >&2; exit 2 ;;
esac
