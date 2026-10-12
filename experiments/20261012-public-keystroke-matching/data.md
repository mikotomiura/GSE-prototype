# 入力データ（取得の前・下書き）

どのデータもまだ取得していない。取得したら、この文書に版と SHA-256 を書き、`config.json` の `to be filled at acquisition` を埋める。記録と本文は公開データだが repo に入れない（`raw/`・git に入らない）。repo に入れるのは集計だけ。記録と本文を外部の LLM（Codex を含む）に送らない。

## KLiCKe [V264]

- 入手先: GitHub の README が指す Google Drive のフォルダ（zip 3 つと人口統計の CSV。2026-10-12 に構成だけを見た・[V264] の行）。
- 利用条件: Inputlog のページ [V273] 逐語 *"These files can be downloaded and used freely. However, if you wish to use them in your research project, please reference this repository as an original"*。
- 取得するもの: 議論文の課題の記録（CSV）・本文・人の採点だけ。人口統計のファイルは取得しない（調査票が MTurk の worker ID を尋ねている・[V264] の付録 A）。zip に同梱されていれば展開せず、zip の SHA-256 だけを記録する。打ち写しの試験・語彙の試験も使わない。
- 取得の開始条件: 著者への問い合わせ（`.steering/20261012-public-keystroke-matching-judgement/author-inquiry-draft.md`・研究者が送付済み）の返事を見て、研究者が進めると決めた。
- 版の固定（取得のときに書く）: 取得の日・Drive のファイル ID・各ファイルの SHA-256・GitHub のリポジトリのコミット。

## ENJA15 [P273] [P359] [P360]

- 入手先: CRITT TPR-DB の SVN の DAV エンドポイント（`https://svn.code.sf.net/p/tprdb/svn/TPRDB/ENJA15/`・[P360]）。
- 取得の前に確かめること: ライセンスの種類（[P273] は "creative commons license" とだけ書く）と利用条件、T・P・D の意味（[P273] [P359] の本文）。
- 版の固定（取得のときに書く）: SVN のリビジョン・各ファイルの SHA-256。
- 2026-09-13 に別の目的で取得した `P01_T1.xml` は使わない（版が固定されていない）。

## KeyTAR の公開モデル [V267]

- 入手先: Zenodo records/17254163 の `keytar.zip`（15,039 MB・CC BY 4.0・2026-10-12 に API とプレビューで確かめた）。
- 取得の開始条件: 研究者が 15 GB の取得を認めた。取得の後、本計算の前に `model_licenses`・`ethics.txt`・`limitations.txt` を読む。
- 版の固定（取得のときに書く）: `keytar.zip` の SHA-256。
