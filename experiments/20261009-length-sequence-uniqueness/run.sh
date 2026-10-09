#!/usr/bin/env bash
# 1 コマンド再現 — experiments/20261009-length-sequence-uniqueness
# reproducibility-discipline ルール 4。
#
# 使い方（このディレクトリで）:
#   bash run.sh            # 自己検査 → 作品の選定 → 取得（無ければ）と SHA-256 の照合 → 前処理 → 指標 1 → 指標 2 → 表
#   bash run.sh selftest   # 自己検査だけ
#   bash run.sh verify     # 取得済みの zip を manifest と照らすだけ（ダウンロードしない）
#
# 人のデータ（NDJSON）は 1 行も読まない。入力は青空文庫の公開テキストだけ（data.md）。
# Python は .venv（requirements.txt の 2 つだけを入れる）:
#   python -m venv .venv && .venv/Scripts/python -m pip install -r requirements.txt   # Windows
#   python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt      # macOS / Linux
# ⚠️ Windows コンソールは cp932。Python は -X utf8 で動かす（-I は PYTHON* の環境変数を無視するため）。
set -euo pipefail

cd "$(dirname "$0")"
if [ -x .venv/Scripts/python ]; then PY=.venv/Scripts/python; else PY=.venv/bin/python; fi
[ -x "$PY" ] || { echo "!! .venv が無い（上のコメントの手順で作る）" >&2; exit 1; }
run() { "$PY" -I -X utf8 -W ignore "$@"; }
PROCS="${PROCESSES:-4}"
# sha256sum (Linux, git-bash) or shasum -a 256 (macOS)
if command -v sha256sum >/dev/null 2>&1; then SHA256="sha256sum"; else SHA256="shasum -a 256"; fi

mkdir -p results raw/index raw/zips raw/derived

selftest() {
  echo "== 自己検査（落ちたら本計算をしない）=="
  run scripts/selftest.py
}

index() {
  local zip=raw/index/list_person_all_extended_utf8.zip
  local want=a615fa6ddb6ef3e0ad598337f5d08f1570c3d2aa51cc5d43a62998ca904905be
  if [ ! -f "$zip" ]; then
    curl -fsS --proto =https --max-time 300 -o "$zip.part" \
      https://www.aozora.gr.jp/index_pages/list_person_all_extended_utf8.zip
    mv "$zip.part" "$zip"
  fi
  local got
  got=$($SHA256 "$zip" | cut -d' ' -f1)
  if [ "$got" != "$want" ]; then
    echo "!! 作品の一覧の SHA-256 が記録と違う（$got）。一覧が更新されたか、取得が壊れた。" >&2
    echo "   取り直すなら $zip を消してから再実行する（更新されていれば同じ選定は再現できない。data.md を見る）" >&2
    exit 1
  fi
}

main() {
  selftest
  index
  echo "== 作品の選定 =="
  run scripts/select_works.py --index raw/index/list_person_all_extended_utf8.zip --seed-file SEED \
    --config config.json --out results/selection.json
  echo "== 取得と SHA-256 の照合（1 秒に 1 件）=="
  run scripts/fetch_works.py --selection results/selection.json --config config.json --zips raw/zips \
    --manifest results/corpus_manifest.json
  echo "== 前処理（かな化・区切り B0〜B3）=="
  run scripts/build_segments.py --manifest results/corpus_manifest.json --zips raw/zips --config config.json \
    --out-dir raw/derived --stats results/corpus_stats.json
  echo "== 指標 1（位置が一意に決まる割合）=="
  run scripts/uniqueness.py --derived raw/derived --stats results/corpus_stats.json --config config.json \
    --out results/uniqueness.json
  echo "== 指標 2（候補 N 本からの照合）=="
  run scripts/matching.py --derived raw/derived --stats results/corpus_stats.json --config config.json \
    --seed-file SEED --out results/matching.json --processes "$PROCS"
  echo "== notes.md が引く件数（ルビ・B2 の書き手の読み）=="
  run scripts/extra_counts.py --manifest results/corpus_manifest.json --zips raw/zips --derived raw/derived \
    --stats results/corpus_stats.json --out results/extra_counts.json
  echo "== 表 =="
  run scripts/summarize.py --results results --out results/summary.md
  $SHA256 results/*.json results/summary.md
}

case "${1:-all}" in
  selftest) selftest ;;
  verify) run scripts/fetch_works.py --selection results/selection.json --config config.json --zips raw/zips \
            --manifest results/corpus_manifest.json --verify-only ;;
  all) main ;;
  *) echo "usage: bash run.sh [all|selftest|verify]" >&2; exit 2 ;;
esac
