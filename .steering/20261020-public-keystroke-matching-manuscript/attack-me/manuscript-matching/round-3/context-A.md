# context A（査読者・編集者・監査役に渡す・stage: manuscript・round 3・原稿の全体）

対象物は commit c3f3f5b5（branch docs/public-keystroke-matching-manuscript）の原稿。PoPETs 2027 Issue 3（締切 2026-11-30）に投稿する予定の論文の全体。

## 対象物の状態
- 結果（§7）・序論・考察・結論・抄録は、事前登録の本計算の集計から書いた。表の値は集計の JSON から機械で生成し、`sections/generated/` から読み込む。
- 残っている空欄（角括弧 `[...]`）は 3 つで、どれも欠陥にしない: 倫理の節の公開元へ知らせた日付と応答（ethics.tex）・Open science の匿名リンク（open-science.tex）・付録 E の全員（4,992 人）の結果（appendix-results.tex。計算中）。
- 脅威モデル・攻撃者・手順は、データを取得する前に固定した事前登録（OSF）にあり、原稿はそれを変えずに述べる。逸脱は §6.8 に一覧がある。
- 二重盲検の投稿なので、著者・所属・登録のリンクは伏せてある。

## 読んでよいファイルの一覧（印: 本文 / 必須の節 / 補足）
印の根拠: authors-2027.php の "The main body excludes the three mandatory sections … as well as any acknowledgements, the bibliography, and any clearly-marked appendices" と "PC members are not required to read the appendices during review"。main.tex で `\appendix` の後に必須の 3 節、参考文献、付録 A〜E の順に置く（テンプレートの指定）。
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/main.tex 〔本文〕題・抄録・節の並び（付録と必須の節の \input を含む。PoPETs の規程で抄録は本文の頁に入る）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/introduction.tex 〔本文〕
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/related.tex 〔本文〕
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/threat-model.tex 〔本文〕
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/data.tex 〔本文〕
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/attackers.tex 〔本文〕
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/protocol.tex 〔本文〕
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/results.tex 〔本文〕
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/discussion.tex 〔本文〕
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/conclusion.tex 〔本文〕
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/main-1000.tex 〔本文〕results.tex の表 4（主表）の中身（\tabinput で読み込む・集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/main-10.tex 〔本文〕results.tex の表 4（主表）の中身（\tabinput で読み込む・集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/main-a4-1000.tex 〔本文〕results.tex の表 4（主表）の中身（\tabinput で読み込む・集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/main-a4-10.tex 〔本文〕results.tex の表 4（主表）の中身（\tabinput で読み込む・集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/ethics.tex 〔必須の節〕上限の外・テンプレートが必須とし、査読者が読む
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/open-science.tex 〔必須の節〕上限の外・テンプレートが必須とし、査読者が読む
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/ai-use.tex 〔必須の節〕上限の外・テンプレートが必須とし、査読者が読む
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/references.bib 〔必須の節〕参考文献（上限の外）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/appendix-checks.tex 〔補足〕付録（規程: 査読者に読む義務は無い）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/appendix-enja.tex 〔補足〕付録（規程: 査読者に読む義務は無い）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/appendix-attackers.tex 〔補足〕付録（規程: 査読者に読む義務は無い）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/appendix-exploratory.tex 〔補足〕付録（規程: 査読者に読む義務は無い）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/appendix-results.tex 〔補足〕付録（規程: 査読者に読む義務は無い）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/a4-full.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/a4-windows.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/cells-1.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/cells-2.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/enja.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/explore-band.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/explore-dp-r0.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/explore-dp-score.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/explore-dp.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/explore-margin.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/explore-tail.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/explore-unicity.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/negative.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/open-world.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/secondary.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/split.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/utility-r0.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/utility-score.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/windows.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/experiments/20261012-public-keystroke-matching/preregistration.en.md 〔補足〕事前登録の正の版（読者は OSF で読める）

節の順は main.tex の \input の順（§1〜§9 → 必須の 3 節 → 参考文献 → 付録 A〜E）。`generated/figure-coords.tex` はコメントだけなので一覧に入れない（図 1 の座標は results.tex の中にある）。outline.md（著者の計画の文書）はこの round から一覧に入れない（読者が見ないもの）。

## 測った値（メインが機械で測った・2026-10-29・commit c3f3f5b5）
- ビルド（PoPETs 2027 テンプレート・pdfLaTeX）: エラー 0・未定義の参照 0・未定義の引用 0・overfull 2。全 28 頁。本文（§1〜§9）は 1 頁目から 12 頁目の右段の終わりまで（12 頁ちょうど・余白はほぼ無い）。上限は本文 12 頁。
- 本文の語数: 11,086 語（texcount を本文の 9 節に当てた和。表の中とキャプションを含む。抄録・必須の節・付録・参考文献は除く）。PDF の 1 頁目から "Ethical Considerations" の前までの英字 2 文字以上の語は 11,053。前の round の版（commit 92c0cadb・結果の前）の本文は同じ数え方で 11,046 語（+40）。
- 抄録: 約 240 語。必須の 3 節: 2,138 語。付録 A〜E: 3,873 語。
- 本文の表 4 つ（表 1 threat-model の設定・表 2 data の公開の形・表 3 attackers・表 4 results の主表〔(a) N = 1,000・(b) N = 10〕）、図 1（results）。付録の表 17。参考文献 32 件。

## 投稿規程と投稿先の範囲（Aims & Scope）の一次の抜粋

⚠️ この round では取り直せなかった。2026-10-29 に petsymposium.org の名前を curl・WebFetch・Chrome のどれでも引けず、研究者のブラウザでも開けなかった。下は round 1（2026-10-21）に curl で原文を取り、逐語を照合したもの。照合済み（2026-10-21）として扱う。CfP の 2 文（"The core contribution must be relevant …" と "Papers that treat privacy as a superficial application domain …"）が投稿先の範囲の一次の文である。
- authors-2027.php（https://petsymposium.org/authors-2027.php）・照合済み:
  - "The paper should start with the title and an abstract. The first page must clearly state how the work is relevant to real-world privacy applications. The introduction should give some background and summarize the contributions of the paper at a level appropriate for a non-specialist reader."
  - "Submissions and resubmissions to PoPETs must consist of at most 12 typeset pages for the main body of the paper. The main body excludes the three mandatory sections per the 2027 template (ethical considerations, open science, and AI use) as well as any acknowledgements, the bibliography, and any clearly-marked appendices contained in the submission."
  - "However, appendices should only be used to provide supplementary information that falls outside of the stated contribution of the paper or to provide extended details that would not be of interest to most readers. The paper should be complete and self-contained without appendices. PC members are not required to read the appendices during review."
  - "This section should include a justification of the ethics of the work and information about whether the work was submitted to an external ethics panel such as an IRB or the Tor Research Safety Board. Research that is deemed to not have met adequate ethical standards may be rejected on those grounds."
  - "Mandatory disclosure of AI use; see new mandatory section in the PoPETs 2027 LaTeX template (does not count towards page limit). Hallucinations, fabrication, omissions, plagiarism, and falsification are treated as research misconduct."
  - "Instead, reference your past work in the third person, just as you would any other piece of related work by another author."
- cfp27.php（https://petsymposium.org/cfp27.php）・照合済み:
  - "The core contribution must be relevant to real-world privacy applications. The first page must clearly state how the work is relevant to real-world privacy applications."
  - "Papers that treat privacy as a superficial application domain (e.g., if the only relationship to privacy is a privacy-related dataset) do not demonstrate relevance to real-world privacy problems and are therefore out of scope."
  - "Issue 3 Paper submission deadline: November 30, 2026 (firm)"
- 2027 の LaTeX テンプレート（submission-template-2027.zip・2026-10-20 取得・SHA-256 b1abbcc0…）・照合済み（2026-10-20）:
  - 必須の 3 節は "MUST have exactly this title and placement (between acknowledgements and references) or risk desk rejection."
  - "If it is important to reference such material, consider setting up a cloned version with identifying information removed, perhaps using anonymization tools such as \url{https://anonymous.4open.science}."
