# タスクリスト

## 場面ごとの道具（完了前に照合する）

| 場面 | 使うもの |
|---|---|
| 設計の比べ | `/reimagine`（実装の前） |
| 条件・SEED | reproducibility-discipline（コードより前にコミット） |
| 計算の前のレビュー | code-reviewer |
| 結果の後のレビュー | code-reviewer ＋ /cross-review（Codex を加える・条件・コード・集計値の文だけ） |
| 本計算 | 職場の PC（HP Z2）・引き継ぎに手順 |

## 設計
- [x] grill（判断 1〜7）
- [x] design.md 初回案 v1
- [x] /reimagine で v2 と比べ、採る案を研究者が選ぶ（v2・判断 8）
- [x] conditions.md と SEED を書き、コミット（コードより前）

## 実装（Mac）
- [x] 前の試験の scripts を写す
- [x] 量子化の列（P-Q）・並べ替え（P-SHUF）・6 構造・k の絞り・D の量
- [x] 陽性対照と変異の門を通す（m1・m35 を直した・判断 12。eb8bdfd9 で selftest 19・変異 16 すべて緑）
- [x] 時間を合成で測り、見積もりを条件に足す（条件の後の変更として）
- [x] 計算の前の code-reviewer・HIGH を直す
- [x] 職場の PC の引き継ぎを書く

## 職場の PC（研究者）
- [x] P-D1・P-Q・P-REPRO（P-Q 外れ 0・P-REPRO tau 6,741・mli 1,363 の葉で外れ 0）
- [x] 本計算（6 組・HP Z2・run_id 20261109T122107-1576・約 12 時間 40 分・終了コード 0）

## 結果の後
- [x] notes.md（読みの形 A・B・C）・report.py の表（CoAuthor の主のセルは形 B・CS1 C5 k = 5 は形 C）
- [x] code-reviewer ＋ /cross-review（Codex）（HIGH なし・判断 13 で直した）
- [x] 2 系統目のレビューの残り 4 件を直し（判断 14）、code-reviewer ＋ /cross-review（Codex）の 2 巡目を通す（判断 15 で直した）
- [ ] push・PR は研究者が確かめてから
