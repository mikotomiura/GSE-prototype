# タスクリスト

## 準備
- [x] issue #333 の本文と 5 件のコメント・ADR-039・同意文 v2 の草案・サーヴェイのカードを読む
- [x] grill（AskUserQuestion・判断 1）
- [x] requirement.md・decisions.md

## 段 1 の表
- [x] 段 1 の候補の表現と事前登録の数値を一次で集める（Explore・sonnet）
- [x] 戻り値を一次で裏取りする
- [x] `.steering/20261007-research-use-and-release/tier1-item-table.md` を書く

## 同意文 v2
- [x] 第 2 層・第 3 層を改訂する（判断 2〜4）
- [x] ADR-039 に日付つきの注（本文は書き換えない）

## 完了処理（/finish-task）
- [x] レビュー 1 巡目（code-reviewer のみ・Codex は予算超過で省略・判断 5）→ 全部直した
- [x] レビュー 2 巡目（直した差分・code-reviewer のみ）→ 3 件を直した（判断 6）
- [x] commit → push → PR #344 → CI 緑 → merge `699f3677` → main の run 38060058034（発火を確認）
- [x] issue #333 にコメントし（#issuecomment-6098585297）、本文のチェックボックス 3 つを更新した
