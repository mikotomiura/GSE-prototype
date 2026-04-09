---
description: >
  タスクの完了処理を行う。steering 最終化・テスト実行・コミット提案までを実行する。
  /implement の完了後に必ず実行する。
allowed-tools: Read, Write, Edit, Bash(git *), Task
---

# /finish-task

## Step 1: tasklist 確認

`.steering/[現在のタスク]/tasklist.md` を Read で確認する。

未完了タスクがあればユーザーに確認:
> 「未完了: [タスク名] — 完了させますか? 次タスクに繰り越しますか?」

---

## Step 2: steering の最終化

実装中に変わった設計判断や判明した事実を `design.md` に追記する。
重要な設計判断があれば `decisions.md` を作成する（任意）。

---

## Step 3: レビューとテスト（並列）

```
/review-changes を実行
test-runner を起動
```

CRITICAL/HIGH 指摘 or テスト失敗があれば対応してから次へ。

---

## Step 4: コミットメッセージ提案

```
[type]([scope]): [短い説明]

- 変更内容 1
- 変更内容 2

Refs: .steering/[YYYYMMDD]-[task-name]/
```

type: `feat` / `fix` / `refactor` / `docs` / `test` / `chore`

ユーザー承認後に `git commit` を実行する。

---

## Step 5: 完了通知

```
完了しました。
次タスクを始める前に `/clear` でセッションをリセットしてください。
```

## 制約

- テスト失敗・CRITICAL/HIGH 指摘を残したまま完了しない
- ユーザー承認なしで commit しない
- steering の記録を省略しない
