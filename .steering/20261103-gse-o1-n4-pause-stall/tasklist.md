# タスクリスト

## 場面ごとの対応（完了前に照合する）

| 場面 | 使うもの |
|---|---|
| 判断 | AskUserQuestion で 1 問ずつ（判断 1〜5 は済み） |
| 実験 | reproducibility-discipline（条件を計算の前にコミット・陽性対照・変異） |
| コードのレビュー | code-reviewer（計算の前）・完了時に code-reviewer＋security-checker＋/cross-review |
| 記録の扱い | data-privacy（Codex に記録・中間・結果の本文を送らない） |

## 作業

- [x] 引き継ぎ・削除台帳・前の実験の条件を読む
- [x] 判断 1〜5（対象・本人の入口・取り置き・G1・値の置き場）
- [x] requirement.md・design.md・decisions.md
- [x] 条件（conditions.md）とコード・陽性対照・変異
- [x] 計算の前のレビュー（code-reviewer）と直し（HIGH 2・MEDIUM 7・LOW 9。判断 6・7）
- [x] 条件とコードをコミット（計算の前・c567c88c）
- [x] run.sh を 1 回（exit 0・自己検査の食い違い 0）→ 記号の付け直し（判断 8）のため 2 回目（量は同じ）
- [ ] notes.md（人ごとの値・人の間の幅・言える範囲・事前登録 §3 と S1-E7 への材料）
- [ ] code-reviewer・security-checker・/cross-review
- [ ] 引き継ぎの更新（C の済み・B の入口・G1 の 2 名の別タスク）
- [ ] push（PR は研究者に確かめてから）
