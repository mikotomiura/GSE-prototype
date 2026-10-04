# context-A — 査読者役と監査役の両方に渡すもの（attack-me・stage `outline`・round 2）

作成: 2026-10-05（G-GEAR・メイン）。対象物は commit `9463fae6`（枝 `docs/ime-manuscript-outline`・外枠を最後に変えた commit。round 1 の指摘を直したもの）。

## 対象物

原稿の外枠（節構成・主張 ↔ 根拠の対応表）: `C:\GSE-prototype\papers\ime-observation\manuscript\outline.md`

★ この段階では原稿の本文はまだ無く、計測の結果も解析されていない（結果の値は外枠に 1 つも無い）。それ自体を欠陥にしない。外枠が名指しする事前登録（凍結済み）と記録は下の一覧で読める。

## 読んでよいファイルの一覧（これだけ・絶対パス）

round 1 と同じ 11 本:

- C:\GSE-prototype\papers\ime-observation\manuscript\outline.md
- C:\GSE-prototype\papers\ime-observation\README.md
- C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md
- C:\GSE-prototype\papers\ime-observation\experiment\deviations.md
- C:\GSE-prototype\papers\ime-observation\experiment\notes.md
- C:\GSE-prototype\papers\ime-observation\experiment\data.md
- C:\GSE-prototype\papers\ime-observation\experiment\data.windows.md
- C:\GSE-prototype\papers\ime-observation\experiment\pilot-macos.md
- C:\GSE-prototype\papers\ime-observation\experiment\pilot-windows.md
- C:\GSE-prototype\papers\ime-observation\kit\formats\FORMATS.md
- C:\GSE-prototype\papers\ime-observation\kit\logger\README.md

round 2 で足したもの（直した外枠が根拠として新しく名指ししたファイル）:

- C:\GSE-prototype\papers\ime-observation\kit\run\README.windows.md（RE4 の根拠）
- 〔任意〕ロガーのソースと単体テスト（LG1b・LG2a・LG2b の根拠）:
  - C:\GSE-prototype\papers\ime-observation\kit\logger\src\input\ime_compose.rs（macOS のセッションの規則・単体テスト 37 本）
  - C:\GSE-prototype\papers\ime-observation\kit\logger\src\input\ime_cloak.rs（Windows の隠蔽の経路・単体テスト 12 本）
  - C:\GSE-prototype\papers\ime-observation\kit\logger\src\driver_windows\ime_winevent.rs（Windows の窓のイベントの経路・単体テスト 8 本）
  - C:\GSE-prototype\papers\ime-observation\kit\logger\src\driver_windows\cloak.rs（単体テスト 12 本）
  - C:\GSE-prototype\papers\ime-observation\kit\logger\src\driver_windows\candidate.rs（単体テスト 9 本）

★ ロガーのソースを読むのは任意で、目的は「外枠が根拠に名指ししたファイルが在り、名指した性質（打ち切り・安全弁・閉じる鍵・文字を書かないこと）を試しているか」を確かめることだけ。実装の品質のレビューはこの stage の対象ではない。単体テストの本数は `#[test]` の数をメインが数えた値。

外枠が名指しするほかのコード（`kit/analysis/pipeline.py`・`spec_predict.py`・`kit/pilot/clock_sync.py`・`kit/formats/validate_logs.py`・`experiment/run.sh`）は、round 1 と同じく一覧に入れていない（外枠の段階で問うのは主張の骨格であって実装ではない）。読んでいないことを前提に評価してよい。

## 測った値（メインが機械で測った・2026-10-05）

| 項目 | 値 |
|---|---|
| 外枠の語数（`wc -w`） | 6,984（round 1 は 4,374） |
| 主張 ↔ 根拠の表の行数 | 31（OB 4・LG 5・RF 1・AG 8・KT 1・RC 3・RT 1・RE 5・DS 3） |
| 予定の図 | 5（Figure 1〜5） |
| 予定の表 | 12（Table 1〜12）＋ 試行の表（Table of attempts）＋ 補遺（層ごとの表・観測可能性の分析の文書の一覧） |
| 節 | 13 ＋ Declarations ＋ Open Practices Statement ＋ References |
| 参考文献 | まだ無い（外枠は引く文献を名指しするだけ） |
| 要旨 | まだ無い（外枠は要旨の骨子と「Rule for the abstract」だけ） |

## 投稿規程の一次の抜粋（Behavior Research Methods）

- URL: https://link.springer.com/journal/13428/submission-guidelines
- 取得: 2026-10-05 00:39 JST、`curl -sL`（cookie つき）で原文の HTML を取得し直した（HTTP 200・283,581 バイト）。以下の文は**この round の取得で原文に逐語で在ることを確かめた（照合済み・26 文）**。

| 要件 | 逐語 | 状態 |
|---|---|---|
| 記事の種別 | "Behavior Research Methods accepts original research articles, as well as tutorials." | 照合済み |
| 誌の範囲 | "Behavior Research Methods publishes articles concerned with the methods, techniques, and instrumentation of research in experimental psychology." / "Authors are encouraged to write their articles in such a way that readers can easily use the materials in their own work (e.g., by making stimuli and programming code available)." | 照合済み |
| 書式 | "Manuscripts are to adhere to the conventions described in the Publication Manual of the American Psychological Association (7th ed.)." / "All manuscripts are to be double spaced and have 1” margins with page numbers in the upper right corner of each page." | 照合済み |
| タイトル頁 | "The title page must include the authors’ names and affiliations and the corresponding author’s address, telephone number, and e-mail address." | 照合済み |
| 要旨 | "There must be an abstract of no more than 250 words." | 照合済み |
| 節 | "Manuscript should be divided into sections (and perhaps subsections) appropriate for their content (e.g., introduction/background, Method, Results, etc.), as per APA style." | 照合済み |
| Declarations | "All manuscripts must contain the following sections under the heading 'Declarations'." / "If any of the sections are not relevant to your manuscript, please include the heading and write 'Not applicable' for that section." 見出し: Funding / Conflicts of interest/Competing interests / Ethics approval / Consent to participate / Consent for publication / Availability of data and materials / Code availability / Authors' contributions (optional …) / "placed in a ‘Declarations’ section before the reference list" | 照合済み |
| Open Practices | "All submitted manuscripts must include an Open Practices Statement immediately prior to the References section of the paper." | 照合済み |
| TOP Level 2 | "In 2020, the Editorial Board of Behavior Research Methods decided that the journal follows the Open Science Initiative’s Level 2 Transparency and Openness Guidelines." / "This means that all relevant information must be placed in a trusted repository." / "This applies to stimuli and methods being validated, new analyses being reported, and new equipment being described." / "BRM readers want practical solutions." / "There is little point in describing new materials that cannot be applied easily and correctly." | 照合済み |
| データの方針 | "This journal operates a type 4 research data policy" / "A submission to the journal implies that materials described in the manuscript, including all relevant raw data, will be freely available to any researcher wishing to use them for non-commercial purposes, without breaching participant confidentiality." / "All original research must include a data availability statement." | 照合済み |
| データの引用 | "Data citations should include a persistent identifier (such as a DOI), should be included in the reference list using the minimum information recommended by DataCite" | 照合済み |
| 統計 | 投稿時の確認の一つ: "the manuscript includes appropriate measures of variability, effect size, and (when relevant) statistical power." | 照合済み |
| 投稿 | "Manuscripts are to be submitted electronically via ScholarOne" | 照合済み |
| 本文の分量の上限 | — | 規定なし（取得した範囲の原文に "word limit"・"maximum length" などの語が無い） |
| LaTeX の雛形 | — | 規定なし（取得した範囲の原文に "LaTeX" の語が無い） |
