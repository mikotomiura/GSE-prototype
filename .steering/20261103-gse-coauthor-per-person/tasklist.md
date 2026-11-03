# タスクリスト

## 場面ごとの道具（先に書き、完了前に照合する）

- 設計判断 → grill（AskUserQuestion）と /reimagine（v1 を見ない別のエージェント）
- 実験 → reproducibility-discipline（条件を計算の前にコミット・陽性対照と変異・provenance）
- コード（experiments のスクリプト）→ code-reviewer と /cross-review（Codex には条件とコードだけ・記録と値は送らない）
- 外部の文献 → 新しく依拠するものは無い（[V348] CoAuthor は既存）

## 手順

- [x] grill（判断 1〜5）
- [x] /reimagine（design-v1.md・design.md・design-comparison.md・判断 6〜8）
- [x] 条件 `conditions.md` をコミット（計算の前）
- [x] 解析のスクリプトと `--selftest`・変異
- [x] 計算の前のレビュー（code-reviewer）
- [x] 中間の作り直しと門（Q1）
- [x] 陽性対照と変異（Q7）
- [x] 本計算
- [x] notes.md（学習曲線・越える k・言える範囲）
- [x] code-reviewer・/cross-review
- [x] 引き継ぎの更新・コミット・push
