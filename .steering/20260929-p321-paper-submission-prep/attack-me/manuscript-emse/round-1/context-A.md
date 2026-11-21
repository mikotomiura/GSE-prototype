# context-A — 査読者と監査役の両方に渡すもの（attack-me・stage `manuscript`・round 1）

作成: 2026-10-02（G-GEAR・メイン）。

## 対象物

- 論文: *When "no help" is not "solved": outcome-agnostic self-resolution measures in two public debugging datasets*（単著）
- 投稿先: *Empirical Software Engineering*（Springer）の Research Papers。**2026-09-29 に投稿済み**（原稿番号 EMSE-D-26-01273・査読はまだ返っていない）。
- 版: 再現一式のリポジトリ（公開）のタグ `submission-2026-09-29`（コミット `75ce1ff`）。下の一覧のファイルは、そのタグを展開した写し（作業ツリーの外に固定した）。
  - 投稿した `main.tex` は、このタグの `paper/main.tex` と次の 2 点だけが違う: (1) 文書クラスの選択肢が `[pdflatex,sn-basic,referee,lineno]`（査読用の組版・行番号つき）、(2) 投稿システムが `.tex` を 1 つしか受け付けないため `results.tex` の中身（数値の定義だけ）を本文の先頭に埋め込んだ。本文は同一。
  - 投稿した組版（査読用の 32 頁）から取り出したテキストも一覧に入れた（数値が埋まった形で読める・参考文献の一覧を含む）。
- ★ 数値の読み方: `main.tex` の数値は `\R{<key>}` のマクロで、値は `results.tex` にある。**読むときは `main.resolved.tex`**（`main.tex` と**行番号が同じ**で、マクロを値に置き換えた写し）を使い、位置の引用は `main.tex` の行番号で書いてよい（2 つのファイルの行番号は一致する）。

## 読んでよいファイルの一覧（これだけ・絶対パス・1 行 1 件）

### 原稿

- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\paper\main.resolved.tex`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\paper\main.tex`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\paper\results.tex`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\paper\refs.bib`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\emse-submitted-preview.txt`（投稿した組版の PDF から pypdf で取り出したテキスト・32 頁）

### 再現一式（原稿の Data availability / Code availability が指す公開物）

- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\README.md`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\NOTES.md`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\DATA.md`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\ENV.md`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\config.json`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\SEED`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\run.sh`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\analysis\analyze.py`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\analysis\d1.py`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\analysis\d2.py`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\analysis\stats.py`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\data\li-coblenz-2026\README.md`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\data\li-coblenz-2026\transcription_a.csv`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\data\li-coblenz-2026\transcription_b.csv`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\data\li-coblenz-2026\text_external.csv`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\results\metrics.json`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\results\report.md`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\results\provenance.txt`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\paper\build.sh`
- `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\paper\make_results.py`

### 再解析の原典（公開版・事実の確かめに使う。精読は求めない —— `Grep` で該当箇所を引けばよい）

- D1 のプレプリント（arXiv:2105.02162v1）: `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\sources\alaboudi2021.txt`
- D2（arXiv:2602.11435v3。原稿が表を転記した版）: `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\sources\li2026.txt`
- ⚠️ D1 の journal 版（Alaboudi & LaToza 2023, *EMSE* 28:117）は無料で読める版が無いので一覧に入れていない。原稿がそこから引いた逐語・数値は、この一覧の中では確かめられない（確かめられないことを「誤り」としない）。
- ⚠️ D1 のコード化データ（`rowData.json`）と再現パッケージの zip は渡さない（生データ）。集計の結果は `results/` にある。

### 入れていないもの（理由）

`LICENSE`・`LICENSE-DATA`（ライセンスの全文。README にライセンスの表がある）・`.gitattributes`・`.gitignore`・`paper/main.tex` 以外の組版の中間物・データの zip と `rowData.json`。

## 測った値（メインが機械で測った）

| 項目 | 値 | 測り方 |
|---|---|---|
| 要旨の語数 | **234 語** | 投稿システムに入れた要旨の平文を空白で区切って数えた（LaTeX のマクロを除いて数えると 236 語） |
| キーワード | **6 個**（Debugging, Help seeking, Measurement, Construct validity, Reanalysis, Reproducibility） | `main.tex` の `\keywords` |
| 本文の語数 | 約 **7,060 語**（表・数式・Statements を除く散文） | `main.resolved.tex` の `\maketitle` から `\backmatter` までからマクロを除いて数えた（概数） |
| 表 / 図 | 表 **5** / 図 **0** | `\begin{table}` / `\begin{figure}` の数 |
| 参考文献 | **21 件**（引用されていない項目 0・未定義の引用 0） | `refs.bib` と `\cite` の突き合わせ |
| 頁数 | 通常の組版 **21 頁**／投稿した査読用の組版 **32 頁** | 組版の結果（作業記録） |
| 節 | Introduction / Background and related work / Measures / Data / Method / Results / Discussion / Threats to validity / Conclusion / Statements and Declarations | `\section` |

## 投稿規程の一次の抜粋（EMSE・Submission guidelines）

- URL: <https://link.springer.com/journal/10664/submission-guidelines>・取得日 2026-10-02・`curl -sL`（cookie つき）で原文の HTML を取得（200）。下の逐語は、その原文のテキストに**逐語で在ることを確かめた**（＝**照合済み**。「要件のまとめ」の 1 文目と「LLM の利用」の 1 文目は、原文ではリンクの境目に空白が入り、引用符の字形が違うだけで、語は一致する）。

| 要件 | 逐語 | 照合 |
|---|---|---|
| 査読方式 | "This journal follows a single-blind reviewing procedure." | 照合済み |
| 要旨 | "Please provide an abstract of 150 to 250 words. The abstract should not contain any undefined abbreviations or unspecified references." | 照合済み |
| キーワード | "Please provide 4 to 6 keywords which can be used for indexing purposes." | 照合済み |
| 声明 | "The following statements should be included under the heading "Statements and Declarations" for inclusion in the published paper. Please note that submissions that do not include relevant declarations will be returned as incomplete." | 照合済み |
| 声明（要件のまとめ） | "The above should be summarized in a statement and included on a title page that is separate from the manuscript with a section entitled "Declarations" when submitting a paper." ／ "Declarations include Funding, Competing interests, Ethics approval, Consent, Data, Materials and/or Code availability and Authors' contribution statements." ／ "Please use the title page for providing the statements." | 照合済み |
| タイトル頁 | "Please make sure your title page contains the following information." — Title / "The name(s) of the author(s)" / "The affiliation(s) of the author(s), i.e. institution, (department), city, (state), country" / "A clear indication and an active e-mail address of the corresponding author" / "If available, the 16-digit ORCID of the author(s)" ／ "For authors that are (temporarily) unaffiliated we will only capture their city and country of residence, not their e-mail address unless specifically requested." | 照合済み |
| LLM の利用 | "Large Language Models (LLMs), such as ChatGPT, do not currently satisfy our authorship criteria." ／ "Use of an LLM should be properly documented in the Methods section (and if a Methods section is not available, in a suitable alternative part) of the manuscript." ／ "The use of an LLM (or other AI-tool) for "AI assisted copy editing" purposes does not need to be declared." | 照合済み |
| データ | "Sharing of all relevant research data is strongly encouraged and authors must add a Data Availability Statement to original research articles." ／ "All original research must include a data availability statement. This statement should explain how to access data supporting the results and analysis in the article, including links/citations to publicly archived datasets analysed or generated during the study." ／ "When creating a data availability statement, authors are encouraged to consider the minimal dataset that would be necessary to interpret, replicate and build upon the findings reported in the article." | 照合済み |
| 原ファイル | "Please ensure you provide all relevant editable source files at every submission and revision. Failing to submit a complete set of editable source files will result in your article not being considered for review." | 照合済み |
| LaTeX | "Please do not use subfolders for your LaTeX submission, e.g. for figures or bibliographic files." | 照合済み |
| 謝辞 | "Acknowledgments of people, grants, funds, etc. should be placed in a separate section on the title page." | 照合済み |
| 分量の上限 | — | **規定なし**（取得した範囲の原文に、本文の語数・頁数の上限の文が無い） |

- 補足（事実）: 投稿システムでは、タイトル頁（題・著者・メール・ORCID・都市と国）を別のファイルで上げた。声明は原稿の末尾の "Statements and Declarations" にある（タイトル頁には載せていない）。原稿の所属は都市と国だけ（独立の研究者）。
