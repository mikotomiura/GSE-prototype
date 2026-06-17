---
description: >
  バグ修正のワークフロー。TDD 順序（回帰テスト先行）で修正する。
  implementation-workflow Skill の共通骨格をバグ修正固有の制約で上書きして実行する。
  /start-task で作業ディレクトリを作成した後に実行する。
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git *), Task
---

# /fix-bug

## 前提条件

- [ ] `/start-task` で作業ディレクトリ作成済み

## 実行フロー

### Step 1: implementation-workflow Skill の読み込み

`.claude/skills/implementation-workflow/SKILL.md` を Read で読む。

### Step 2: バグ固有の前処理（1 問ずつ聞く）

ユーザーから以下を収集し `.steering/[現在のタスク]/requirement.md` に追記する:

1. 再現手順は?
2. 期待される動作と実際の動作は?
3. エラーメッセージ・ログはあるか?

ログがある場合は `log-analyzer` を起動して原因の手がかりを得る。

### Step 3: Skill 共通骨格の実行（以下のオーバーライド付き）

Skill の Step A〜I を実行するが、`/fix-bug` では以下を上書き:

| 上書き対象 | 内容 |
|---|---|
| Step C（設計） | バグの根本原因・修正方針を design.md に記録してから承認を求める。原因未特定のまま進まない |
| Step E 開始前 | **回帰テストを先に追加**（TDD 順序）。このテストは現時点で失敗するはず |
| Step E 本体 | **最小限の変更で修正**。広範囲のリファクタは別タスクに分離 |
| Step F | Step E で追加した回帰テストを含む全テストが通ることを確認 |

`/reimagine 適用: Yes` なら Step C の設計承認後に `/reimagine` を実行してから Step D へ。

### Step 4: 完了処理

> 「バグ修正が完了しました。`/finish-task` を実行してください。」

## 制約

- 原因が特定できないまま修正しない
- 回帰テストを追加せずに修正に入らない（TDD 順序厳守）
- バグ修正の範疇を超えるリファクタリングを混ぜない
- Skill の Step G の HIGH 指摘を残したまま完了しない
