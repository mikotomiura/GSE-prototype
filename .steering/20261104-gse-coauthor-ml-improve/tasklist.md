# タスクリスト

## 場面ごとの道具（先に書き、完了前に照合する）

- 設計判断 → grill（AskUserQuestion・1 問ずつ・推奨と理由）と /reimagine（v1 を見ない別のエージェント・Opus）
- 実験 → reproducibility-discipline（条件を計算の前にコミット・陽性対照と変異・provenance）
- コード（experiments のスクリプト）→ 計算の前に code-reviewer、完了時に code-reviewer と /cross-review（Codex には条件とコードだけ・CoAuthor と CS1 の記録と値は送らない）
- 外部の文献 → 新しく依拠するものは無い見込み（CoAuthor [V348]・CS1 [V243] は既存）。AR-HMM・部分プールの手法の出典を本文で引くなら citation-ssot

## 手順

- [x] grill（判断 1・2）
- [x] /reimagine（design-v1.md・design.md・design-comparison.md）と研究者の選択（判断 3・4）
- [x] CS1 2021 の中間の作り直し（8 列の feat・受け入れの時刻）と門（判断 5・6）。パネルは design §2.1 の規則（C5・k ∈ {1,2,3,5}）
- [x] 合成で時間を測り、格子を決める（全格子・判断 8）
- [x] 条件 `conditions.md` をコミット（計算の前・判断 9〜11 を含む）
- [x] 解析のスクリプト・`--selftest`・変異（B の判断 11 の直しを含む）
- [x] 計算の前のレビュー（code-reviewer・security-checker・判断 12）
- [x] 陽性対照と変異の門（Mac・判断 9〜13。職場の PC の run.sh でも回る）
- [x] 本計算（職場の HP Z2・`.steering/_handoff/next-session-gse-coauthor-ml-run-on-hp-z2.md`）
- [x] notes.md（4 つ組・各表・言える範囲・逸脱）（Mac・`.steering/_handoff/next-session-gse-coauthor-ml-after-run.md`）
- [ ] code-reviewer・/cross-review
- [ ] 引き継ぎの更新・コミット・push（PR は研究者が確かめてから）
