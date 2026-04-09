---
description: >
  新機能追加・バグ修正・リファクタリングの統合ワークフロー。
  /start-task で作業ディレクトリを作成した後に実行する。
  file-finder, impact-analyzer, code-reviewer, test-runner などを呼び出す。
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git *), Task
---

# /implement

## Step 0: モード選択

```
1. feat  — 新機能追加
2. fix   — バグ修正
3. refactor — リファクタリング（振る舞いを変えない）
```

ユーザーに選択させる。以降の差分は【feat/fix/refactor 固有】で明示する。

---

## Step 1: 文脈把握

以下を Read で読む:

- `.steering/[現在のタスク]/requirement.md`
- `docs/architecture.md`（変更対象モジュールに関係する箇所）

---

## Step 2: 調査（並列実行）

`file-finder` と `impact-analyzer` を同時に起動する:

- **file-finder**: 変更対象ファイルと類似実装を特定
- **impact-analyzer**: 変更による波及範囲を分析

【fix 固有】: ログがある場合は `log-analyzer` も並列起動する。

---

## Step 3: 設計と承認

調査結果をもとに `.steering/[現在のタスク]/design.md` を記入:

- 実装アプローチ
- 変更対象ファイル
- テスト戦略

【refactor 固有】: 振る舞いを変えないことの保証方法を必ず明記する。

**ユーザーに承認を求める。承認前に実装に進まない。**

---

## Step 4: tasklist 作成

`.steering/[現在のタスク]/tasklist.md` に実装ステップを列挙する。
各タスクは 30 分以内で完了できる粒度に分割する。

【refactor 固有】: 各ステップの後にテスト実行を挟む。一度に大きく変えない。

---

## Step 5: 実装

tasklist を順番に実施する。各完了後にチェックボックスを更新する。

【fix 固有】: 修正前に回帰テストを追加する（TDD アプローチ）。

---

## Step 6: テスト

`test-runner` を起動する。失敗があれば `test-analyzer` で原因を分析し、修正後に再実行する。全通過まで繰り返す。

---

## Step 7: レビュー（並列実行）

`code-reviewer` を起動する。外部入力を扱う変更の場合は `security-checker` も並列起動する。

- HIGH 指摘: すべて対応する
- MEDIUM 指摘: ユーザーに確認する

---

## Step 8: 完了

`/finish-task` を実行する。

---

## 制約

- Step 3 の承認なしに Step 5 に進まない
- Step 6 のテストが失敗したまま Step 7 に進まない
- Step 7 の HIGH 指摘を残したまま完了しない
- refactor では既存テストを変更しない（新規追加は OK）
