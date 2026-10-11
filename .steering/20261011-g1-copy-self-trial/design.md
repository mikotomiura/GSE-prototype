# 設計

手順と値の正本は `experiments/20261011-g1-copy-self-trial/preregistration.md` と `config.json`（結果の前にコミット）。ここには構成だけを書く。

## アプローチ

前の 2 回（`20261009-length-sequence-uniqueness`・`20261009-matching-attack-prototype`）の長さだけの攻撃 L を、人の記録に当てる。G1 のアプリは句読点と記号を `other` にまとめるので、区切りを「`other` の押下」に変え、原文とおとりを同じ規則で作り直す（判断 1）。

## 変更対象（すべて新規・`experiments/20261011-g1-copy-self-trial/`）

| ファイル | 役割 |
|---|---|
| `scripts/common.py` | 入力の SHA-256 の照合・前の実測のコードの読み込み・乱数 |
| `scripts/g1rule.py` | 本文の行 → G1 の規則の区間（原文とおとりで共通） |
| `scripts/build_corpus.py` | 1,500 作品の区間の並び（`raw/corpus_g1.json`）と原文の区間（`results/copy_segments.json`） |
| `scripts/records.py` | NDJSON → 記録の区間（plain・clean）。`G1_WORK` に書く |
| `scripts/align.py` | 動的計画法の揃え |
| `scripts/crosscheck.py` | 照らし合わせ（集計だけを `results/` に） |
| `scripts/matching.py` | 照合・加工・診断 |
| `scripts/summarize.py` | 表 |
| `scripts/selftest.py` | 自己検査 |
| `run.sh` | 1 コマンド再現 |

## テスト戦略

`selftest.py`: 規則の単体（区切りの文字・「ー」・記号・数字）、記録の区切りと掃除、揃え（既知の挿入・欠落を戻す）、加工の定義が前の試作と同じ値を返すこと、合成の記録（原文そのもの）で照合が正解を選ぶこと、`bininf` が 1/N になること。本計算の前にコミットする。
