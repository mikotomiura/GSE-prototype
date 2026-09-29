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
- [x] `scripts/issues_data.py`（issue 34 件・用語 19・照会 5 通・件数・種文献）
- [x] `scripts/build_readable.py`（7 シートの追加・検算・issues.md の生成・記入欄の引き継ぎ）
- [x] `scripts/selftest.py`・`scripts/verify_recalc.py`（判断 9 で追加）
- [x] 新 xlsx（archive/）と `issues.md`

## 検算（最終版）
- [x] 既存 26 シートのセル値・構成の不変、シートの並び、判定欄が「未判定」のまま（build 内の検算）
- [x] 追加シートに書いた 1,803 セルを保存・再読込後に照合（build 内の検算）
- [x] issue 番号の相互参照（`check_refs`）
- [x] `selftest.py`: 変異 5 種（セル・並び・構成・読み戻し・日本語に接した相互参照）がそれぞれ期待した検査で止まり、出力も一時ファイルも残らない／記入欄の引き継ぎ／引き継ぎの守り 3 種（元が無い・旧版の構成・今の版に無い番号）／複製先の保護と強制上書き → ALL OK
- [x] `verify_recalc.py`: LibreOffice で再計算し、追加シートの数式 70 個にエラー・空なし、主要な数 14 個がデータから独立に数えた期待値と一致、主要な数と地図 ② が数式のまま、元データを変えると値が動く → ALL OK。★ 陰性対照（数式を定数に壊したコピー）で失敗することも確認
- [x] 追加シートを画像にして見た目を確認（初回。横向き・幅に合わせて印刷の設定）

## レビュー
- [x] code-reviewer（HIGH 2・MEDIUM 5・LOW 7）＋ security-checker（CRITICAL/HIGH 0・MEDIUM 1・LOW 4）を並列 → 判断 9 で対応
- [x] /cross-review の Codex 系統（P1 1・P2 4）→ 判断 9 で対応（1 件は一部採用）
- [x] Codex 2 巡目（今回足した規則の境界条件・P1 2・P2 2）→ 判断 10 で対応

## 完了処理
- [x] 前回の tasklist の未チェック 2 項目を実態に合わせて閉じる
- [x] 研究者の Downloads に新 xlsx を置く（別名・既存は上書きしない・SHA-256 は archive と一致）
- [ ] コミット → push → PR → CI → merge
- [ ] 研究者へ報告（前回の未コミットの作業の扱いを確認する）
