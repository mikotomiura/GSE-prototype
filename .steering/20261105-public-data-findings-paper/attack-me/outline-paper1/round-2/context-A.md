# context A（outline round 2・査読者・編集者・監査役に渡す）

- 対象物: 論文 1 の原稿の外枠（round 1 の指摘を直し、関連研究の文献と休止の位置の探索を入れた版）。commit 30a785e3（枝 docs/public-data-findings-paper）。外枠は日本語で、原稿の本文（英語・LaTeX）はまだ無い。
- stage: outline。投稿先: Journal of Educational Data Mining（JEDM）。
- 事前登録は OSF で凍結済み（英語版が正）。確認（取り置き）は完走し、結果も OSF に登録した。
- 分量（機械で測った値）: 外枠の節ごとの語数の予算の合計 6,650 語（序論 900・関連研究 800・データ 850・評価の設計 1,200・結果 1,550・考察 900・限界 350・結論 100）。目標 7,000 語・上限 8,500 語。本文（散文）はまだ無い（本文なし）。外枠のファイルは 101 行（round 1 の版は 94 行・予算の合計 6,800 語）。
- 外枠の [Vn]・[Pn] は中央書誌の番号。番号ごとの書誌と要点は、一覧の 2 つの文献の記録（novelty と related-work）にある。

## 読んでよいファイルの一覧（これだけ・印は 本文 / 補足）

本文（外枠そのもの。原稿の本文になる部分の設計）:
/Users/johnd/GSE-prototype-public-findings/.steering/20261105-public-data-findings-paper/paper-write/outline.md

補足（外枠が根拠として名指す材料。読者に読む義務は無い。編集者の役は読まない）:
/Users/johnd/GSE-prototype-public-findings/.steering/20261105-public-data-findings-paper/paper-write/prereg-draft.en.md
/Users/johnd/GSE-prototype-public-findings/.steering/20261105-public-data-findings-paper/paper-write/prereg-draft.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/notes.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/results_holdout/confirm_holdout.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261106-findings-paper1-exploration/conditions.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261106-findings-paper1-exploration/notes.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261106-findings-paper1-exploration/results/explore_coauthor.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261106-findings-paper1-exploration/results/explore_cs1_2021.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261106-findings-paper1-exploration/results/explore_klicke.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261106-findings-paper1-exploration/results/explore_position.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261106-findings-paper1-exploration/results/seed_spread.json
/Users/johnd/GSE-prototype-public-findings/docs/literature/20261105-public-data-findings-novelty.md
/Users/johnd/GSE-prototype-public-findings/docs/literature/20261106-public-data-findings-related-work.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261101-klicke-early-stall-trigger/notes.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261101-coauthor-pre-stall-signal/notes.md

（印の根拠: テンプレートの説明は補足の技術的な材料を参考文献の後の付録へ置くと書く。事前登録（英語版が正・日本語版は対訳）・結果・探索の記録・文献の記録は、外枠の数値と主張の出どころ。書き手ごとの値は含まない。一覧の外は読まない。）

## 投稿規程と Aims & Scope の一次の抜粋

- https://jedm.educationaldatamining.org/index.php/JEDM/about/submissions（2026-11-06 にこの round で curl で取り直した原文で照合済み）
  - "You may submit an anonymized version of your manuscript. If you choose this possibility, the review process will be double-blind."
  - 生成 AI の申告は参考文献の前の節 "Declaration of Generative AI Software tools in the writing process" に定型の文で書く。
  - "Authors are encouraged to share the code behind their submissions."
- https://jedm.educationaldatamining.org/index.php/JEDM/about（Focus and Scope・2026-11-06 にこの round で curl で取り直し、逐語で在ることを照合した）
  - "Replicability: All submissions should present their methodologies and findings in a way that ensures replicability by other researchers. This includes clear descriptions of the data, tools, and procedures used."
  - "Data and Code Availability: Authors are strongly encouraged to make their data sets, software code, and intermediate results available to the community."
  - "Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses."
  - Aims & Scope の全文は編集者の接地の本文 jedm_aims.txt にある。
- テンプレートの説明（2024_08_02_jedm-latex.zip の instructions.pdf・前の事前登録の round 1 に照合済み。この round では取り直していない＝この round では未照合）
  - 要旨: "It should contain from 100 to 300 words."
  - "Supplementary technical material (e.g., mathematical proofs or descriptions of experimental procedures) should be collected in an appendix at the end of the paper (after the references)."
- 本文の分量の上限: 規定なし（取得した範囲の原文に該当の文が無い）。
