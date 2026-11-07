# context A（outline round 5・論文 2・査読者・編集者・監査役に渡す）

- 対象物: 論文 2（停滞の形）の原稿の外枠 v7。commit 1d79f1c9（枝 docs/gse-paper2-stall-shape）。外枠は日本語で、原稿の本文（英語・LaTeX）はまだ無い。
- stage: outline。投稿先: Journal of Educational Data Mining（JEDM）。
- 計算はすべて終わっている。条件は計算の前に repo にコミットした（主の条件 08010482・長さの追加 6df7bde6・区間と得点の追加 b5687936・押下の率の追加 9a1b321c・打鍵の速さの追加 777da413・速さの測り方の追加 980a8393）。OSF などの第三者の登録は無い。
- 分量（機械で測った値）: 外枠の節ごとの語数の予算の合計 6,000 語（序論 800・関連研究 700・データと方法 1,000・結果 4 節 2,250・考察 700・限界 400・結論 150）。目標 6,500 語・上限 8,000 語。本文（散文）はまだ無い（本文なし）。外枠のファイルは 131 行（前回 v6 は 130 行）。
- 外枠の [Vn] は中央書誌の番号で、書誌の本体はこの一覧に無い（新しく引く [V472]〜[V488] は文献カード 2 枚に書誌がある）。
- 同じ著者の論文 1（停滞の手前の信号の事前登録した同等の確認）が JEDM で査読中。論文 2 の基準の定義は論文 1 の付録と同じ。

## 読んでよいファイルの一覧（これだけ・印は 本文 / 補足）

本文（外枠そのもの。原稿の本文になる部分の設計）:
/Users/johnd/GSE-prototype-paper2/.steering/20261107-paper2-outline/paper-write/outline.md

補足（外枠が根拠として名指す材料。読者に読む義務は無い。編集者の役は読まない）:
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/conditions.md
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/conditions-length90.md
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/conditions-round1.md
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/conditions-round2.md
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/conditions-round3.md
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/conditions-round4.md
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/notes.md
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/judgement.json
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/c2_overdispersion.json
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/c3b_aligned_level.json
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/c1_lengths90.json
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/round1_extra.json
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/round2_press.json
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/round3_speed.json
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/round4_speedvar.json
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/c1_decomposition.json
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/c3_multiverse.json
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/prep_summary.json
/Users/johnd/GSE-prototype-paper2/docs/literature/20261107-stall-shape-paper2-novelty.md
/Users/johnd/GSE-prototype-paper2/docs/literature/20261107-stall-shape-paper2-outline-priors.md
/Users/johnd/GSE-prototype-paper2/docs/literature/20261107-stall-shape-paper2-round1-priors.md

（印の根拠: JEDM のテンプレートの説明は補足の技術的な材料を参考文献の後の付録へ置くと書く。条件・結果の集計・新しさの文献の記録は、外枠の数値と主張の出どころ。書き手ごとの値は含まない。一覧の外は読まない。）

## 投稿規程と Aims & Scope の一次の抜粋（2026-11-07 に round 1 で curl で取り直し、round 2 も同日のため取り直していない、逐語で在ることを照合した）

- https://jedm.educationaldatamining.org/index.php/JEDM/about（Focus and Scope）
  - "Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses."
  - "Replicability: All submissions should present their methodologies and findings in a way that ensures replicability by other researchers. This includes clear descriptions of the data, tools, and procedures used."
  - "Data and Code Availability: Authors are strongly encouraged to make their data sets, software code, and intermediate results available to the community."
  - "It is the policy of the journal that no submission, or substantially overlapping submission, be published or be under review elsewhere."
  - 全文は編集者の接地の本文 jedm_aims.txt にある。
- https://jedm.educationaldatamining.org/index.php/JEDM/about/submissions
  - "You may submit an anonymized version of your manuscript. If you choose this possibility, the review process will be double-blind."
  - 生成 AI の申告は参考文献の前の節 "Declaration of Generative AI Software tools in the writing process"。
  - "Authors are encouraged to share the code behind their submissions."
- テンプレートの説明（2024_08_02_jedm-latex.zip の instructions.pdf・2026-11-05 に論文 1 の作業で照合済み・この round では取り直していない＝未照合）
  - 要旨: "It should contain from 100 to 300 words."
  - "Supplementary technical material (e.g., mathematical proofs or descriptions of experimental procedures) should be collected in an appendix at the end of the paper (after the references)."
- 本文の分量の上限: 規定なし（取得した範囲の原文に該当の文が無い）。
