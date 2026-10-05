# context-A — 査読者役と監査役の両方に渡すもの（attack-me・stage `manuscript`・round 1）

作成: 2026-10-05 夜（G-GEAR・メイン）。対象物は commit `f30a6e6c`（`origin/main`。原稿を最後に変えた commit は `b12729aa`）。

## 対象物

原稿の全体（Behavior Research Methods に投稿する予定の original research article）: `C:\GSE-prototype\papers\ime-observation\manuscript\`
の `main.tex` が `\input` する節・図・表と、補遺 `supplement\supplement.tex`。

★ 読み方:

- 本文の値は `\rv{<key>}` で、`generated\values.tex` の `\csname rv@<key>\endcsname{<値>}` の行から読む（例: `\rv{macos-standard-live-off.primary.recall.range}` は `rv@macos-standard-live-off.primary.recall.range` の行）。表と図は `generated\` の `table-*.tex`・`fig-*.tex`。
- ★ **読む補助**: 組んだ PDF からテキストを抜き出したもの（値が埋まった状態で読める）を `C:\GSE-prototype\.steering\20260927-ime-observation-paper-eval-design\attack-me\manuscript-ime-observation\round-1\tmp\rendered\main.txt` に置いた（66 頁・頁の区切りは `===== page N =====`）。⚠️ 表の体裁は崩れ、改行が語の途中に入る。**指摘の位置と逐語は `.tex` のファイルと行で示す**こと（補助のテキストの頁は添えてよい）。
- `\tbd{…}` の 15 か所（データセットの DOI・repo の URL・release の DOI・外枠を固定した commit・表 1 の版・寄託の欄）は、**データの寄託と公開 repo の作成の後に埋める予定の欄**で、それ自体を欠陥にしない。ただし、埋まった後に規程を満たす形になっているか（何を書く欄か）は見てよい。
- `%` で始まる行は LaTeX のコメントで、読者には見えない（著者の覚え書き）。指摘の根拠にしてよいが、読者に見える本文と区別すること。

## 読んでよいファイルの一覧（これだけ・絶対パス）

### 対象物（原稿）

- C:\GSE-prototype\papers\ime-observation\manuscript\main.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\introduction.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\related.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\observability.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\logger.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\method.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\results-agreement.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\results-text.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\recoverability.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\cost.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\dataset.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\recommendations.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\limitations.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\conclusions.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\sections\declarations.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\figures\components.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\generated\values.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\generated\ の `table-*.tex`（8 本: closed-set・cost・detection・key-timing・open-set・reference・session・text-agreement）と `fig-*.tex`（4 本: closed-set・detection・dwell・text-agreement）
- C:\GSE-prototype\papers\ime-observation\manuscript\references.bib
- C:\GSE-prototype\papers\ime-observation\manuscript\supplement\supplement.tex
- C:\GSE-prototype\papers\ime-observation\manuscript\supplement\observability-documents.tex
- 〔任意・大きい〕補遺の層ごとの表: C:\GSE-prototype\papers\ime-observation\manuscript\generated\ の `detection-strata.tex`・`session-strata.tex`・`reference-strata.tex`・`text-agreement.tex`・`closed-set-all.tex`・`detection-layers.tex`
- 読む補助（上）: C:\GSE-prototype\.steering\20260927-ime-observation-paper-eval-design\attack-me\manuscript-ime-observation\round-1\tmp\rendered\main.txt

### 原稿が名指す公開物（原稿は「公開 repo」「事前登録」「逸脱の記録」「計測の記録」「データの形式」としてこれらを指す）

- C:\GSE-prototype\papers\ime-observation\manuscript\outline.md（Open Practices Statement が「結果を解析する前に報告の規則を固定した外枠」として名指す）
- C:\GSE-prototype\papers\ime-observation\README.md
- C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md（凍結した事前登録・macOS の本体と §10 の Windows の追補）
- C:\GSE-prototype\papers\ime-observation\experiment\deviations.md（逸脱 D1〜D10）
- C:\GSE-prototype\papers\ime-observation\experiment\notes.md
- C:\GSE-prototype\papers\ime-observation\experiment\data.md
- C:\GSE-prototype\papers\ime-observation\experiment\data.windows.md
- C:\GSE-prototype\papers\ime-observation\experiment\pilot-macos.md
- C:\GSE-prototype\papers\ime-observation\experiment\pilot-windows.md
- C:\GSE-prototype\papers\ime-observation\kit\formats\FORMATS.md
- C:\GSE-prototype\papers\ime-observation\kit\logger\README.md
- C:\GSE-prototype\papers\ime-observation\kit\run\README.windows.md
- C:\GSE-prototype\papers\ime-observation\kit\e3\README.md（問 5 の計測の手順）
- C:\GSE-prototype\papers\ime-observation\experiment\results\e3_macos.txt と C:\GSE-prototype\papers\ime-observation\experiment\results\windows\e3_windows.txt（問 5 の結果のファイル・各 1 KB）
- 〔任意〕ロガーのソースと単体テスト（原稿の §4 の性質を確かめるためだけ。実装の品質のレビューは対象外）:
  - C:\GSE-prototype\papers\ime-observation\kit\logger\src\input\ime_compose.rs（macOS のセッションの規則）
  - C:\GSE-prototype\papers\ime-observation\kit\logger\src\input\ime_cloak.rs
  - C:\GSE-prototype\papers\ime-observation\kit\logger\src\driver_windows\ime_winevent.rs
  - C:\GSE-prototype\papers\ime-observation\kit\logger\src\driver_windows\cloak.rs
  - C:\GSE-prototype\papers\ime-observation\kit\logger\src\driver_windows\candidate.rs
  - C:\GSE-prototype\papers\ime-observation\kit\logger\src\main.rs（Windows の安全弁）
  - C:\GSE-prototype\papers\ime-observation\kit\logger\src\driver_macos.rs と C:\GSE-prototype\papers\ime-observation\kit\logger\src\driver_macos\keymap.rs（macOS のキー行・行を書くキーの集合）

一覧に入れていないもの: 解析のコード（`kit/analysis/`・`kit/pilot/`）・結果の JSON（`experiment/results/*.json`・数 MB。原稿の値はそこから道具が生成した `values.tex` と表で読む）・表を生成する道具・生ログ・封印物。読んでいないことを前提に評価してよい（「確かめられない」と書いてよい）。

## 測った値（メインが機械で測った・2026-10-05 夜）

| 項目 | 値 |
|---|---|
| 要旨の語数 | 249（`\rv` を展開して数えた。規程の上限は 250） |
| 本文の分量 | 組んだ PDF で 66 頁（sn-jnl・単段）。表紙から References の前までの語数は約 21,100（PDF のテキスト抽出で数えた・表と図の字を含む） |
| 節 | 13 ＋ Declarations ＋ Open Practices Statement ＋ References |
| 図 | 5（Figure 1〜5。Figure 2 は横向きの頁） |
| 表 | 18（うち横向き 10） |
| 参考文献 | 68 件（`main.bbl` の項目の数） |
| 補遺 | 163 頁（層ごとの表 66 本 ＋ 観測可能性の分析の文書の一覧） |
| 組版 | `main` はエラー 0・未定義の参照 0・生成されていない値 0（`build.sh`） |
| `\tbd` | 15 か所（上の「読み方」） |
| 書式 | `\documentclass[pdflatex,sn-apa]{sn-jnl}`（Springer Nature の雛形・APA の参照の様式） |

## 投稿規程の一次の抜粋（Behavior Research Methods）

- URL: https://link.springer.com/journal/13428/submission-guidelines
- 取得: 2026-10-05 23:00 JST、`curl -sL`（cookie つき）で原文の HTML を取り直した（HTTP 200・283,581 バイト）。以下の文は**この round の取得で原文に逐語で在ることを確かめた（照合済み・32 文）**。

| 要件 | 逐語 | 状態 |
|---|---|---|
| 記事の種別 | "Behavior Research Methods accepts original research articles, as well as tutorials." / "Tutorial manuscripts provide a practical guide for researchers to implement new technologies, code solutions, and/or methodology." | 照合済み |
| 誌の範囲 | "Behavior Research Methods publishes articles concerned with the methods, techniques, and instrumentation of research in experimental psychology." / "Authors are encouraged to write their articles in such a way that readers can easily use the materials in their own work (e.g., by making stimuli and programming code available)." | 照合済み |
| 書式 | "Manuscripts are to adhere to the conventions described in the Publication Manual of the American Psychological Association (7th ed.)." / "All manuscripts are to be double spaced and have 1” margins with page numbers in the upper right corner of each page." | 照合済み |
| 図と表 | "Figures and tables are to be designed as per APA style." / "In submitted manuscripts, figures and tables can be embedded in the body of the text" / "Graphs and figures can be published in color in the journal at no cost to the author" | 照合済み |
| タイトル頁 | "The title page must include the authors’ names and affiliations and the corresponding author’s address, telephone number, and e-mail address." | 照合済み |
| 要旨 | "There must be an abstract of no more than 250 words." | 照合済み |
| 節 | "Manuscript should be divided into sections (and perhaps subsections) appropriate for their content (e.g., introduction/background, Method, Results, etc.), as per APA style." | 照合済み |
| Declarations | "All manuscripts must contain the following sections under the heading 'Declarations'." / "If any of the sections are not relevant to your manuscript, please include the heading and write 'Not applicable' for that section." 見出し: Funding / Conflicts of interest/Competing interests / Ethics approval / Consent to participate / Consent for publication / Availability of data and materials / Code availability / Authors' contributions (optional …) / "placed in a ‘Declarations’ section before the reference list"。⚠️ 見出しの一覧の直前に "To be used for life science journals + articles with biological applications" の行がある | 照合済み（⚠️ 一覧の適用範囲は原文から読み切れない → 未照合（適用範囲）） |
| Open Practices | "All submitted manuscripts must include an Open Practices Statement immediately prior to the References section of the paper." / 例文 "Stimuli, validation data and analysis code are available at (url for the site hosting the data and materials). Validation study 1 was preregistered (url for the preregistration)." | 照合済み |
| TOP Level 2 | "In 2020, the Editorial Board of Behavior Research Methods decided that the journal follows the Open Science Initiative’s Level 2 Transparency and Openness Guidelines." / "This means that all relevant information must be placed in a trusted repository." / "This applies to stimuli and methods being validated, new analyses being reported, and new equipment being described." / "BRM readers want practical solutions." / "There is little point in describing new materials that cannot be applied easily and correctly." | 照合済み |
| データの方針 | "This journal operates a type 4 research data policy" / "A submission to the journal implies that materials described in the manuscript, including all relevant raw data, will be freely available to any researcher wishing to use them for non-commercial purposes, without breaching participant confidentiality." / "All original research must include a data availability statement." | 照合済み |
| データの引用 | "Data citations should include a persistent identifier (such as a DOI), should be included in the reference list using the minimum information recommended by DataCite" | 照合済み |
| 統計 | 投稿時の確認の一つ: "the manuscript includes appropriate measures of variability, effect size, and (when relevant) statistical power." / 統計の指針: "Alternatively an analysis might focus on estimation of an effect size rather than on a hypothesis test." / "In any case, the Method section should make clear what criteria were used to determine the sample size." / "If participants or observations were eliminated, then explicitly indicate why, when, and how this was done and either (a) report or synopsize the results of analyses that include all of the observations or (b) explain why such analyses would not be appropriate." | 照合済み |
| 投稿 | "Manuscripts are to be submitted electronically via ScholarOne" | 照合済み |
| 本文の分量の上限 | — | 規定なし（取得した範囲の原文に "word limit"・"maximum length" の語が無い） |
| LaTeX の雛形 | — | 規定なし（取得した範囲の原文に "LaTeX" の語が無い） |
| キーワード | — | 規定なし（取得した範囲の原文に "keywords" の語が無い） |
| AI の使用 | — | BRM の規程のページには無い（"Large Language"・"artificial intelligence" の語が無い）。出版社の方針は下 |

### 出版社（Springer Nature）の方針: AI use in manuscript preparation

- URL: https://www.springernature.com/gp/policies/editorial-policies/ai-manuscript-preparation
- 取得: 2026-10-05 23:00 JST、`curl -sL`（HTTP 200・84,142 バイト）。次の文が原文に逐語で在ることを確かめた（照合済み）: "Clearly describe use and confirm author accountability" / "drafting sections based on author input" / "Writing results or discussion independently" / "generating scientific claims or interpretations" / "the argument, interpretation, and conclusions must be author-led" / "Specific disclosure should be provided within the caption or legend of the visual content."
- ⚠️ この方針が BRM に適用されることは、BRM の規程のページからは読み取れない（出版社の全体の方針）→ 未照合（適用範囲）。
