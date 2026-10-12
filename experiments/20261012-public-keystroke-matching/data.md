# 入力データ（取得の前・下書き）

どのデータもまだ取得していない。取得したら、この文書に版と SHA-256 を書き、`config.json` の `to be filled at acquisition` を埋める。記録と本文は公開データだが repo に入れない（`raw/`・git に入らない）。repo に入れるのは集計だけ。記録と本文を外部の LLM（Codex を含む）に送らない。

## KLiCKe [V264]

- 入手先: GitHub の README が指す Google Drive のフォルダ（zip 3 つと人口統計の CSV。2026-10-12 に構成だけを見た・[V264] の行）。
- 利用条件: Inputlog のページ [V273] 逐語 *"These files can be downloaded and used freely. However, if you wish to use them in your research project, please reference this repository as an original"*。
- 取得するもの: 議論文の課題の記録（CSV）・本文・人の採点だけ。人口統計のファイルは取得しない（調査票が MTurk の worker ID を尋ねている・[V264] の付録 A）。zip に同梱されていれば展開せず、zip の SHA-256 だけを記録する。打ち写しの試験・語彙の試験も使わない。
- 取得の開始条件: 事前登録の凍結の後に取得する。著者への問い合わせ（`.steering/20261012-public-keystroke-matching-judgement/author-inquiry-draft.md`・研究者が 2026-10-12 に送付）の返事は待たない（判断 51）。返事で利用に懸念が示されたら、計算を止め、取得したデータを消し、その経緯を報告する。
- 版の固定（取得のときに書く）: 取得の日・Drive のファイル ID・各ファイルの SHA-256・GitHub のリポジトリのコミット。

## ENJA15 [P273] [P359] [P360]

- 入手先: CRITT TPR-DB の SVN の DAV エンドポイント（`https://svn.code.sf.net/p/tprdb/svn/TPRDB/ENJA15/`・[P360]）。
- 取得の前に確かめること: ライセンスの種類（[P273] は "creative commons license" とだけ書く）と利用条件、T・P・D の意味（[P273] [P359] の本文）。
- 版の固定（取得のときに書く）: SVN のリビジョン・各ファイルの SHA-256。
- 2026-09-13 に別の目的で取得した `P01_T1.xml` は使わない（版が固定されていない）。

### 取得の前の確認（2026-10-13・事前登録「データ」の開始条件）

- T・P・D の意味: [P483] §2 逐語 *"1. from-scratch translation (T) 2. translation dictation (D) 3. MT post-editing (P)"*。T は白紙からの翻訳で、事前登録の「使うセッション」と一致する。[P273] の APTIF の PDF は置き場（Dropbox）が 404 で読めず、[P359] は MDPI の PDF が curl に 403 を返した（Chrome では未確認）。T の意味は同じ著者・同じ研究の [P483] で確かめた。
- ライセンスの種類: CRITT TPR-DB のページで食い違う（[P484]）。License のページは "CC BY-NC-SA"（版の記載なし）、TPR-DB のページの License の節は "Creative Commons Attribution-NonCommercial 4.0 International License"。どちらも非営利・出典の表示で、厳しい方は継承（SA）。本研究は非営利で、データを再配布せず集計だけを公開するので、どちらにも合う。厳しい方（BY-NC-SA）に従い、出典として [P273] [P360] [P484] を示す。
- 参加者の同意: [P483] §2 逐語 *"they signed a form in which they agreed that their translation data would be made publicly available under a creative commons license"*（倫理の節の材料）。

### 取得（2026-10-12T19:22:52Z・UTC）

- 経路: DAV のリビジョン固定のパス `https://svn.code.sf.net/p/tprdb/svn/!svn/bc/649/TPRDB/ENJA15/`。取得の時点のリポジトリの最新は Revision 649。
- 取得したもの: T のセッションだけ。`Translog-II/P??_T?.xml` 76 本（888 MB）と、同じセッションの `Alignment/` の `.atag`・`.src`・`.tgt` 各 76 本（3.2 MB）。P・D のセッションと `projects/` は取得していない。失敗 0。
- 版: 各ファイルの SHA-256 は `enja15-manifest-r649.sha256`（この一覧の SHA-256 は `401c922535f788cf0ae46eea92d6ef4703c3bf37ce6bd6af69ddad73c854a4c8`）。置き場は `raw/enja15/`（git に入らない）。
- 中身はまだ開いていない（検査 5 で数だけを出す）。

## KeyTAR の公開モデル [V267]

- 入手先: Zenodo records/17254163 の `keytar.zip`（15,039 MB・CC BY 4.0・2026-10-12 に API とプレビューで確かめた）。
- 取得の開始条件: 研究者が 15 GB の取得を認めた。取得の後、本計算の前に `model_licenses`・`ethics.txt`・`limitations.txt` を読む。
- 版の固定（取得のときに書く）: `keytar.zip` の SHA-256。
- 取得の開始: 2026-10-13（`raw/keytar/`）。Zenodo の API の記録の応答を `raw/keytar/zenodo_record_17254163.json` に保存した: `keytar.zip`・15,039,177,667 バイト・`md5:a56da07f5a086bcc8c9763abe1b00934`・cc-by-4.0。取得が終わったら md5 を照合し、SHA-256 をここと `config.json` に書く。
