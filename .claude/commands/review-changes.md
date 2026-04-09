---
description: >
  直近の git 変更を多角的にレビューする。code-reviewer と security-checker を
  並列起動し、結果を統合して報告する。コミット前・PR 作成前に実行する。
allowed-tools: Read, Bash(git *), Task
---

# /review-changes

## Step 1: 現在の変更を動的に取得

```bash
git status --short
git diff --stat HEAD
```

変更がない場合は中断:
> 「変更がありません。レビュー対象がないため終了します。」

---

## Step 2: エージェント起動

以下を並列で起動する:

- **code-reviewer**: `git diff HEAD` の内容をレビュー。HIGH/MEDIUM の指摘を優先。
- **security-checker**: 外部入力・認証・データ保存に関わる変更がある場合のみ起動。

---

## Step 3: 結果を統合して報告

```markdown
## レビュー結果

### 変更概要
- ファイル数: N / 追加: +N / 削除: -N

### 必須対応 (CRITICAL/HIGH)
...

### 推奨対応 (MEDIUM)
...

### 任意対応 (LOW) / 良かった点
...
```

---

## Step 4: 判定

- CRITICAL/HIGH あり → 「修正してから commit してください」
- なし → 「commit して問題ありません」

## 制約

- 生のレポートを流さない。必ず統合・要約する
- 「問題なし」の場合も根拠を述べる
