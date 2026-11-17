# context A（査読者・編集者・監査役に渡す・stage: manuscript・round 4・原稿の全体）

対象物は commit bf0d2450（branch docs/public-keystroke-matching-manuscript）の原稿。PoPETs 2027 Issue 3（締切 2026-11-30）に投稿する予定の論文の全体。

## 対象物の状態
- 結果（§7）・序論・考察・結論・抄録は、事前登録の本計算の集計から書いた。表の値は集計の JSON から機械で生成し、`sections/generated/` から読み込む。
- 前の round の後に入ったもの: 本文の直し（付録への移動・C2 の書き直し・1 頁目のプライバシー）、付録 E の全員（4,992 人）の結果、倫理の節の確定、本計算の結果を見た後に決めた探索的な分析 6・7（攻撃者を強める: 罰 λ の格子と窓の走査・付録 D）の結果と、その抄録・序論・§7・§8・結論への 1 文ずつ。
- 残っている空欄（角括弧 `[...]`）は 1 つで、欠陥にしない: Open science の匿名リンク（open-science.tex）。
- 脅威モデル・攻撃者・手順は、データを取得する前に固定した事前登録（OSF）にあり、原稿はそれを変えずに述べる。逸脱は付録に一覧がある。
- 二重盲検の投稿なので、著者・所属・登録のリンクは伏せてある。

## 読んでよいファイルの一覧（印: 本文 / 必須の節 / 補足）
印の根拠: authors-2027.php の "The main body excludes the three mandatory sections … as well as any acknowledgements, the bibliography, and any clearly-marked appendices" と "PC members are not required to read the appendices during review"。main.tex で `\appendix` の後に必須の 3 節、参考文献、付録 A〜E の順に置く（テンプレートの指定）。
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/main.tex 〔本文〕題・節の並び（抄録と節の \input を含む）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/abstract.tex 〔本文〕抄録（PoPETs の規程で抄録は本文の頁に入る・2026-11-12 に main.tex から切り出した）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/introduction.tex 〔本文〕
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/related.tex 〔本文〕
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/threat-model.tex 〔本文〕
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/data.tex 〔本文〕
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/attackers.tex 〔本文〕
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/protocol.tex 〔本文〕
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/results.tex 〔本文〕
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/discussion.tex 〔本文〕
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/conclusion.tex 〔本文〕
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/main-1000.tex 〔本文〕results.tex の表 4（主表）の中身（	abinput で読み込む・集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/main-10.tex 〔本文〕同上
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
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/all-writers.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/cells-1.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/cells-2.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/enja.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/explore-band.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/explore-dp-r0.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/explore-dp-score.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/explore-dp.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/explore-lambda-scan-10.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/explore-lambda-scan-1000.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/explore-margin.tex 〔補足〕付録の表の中身（集計から生成）
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/generated/explore-strongest.tex 〔補足〕付録の表の中身（集計から生成）
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

節の順は main.tex の \input の順（抄録 → §1〜§9 → 必須の 3 節 → 参考文献 → 付録 A〜E）。`generated/figure-coords.tex` はコメントだけなので一覧に入れない（図 1 の座標は results.tex の中にある）。`generated/main-a4-*.tex` はどこからも読み込まれていないので入れない。

## 測った値（メインが機械で測った・2026-11-17・commit bf0d2450）
- ビルド（PoPETs 2027 テンプレート・pdfLaTeX）: エラー 0・未定義の参照 0・未定義の引用 0・overfull 2。全 31 頁。本文（§1〜§9）は 1 頁目から 12 頁目の右段まで（Ethical Considerations の見出しは 12 頁目の右段・本文の余白は約 0.3 頁）。上限は本文 12 頁。
- 本文の語数: 11,009 語（texcount を本文の 9 節に当てた和。表の中とキャプションを含む。抄録・必須の節・付録・参考文献は除く）。前の round の版（commit c3f3f5b5）は同じ数え方で 11,086 語（−77）。
- 抄録: 348 語（texcount・abstract.tex）。前の round の版は 242 語。規程に抄録の語数の上限は無い（取得した authors-2027.php と cfp27.php の原文に該当の文が無い）。
- 必須の 3 節: 2,113 語。付録 A〜E: 5,367 語。
- 本文の表 4 つ（表 1 threat-model の設定・表 2 data の公開の形・表 3 attackers・表 4 results の主表〔(a) N = 1,000・(b) N = 10〕）、図 1（results）。付録の表 21（表 5〜25）。参考文献 34 件。

## 投稿規程と投稿先の範囲（Aims & Scope）の一次の抜粋

2026-11-17 に curl で原文を取り直し、タグを除いて空白を正規化した本文に下の逐語が在ることを機械で確かめた（照合済み・2026-11-17）。CfP の 2 文（"The core contribution must be relevant …" と "Papers that treat privacy as a superficial application domain …"）が投稿先の範囲の一次の文である。
- authors-2027.php（https://petsymposium.org/authors-2027.php）・照合済み:
  - "The paper should start with the title and an abstract. The first page must clearly state how the work is relevant to real-world privacy applications. The introduction should give some background and summarize the contributions of the paper at a level appropriate for a non-specialist reader."
  - "Submissions and resubmissions to PoPETs must consist of at most 12 typeset pages for the main body of the paper. The main body excludes the three mandatory sections per the 2027 template (ethical considerations, open science, and AI use) as well as any acknowledgements, the bibliography, and any clearly-marked appendices contained in the submission."
  - "The paper should be complete and self-contained without appendices. PC members are not required to read the appendices during review."
  - "Research that is deemed to not have met adequate ethical standards may be rejected on those grounds."
  - "Hallucinations, fabrication, omissions, plagiarism, and falsification are treated as research misconduct."
  - "Instead, reference your past work in the third person, just as you would any other piece of related work by another author."
  - "If it is important to reference such material, consider setting up a cloned version with identifying information removed, perhaps using anonymization tools"
- cfp27.php（https://petsymposium.org/cfp27.php）・照合済み:
  - "The core contribution must be relevant to real-world privacy applications."
  - "Papers that treat privacy as a superficial application domain (e.g., if the only relationship to privacy is a privacy-related dataset) do not demonstrate relevance to real-world privacy problems and are therefore out of scope."
  - "Issue 3 Paper submission deadline: November 30, 2026 (firm)"
- 2027 の LaTeX テンプレート（submission-template-2027.zip・2026-11-17 に取り直し・SHA-256 b1abbcc0…〔2026-10-20 の取得と同じ〕）:
  - 必須の 3 節は "MUST have exactly this title and placement (between acknowledgements and references) or risk desk rejection."
