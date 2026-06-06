---
name: "source-command-smart-compact"
description: "コンテキスト使用率が 50% を超えたときに実行する中間圧縮コマンド。 設計判断・未解決事項・採用ライブラリ・タスク進捗を保持したまま /compact を実行する。 タスク切り替え時は /clear を使い、このコマンドは使わない。"
---

# source-command-smart-compact

Use this skill when the user asks to run the migrated source command `smart-compact`.

## Command Template

# /smart-compact

## いつ使うか

- コンテキスト使用率が **50% を超えた**タイミング
- 同一タスクを継続しながら圧縮したい場合
- タスク切り替えには使わない（その場合は `/clear`）

---

## Step 1: 保持情報の確認

以下を Read で確認し、圧縮後も失われてはいけない情報をリストアップする:

```
- .steering/[現在のタスク]/design.md     → 実装アプローチ・変更対象
- .steering/[現在のタスク]/tasklist.md   → 完了済み・未完了タスク
- .steering/[現在のタスク]/decisions.md  → 重要な設計判断（あれば）
```

---

## Step 2: 保持サマリの生成

以下の形式でサマリを作成する（/compact への引き継ぎ情報）:

```
## 保持すべきコンテキスト

### 現在のタスク
- タスク名: [.steering/ のディレクトリ名]
- 進捗: [完了 N / 全 M ステップ]

### 実装アプローチ（design.md より）
- [採用した方針を 2-3 行で]

### 未解決事項
- [ブロッカー・未決定事項があれば]

### 採用したライブラリ・API
- [新規追加があれば]

### 次にやること
- [tasklist の次の未完了タスク]
```

---

## Step 3: /compact 実行

上記サマリを **保持するよう指示しながら** `/compact` を実行する。

> `/compact` 実行時に「以下を必ず保持してください: [サマリ]」と明示する。

---

## 制約

- タスク切り替え時は `/clear` を使う（このコマンドではない）
- 保持サマリの生成を省略しない
- 50% 未満での実行は不要（使用率を `/context` で確認してから使う）
