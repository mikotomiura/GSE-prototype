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

<!-- loop:begin -->
## [Loop] Step 1 の置換: 固定 3 問ヒアリング → adaptive grill

**この節は上記 Step 1「3 問ヒアリング（1 問ずつ）」を置き換える (REPLACE)。**
3 問を順に聞いて完結させるのをやめ、`grilling` skill を参照した **適応的な追い込み** を行う:

- 回答の曖昧さ・矛盾を検出し、**判断分岐が閉じるまで** 掘り下げる (定型 3 問に固執しない)。
- タスク名・背景/ゴール・スコープ外は grill の副産物として自然に確定する
  (別途 3 問として聞き直さない)。
- 確定したドメイン用語は `docs/glossary.md` に追記する。
- 下した意思決定は該当タスクの `.steering/[task]/decisions.md` に記録する
  (`.steering/_template/decisions.md` の「決定 / 理由 / 却下案」書式)。
- 出力は「検証可能なゴール」= Done/Stop が exit code / test 名で言える形。
- grill はループの前に・タスクにつき 1 回・main チェックアウトで行う (worktree 内では行わない)。
- grill は **Opus** で実行する (`docs/loop-engineering.md` モデル割当ポリシー)。

grill 後、ループ工学で issue 単位に分解して回すタスクは
`to-prd`（grill 結果をそのまま要件として扱う）→ `to-issues`（`issue-slicing` skill、Opus）
で縦切り issue 群に分解し、`.steering/[task]/issues/00X.md` として出力する
(テンプレ: `.steering/_template/loop-issue.md`)。

`to-issues` 完了後は **`/clear` して新セッションで実行を始める**。分解セッションには
却下案・議論・暗黙の前提が残っており、そのまま実行すると「issue に書いていない前提」を
持ち込んで issue ファイル = SSOT の契約が壊れる。*issue ファイルだけを読んで実行が成立
しないなら、分解が失敗している* — 新セッションはこの契約の検査装置でもある。

通常の単発タスク (issue 単位ループを回さない) は、grill 後そのまま Step 2〜4 に進めばよい。
issue 分解は Loop Engineering (`docs/loop-engineering.md`) を使う場合のみ必要。
<!-- loop:end -->
