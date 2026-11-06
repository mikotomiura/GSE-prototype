# context A（manuscript round 3・査読者・編集者・監査役に渡す）

- 対象物: 論文 1 の原稿の草稿 v3（英語・LaTeX）。commit 7fc19bc6（枝 docs/public-data-findings-paper）。草稿 v2 への査読（manuscript round 2）を受けて直した版。草稿 v3 の後に、推定器と replay の道具を公開し、公開物（GitHub と Zenodo）の DOI を要旨と Materials に入れた。
- stage: manuscript。投稿先: Journal of Educational Data Mining（JEDM）。
- 事前登録は OSF で凍結済み（英語版が正）。確認（取り置き）は完走し、結果も OSF に登録した。確認の後に、登録の外の探索を、条件を先にコミットしてから回した。
- 原稿は節ごとのファイルに分かれている（main.tex が \input で並べる）。補足（S1〜S10）は参考文献の後の付録（appendix/supplement.tex）。組版した PDF は 28 頁（補足を含む）。図は pgfplots で本文の中に座標を書いている。
- 引用は BibTeX の鍵（\cite{...}）で、書誌は references.bib にある。
- 公開物: https://github.com/mikotomiura/stall-runup-equivalence（v0.1.0）・Zenodo 10.5281/zenodo.24014042。その手元の写しの README と推定器の README を下の一覧に入れた（公開物の中身はこの 2 つから読める範囲だけを読む）。

## 測った値（機械で測った）

- 本文（序論の最初から結論の最後まで・見出しとキャプションを含む）: 7,424 語（round 2 の版 2a0e46f0 は 7,033 語・+391）。コマンド: `texcount -inc -sum -merge sections/introduction.tex sections/related.tex sections/data.tex sections/design.tex sections/results.tex sections/discussion.tex sections/limitations.tex sections/conclusion.tex`（表の中身も数えている）。節ごと: 序論 1,133・関連研究 770・データ 1,182・評価の設計 1,249・結果 1,433・考察 947・限界 587・結論 123。著者が決めた予算は目標 7,000 語・上限 8,500 語。
- 要旨: 300 語（`texcount -1 -sum sections/abstract.tex`。キーワードと URL の語を含む）。
- 本文の表 4・図 1（主の結果と感度・探索の AUC）。補足の表 2。参考文献 66 件。

## 読んでよいファイルの一覧（これだけ・印は 本文 / 必須の節 / 補足）

本文:
/Users/johnd/GSE-prototype-public-findings/papers/public-data-findings/manuscript/main.tex
/Users/johnd/GSE-prototype-public-findings/papers/public-data-findings/manuscript/sections/abstract.tex
/Users/johnd/GSE-prototype-public-findings/papers/public-data-findings/manuscript/sections/introduction.tex
/Users/johnd/GSE-prototype-public-findings/papers/public-data-findings/manuscript/sections/related.tex
/Users/johnd/GSE-prototype-public-findings/papers/public-data-findings/manuscript/sections/data.tex
/Users/johnd/GSE-prototype-public-findings/papers/public-data-findings/manuscript/sections/design.tex
/Users/johnd/GSE-prototype-public-findings/papers/public-data-findings/manuscript/sections/results.tex
/Users/johnd/GSE-prototype-public-findings/papers/public-data-findings/manuscript/sections/discussion.tex
/Users/johnd/GSE-prototype-public-findings/papers/public-data-findings/manuscript/sections/limitations.tex
/Users/johnd/GSE-prototype-public-findings/papers/public-data-findings/manuscript/sections/conclusion.tex

必須の節:
/Users/johnd/GSE-prototype-public-findings/papers/public-data-findings/manuscript/sections/declarations.tex

補足（参考文献の後の付録と、原稿が根拠として名指す材料。読者に読む義務は無い。編集者の役は読まない）:
/Users/johnd/GSE-prototype-public-findings/papers/public-data-findings/manuscript/appendix/supplement.tex
/Users/johnd/GSE-prototype-public-findings/papers/public-data-findings/manuscript/references.bib
/Users/johnd/GSE-prototype-public-findings/papers/public-data-findings/README.md
/Users/johnd/stall-runup-equivalence/README.md
/Users/johnd/stall-runup-equivalence/estimator/README.md
/Users/johnd/GSE-prototype-public-findings/.steering/20261105-public-data-findings-paper/paper-write/prereg-draft.en.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/deviation-1.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/notes.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/results_holdout/confirm_holdout.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261106-findings-paper1-exploration/conditions.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261106-findings-paper1-exploration/notes.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261106-findings-paper1-exploration/results/explore_predraft.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261106-findings-paper1-exploration/results/explore_position.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261106-findings-paper1-exploration/results/explore_cs1_2021.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261106-findings-paper1-exploration/results/explore_klicke.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261106-findings-paper1-exploration/results/explore_coauthor.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261106-findings-paper1-exploration/results/seed_spread.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261106-findings-paper1-exploration/results/explore_positive_control.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261106-findings-paper1-exploration/results/explore_positive_control_v2.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261106-findings-paper1-exploration/results/explore_comparison.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261106-findings-paper1-exploration/results/explore_ctrl_lo.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261106-findings-paper1-exploration/results/explore_learner_features.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261106-findings-paper1-exploration/results/explore_length_calibration.json
/Users/johnd/GSE-prototype-public-findings/docs/literature/20261105-public-data-findings-novelty.md
/Users/johnd/GSE-prototype-public-findings/docs/literature/20261106-public-data-findings-related-work.md

（印の根拠: JEDM のテンプレートの説明 "Supplementary technical material (e.g., mathematical proofs or descriptions of experimental procedures) should be collected in an appendix at the end of the paper (after the references)." に従い、補足は参考文献の後の付録。生成 AI の申告は規程が参考文献の前の節として求める。事前登録（英語版が正）・逸脱・結果・探索の記録・文献の記録・公開物の README は、原稿の数値と主張の出どころ。書き手ごとの値は含まない。一覧の外は読まない。）

## 投稿規程と Aims & Scope の一次の抜粋

- https://jedm.educationaldatamining.org/index.php/JEDM/about/submissions（2026-11-07 に curl で取り直し、下の文が原文に逐語で在ることを照合済み）
  - "You may submit an anonymized version of your manuscript. If you choose this possibility, the review process will be double-blind."
  - 生成 AI の申告: "the use of generative AI software tools such as ChatGPT in writing your submission is documented at the end of your manuscript before the References in a special section called 'Declaration of Generative AI Software tools in the writing process' with the following statement: During the preparation of this work, the author(s) used [NAME TOOL(S) / SERVICE(S)] in the section(s) [mention precisely all sections or subsections where you used the tool(s) or services(s)] in order to [REASON(S)]. After using this tool/service, the author(s) reviewed and edited the content as needed and take(s) full responsibility for the content of the publication."
  - "Authors are encouraged to share the code behind their submissions."
- https://jedm.educationaldatamining.org/index.php/JEDM/about（Focus and Scope・2026-11-07 に curl で取り直し、照合済み）
  - "Replicability: All submissions should present their methodologies and findings in a way that ensures replicability by other researchers."
  - "Data and Code Availability: Authors are strongly encouraged to make their data sets, software code, and intermediate results available to the community."
  - "Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses."
  - Aims & Scope の全文は編集者の接地の本文 jedm_about.txt にある。
- テンプレートの説明（2024_08_02_jedm-latex の instructions.tex・2026-11-06 に取得した zip〔SHA-256 2ee69df4…a7ab043〕で照合済み。この round では zip を取り直していない）
  - 要旨: "It should contain from 100 to 300 words."
  - "Supplementary technical material (e.g., mathematical proofs or descriptions of experimental procedures) should be collected in an appendix at the end of the paper (after the references)."
  - "Authors should add a sentence at the end of the abstract giving the link(s) to supporting materials."
- 本文の分量の上限: 規定なし（取得した範囲の原文に該当の文が無い）。
