# context A（査読者と監査役の両方に渡す・stage: manuscript・round 1）

対象物は commit 727647a2（branch docs/public-keystroke-matching-manuscript）の原稿。

## 対象物
PoPETs 2027 Issue 3（締切 2026-11-30）に投稿する予定の論文の原稿の全体（結果の前の版）。
本計算の結果はまだ出ていない。そのため次のものはまだ無く、角括弧 `[...]` の空欄や計画の文として残っている:
抄録・§1 序論の方法・害・貢献の段落・§7 結果・§8.3 持ち帰り・§9 結論・§4 の除外の後の件数・倫理の節の公開元への連絡の日付・Open science の匿名リンク。
⚠️ これらが無いこと・空欄があることは、それ自体を欠陥にしない（結果を見る前に書ける部分の査読である）。
脅威モデル・攻撃者・手順は、データを取得する前に固定された事前登録（OSF に登録済み）にあり、原稿はそれを変えずに述べる。

## 読んでよいファイルの一覧
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/main.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/introduction.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/related.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/threat-model.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/data.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/attackers.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/protocol.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/results.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/discussion.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/conclusion.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/ethics.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/open-science.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/ai-use.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/references.bib
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/outline.md （原稿の外枠・主張と根拠の対応表・頁の見積もり）
- /Users/johnd/GSE-wt-matching-manuscript/experiments/20261012-public-keystroke-matching/preregistration.en.md （事前登録の正の版。読者は OSF で読める）

節の順は main.tex の \input の順（§1〜§9、付録の後に必須の 3 節）。

## 測った値（メインが機械で測った・2026-10-21）
- ビルド（PoPETs 2027 テンプレート・pdfLaTeX）: 全 13 頁。本文（§1〜§9）は 1 頁目から 11 頁目の左段まで（約 10.5 頁）。上限は本文 12 頁。
- 本文の語数: 約 10,600 語（PDF のテキストから行番号を除いて数えた・表を含む）。抄録は未記入（0 語）。
- 表 4 つ（Table 1 settings・Table 2 forms・Table 3 attackers・Table 4 utility）、図 0。参考文献 28 件。
- 著者の見積もり（outline.md の Page budget）: 結果（表 2・図 1・ENJA15 の小節）などを足すと約 14 頁になり、約 2 頁を付録へ移す予定。

## 投稿規程の一次の抜粋（2026-10-21 に curl で取り直し、逐語を照合済み）
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
