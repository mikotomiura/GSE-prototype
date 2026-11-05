# context A（round 5・査読者・編集者・監査役に渡す）

- 対象物: 論文 1 の事前登録の草案 v6（OSF で凍結する前）。commit 036fbd92（枝 docs/public-data-findings-paper）。round 1 は v1（87b2f159）、round 2 は v3（49f8b96a）、round 3 は v4（dad32265）、round 4 は v5（a5b7803b）を見た。
- stage: prereg。投稿先: Journal of Educational Data Mining（JEDM）。論文の原稿はまだ無い。登録の英語版は、attack-me が minor になってから凍結の前に作る（今は日本語の版だけ）。
- 分量（機械で測った値）: 草案は 200 行・19,701 字（日本語）。本文（冒頭〜P11・付録の前）は 12,328 字（v5 は P0〜P10 が 13,589 字・付録 A の前が 15,695 字）。節は冒頭の注記と正の順位・P0〜P11・付録 A〜D。
- v6 で変わったもの: 構成の組み直し（P0 に貢献と仮説ごとの表・用語の表・推定量と判定を前へ・経緯と凍結の前の値を付録 B〜D へ）・停滞にも条件 A・H2 の除外を全ての長い休止に・凍結の後の食い違いの扱い・H3 の門を埋め込みの回収に・床にない対の感度・完走と中断の記録・境界の近くの較正・取り置きの手順の予行（凍結の前の計算 4）。

## 読んでよいファイルの一覧（これだけ・印は 本文 / 補足）

本文（事前登録そのもの）:
/Users/johnd/GSE-prototype-public-findings/.steering/20261105-public-data-findings-paper/paper-write/prereg-draft.md

補足（事前登録が固定の根拠として名指すファイル。読者に読む義務は無い。編集者の役は読まない）:
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/conditions.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/conditions-2.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/conditions-3.md
/Users/johnd/GSE-prototype-public-findings/experiments/20261105-findings-paper1-prefreeze/conditions-4.md
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

（印の根拠: 規程は「補足の技術的な材料は参考文献の後の付録へ」と書く。事前登録の本文は草案で、スクリプト・条件・結果は確認を 1 通りに固定する補足の材料。書き手ごとの値は含まない。草案の中の ADR の番号・[Vn] の文献番号の本体は一覧に無い。一覧の外は読まない。v5 で manifest が名指す変換と依存のスクリプトを一覧に加えた。v6 で conditions-4.md を加えた。）

## 投稿規程の一次の抜粋

- https://jedm.educationaldatamining.org/index.php/JEDM/about/submissions（2026-11-05 にこの round で curl で取り直した原文で照合済み）
  - "You may submit an anonymized version of your manuscript. If you choose this possibility, the review process will be double-blind."
  - 生成 AI の申告は参考文献の前の節 "Declaration of Generative AI Software tools in the writing process" に定型の文で書く。
  - "Authors are encouraged to share the code behind their submissions."
- https://jedm.educationaldatamining.org/index.php/JEDM/about（Focus and Scope・2026-11-05 にこの round で curl で取った原文から逐語で切り出した）
  - "Replicability: All submissions should present their methodologies and findings in a way that ensures replicability by other researchers. This includes clear descriptions of the data, tools, and procedures used."
  - "Data and Code Availability: Authors are strongly encouraged to make their data sets, software code, and intermediate results available to the community."
  - "Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses."
- テンプレートの説明（2024_08_02_jedm-latex.zip の instructions.pdf・round 1 に照合済み。この round では投稿規程の頁からテンプレートへのリンクが見つからず取り直せていない）
  - 要旨: "It should contain from 100 to 300 words."
  - "Supplementary technical material (e.g., mathematical proofs or descriptions of experimental procedures) should be collected in an appendix at the end of the paper (after the references)."
- 本文の分量の上限・事前登録の要件: 規定なし（取得した範囲の原文に該当の文が無い）。
