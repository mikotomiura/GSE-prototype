# タスクリスト

## 場面ごとの道具（完了前に照合する）

| 場面 | 使うもの |
|---|---|
| 論点の確定 | grill（AskUserQuestion で 1 問ずつ） |
| 設計の比べ | /reimagine（研究者が「使う」を選んだ） |
| 事実の断定 | verify-before-claiming（ルール 7・8: 全文 grep） |
| 文献 | citation-ssot（新しく依拠する文献が無ければ「無い」と書く） |
| レビュー | /cross-review（code-reviewer ＋ Codex） |
| 出荷 | push。PR は研究者に確かめる（docs だけなら [skip ci]） |

## 準備
- [x] 引き継ぎ・ADR-019・021 D11・042・044・045・mhd-anatomy・空回しの notes を読む
- [x] ADR-045 の枝を main へ（PR #382・判断 0）
- [x] grill（判断 1〜6）

## 設計
- [x] design.md の初回案
- [x] /reimagine で比べ、研究者が採る案を選ぶ（v2・判断 7）

## 実装（文書）
- [x] ADR-046
- [x] README の一覧と注記
- [x] 設計の地図
- [x] glossary の注記

## 確かめ
- [x] 既存 ADR の本文に差分が無い
- [x] 主張の語の全文 grep
- [x] 禁止の言い方の grep

## レビュー
- [x] /cross-review と採否の記録（1 巡目・判断 8）
- [x] /cross-review 2 巡目と採否の記録（判断 9・10）。両巡とも HIGH 0

## 完了処理
- [x] tasklist・design の最終化
- [x] commit・push（PR は研究者に確かめる）
