# タスクリスト

## 準備
- [x] 前回の評価（`.steering/20260928-ai-fatigue-db-appraisal/`）の requirement・design・decisions・README を読む
- [x] 評価版 xlsx 26 シートを読む（Downloads の SHA-256 がアーカイブの記録と一致）
- [x] GSE の既決事項を確認（生成的返権論 §6.3・GR-H11/H12、roadmap §5.7・§10、references [P361]〜[P379]・[P199]〜[P209]、EVAL-NCC 測定辞書、GR-H12 反証表、glossary の常時収集・アウトカム指標、09-19 SR のプロトコル）
- [x] 前回の worktree の未コミットの作業（data_d.py・judge_xlsx.py ほか）を発見し、取り込み方を決めた（判断 2）

## 調べる価値の判断材料
- [x] OpenAlex（初回 7 件のみ・以後 429）
- [x] Europe PMC（題名・抄録に限定して取り直し）
- [x] Semantic Scholar の一括検索（意味を持つ主題だけ採用）
- [x] J-STAGE・CiNii Research（日本語・題名段）
- [x] 種文献 31 件の実在確認（Crossref・DataCite）

## 作成
- [x] `scripts/papers_plain.py`（34 件の平易な要約）
- [x] `scripts/issues_data.py`（issue 34 件・用語 19・照会 6・件数・種文献）
- [x] `scripts/build_readable.py`（7 シートの追加・検算・issues.md の生成）
- [x] 新 xlsx（archive/）と `issues.md`

## 検算
- [x] 既存 26 シートのセル値・構成の不変（build 内の検算）
- [x] 変異試験（`スクリーニング!F5` への書き込み）で止まり、出力も一時ファイルも残らない
- [x] LibreOffice でコピーを再計算: 数式 175 個・エラー 0・主要な数 13 個が期待値どおり（空 34 個は元の `AI判定比較` の人間用欄）
- [x] 追加シートを画像にして見た目を確認（横向き・幅に合わせて印刷の設定）
- [x] issue 番号の相互参照がすべて実在（データモジュールの検査）

## レビュー
- [ ] code-reviewer ＋ security-checker（並列）
- [ ] /cross-review（Codex）

## 完了処理
- [x] 前回の tasklist の未チェック 2 項目を実態に合わせて閉じる
- [ ] 研究者の Downloads に新 xlsx を置く（別名・既存は上書きしない）
- [ ] コミット → push → PR → CI → merge
- [ ] 研究者へ報告（前回の未コミットの作業の扱いを確認する）
