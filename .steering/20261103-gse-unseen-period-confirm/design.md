# 設計

## アプローチ

- 停滞の検出は c1c2c6 の `candidates.py`（`Day`・`day_rows`・`check_structure`・`summarize`）をそのまま読み込む。検出器を写し直さない。
- 新しく書くのは判定の量だけ（`confirm.py`）: H4a の過分散（χ² は標準ライブラリで実装）と 1 時間のブロックの並べ替え、H5 のまとまりの前半・後半の RR とまとまりのブートストラップ、U4 の読みの照合。
- 中間は停滞の分解の `build_o1.py` で作る（同じ `gse-replay`）。

## 変更対象

- 新規: `experiments/20261103-o1-unseen-confirm/`（conditions・data・env・SEED・confirm.py・mutants.py・run.sh）。既存のコードは変えない。

## テスト戦略

- 陽性対照（U5）を `confirm.py --selftest` に置く。χ² は既知の値、H4a は手で出した例とポアソンの模擬（支持の割合・反証の割合）、H5 は答えの分かる合成のまとまり。
- 変異（`mutants.py`）がすべて赤になることを確かめる。最初の版の 17 種で 2 種が緑のまま（判断 6）、1 巡目のレビューの後に 32 種へ増やした（判断 7）。
- `run.sh` が O1 の稼働中に止まることを、今の状態で実際に走らせて確かめる。
