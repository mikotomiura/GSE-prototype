# 設計

## アプローチ

1. 段 1: 一次の資料（positioning §1 の改訂・ADR-040・判断 10〜18・three-parallel-tracks §4）とコードの行種から、`positioning.md` に位置づけの要約・信号の一覧・問いの一覧を置く。
2. 段 2: `experiments/20261102-public-data-landscape/conditions.md` を計算の前にコミットする。取っておく 3 割の書き手を、値を見る前に種で決める。
3. 中間: KLiCKe は T2 の `work.tar.gz` を展開せずに読み、クリックと貼り付けの時刻だけを zip から補う。CoAuthor は 1 セッションずつ変換と replay を回し、解析が読む項目だけを残す（`~/gse-public-data/landscape/`）。
4. 集計: `analyze_landscape.py` が L1〜L6 を出す。T2 の `Theta`・`fires_current` を読み込んで使う（定義を写し直さない）。
5. 結果を `notes.md` に、言える範囲を限って書く。

## 変更対象

- 新規: `.steering/20261102-gse-public-data-landscape/`・`experiments/20261102-public-data-landscape/`
- 既存のコード・docs の本文は変えない。`_handoff/README.md` の自分の行だけを更新する。

## テスト戦略

- 変換と集計の小さな自己検査（合成の入力で、数える規則が期待どおりか）を run.sh の先頭で回す。
- 取っておく書き手が入力に混ざっていないことを集計の中で確かめて止める。
- 本計算の前に、先頭の少数と一時の出力先で走ることだけを確かめる（値は読まない）。

## ディスク

- 空きは 2026-11-02 に 3.8 GB。KLiCKe の中間は展開しない。CoAuthor の中間は 1 本ずつ消す。3 GB を切ったら止める。
