# データ

- 公開データ: 俯瞰（`../20261102-public-data-landscape/data.md`）と同じ入力と中間。KLiCKe [V264] の `work.tar.gz`・`klicke_side.json`、CoAuthor [V348] の `coauthor_work/`（どれも repo の外）。SHA-256 は `public/results/provenance.json`。取っておいた書き手の一覧（`holdout.json`）の SHA-256 も同じ所にある。
- O1: 研究者本人の O1 の記録（この Mac の `~/Documents/GSE-sessions/`・macOS）。名前の日付が 20261018〜20261101 の 18 本（条件のコミットの時点で書き込み中だった 1 本を除く）。フォーカスの行が 0 の 4 本を除いた 14 本を使った。入力の SHA-256 の連結の digest は `o1/results/provenance.json`。個々の SHA-256 は中間（`~/gse-o1-derived/20261102-stall-decomposition/`）にある。gse-dataset には入れていない。
- 打鍵の外の信号を持つ公開データ（`extend/`）: DUX [V352]（Zenodo 7778612 の `v0.csv`・`v1.csv`・CC BY 4.0）と SWELL-KW [V351]（DANS doi:10.17026/dans-x55-69zp の生の uLog の XML 76 本・CC BY-NC-SA 4.0）。置き場は `~/gse-public-data/dux/raw/`・`swell/raw/`、中間と取っておく一覧は `~/gse-public-data/extend/`（どれも repo の外）。入力の SHA-256 は `extend/conditions.md` E1 と `extend/results/build_summary_*.json`。
- repo に入れたのは集計値だけ（ID・時刻・ファイル名・日付・本文なし）。
