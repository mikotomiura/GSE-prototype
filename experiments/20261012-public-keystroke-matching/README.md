# 公開の打鍵の記録の加工は、本文の照合にどこまで効くか（公開データでの照合の論文の本計算）

公開の打鍵の記録の加工（Kaggle の `q` のマスク [V265]・キーの種類への縮約・時刻の丸め・区間の長さを粗くする・置換・並べ替え・抑制）を、本文の分かる公開データ（英語の自由作文 KLiCKe [V264]・日本語 IME の翻訳 ENJA15 [P273] [P360]）で、記録から本文を照合する攻撃（全長 A0・最終稿の長さ A1・エディタの模擬 A1'・区間の揃え A2・区切りの推定 A2-b・時刻 A3・参照の KeyTAR [V267] A4）に当てて測る。合否は判定しない。

- 状態: **事前登録の下書き 7（未凍結）**。凍結の版は OSF に登録し、コードと集計は論文の git リポジトリのリリースを Zenodo に置く（判断 24・25）。データは取得していない。本計算のコードは書いていない（凍結の前の合成の記録の検査のコードだけがある: `scripts/`・結果は `notes.md`）。
- 作業記録: `.steering/20261012-public-keystroke-matching-prereg/`（研究者の判断は `decisions.md` 判断 6〜47）
- 前の作業: `.steering/20261012-public-keystroke-matching-judgement/`（判断 1〜5）・`docs/literature/20261012-public-keystroke-matching-novelty.md`・`docs/literature/20261012-public-keystroke-matching-prereg-search.md`
- 結果の前に固定すること: `preregistration.md`・`config.json`・`SEED`
- 入力: `data.md`（取得の開始条件と版の固定の手順）
- 再利用するコード（予定）: `experiments/20261011-g1-copy-self-trial/scripts/align.py`（区間の揃え）。研究者本人の記録は使わない（判断 6）

## 取得の開始条件（データセットごと・判断 7）

| データ | 条件 |
|---|---|
| KLiCKe | 著者への問い合わせの返事を見て、研究者が進めると決めた |
| ENJA15 | ライセンスの種類と利用条件を一次で確かめた |
| KeyTAR の公開モデル | 研究者が 15 GB の取得を認めた |

## まだ無いもの

`run.sh`・本計算の `scripts/`・`env.md`・`requirements.txt`・本計算の結果。事前登録を凍結し、取得の開始条件を満たしてから作る。凍結の前の検査は `python scripts/selftest_synthetic.py` と `python scripts/synthetic_check.py --out results/synthetic_check.json`（人のデータを使わない）。
