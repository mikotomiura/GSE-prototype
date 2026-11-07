# context A（manuscript round 3・論文 2・査読者・編集者・監査役に渡す）

- 対象物: 論文 2 の原稿の改訂稿（英語・JEDM の LaTeX のテンプレート）。commit 52df151b（枝 docs/gse-paper2-stall-shape）。ビルドした PDF も置いた（図を見るため・同じ commit から作った）。
- stage: manuscript（round 3）。投稿先: Journal of Educational Data Mining（JEDM）。
- round 1 の後に、条件を計算の前に著者の repo にコミットしてから、4 つの計算を足した（第 2 の検出器〔休止の系統〕・θ を書き手の再標本の中で推定し直した区間・観測と作文の長さでの調整・100 個目の間隔より後にそろえた感度）。round 2 の後に、同じ作法で 1 つ足した（θ を各時刻より前の間隔だけから重み付きで引き直す二段の区間。先に置いた読み方により、一段の区間を主に戻した）。条件の文書は日本語。
- 同じ著者の別の論文（原稿の中で companion study と呼ぶもの）が JEDM で査読中。基準の定義・変換・推定器・開けた取り置きを共有する。
- 公開の archive（コード・条件・集計）の DOI は投稿の前に足す（原稿の中では「DOI to be added before submission」）。

## 測った値（機械で測った）

- 本文の語数: 6,272 語（`texcount -inc -sum -merge` で序論〜結論。見出しとキャプションを含み、表と図の中身・数式・抄録・宣言・参考文献・補足を除く）。前の round（commit 4d814bc7）は 5,805 語で、467 語増えた。
- 節ごと: 序論 551・関連研究 572・データと方法 1,814・結果 1,898・考察 753・限界 528・結論 156。
- 抄録: 287 語（texcount）。図 5・表 4（本文）。参考文献 43 件。PDF 28 頁（12pt・テンプレートの既定。1〜18 頁が本文・必須の節・参考文献、18 頁の途中から補足）。

## 読んでよいファイルの一覧（これだけ・印は 本文 / 必須の節 / 補足）

本文:
/Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/main.tex
/Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/sections/abstract.tex
/Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/sections/introduction.tex
/Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/sections/related.tex
/Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/sections/methods.tex
/Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/sections/results.tex
/Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/sections/discussion.tex
/Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/sections/limitations.tex
/Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/sections/conclusion.tex
/Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/references.bib
/Users/johnd/GSE-prototype-paper2/.steering/20261107-paper2-manuscript/attack-me/manuscript-paper2/round-3/tmp/main.pdf（ビルドした PDF。1〜18 頁が本文・必須の節・参考文献、18 頁の途中から補足）

必須の節:
/Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/sections/availability.tex
/Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/sections/declarations.tex

補足（参考文献の後の付録と、公開する archive に入る材料。編集者の役は読まない）:
/Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/appendix/supplement.tex
/Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/appendix/tab_s3.tex
/Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/appendix/tab_s4.tex
/Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/appendix/tab_pause.tex
/Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/figdata/score.csv
/Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/figdata/ratio_cs19_kl.csv
/Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/figdata/ratio_cs19_cs21.csv
/Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/figdata/phi.csv
/Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/figdata/lengths.csv
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/conditions.md
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/conditions-length90.md
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/conditions-round1.md
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/conditions-round2.md
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/conditions-round3.md
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/conditions-round4.md
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/conditions-round5.md
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/conditions-round7.md
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/conditions-round8.md
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/c3_multiverse.json
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/round1_extra.json
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/round3_speed.json
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/round4_speedvar.json
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/round5_pause.json
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/round5_theta.json
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/round5_length.json
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/round7_warm.json
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/round8_causal.json
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/c1_lengths90.json
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/c2_overdispersion.json
/Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/results/prep_summary.json

（印の根拠: JEDM のテンプレートの説明は補足の技術的な材料を参考文献の後の付録に置くと書く（下の抜粋）。条件と結果の集計は archive に入る材料で、本文の数の出どころ。書き手ごとの値は含まない。一覧の外は読まない。）

## 投稿規程と Aims & Scope の一次の抜粋（2026-11-08 の round 3 の前に curl で取り直し、逐語で在ることを照合した）

- https://jedm.educationaldatamining.org/index.php/JEDM/about（Focus and Scope・全文は tmp/sources/jedm_aims.txt）
  - "Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses."
  - "Replicability: All submissions should present their methodologies and findings in a way that ensures replicability by other researchers. This includes clear descriptions of the data, tools, and procedures used."
  - "It is the policy of the journal that no submission, or substantially overlapping submission, be published or be under review elsewhere."
  - 研究での生成 AI の使用は Methodology の節に書く（jedm_aims.txt に "Methodology" の語で在る）。
- https://jedm.educationaldatamining.org/index.php/JEDM/about/submissions（全文は tmp/sources/jedm_submissions.txt）
  - "You may submit an anonymized version of your manuscript. If you choose this possibility, the review process will be double-blind."
  - 生成 AI の申告は参考文献の前の節 "Declaration of Generative AI Software tools in the writing process"。
  - "Authors are encouraged to share the code behind their submissions"
- テンプレートの説明（2024_08_02_jedm-latex.zip の instructions.pdf・2026-11-05 に照合済み・この round では取り直していない＝未照合）
  - 要旨: "It should contain from 100 to 300 words."
  - "Supplementary technical material (e.g., mathematical proofs or descriptions of experimental procedures) should be collected in an appendix at the end of the paper (after the references)."
- 本文の分量の上限: 規定なし（取得した範囲の原文に該当の文が無い）。
