---
description: >
  リファクタリングのワークフロー。振る舞いを変えず、小さな変更を積み重ねる。
  /start-task で作業ディレクトリを作成した後に実行する。
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git *), Task
---

# /refactor

## Step 0: 全テストグリーンの確認（前提条件）

`test-runner` を起動し、現状のテストがすべてグリーンであることを確認する。

赤いテストがある場合は中断:
> 「テストが失敗しています。先に `/fix-bug` で修正してからリファクタリングしてください。」

---

## Step 1: 文脈把握

以下を Read で読む:
- `.steering/[現在のタスク]/requirement.md`
- `docs/architecture.md`（変更対象モジュールに関係する箇所）
- 対象ファイルそのもの（現状を把握する）

---

## Step 2: 調査（並列実行）

`file-finder` と `impact-analyzer` を同時に起動する:
- **file-finder**: 変更対象ファイルと類似パターンを特定
- **impact-analyzer**: 変更による波及範囲を分析

---

## Step 3: 設計と承認

`.steering/[現在のタスク]/design.md` に記入:
- リファクタリングの目的（可読性・保守性・設計改善）
- 変更対象ファイル
- **振る舞いを変えないことの保証方法**（既存テストがカバーしているか）
- 段階的な変更ステップ

**ユーザーに承認を求める。承認前に実装に進まない。**

---

## Step 3.5: /reimagine の適用（条件付き）

`requirement.md` の `## 運用メモ` を確認する:
- **`/reimagine 適用: Yes`** → ここで `/reimagine` を実行してから Step 4 へ進む
- **`/reimagine 適用: No`** → そのまま Step 4 へ進む

`## 運用メモ` がない場合はユーザーに確認する。

---

## Step 4: tasklist 作成

`.steering/[現在のタスク]/tasklist.md` に実装ステップを列挙する。
**各項目は「変更 → テスト → コミット → 次へ」の 1 サイクル単位にする。**
一度に大きく変えない。

---

## Step 5: 実装（交互実行）

tasklist の各項目を以下のサイクルで実行する:

1. 変更を加える
2. `test-runner` を実行する
3. 全グリーン → `git commit`（小さな単位でコミット）→ 次の項目へ
4. 赤くなった → 即ロールバック → 変更を小さく分割し直す → 1 に戻る

---

## Step 6: テスト（最終確認）

全項目完了後、`test-runner` で最終確認する。
失敗があれば `test-analyzer` で原因を分析する。

---

## Step 7: レビュー

`code-reviewer` を起動する。**可読性・保守性・設計改善**の観点を特に重視する。
- HIGH 指摘: すべて対応する
- MEDIUM 指摘: ユーザーに確認する

---

## Step 8: 完了

`/finish-task` を実行する。

> `schema_dto.rs` / `current.json` を touch した場合、finish-task Step 3 の
> schema parity check で停止する可能性がある (詳細: `docs/development-guidelines.md` §10.3.1 tier-3 guard)。

---

## 制約

- Step 0 でテストが赤い状態では絶対に開始しない
- 振る舞いを変える変更を含めない（振る舞い変更は別タスクに分離）
- 既存テストを変更しない（新規追加は OK）
- Step 5 の交互実行（変更→テスト→コミット）を省略しない
- バグ修正・新機能追加を混ぜない（別タスクに分離）
- Step 7 の HIGH 指摘を残したまま完了しない
