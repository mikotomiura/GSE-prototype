# 休止の定義と調整で何が動くか

原稿 *What moves with the pause definition and the adjustment: a multiverse diagnostic of pause and stall labels in
keystroke logs*（三浦尊統・Journal of Educational Data Mining に投稿）のコード・条件・集計の結果です。[English](README.md)

![90 通りの定義での停滞の率と作文の得点](docs/media/score.svg)

窓で停滞を検出する検出器を、研究用に公開された 4 つの打鍵のデータ（入門プログラミングの授業の 2 つの年版 CS1 2019・
CS1 2021、作文のコーパス KLiCKe、言語モデルの提案つきの作文のコーパス CoAuthor）に当て、窓・閾値・止まりの条件・
観測の切り方を基準のまわりの 89 通りに振り、固定の閾値で休止を数える検出器（18 通りと、対照として書き手の分位の 18 通り）
を足しました。どの結論にも書き手の再標本の区間を付けています。図はその 1 つで、停滞の率と作文の総合の得点の相関は、
大半の定義で負、15 秒の窓と書き手の分位の閾値の組でだけ正になり（a）、作文の長さで調整すると負の定義は無くなります（b）。

## 中身

| 場所 | 中身 |
|---|---|
| `experiments/20261107-stall-shape-multiverse/scripts/` | 検出器・90 通りの定義・論文のすべての計算 |
| `experiments/20261107-stall-shape-multiverse/results/` | 定義ごとの集計の結果（JSON） |
| `experiments/20261107-stall-shape-multiverse/conditions*.md` | 各計算の前にコミットした条件（日本語・参照を伏せた写し・`REDACTED.md`） |
| `experiments/20261107-stall-shape-multiverse/conditions-summary-en.md` | 条件の英語の要約（補足 S1 の順） |
| `experiments/20261107-stall-shape-multiverse/notes.md` | 各計算の記録と読み（日本語・参照を伏せた写し） |
| `experiments/20261103-stall-candidates-c1c2c6/candidates.py` | 元のモジュールのうち、スクリプトが使う 2 つの定義をそのまま写したもの |
| `experiments/2026110{1,4}-*/scripts/`・`experiments/20261031-*/scripts/` | データの変換のスクリプト（姉妹の研究のアーカイブと同じバイト） |
| `paper/` | 原稿と補足の LaTeX。`paper/figdata/` は図のデータ（定義ごと） |
| `tools/verify.py` | 生のデータ・書き手ごとの表・識別子・秘密・手元のパスが無いことの検査 |
| `tools/readme_media.py` | 上の図を `paper/figdata/score.csv` から描く |

## ここに無いもの

- データそのもの。KLiCKe と CoAuthor は公開されています。CS1 は著者に申請して受け取るもので、データの著者との約束で
  集計値だけを公開しています。
- 書き手ごとの値・書き手の識別子・中間のファイル（repo の外に置いています）。
- 観測区間を持つ作業用のファイル。姉妹の研究の推定器から作ります。作るには姉妹の研究のアーカイブ
  [10.5281/zenodo.24026278](https://doi.org/10.5281/zenodo.24026278)（推定器・変換・replay）が要ります。
  姉妹の研究の原稿はプレプリント [10.5281/zenodo.24026330](https://doi.org/10.5281/zenodo.24026330) で読めます。
- 著者の内部の作業記録。日本語の条件と記録では、それへの参照を `[internal reference removed]` に置き換えました。
  `REDACTED.md` に、元のファイルの SHA-256 と置き換えた数を載せています。

## 再現の手順

1. 姉妹の研究のアーカイブで作業用のファイルを作ります（各データの変換と推定器の replay は、そちらの README にあります）。
2. Python 3・NumPy・SciPy・statsmodels で（版は `experiments/20261107-stall-shape-multiverse/env.md`。`PY` の既定は
   `$DATA_DIR/venv-paper2/bin/python`）:

   ```
   export DATA_DIR=/path/outside/this/repo PY=/path/to/python3
   bash experiments/20261107-stall-shape-multiverse/run.sh
   ```

   `run.sh` は自己検査・変異の検査・主の計算を回します。追加の計算（補足 S1 の順序 2〜11）は、各条件に書いたスクリプトを
   同じ seed（`SEED`）で回します。検査が通らなければ止まります（たとえば、検出器が保存した始まりを再現しないとき）。
3. `python3 -I tools/verify.py` でアーカイブそのものを検査します。

どの計算も、走らせる前に著者のバージョン管理に条件をコミットしてから回しました。第三者の登録ではなく、順序はリポジトリ
が示すもので、独立の時刻の証明ではありません（`source-commit.txt` は組み立てに使った commit）。

## ライセンス

コード: MIT か Apache-2.0（`LICENSE-MIT`・`LICENSE-APACHE`）。文章・結果・図: CC BY 4.0（`LICENSE-docs`）。

## 引用

`CITATION.cff` を見てください。
