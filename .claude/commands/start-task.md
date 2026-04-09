---
description: >
  新規タスクの作業を開始する。.steering/[YYYYMMDD]-[task-name]/ を作成し、
  requirement.md, design.md, tasklist.md のテンプレートを配置する。
  実装作業を始める前に必ず最初に実行する。
allowed-tools: Write, Edit, Read, Bash(mkdir *), Bash(date *)
---

# /start-task

## 実行フロー

### Step 1: 3 問ヒアリング（1 問ずつ）

1. タスク名を教えてください（kebab-case 推奨）
2. 背景とゴールは何ですか?
3. スコープ外（やらないこと）は何ですか?

### Step 2: ディレクトリ作成とテンプレート配置

```bash
DATE=$(date +%Y%m%d)
TASK_DIR=".steering/${DATE}-[task-name]"
mkdir -p "$TASK_DIR"
cp .steering/_template/requirement.md "$TASK_DIR/"
cp .steering/_template/design.md "$TASK_DIR/"
cp .steering/_template/tasklist.md "$TASK_DIR/"
```

### Step 3: requirement.md にヒアリング結果を記入

Edit ツールで背景・ゴール・スコープ外を記入する。

### Step 4: 完了通知

```
.steering/[DATE]-[task-name]/ を作成しました。
次: /implement を実行してください。
```

## 制約

- ヒアリングは 3 問で完結させる。詳細化は design.md で行う
- タスク名はユーザーに決めさせる
