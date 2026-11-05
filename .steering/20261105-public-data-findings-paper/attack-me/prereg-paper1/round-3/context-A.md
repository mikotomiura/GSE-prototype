# context A（round 3・査読者と監査役の両方に渡す）

- 対象物: 論文 1 の事前登録の草案 v4（OSF で凍結する前）。commit dad32265（枝 docs/public-data-findings-paper）。round 1 は v1（87b2f159）、round 2 は v3（49f8b96a）を見た。
- stage: prereg。投稿先: Journal of Educational Data Mining（JEDM）。論文の原稿はまだ無い。
- 分量（機械で測った値）: 草案は 163 行・13,064 字（日本語）。節 P0〜P10・凍結の前の計算（済み）・付録 A。
- v4 で新しく入ったもの: 確認の解析スクリプト（凍結の前に見た書き手で空回しした・判定の値は出していない）と、取り置きで 1 回だけ回す手順。草案は、規則の実装がこのスクリプトであると書く。

## 読んでよいファイルの一覧（これだけ）

/Users/johnd/GSE-prototype-public-findings/.steering/20261105-public-data-findings-paper/paper-write/prereg-draft.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/conditions.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/notes.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/results/precision.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/results/width_conversion.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/results/counts.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/conditions-2.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/results/confirm_seen.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/scripts/confirm_p1.py
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/scripts/prefreeze.py
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/run-confirm-holdout.sh
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/run-confirm-seen.sh
/Users/johnd/GSE-prototype-public-findings/experiments/20261031-coauthor-pre-request-signal/conditions.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261031-coauthor-pre-request-signal/conditions_round2.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261031-coauthor-pre-request-signal/notes.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261101-coauthor-pre-stall-signal/conditions.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261101-coauthor-pre-stall-signal/notes.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261101-klicke-early-stall-trigger/conditions.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261101-klicke-early-stall-trigger/notes.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261104-cs1-landscape/conditions.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261104-cs1-landscape/notes.md
/Users/johnd/GSE-prototype-public-findings/src-tauri/prereg/p1-episode.json
/Users/johnd/GSE-prototype-public-findings/docs/preregistration-p1-episode.md

（草案が土台として名指す前の実験の条件と集計の結果、凍結の前の計算、停滞の定義の値。書き手ごとの値は含まない。草案の中の ADR の番号・[Vn] の文献番号の本体は一覧に無い。一覧の外は読まない。）

## 投稿規程の一次の抜粋（round 1 と同じ・2026-11-05 にメインが curl で取った原文で照合済み）

- https://jedm.educationaldatamining.org/index.php/JEDM/about/submissions
  - "You may submit an anonymized version of your manuscript. If you choose this possibility, the review process will be double-blind."（照合済み）
  - 生成 AI の申告は参考文献の前の節 "Declaration of Generative AI Software tools in the writing process" に定型の文で書く（照合済み）。
  - "Authors are encouraged to share the code behind their submissions."（照合済み）
- テンプレートの説明（2024_08_02_jedm-latex.zip の instructions.pdf）
  - 要旨: "It should contain from 100 to 300 words."（照合済み）
  - "Supplementary technical material (e.g., mathematical proofs or descriptions of experimental procedures) should be collected in an appendix at the end of the paper (after the references)."（照合済み）
- 本文の分量の上限・事前登録の要件: 規定なし（取得した範囲の原文に該当の文が無い）。
