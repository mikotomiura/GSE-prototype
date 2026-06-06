---
name: "source-command-add-feature"
description: "新機能追加のワークフロー。/start-task で作業ディレクトリを作成した後に実行する。 file-finder, impact-analyzer, code-reviewer, test-runner などを呼び出す。"
---

# source-command-add-feature

Use this skill when the user asks to run the migrated source command `add-feature`.

## Command Template

# /add-feature

## Step 1: 文脈把握

以下を Read で読む:
- `.steering/[現在のタスク]/requirement.md`
- `docs/architecture.md`（変更対象モジュールに関係する箇所）

---

## Step 2: 調査（並列実行）

`file-finder` と `impact-analyzer` を同時に起動する:
- **file-finder**: 変更対象ファイルと類似実装を特定。ゼロから考えず既存パターンに乗る
- **impact-analyzer**: 変更による波及範囲を分析

---

## Step 3: 設計と承認

調査結果をもとに `.steering/[現在のタスク]/design.md` を記入:
- 実装アプローチ
- 変更対象ファイル
- テスト戦略

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
各タスクは 30 分以内で完了できる粒度に分割する。

---

## Step 5: 実装

tasklist を順番に実施する。各完了後にチェックボックスを更新する。

---

## Step 6: テスト

`test-runner` を起動する。失敗があれば `test-analyzer` で原因を分析し、
修正後に再実行する。全通過まで繰り返す。

---

## Step 7: レビュー（並列実行）

`code-reviewer` を起動する。外部入力（ユーザー入力・API・ファイル）を扱う場合は
`security-checker` も並列起動する。
- HIGH 指摘: すべて対応する
- MEDIUM 指摘: ユーザーに確認する

---

## Step 8: 完了

`/finish-task` を実行する。

> `schema_dto.rs` / `current.json` を touch した場合、finish-task Step 3 の
> schema parity check で停止する可能性がある (詳細: `docs/development-guidelines.md` §10.3.1 tier-3 guard)。

---

## 制約

- Step 3 の承認なしに Step 5 に進まない
- Step 6 のテストが失敗したまま Step 7 に進まない
- Step 7 の HIGH 指摘を残したまま完了しない
- 外部入力を扱う場合に Step 7 の security-checker を省略しない
