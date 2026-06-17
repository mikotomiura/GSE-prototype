---
description: >
  リファクタリングのワークフロー。振る舞いを変えず、小さな変更を積み重ねる。
  implementation-workflow Skill の共通骨格をリファクタリング固有の制約で上書きして実行する。
  /start-task で作業ディレクトリを作成した後に実行する。
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git *), Task
---

# /refactor

## 前提条件

- [ ] `/start-task` で作業ディレクトリ作成済み
- [ ] **現状のテストが全てグリーン**（このコマンドはそれを前提に動く）

## 実行フロー

### Step 1: implementation-workflow Skill の読み込み

`.claude/skills/implementation-workflow/SKILL.md` を Read で読む。

### Step 2: 全テストグリーンの確認（最重要）

`test-runner` を起動して現状のテストがすべてグリーンであることを確認する。

**赤いテストがある状態でリファクタリングを始めない。**  
赤があれば中断 → 先に `/fix-bug` を実行するようユーザーに通知。

### Step 3: Skill 共通骨格の実行（以下のオーバーライド付き）

Skill の Step A〜I を実行するが、`/refactor` では以下を上書き:

| 上書き対象 | 内容 |
|---|---|
| Step C（設計） | 「振る舞いを変えないことの保証方法」と「段階的な変更ステップ」を必ず含める |
| Step D（tasklist） | 各項目は **1 コミット分の最小単位**。大きな変更を 1 項目にまとめない |
| Step E（実装） | 各項目ごとに「変更 → Step F → 失敗なら即ロールバック → 成功なら git commit → 次へ」の交互サイクル |
| Step F（テスト） | 各変更ステップ直後に実行。「最後に一括」ではなく **交互実行** |
| Step G（レビュー） | 可読性・保守性・設計改善の観点を特に重視 |

`/reimagine 適用: Yes` なら Step C の設計承認後に `/reimagine` を実行してから Step D へ。

### Step 4: 完了処理

> 「リファクタリングが完了しました。`/finish-task` を実行してください。」

## 制約

- **振る舞いを変える変更は含めない**（リファクタリングの定義違反）
- 既存テストを変更しない（新規追加は OK）
- 大きな変更を一度に行わない（Step E の交互実行を徹底）
- テストが赤い状態でリファクタリングを始めない
- バグ修正・新機能追加を混ぜない（別タスクに分離）
- Skill の Step G の HIGH 指摘を残したまま完了しない
