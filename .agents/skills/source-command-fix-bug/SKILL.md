---
name: "source-command-fix-bug"
description: "バグ修正のワークフロー。TDD 順序（回帰テスト先行）で修正する。 /start-task で作業ディレクトリを作成した後に実行する。"
---

# source-command-fix-bug

Use this skill when the user asks to run the migrated source command `fix-bug`.

## Command Template

# /fix-bug

## Step 0: バグの理解（1 問ずつ）

ユーザーから以下を聞き、`.steering/[現在のタスク]/requirement.md` に追記する:
1. 再現手順は?
2. 期待される動作と実際の動作は?
3. エラーメッセージ・ログはあるか?

---

## Step 1: 文脈把握

以下を Read で読む:
- `.steering/[現在のタスク]/requirement.md`
- `docs/architecture.md`（バグが発生しているモジュールに関係する箇所）

---

## Step 2: 調査（並列実行）

以下を同時に起動する:
- **file-finder**: バグが発生しているファイルと関連する実装を特定
- **impact-analyzer**: 修正による波及範囲を分析
- **log-analyzer**: ログがある場合のみ起動（エラーパターンを抽出）

---

## Step 3: 設計と承認

原因を特定し `.steering/[現在のタスク]/design.md` に記入:
- バグの根本原因
- 修正方針（最小限の変更で直す）
- テスト戦略

**ユーザーに承認を求める。原因が特定できないまま修正しない。**

---

## Step 3.5: /reimagine の適用（条件付き）

`requirement.md` の `## 運用メモ` を確認する:
- **`/reimagine 適用: Yes`** → ここで `/reimagine` を実行してから Step 4 へ進む
- **`/reimagine 適用: No`** → そのまま Step 4 へ進む

`## 運用メモ` がない場合はユーザーに確認する。

---

## Step 4: tasklist 作成

`.steering/[現在のタスク]/tasklist.md` に実装ステップを列挙する。
**最初の項目は必ず「回帰テストの追加」にする。**

---

## Step 5: 実装（TDD 順序）

**順序厳守**: 修正コードを書く前に、バグを再現する回帰テストを追加する。
テストが赤いことを確認してから修正コードを書く。

tasklist を順番に実施する。各完了後にチェックボックスを更新する。

バグ修正の範疇を超えるリファクタリングは混ぜない（別タスクに分離する）。

---

## Step 6: テスト

`test-runner` を起動する。Step 5 で追加した回帰テストを含む全テストが通ることを確認する。
失敗があれば `test-analyzer` で原因を分析し、修正後に再実行する。

---

## Step 7: レビュー（並列実行）

`code-reviewer` を起動する。外部入力に関わる修正の場合は `security-checker` も並列起動する。
- HIGH 指摘: すべて対応する
- MEDIUM 指摘: ユーザーに確認する

---

## Step 8: 完了

`/finish-task` を実行する。

> `schema_dto.rs` / `current.json` を touch した場合、finish-task Step 3 の
> schema parity check で停止する可能性がある (詳細: `docs/development-guidelines.md` §10.3.1 tier-3 guard)。

---

## 制約

- 原因が特定できないまま修正しない
- 回帰テストを追加せずに修正に入らない（TDD 順序厳守）
- バグ修正の範疇を超えるリファクタリングを混ぜない
- Step 6 の全テスト通過前に Step 7 に進まない
- Step 7 の HIGH 指摘を残したまま完了しない
