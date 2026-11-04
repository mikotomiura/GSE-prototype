# タスクリスト

## 道具の対応（完了前に照合）

- 実験の条件・コード → reproducibility-discipline（条件を計算の前にコミット・SEED・provenance）
- コード → 計算の前に code-reviewer、完了時に code-reviewer と /cross-review（Codex には条件・コード・集計値の文だけ）
- 決めること → AskUserQuestion で 1 問ずつ（日本語）

## このセッション（条件）

- [x] 引き継ぎ・前回の conditions D3・notes 結果 1 を読む
- [x] 引き継ぎ 1 が済んでいることを確かめる（`exp/gse-stage1-penalty-synthetic` の `db45ccd2`・push だけ残る）
- [x] worktree `/Users/johnd/GSE-prototype-tau-extend`（枝 `exp/gse-timeseries-tau-extend`・前回の枝の `b1771098` から）
- [x] grill（範囲・τ の格子・構造・集計の行・計算の場所）→ 判断 1〜5
- [x] `conditions.md`・`SEED`
- [ ] 条件をコミット（計算の前）

## 次のセッション（コード・合成）

- [ ] 前回の scripts・run.sh・mutate.sh を写し、条件どおりに変える
- [ ] code-reviewer（計算の前）
- [ ] 合成の selftest・変異の門を Mac で通す・時間を測り直す
- [ ] 職場の PC 向けの引き継ぎ（manifest・`-X utf8`・JOBS・P-REPRO）

## 本計算の後

- [ ] P-REPRO の結果を確かめる
- [ ] notes（言えること・言えないこと）
- [ ] code-reviewer と /cross-review
- [ ] push（研究者の手元で）・PR は研究者に確かめてから・`[skip ci]`
