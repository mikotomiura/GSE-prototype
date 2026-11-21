# context-A — 査読者と監査役の両方に渡すもの（attack-me・stage `manuscript`・round 2）

作成: 2026-11-21（Surface・メイン）。

## 対象物

- 論文: *When "no help" is not "solved": unconsulted shares and unaided resolution in two public debugging datasets*（単著）
- 投稿先: *Journal of Systems and Software*（JSS・Elsevier）。**まだ投稿していない**（投稿の前の round）。
- 経緯: round 1 は、同じ論文の前の版（*Empirical Software Engineering* に投稿した版）に当てた。その版は EMSE で査読に回らず不採択になり、著者は round 1 の指摘を受けて改訂し、出し先を JSS に替えた。⚠️ 前の版のファイルは渡さない。round 1 の自分の指摘と、その対応は引き継ぎ（carryover）に書いてある。
- 版: 再現一式のリポジトリ（公開予定の改訂版・ブランチ `revision-jss`・コミット `75e8e76`）を展開した写し（作業ツリーの外に固定した）。
- 原稿の組み立て: `paper/main-jss.tex`（elsarticle の枠）が `abstract.tex`・`body.tex`（第 1 節から結論まで）・`declarations.tex`（文献表の前の声明）を読み込む。Highlights は別のファイル `highlights.tex`。
- ★ 数値の読み方: 本文の数値は `\R{<key>}` のマクロで、値は `results.tex` にある。**読むときは `*.resolved.tex`**（元のファイルと**行番号が同じ**で、マクロを値に、`\Rz{}`・`\Rzp{}`・`\Ro{}` を U・A・A|R に置き換えた写し）を使い、位置の引用は元のファイルの行番号で書いてよい（行番号は一致する）。
- 組版の結果（26 頁）から取り出したテキストも一覧に入れた（数値が埋まった形で読める・参考文献の一覧を含む）。

## この round の範囲

- ★ **重点**: 改訂で足した、または書き直した次の箇所。
  - §3.1 Definitions（`body.tex` 61–70 行）: r_i・c_i が何を記録しているか・b/(a+b) の定義。§3.4 の冒頭の但し書き（89 行から）
  - RQ1（`body.tex` 185–233 行）: b/(a+b)・DF3 の寄与・leave-one-developer-out・CR2 の区間・2×2 表
  - §7 "Beyond these two datasets"（`body.tex` 330–335 行）
  - 2 つ目の実装による数え直し（`audit/independent-recount/` と、それを述べる §5.5・§8）
- ⚠️ **対象外**: §2.5 Literature search（`body.tex` 52–58 行）と、それを指す序論の文（`body.tex` 8 行）。この節は、記録を付けた文献検索のやり直しが終わってから書き直す予定で、いまの文は古い。**この節の中身（検索の範囲・件数）を指摘の対象にしない**。ただし、序論や他の節がこの節に頼りすぎている、という構成の指摘はしてよい。
- 照会: 原著者への照会は 2026-11-21 に送った。投稿の時点で返事が無ければ、本文の "at the time of submission we had not received a reply" のまま出す（返事が来れば RQ4 に書く）。

## 読んでよいファイルの一覧（これだけ・絶対パス・1 行 1 件）

### 原稿

- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\paper\body.resolved.tex`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\paper\body.tex`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\paper\abstract.resolved.tex`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\paper\abstract.tex`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\paper\highlights.resolved.tex`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\paper\highlights.tex`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\paper\declarations.resolved.tex`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\paper\declarations.tex`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\paper\main-jss.tex`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\paper\results.tex`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\paper\refs.bib`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\jss-preview.txt`（組版の PDF から pypdf で取り出したテキスト・26 頁）

### 再現一式（原稿の Data availability が指す公開物）

- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\README.md`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\NOTES.md`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\DATA.md`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\ENV.md`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\config.json`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\SEED`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\run.sh`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\analysis\analyze.py`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\analysis\d1.py`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\analysis\d2.py`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\analysis\stats.py`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\analysis\post_review.py`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\analysis\derived.py`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\audit\independent-recount\README.md`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\audit\independent-recount\recount.py`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\audit\independent-recount\output.txt`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\data\li-coblenz-2026\README.md`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\data\li-coblenz-2026\transcription_a.csv`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\data\li-coblenz-2026\transcription_b.csv`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\data\li-coblenz-2026\text_external.csv`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\results\metrics.json`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\results\report.md`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\results\provenance.txt`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\results\d1_episodes.csv`（D1 の episode 単位の派生表・匿名の開発者とセッションの番号・符号・長さ。名前・URL・元のセッション ID は無い）
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\paper\build.sh`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\paper\make_results.py`
- `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\target\self-resolution-measure\paper\check_frontmatter.py`

### 再解析の原典（公開版・事実の確かめに使う。精読は求めない —— `Grep` で該当箇所を引けばよい）

- D1 のプレプリント（arXiv:2105.02162v1）: `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\sources\alaboudi2021.txt`
- D2（arXiv:2602.11435v3。原稿が表を転記した版）: `C:\GSE-wt\p321-desk-reject\.steering\20261121-p321-paper-revision\attack-me\manuscript-jss\round-2\tmp\sources\li2026.txt`
- ⚠️ D1 の journal 版（Alaboudi & LaToza 2023, *EMSE* 28:117）は一覧に入れていない。原稿がそこから引いた逐語・数値は、この一覧の中では確かめられない（確かめられないことを「誤り」としない）。
- ⚠️ D1 のコード化データ（`rowData.json`）と再現パッケージの zip は渡さない（生データ）。集計の結果は `results/` にある。

### 入れていないもの（理由）

`LICENSE`・`LICENSE-DATA`（ライセンスの全文。README にライセンスの表がある）・`.gitattributes`・`.gitignore`・組版の中間物・データの zip と `rowData.json`。

## 測った値（メインが機械で測った）

| 項目 | 値 | 測り方 |
|---|---|---|
| 要旨の語数 | **249 語**（素朴な数え方では 250 語） | 再現一式の `paper/check_frontmatter.py`（マクロを値に置き換えた後）／ メインがマクロを除き空白で区切って数えた値 |
| キーワード | **6 個**（Debugging, Help seeking, Measurement, Construct validity, Reanalysis, Reproducibility） | `main-jss.tex` の `keyword` 環境 |
| Highlights | **5 本**（82・71・77・78・73 字） | `highlights.tex` の `\item`（マクロを値に置き換えた後・空白を含む） |
| 本文の語数 | 約 **11,100 語**（表・数式を除く散文。第 1 節から結論まで） | `body.resolved.tex` からマクロを除いて数えた（概数） |
| 表 / 図 | 表 **6** / 図 **0** | `\begin{table}` / `\begin{figure}` の数 |
| 参考文献 | **28 件**（引用されていない項目 0・未定義の引用 0） | `refs.bib` と `\cite` の突き合わせ |
| 頁数 | **26 頁**（elsarticle の preprint・12pt・1 段組） | 組版の結果（PDF の頁数） |
| 節 | Introduction / Background and related work / Measures / Data / Method / Results / Discussion / Threats to validity / Conclusion（声明は `declarations.tex`） | `\section` |

## 投稿規程の一次の抜粋（JSS・Guide for authors）

- URL: <https://www.sciencedirect.com/journal/journal-of-systems-and-software/publish/guide-for-authors>・取得日 2026-11-21・`curl` は 403 だったので Chrome で開き、ページの本文のテキスト（空白を詰め、引用符の字形をそろえた後）に下の文が**逐語で在ることを機械で確かめた**（＝**照合済み**・17 文すべて在った）。

| 要件 | 逐語 | 照合 |
|---|---|---|
| LaTeX | "We encourage you use our LaTeX template when preparing a LaTeX submission." ／ "You will be asked to provide all relevant editable source files upon submission or revision." | 照合済み |
| 原ファイル | "Submit files with .doc/.docx extensions for Word and .tex for LaTeX files." ／ "A PDF is not an acceptable source file." ／ "Double-column formatting is only permitted for LaTeX submissions." | 照合済み |
| 要旨 | "You are required to provide a concise and factual abstract that does not exceed 250 words." | 照合済み |
| Highlights | "You are required to provide article highlights at submission." ／ "Highlights should consist of 3 to 5 bullet points, each a maximum of 85 characters, including spaces." | 照合済み |
| キーワード | "You are required to provide 1 to 7 keywords for indexing purposes." | 照合済み |
| 生成 AI | "Authors must declare the use of generative AI tools in the manuscript preparation process upon submission of the paper." ／ "Editing and adapting all material thoroughly to ensure the manuscript represents the author's authentic and original contribution and reflects their own analysis, interpretation, insights, and ideas." ／ 置き場: "should be placed in a new section before the reference list." ／ 見出しの例: "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process" | 照合済み |
| 謝辞 | "Acknowledgments should be placed in a separate section that appears directly before the reference list." | 照合済み |
| データ | "Deposit your research data in a relevant data repository." ／ "Provide a link to the dataset during the submission process." | 照合済み |
| Open Science | 採択の後の審査について "which does not affect acceptance of the paper" | 照合済み |
| 範囲 | "All articles should provide evidence to support their claims" ／ "as well as replication studies and studies with negative results" | 照合済み |
| 分量の上限 | — | **規定なし**（取得した範囲の原文に、本文の語数・頁数の上限の文が無かった〔"page limit"・"word limit"・"maximum length" を探して 0 件〕） |
| 利益相反の声明の形 | — | **未照合**（"declaration of competing interests section" という語はあるが、その節の書式を定める文を照合していない） |
