# context A（査読者と監査役の両方に渡す）

## 対象物
PoPETs 2027 に投稿する予定の論文の原稿の外枠と、最初に書いた節（Section 3 Threat model）。原稿の他の節はまだ書かれていない（"To be written."）。
結果（本計算）はまだ出ていない。脅威モデル・攻撃者・手順は、データを取得する前に固定された事前登録（OSF に登録済み）にあり、
原稿はそれを変えずに述べる。この段階で見てほしいのは、Section 3 の動機（現実に誰が、どの公開物と、どの候補の本文で照合できるか）の
書き方・根拠の強さ・抜けている限界と、原稿の外枠（outline.md の構成と主張 ↔ 根拠の対応表）。

## 読んでよいファイルの一覧
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/threat-model.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/outline.md
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/main.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/references.bib
- /Users/johnd/GSE-wt-matching-manuscript/experiments/20261012-public-keystroke-matching/preregistration.en.md （事前登録の正の版。読者は OSF で読める）

## 測った値（メインが機械で測った・2026-10-20）
- Section 3 の語数: 約 1,094 語（LaTeX の命令を除いて数えた）。引用 13 箇所。references.bib の文献 9 件。
- 現在のビルドは 2 頁（他の節は空）。本文の上限は 12 頁。

## 投稿規程の一次の抜粋（2026-10-20 に curl で取得し、逐語を照合済み）
- authors-2027.php（https://petsymposium.org/authors-2027.php）・照合済み:
  - "The first page must clearly state how the work is relevant to real-world privacy applications. The introduction should give some background and summarize the contributions of the paper at a level appropriate for a non-specialist reader."
  - "Submissions and resubmissions to PoPETs must consist of at most 12 typeset pages for the main body of the paper. The main body excludes the three mandatory sections per the 2027 template (ethical considerations, open science, and AI use) as well as any acknowledgements, the bibliography, and any clearly-marked appendices"
  - "This section should include a justification of the ethics of the work and information about whether the work was submitted to an external ethics panel such as an IRB or the Tor Research Safety Board. Research that is deemed to not have met adequate ethical standards may be rejected on those grounds."
  - "The paper should be complete and self-contained without appendices. PC members are not required to read the appendices during review."
  - "Instead, reference your past work in the third person, just as you would any other piece of related work by another author."
- cfp27.php（https://petsymposium.org/cfp27.php）・照合済み:
  - "The core contribution must be relevant to real-world privacy applications. The first page must clearly state how the work is relevant to real-world privacy applications."
  - "Papers that treat privacy as a superficial application domain (e.g., if the only relationship to privacy is a privacy-related dataset) do not demonstrate relevance to real-world privacy problems and are therefore out of scope."
- 2027 の LaTeX テンプレート（submission-template-2027.zip の main.tex・2026-10-20 取得）・照合済み:
  - "If it is important to reference such material, consider setting up a cloned version with identifying information removed, perhaps using anonymization tools such as \url{https://anonymous.4open.science}."
  - 必須の 3 節は "MUST have exactly this title and placement (between acknowledgements and references) or risk desk rejection."
