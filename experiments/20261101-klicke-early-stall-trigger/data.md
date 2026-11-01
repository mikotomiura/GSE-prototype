# 入力データ

- KLiCKe [V264]（Tian, Crossley & Van Waes, 2025）。GitHub `terryyutian/KLiCKe-Corpus` の README が指す Drive のフォルダの `WritingTask.zip`（ファイル ID `120FkdzVlVBsyYQdvwLhlcLToTDRDStb_`）。
- 取得: 2026-11-01T08:10:04Z（UTC）に curl で取り直した。699,610,000 バイト・SHA-256 `ffa4d753fdb9a54f5cadd6836426d56a0cabe73ceade8e7e40dddbbae178555d`（照合論文のトラックの `experiments/20261012-public-keystroke-matching/data.md` の 2026-10-12 の取得と一致）。
- 使ったもの: `keystrokelogs/csv/*.csv` 4,992 本の `DownTime`・`UpTime`・`DownEvent` の 3 列だけ。zip から 1 本ずつ読み、展開していない。本文・採点・課題文・IDFX・`TextChange`・`Activity` は読んでいない。人口統計のファイル・打ち写しと語彙の試験は取っていない。
- 利用条件: Inputlog のページ [V273] 逐語 *"These files can be downloaded and used freely. However, if you wish to use them in your research project, please reference this repository as an original"*。出典として [V264] を示す。
- 置き場: `~/gse-public-data/klicke/raw/`（repo の外・再配布しない）。中間は `~/gse-public-data/klicke/work/`（書き手の番号は zip の中の名前の昇順の通し番号で、ID を書かない）。
- 記録を外部の LLM（Codex を含む）に送っていない。
