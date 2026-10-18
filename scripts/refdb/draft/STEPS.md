# 2026-10-18 に文献 DB を作った手順（下書き・次のセッションで 1 本の仕組みに直す）

このフォルダのスクリプトは、2026-10-18 のセッション（枝 `docs/tangibility-design` の作業中）に作業用の一時ディレクトリで書いた下書きの写し。パスは当時の一時ディレクトリを指したままで、そのままでは動かない。下の 1〜8 のうち、ファイルとして残っているのは 1・2・3・5・6 だけで、4・7・8 はその場で書いたコードだった（手順だけを書く）。

## 1. 書誌と引用を集める（`build.py`）

- 読む枝: `origin/main`・`origin/docs/tangibility-design`・`origin/docs/ai-fatigue-c-outline`・`origin/docs/ai-fatigue-core1-item-analysis`・`origin/docs/ai-fatigue-core2-discriminant`・`origin/docs/ai-fatigue-motivation-claims`。
- 各枝の `docs/references.md` の `| [Pn] |`・`| [Vn] |` の行を読む。列は 8 列（id・key・著者と題・出典・URL・接地・重複・状態）。7 列の行（重複の列が無い）もある。初版はこれを取りこぼした。
- key（DOI・arXiv・URL など）で文献をまとめる。同じ番号が枝によって別の文献を指すもの（番号の衝突）が 48 個ある。
- 各枝の `docs/` と `experiments/` の `.md` から `[Pn]` / `[Vn]` を拾い、その枝の番号表で key に直す。精読カード（`docs/literature/*.md`・`_index.md` を除く）からの引用と、それ以外の文書からの引用を分ける。
- 出力 `data.json`: `works`（key ごとの ids・枝・著者と題・出典・URL・接地・状態）、`cite`（key → カードのファイル名）、`other`（key → カード以外の文書）。
- 2026-10-18 の結果: 906 件。カードから引かれている 675 件、カード外 128 件、未引用 103 件。

## 2. カードでの記述を拾う（`claims.py`）

- カードの表の行と `### ` の見出しのうち、番号を含む行を拾う。表の行は最も長いセルを記述とする。
- 温度は行の中の語（確定・PLAUSIBLE BUT UNPROVEN・判定不能・否決・confirmed・refuted・3-0・2-1・1-2・0-3）の最後のもの。
- 出力 `claims.json`: key → [{d: カードの日付, t: 記述 220 字まで, temp}]。576 件・1,571 行。見出しの行も混じる。

## 3. 抄録を取る（`fetch_abs.py`）

- カードから引かれている 675 件のうち DOI と arXiv（579 件）。OpenAlex（`abstract_inverted_index` を並べ直す）→ Semantic Scholar → Crossref の順。
- 連絡先のメールアドレスは送らない。
- 2026-10-18 の結果: 513 件（OpenAlex 503・Semantic Scholar 10）。キャッシュは `~/.cache/gse-refdb/abstracts.json`（抄録は著作物なので repo に入れない）。

## 4. 要約を書く（その場のコード・探索役 7 本）

- 675 件を 7 束（約 97 件）に分け、入力は key・title・venue・abstract（3,000 字まで）・gse_note（接地 700 字まで）。
- Sonnet の探索役に、要約（80〜160 字・自分の言葉・連続 15 語以上の写しを作らない）、特徴（「種類 ｜ 対象・N ｜ 主な結果・数値」・数値は材料にあるものだけ）、材料（抄録 / 接地のみ / 題のみ）を書かせた。依頼文は次のセッションで `scripts/refdb/summary_prompt.md` に起こす。
- メインの検算: JSON の形・件数・key の一致、英語 15 語の n-gram で抄録との重なり（0 件）、要約と特徴の数値が材料にあるか（31 件を目で確かめ、推測の 1 件を直した: Eich & Beck の人数）、4 件の抜き取り。
- 結果は `docs/literature/refdb/summaries.json`（675 件・抄録 505・接地のみ 169・題のみ 1）。

## 5. 書誌を取る（`fetch_csl.py`）

- DOI と arXiv の全件を `https://doi.org/<doi>` に `Accept: application/vnd.citationstyles.csl+json` で問い合わせる。2026-10-18 の結果: 715 件取得・失敗 2 件。キャッシュは `~/.cache/gse-refdb/csl_raw.json`。

## 6. 検索のページ（`template.html`）

- `__DATA__` と `__STRANDS__` を JSON で置き換える（`</` は `<\/` に）。公開先は Artifact https://claude.ai/artifact/Js8ZBgzkWAZBHdgrzqjwSA （同じ URL に出し直す）。
- データの形: id・coll・ns・at・src・yr・strands・cards [{t, f}]・other・st・br・key・url・note（接地の全文）・sum・feat・basis・cc（カードでの記述）。

## 7. スプレッドシート用の CSV（その場のコード）

- 列: ID・番号の衝突・名前空間・著者・題・出典・年・研究の筋・要約・特徴・要約の材料・カードでの記述・接地（全文）・カード・カード外の引用元・状態・枝・key・URL・読んだ・メモ（20 列）。UTF-8 の BOM 付き。
- 研究の筋は、カード 52 枚を 9 つに分けた対応（`build.py` の後の手順で使った表。下）から、引いたカードの筋をすべて持たせる。カードに引かれていないものは「カード外」「未引用」。
- URL が空で key が DOI / arXiv なら `https://doi.org/…` / `https://arxiv.org/abs/…` で補う。
- シートへの入れ方（API で 906 行を送ると量が大きすぎるため）: CSV を Drive for desktop の同期フォルダ（フォルダ GSE の手元の場所 `~/Library/CloudStorage/GoogleDrive-…/マイドライブ/Doe_Systems/Reserch_production/GSE`）に置く → Chrome でその CSV の「Google スプレッドシート で開く」を押して一時のシートにする → `copy_sheet_to_another_spreadsheet` で DB へ写す → `copyPaste`（PASTE_VALUES）で「一覧」へ貼る → 写したシートを消す → 一時のシートをゴミ箱へ。
- 読んだ・メモ（S・T 列）は、貼る前に API で読み、key で結び直してから貼る（2026-10-18 時点では空だったので未実装）。

## 8. 書誌のファイル（その場のコード）

- 5 の取得分は type・title・author・editor・container-title・volume・issue・page・issued・DOI・URL・publisher・ISBN・event・collection-title・number だけを残す。取れなかったものは手元の題・出典・年から最小限に作る。
- 引用キーは最初の番号（例 `P534`）。重なれば key の末尾 8 字を足す。`keyword` に研究の筋、`note` に「GSE <ID> ｜ <要約>」。
- pandoc が受け付けない形を直す: 文字列の欄が配列や数（DataCite 経由）→ 先頭の要素の文字列に、`issued` の `date-parts` に null や文字が混じる → 数だけ残し、空なら欄ごと外す。
- `pandoc -f csljson -t biblatex` と `-t bibtex` で 906 件ずつ。

## 研究の筋（カード 52 枚 → 9 つ）

| 筋 | カードのファイル名に含まれる語 |
|---|---|
| 1 較正・自己申告・プローブ | calibration-sampling / probe-timing / recovery-labeling / self-resolution / auto-onset |
| 2 介入・摩擦・AI への依存 | intervention-content / activation-layer / agentic-coding / friction-retention / behavioral-economics / ai-escape / avoidance-guilt / motivation-fatigue-reentry |
| 3 打鍵の動態・IME・停滞の推定 | task-type-writing / desk-behavior / silence-discrimination / typing-dynamics / japanese-ime / stall-onset / content-free-revision / resumption-restop / controlled-task / scope-detection |
| 4 ambient・表現の媒体・周辺の注意 | self-state-externalization / auditory-modality / sound-necessity / design-parsimony / portable-ambient / smartphone-ambient / interruption-coupling / legibility-demotion / pc-invitation-surface / third-place-norms |
| 5 理論・規範 | theory-scaffold / unmeasured-embodied-return / authority-return-burden / non-domination / digital-nature |
| 6 肖像・生成芸術 | autographic-book / data-portrait / generative-art-process |
| 7 手跡・タンジビリティ | rhythm-stage / tangibility- / handmark- |
| 8 打鍵データの公開・再識別 | keystroke-release / public-keystroke-matching / length-unicity |
| 9 AI 疲労 | ai-fatigue |

## 外にあるもの（2026-10-18）

- スプレッドシート「GSE 文献DB」: https://docs.google.com/spreadsheets/d/1v7frJm2a6BkXzepEpglB62AT_2c3t0NzJ2mNA8UfRFw/edit （シート: 検索・集計・一覧・凡例。フォルダ GSE `1-AeR6-4iqKtRrgO_gR2pRVKB5l-gN1pf`）
- 検索のページ: https://claude.ai/artifact/Js8ZBgzkWAZBHdgrzqjwSA
- 書誌のファイル: フォルダ GSE の `GSE文献DB_2026-10-18_biblatex.bib`・`_bibtex.bib`・`.csl.json`
- 変換に使った CSV 2 本（`GSE文献DB_2026-10-18.csv`・`GSE文献DB_v2_2026-10-18.csv`）も同じフォルダに残っている。
