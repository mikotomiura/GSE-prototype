# 入力データ

3 つとも取得した（2026-10-12〜13・各節の「取得」）。版と SHA-256 はこの文書と `config.json` に書いた。取得の後の検査は `notes.md` の「データの検査」。記録と本文は公開データだが repo に入れない（`raw/`・git に入らない）。repo に入れるのは集計だけ。記録と本文を外部の LLM（Codex を含む）に送らない。

## KLiCKe [V264]

- 入手先: GitHub の README が指す Google Drive のフォルダ（zip 3 つと人口統計の CSV。2026-10-12 に構成だけを見た・[V264] の行）。
- 利用条件: Inputlog のページ [V273] 逐語 *"These files can be downloaded and used freely. However, if you wish to use them in your research project, please reference this repository as an original"*。
- 取得するもの: 議論文の課題の記録（CSV）・本文・人の採点だけ。人口統計のファイルは取得しない（調査票が MTurk の worker ID を尋ねている・[V264] の付録 A）。zip に同梱されていれば展開せず、zip の SHA-256 だけを記録する。打ち写しの試験・語彙の試験も使わない。
- 取得の開始条件: 事前登録の凍結の後に取得する。著者への問い合わせ（`.steering/20261012-public-keystroke-matching-judgement/author-inquiry-draft.md`・研究者が 2026-10-12 に送付）の返事は待たない（判断 51）。返事で利用に懸念が示されたら、計算を止め、取得したデータを消し、その経緯を報告する。
- 版の固定（取得のときに書く）: 取得の日・Drive のファイル ID・各ファイルの SHA-256・GitHub のリポジトリのコミット。

### 取得（2026-10-12T19:29:56Z・UTC）

- GitHub のリポジトリ `terryyutian/KLiCKe-Corpus` のコミット `37b94b72d6cec485f3f475f712ea4032c9101875`（2025-02-11）の README が指す Drive のフォルダ `13Q02Mvj7T-T1OpZzkEqfHwqM7oI61lLR`。フォルダの目録（ファイル名と ID）は `raw/klicke/drive_folder_listing.html`。Chrome は使わず curl で取得した。
- 取得したもの: `WritingTask.zip` だけ（Drive のファイル ID `120FkdzVlVBsyYQdvwLhlcLToTDRDStb_`・699,610,000 バイト・SHA-256 `ffa4d753fdb9a54f5cadd6836426d56a0cabe73ceade8e7e40dddbbae178555d`）。`demographic_info.csv`・`TypingTests.zip`・`VocabularyKnowledgeTest.zip` は取得していない。
- zip の目録（名前と大きさだけを見た）: `keystrokelogs/csv` 4,992・`keystrokelogs/idfx` 4,992・`texts` 4,992（`.txt`）・`holistic_scores.csv`（11,360,401 バイト）・`holistic_rating_form.docx`・`writing_prompts.docx`。人口統計のファイルは入っていない。ファイル名の ID は 8 桁の数字で、記録と本文で同じ 4,992 個（MTurk の worker ID の形ではない）。
- 展開したもの: 記録の CSV・本文・`holistic_scores.csv`・`writing_prompts.docx`（IDFX と採点の様式は展開しない）。各ファイルの SHA-256 の一覧は `raw/klicke/manifest_extracted.sha256`（書き手の ID を含むので repo に入れない。一覧そのものの SHA-256 は `8a039a71b8e8b142580cdd30467eeff58217d71ca65262dbab37965e585c2066`）。展開は zip から決まるので、zip の SHA-256 で再現できる。
- 検査 1・2（2026-10-13・数と列名だけ）: `holistic_scores.csv` の列は `ID,Prompt,Text,Score`。`Text` の列は読み込みに使わず、本文は `texts/<ID>.txt` を使う。記録の CSV は `TextChange`・`DownEvent`・`UpEvent` で改行・タブ・二重引用符・バックスラッシュをバックスラッシュつきの 2 字で書いている（読み込みで戻す・`notes.md` の逸脱 D1）。記録の CSV の 21 本と `holistic_scores.csv` は utf-8 で読めず cp1252 で読む。

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
- 検査 5（2026-10-13・数と名前と値の形だけ）: 76 セッション・訳者 39・原文 6（交差）。訳文は各 XML の `LogFile/FinalTextUTF8` を使い、`Alignment/*.tgt` は使わない（`notes.md`）。

## KeyTAR の公開モデル [V267]

- 入手先: Zenodo records/17254163 の `keytar.zip`（15,039 MB・CC BY 4.0・2026-10-12 に API とプレビューで確かめた）。
- 取得の開始条件: 研究者が 15 GB の取得を認めた。取得の後、本計算の前に `model_licenses`・`ethics.txt`・`limitations.txt` を読む。
- 版の固定（取得のときに書く）: `keytar.zip` の SHA-256。
- 取得の開始: 2026-10-13（`raw/keytar/`）。Zenodo の API の記録の応答を `raw/keytar/zenodo_record_17254163.json` に保存した: `keytar.zip`・15,039,177,667 バイト・`md5:a56da07f5a086bcc8c9763abe1b00934`・cc-by-4.0。取得が終わったら md5 を照合し、SHA-256 をここと `config.json` に書く。
- 取得の完了: 2026-10-12T21:56:20Z（UTC）・15,039,177,667 バイト（Zenodo の値と一致）・md5 `a56da07f5a086bcc8c9763abe1b00934`（Zenodo の値と一致）・SHA-256 `d2fe250a7219b7f6f796d52d2cacda35d5b2d3dab2f4847c0ddbbb6ca1159876`。

### 検査 6（2026-10-13）

- 読んだ文書（`raw/keytar/docs_extracted/`）: `README.md`・`license.txt`（MIT）・`citation.txt`・`code_artifact/README.md`・`use.txt`・`destructive.txt`・`install.sh`・`data_artifact/README.md`・`ethics.txt`・`limitations.txt`・`provenance.txt`・`code_artifact/artifact/LICENSE`（Apache 2.0・open-instruct）と、推論のコード（`scripts/eval/evaluate_key.py`・`convert_data_inference.py`・`claims/llm_reconstruction/`）。`model_licenses`（`code_artifact/artifact/assets/model_licenses/`）は llama・opt・pythia・tulu の利用条件で、KeyTAR のチェックポイントの基（`allenai/OLMo-1B-0724-hf`・Hugging Face の API で `apache-2.0`）のものではない。利用条件と ethics は本研究の使い方に反しない（`notes.md` の検査 6）。A4 を行う。
- 展開したもの（`raw/keytar/extracted/`・git に入らない）: `data_artifact/data/key_ground_truth_olmo/`（`.jsonl` を除く・`pytorch_model.bin` の SHA-256 `d09f06db0f3dbaebf28a6a80e4d4651629dbf8ca3d20bc6d5656ee5d13f7144f`・2,559,611,026 バイト。`config.json`・`generation_config.json`・`special_tokens_map.json`・`tokenizer.json`・`tokenizer_config.json` の SHA-256 は `scripts/check6_keytar.py` の `CHECKPOINT_SHA256` にあり、読み込みの前に照合する）と `data_artifact/data/key_ground_truth/test/`（学習の書式を確かめるため）。
- 使うチェックポイント: `key_ground_truth_olmo`（元の打鍵の間隔で学習した方。`key_cache_olmo` はキャッシュから取った間隔で学習した方で、使わない）。基は OLMo-1B-0724（16 層・隠れ 2,048・語彙 50,304・bfloat16 で保存）。
- KeyTAR の既定の設定（`scripts/eval/evaluate_key.py` の `model.generate` の引数）: `max_new_tokens` 50・`num_beams` 64・`num_beam_groups` 16・`diversity_penalty` 0.8・`no_repeat_ngram_size` 2・`num_return_sequences` 50・`do_sample` False・`top_k` 50・`temperature` 1.0・`top_p` 1.0・`repetition_penalty` 1.0。読み込みは `AutoModelForCausalLM.from_pretrained(..., device_map="auto")` で型の指定なし（float32）。transformers 4.49.0。
- 入力の書式（成果物の学習のデータ `key_ground_truth/test` の `messages`）: 対話の型（`<|user|>`・`<|assistant|>`）で、利用者の文は "Translate the Time intervals to Keystrokes.\nTime intervals: " に間隔を空白で区切った整数（ms）を続けたもの。間隔は Shift と句読点を含む全部の押下の間で、上限 1,023 で切られている（10,481 例の最大が 1,023）。例の 52% は文脈なしの 1 往復、残りは同じ書き手の前の文を 1〜4 往復含む。
- A4 の実装の段で決めること（登録の「英字・数字・Space の押下だけ」「20 区間の塊」は固定）: 間隔の上限 1,023 を当てるか・前の往復を入れないこと・復元の 50 本のうち比べる 1 本（既定の出力の先頭）。検査 6 の時間は、上限を当て・前の往復なしで測った。
