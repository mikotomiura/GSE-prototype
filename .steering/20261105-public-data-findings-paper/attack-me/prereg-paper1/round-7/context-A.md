# context A（round 7・査読者・編集者・監査役に渡す）

- 対象物: 論文 1 の事前登録の草案 v8（OSF で凍結する前）。commit 17eb9e34（枝 docs/public-data-findings-paper）。round 1 は v1（87b2f159）、round 2 は v3（49f8b96a）、round 3 は v4（dad32265）、round 4 は v5（a5b7803b）、round 5 は v6（036fbd92）、round 6 は v7（f97cdf84）を見た。
- stage: prereg。投稿先: Journal of Educational Data Mining（JEDM）。論文の原稿はまだ無い。登録の英語版は、attack-me が minor になってから凍結の前に作る（今は日本語の版だけ）。
- 分量（機械で測った値）: 草案は 241 行・26,802 字（日本語）。本文（冒頭〜P11・付録の前）は 16,540 字（v7 は 15,355 字）。節は冒頭の注記・P0〜P11・付録 A〜F。
- v8 で変わったもの: 誤って同等とする割合を最も不利な配置の値で書いた（P10・付録 C・計算 7）・H1 × H2 の組の文を記述に（P0）・H2 の分岐 2 の語（P0・P7）・対照の集団と推定の対象（P4・P6）・英語版の照合（P11）・OSF の 3 つの登録（P11）・付録 F の SEED と新しい実装・見た書き手の数値を本文から付録 C へ。英語版は照合の前の下書きがある（この round では読まない）。

## 読んでよいファイルの一覧（これだけ・印は 本文 / 補足）

本文（事前登録そのもの）:
/Users/johnd/GSE-prototype-public-findings/.steering/20261105-public-data-findings-paper/paper-write/prereg-draft.md

補足（事前登録が固定の根拠として名指すファイル。読者に読む義務は無い。編集者の役は読まない）:
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/conditions.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/conditions-2.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/conditions-3.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/conditions-4.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/conditions-5.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/conditions-6.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/conditions-7.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/notes.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/requirements-confirm.txt
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/confirm-manifest.sha256
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/make-manifest.sh
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/build-variants.sh
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/run-confirm-holdout.sh
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/run-confirm-seen.sh
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/scripts/confirm_p1.py
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/scripts/prefreeze.py
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/scripts/rebuild_onsets.py
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/results/confirm_seen.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/results/provenance_confirm_seen.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/results/rebuild_control_summary_seen.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/results/rebuild_summary_q995_seen.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/results/rebuild_summary_w15_seen.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/results/rebuild_summary_w60_seen.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/results/precision.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/results/width_conversion.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/results/counts.json
/Users/johnd/GSE-prototype-public-findings/experiments/20261104-cs1-landscape/scripts/build_cs1.py
/Users/johnd/GSE-prototype-public-findings/experiments/20261104-cs1-landscape/scripts/analyze_cs1.py
/Users/johnd/GSE-prototype-public-findings/experiments/20261102-public-data-landscape/scripts/analyze_landscape.py
/Users/johnd/GSE-prototype-public-findings/experiments/20261101-klicke-early-stall-trigger/scripts/analyze_item2.py
/Users/johnd/GSE-prototype-public-findings/experiments/20261031-coauthor-pre-request-signal/scripts/convert.py
/Users/johnd/GSE-prototype-public-findings/experiments/20261031-coauthor-pre-request-signal/scripts/add_feat.py
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

（印の根拠: 規程は「補足の技術的な材料は参考文献の後の付録へ」と書く。事前登録の本文は草案で、スクリプト・条件・結果は確認を 1 通りに固定する補足の材料。書き手ごとの値は含まない。草案の中の ADR の番号・[Vn] の文献番号の本体は一覧に無い。一覧の外は読まない。v5 で manifest が名指す変換と依存のスクリプトを一覧に加えた。v6 で conditions-4.md を、v7 で conditions-5.md と conditions-6.md を、v8 で conditions-7.md を加えた。）

## 投稿規程の一次の抜粋

- https://jedm.educationaldatamining.org/index.php/JEDM/about/submissions（2026-11-06 にこの round で curl で取り直した原文で照合済み）
  - "You may submit an anonymized version of your manuscript. If you choose this possibility, the review process will be double-blind."
  - 生成 AI の申告は参考文献の前の節 "Declaration of Generative AI Software tools in the writing process" に定型の文で書く。
  - "Authors are encouraged to share the code behind their submissions."
- https://jedm.educationaldatamining.org/index.php/JEDM/about（Focus and Scope・2026-11-06 にこの round で curl で取り直し、逐語で在ることを照合した）
  - "Replicability: All submissions should present their methodologies and findings in a way that ensures replicability by other researchers. This includes clear descriptions of the data, tools, and procedures used."
  - "Data and Code Availability: Authors are strongly encouraged to make their data sets, software code, and intermediate results available to the community."
  - "Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses."
- テンプレートの説明（2024_08_02_jedm-latex.zip の instructions.pdf・round 1 に照合済み。この round では投稿規程の頁からテンプレートへのリンクが見つからず取り直せていない）
  - 要旨: "It should contain from 100 to 300 words."
  - "Supplementary technical material (e.g., mathematical proofs or descriptions of experimental procedures) should be collected in an appendix at the end of the paper (after the references)."
- 本文の分量の上限・事前登録の要件: 規定なし（取得した範囲の原文に該当の文が無い）。
