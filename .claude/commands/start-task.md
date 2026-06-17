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

### Step 3.5: /reimagine 適用判断

以下のいずれかに該当するか確認する（ユーザーに問う）:

- アーキテクチャや重要な設計判断を伴う
- 公開 API / 外部インターフェースを定義する
- 再現や原因特定が難しいバグ
- 複数の実装案が考えられ、最良案が自明でない

**該当する → 推奨**: 各ワークフローコマンドの設計承認 (Step C) 後に `/reimagine` を実行してください。  
**該当しない → 不要**: 自明な実装・小さなリファクタ・ドキュメント更新では不要です。

ユーザーの回答を `requirement.md` 末尾に Edit で追記:

```markdown
## 運用メモ
- /reimagine 適用: Yes / No
- 理由: [ユーザーの回答]
```

### Step 4: 完了通知

```
.steering/[DATE]-[task-name]/ を作成しました。
次: タスク種別に応じて以下を実行してください:
- 新機能追加 → /add-feature
- バグ修正   → /fix-bug
- リファクタリング → /refactor
（/reimagine 適用 Yes の場合は設計承認後に /reimagine を実行）
```

## 制約

- ヒアリングは 3 問で完結させる。詳細化は design.md で行う
- タスク名はユーザーに決めさせる
- /reimagine 適用判断の記録を省略しない
