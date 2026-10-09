#!/usr/bin/env bash
# 1 コマンド再現 — experiments/20261009-matching-attack-prototype
# reproducibility-discipline ルール 4。
#
# 使い方（このディレクトリで）:
#   bash run.sh            # 自己検査 → 割り当て → 照らし合わせ → 距離 → 再現の確認 → 照合 → 表
#   bash run.sh selftest   # 自己検査だけ
#
# 入力は IME 論文の Windows のセルの記録（合成入力）と、その計画・語句・手順（data.md）。人のデータ（O1・G1・
# Phase1 の NDJSON）は 1 行も読まない。各スクリプトが入力と読み込むコードの SHA-256 を config.json と照らし、
# 違えば止まる。記録の中身（カテゴリの列）を含む派生データは raw/（git に入らない）に置く。
# Python は .venv（requirements.txt の 2 つだけを入れる。SudachiPy は照らし合わせの読みに使う）:
#   python -m venv .venv && .venv/Scripts/python -m pip install -r requirements.txt   # Windows
#   python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt      # macOS / Linux
# Windows コンソールは cp932。Python は -X utf8 で動かす（-I は PYTHON* の環境変数を無視するため）。
set -euo pipefail

cd "$(dirname "$0")"
if [ -x .venv/Scripts/python ]; then PY=.venv/Scripts/python; else PY=.venv/bin/python; fi
[ -x "$PY" ] || { echo "!! .venv が無い（上のコメントの手順で作る）" >&2; exit 1; }
run() { "$PY" -I -X utf8 -W ignore "$@"; }
PROCS="${PROCESSES:-4}"
if command -v sha256sum >/dev/null 2>&1; then SHA256="sha256sum"; else SHA256="shasum -a 256"; fi

mkdir -p results raw/dist

selftest() {
  echo "== 自己検査（落ちたら本計算をしない）=="
  run scripts/selftest.py
}

main() {
  selftest
  echo "== 記録の割り当てと試行ごとの値 =="
  run scripts/prepare.py --out raw/trials.json --summary results/prepare.json
  echo "== 照らし合わせ（攻撃より先）=="
  run scripts/crosscheck.py --trials raw/trials.json --prepare results/prepare.json --out results/crosscheck.json
  echo "== シミュレーション攻撃の試行ごとの距離 =="
  run scripts/distances.py --trials raw/trials.json --prepare results/prepare.json --out-dir raw/dist \
    --summary results/distances.json --processes "$PROCS"
  echo "== k = 1 の再現の確認（IME 論文の公開値と一致しなければ止まる）=="
  run scripts/reproduce_ime.py --trials raw/trials.json --prepare results/prepare.json --dist-dir raw/dist \
    --dist-summary results/distances.json --out results/reproduce_ime.json
  echo "== 照合（441 セルと診断）=="
  run scripts/matching.py --trials raw/trials.json --prepare results/prepare.json --dist-dir raw/dist \
    --dist-summary results/distances.json --out results/matching.json --processes "$PROCS"
  echo "== 表 =="
  run scripts/summarize.py --results results --out results/summary.md
  $SHA256 results/*.json results/summary.md
}

case "${1:-all}" in
  selftest) selftest ;;
  all) main ;;
  *) echo "usage: bash run.sh [all|selftest]" >&2; exit 2 ;;
esac
