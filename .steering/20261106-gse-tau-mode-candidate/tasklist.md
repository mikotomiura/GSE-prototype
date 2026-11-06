# タスクリスト

## 道具の対応（完了前に照合）

- 実験の条件・コード → reproducibility-discipline（条件と SEED を計算の前にコミット・provenance・P-REPRO）
- 設計 → /reimagine（研究者の指定・v2 は初回案を読まない Opus のエージェント）
- コード → 計算の前に code-reviewer。結果の後（Mac の次のセッション）に code-reviewer と /cross-review（Codex を加える・Codex には条件・コード・集計値の文だけ）
- 決めること → AskUserQuestion で 1 問ずつ（日本語・推奨と理由）
- Drive への置き → 上書きの前に研究者の手直しを確かめる・置いた後にサイズを照合

## このセッション（条件・コード・合成・引き継ぎ）

- [x] 引き継ぎ・前の試験の conditions・notes の結果 2 の但し書き・ml.py・hmm2.py を読む
- [x] worktree `/Users/johnd/GSE-prototype-tau-mode`（枝 `exp/gse-tau-mode-candidate`・`2911f940` から・fetch 済み）
- [x] grill → 判断 1〜6
- [x] /reimagine（v1 と v2 を比べて研究者が選ぶ）
- [x] `experiments/20261106-tau-mode-candidate/conditions.md`・`SEED` をコミット（コードより前）
- [x] 前の試験の scripts・run.sh・mutate.sh を写して変える
- [x] 合成の selftest（全対照）を Mac で通す
- [x] code-reviewer（計算の前）
- [x] 変異の門を Mac で通す
- [x] 時間を測り直す（合成）
- [x] 職場の PC 向けの引き継ぎ（repo と Drive の `GSE_ML_run`）
- [x] 結果が戻った後の Mac 向けの引き継ぎ（notes の骨組み・値なし）
- [ ] コミット（push と PR は研究者が確かめてから）

## 本計算の後（別のセッション）

- [ ] P-REPRO・門・来歴を確かめる
- [ ] notes（読みの形は判断 5）・tables.md
- [ ] code-reviewer と /cross-review（Codex を加える）
