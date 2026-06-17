---
name: implementation-workflow
description: >
  GSE プロジェクトの実装タスク共通骨格。新機能追加・バグ修正・リファクタリングの
  いずれかを行うとき、まずこの Skill を参照してから作業を始める。
  調査 → 設計 → 実装 → テスト → レビューの流れと、各ステップでのサブエージェント
  呼び出し方法を定義する。`/add-feature`, `/fix-bug`, `/refactor` コマンドから
  必ず参照される。`src-tauri/src/**/*.rs` または `src/**/*.tsx` を追加・修正するとき、
  `.steering/` に tasklist.md を作るとき、実装完了後に PR を出すときに必須参照。
allowed-tools: Read, Edit, Glob, Grep, Task
---

# Implementation Workflow

## このスキルの目的

GSE の実装タスクに共通する骨格を一箇所に集約し、各ワークフローコマンドが
プロジェクト固有の制約だけに集中できるようにする。
「調査なしに書き始める」「テストなしにマージする」「レビューなしにコミットする」
を構造的に防ぐ。

## 共通ステップ（いずれの実装タスクでも適用）

### Step 0: 設計計画（条件付き — 設計重タスクのみ）

以下のいずれかに該当するタスクは、Step A の前に **Plan Mode (Opus)** で計画を立て、
ユーザー承認を得てから着手する:

- アーキテクチャ / 重要な設計判断を伴う
- 公開 API / 外部インターフェースを定義する
- 再現や原因特定が難しいバグ
- 複数の実装案が考えられ、最良案が自明でない

該当タスク: Plan Mode で計画 → 必要に応じ `/reimagine` で 2 案比較 → 承認後に Step A へ。
**自明な小タスク・リネーム・フォーマット・1 行修正は Step 0 を省略**してよい。
（CLAUDE.md モデル選択ルール: Plan Mode / 設計判断は Opus。Step 0 の計画承認と Step C の設計記録は
別物 — Step 0 は高レベルの方針合意、Step C は `design.md` への落とし込みと最終承認。）

### Step A: コンテキスト確認

以下を **この順で** Read する:

1. `docs/agent-shared.md` — プロジェクト概要・アーキテクチャ要約・技術制約
2. `.steering/[現在のタスク]/requirement.md` — 背景・ゴール・受け入れ条件
3. 必要に応じて:
   - `docs/architecture.md` — スレッドモデル・データフロー確認
   - `docs/repository-structure.md` — ファイル配置確認
   - 関連 Skill の SKILL.md（下記「関連 Skill 参照マップ」参照）

**関連 Skill 参照マップ**（どの Skill をいつ読むか）:

| 作業内容 | 参照 Skill |
|---|---|
| `*.rs` ファイルを書く / 修正する | `rust-standards` |
| `hook_*.rs` / `ime_*.rs` のコールバック / Atomic | `hook-constraints` |
| `*.tsx` / `*.ts` を書く / 修正する | `typescript-standards` |
| `features.rs` / `engine.rs` の特徴量・HMM | `hmm-analysis` |
| `*.rs` を新規追加 / モジュール境界変更 | `architecture-rules` |
| `logger.rs` / `hook.rs` / `wall_server.rs` / 外部送信 | `data-privacy` |
| 介入ロジック / Nudge / Wall | `intervention-design` |
| ML チューニング / ONNX 移行 | `ml-workflow` |
| コミット / ブランチ / PR | `git-workflow` |

### Step B: 既存パターン調査

2 つのサブエージェントを **1 メッセージで並列起動**:

```
Task 1: file-finder で「[対象機能] に類似する既存実装ファイル」を列挙
Task 2: impact-analyzer で変更予定ファイルの影響範囲（呼び出し元・テスト・mod.rs）を分析
```

※ 並列起動が可能な場合は単一メッセージに 2 つの Task tool 呼び出しを並べる。

### Step C: 設計記録とユーザー承認

`.steering/[現在のタスク]/design.md` に記入:

```markdown
## アプローチ
[実装方針または修正方針 — 1-3 段落]

## 変更対象ファイル
- `src-tauri/src/analysis/xxx.rs` — [何を変えるか]
- ...

## 既存パターンとの整合
[Step B で見つけた類似実装との関係]

## テスト戦略
- `cargo test --workspace` で [何を確認するか]
- `gse-replay --snapshot` で [回帰テスト対象]
- 手動確認が必要な項目: [実機でしか確認できないもの]
```

**ユーザーに設計の承認を求める。承認なしに Step D へ進まない。**
（設計が不明瞭な場合は質問して解消してから承認を求める。推測で進まない。）

### Step D: tasklist.md 作成

`.steering/[現在のタスク]/tasklist.md` にチェックボックス形式で列挙:

```markdown
## tasklist

- [ ] [具体的な実装ステップ 1]（30 分以内）
- [ ] [具体的な実装ステップ 2]（30 分以内）
- [ ] cargo test --workspace パス
- [ ] gse-replay --snapshot 回帰チェック
- [ ] code-reviewer + security-checker 実行・指摘対応
- [ ] /finish-task で /cross-review（Claude ∥ Codex）必須・両者一致の CRITICAL/HIGH を最優先対応
- [ ] git コミット（git-workflow Skill に従う）
```

各タスクは 30 分以内で完了できる粒度に分割する。

### Step E: 実装

tasklist の各項目を **順番に** 実装。完了したらチェックを更新。

実装中の規約:
- Rust を書くなら `rust-standards` Skill のチェックリストを確認
- TypeScript を書くなら `typescript-standards` Skill のチェックリストを確認
- フックコールバックを触るなら `hook-constraints` Skill を確認
- `any` 型・`println!`・`eprintln!`・`winapi` は使わない
- `/context` が 50% を超えたら `/smart-compact`

### Step F: テストと検証

以下を **この順で** 実行:

```bash
# 1. 単体テスト
cargo test --workspace

# 2. 回帰テスト（HMM 挙動を変えた場合は必須。そうでなければ任意）
cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json

# 3. Schema drift check（schema_dto.rs を変えた場合のみ）
cargo run --bin emit_schema
# → 出力と src-tauri/schema/current.json を byte-equal 比較
```

`test-runner` サブエージェントを起動して実行させることを推奨（大量出力をメインコンテキストに流さない）:

```
Task: test-runner で cargo test --workspace を実行し、失敗・警告のサマリを報告
```

失敗があれば `test-analyzer` サブエージェントで原因分析 → 修正 → 再実行。

### Step G: コードレビュー

`code-reviewer` と `security-checker` を **1 メッセージで並列起動**:

```
Task 1: code-reviewer で変更ファイルをレビュー（docs/development-guidelines.md 参照）
Task 2: security-checker で変更ファイルのセキュリティチェック
        ※ logger.rs / hook.rs / wall_server.rs を変更した場合は必須
```

対応基準:
- **HIGH**: 必ず対応してから次へ
- **MEDIUM**: ユーザーに判断を仰ぐ
- **LOW / INFO**: 記録のみ（対応任意）

> **二層レビュー**: Step G は実装中の Claude 高速反復レビュー（code-reviewer + security-checker）。
> **最終の独立第二意見は `/finish-task` Step 3 の `/cross-review`（Claude code-reviewer ∥ Codex
> codex-review）で実施し、タスク完了ごとに必須**（CLAUDE.md 項6 / 2026-06-16 ポリシー）。
> 安全ゲート（proprietary/機密/予算/codex 不在）でブロック時のみ Claude 単独へ縮退し理由を明記。

### Step H: ドキュメント更新（該当時のみ）

以下の場合はドキュメントを更新する:

| 変更内容 | 更新するドキュメント |
|---|---|
| 新しい概念・用語の追加 | `docs/glossary.md` |
| アーキテクチャ上の変更 | `docs/architecture.md` |
| 機能の追加・削除 | `docs/functional-design.md` |
| ディレクトリ構造の変更 | `docs/repository-structure.md` |

### Step I: コミットと PR

`git-workflow` Skill のチェックリストに従う:

```bash
git add [変更した具体的なファイルを列挙]   # git add -A / git add . は使わない
git commit -m "feat(scope): [説明]

- 変更内容 1
- 変更内容 2

Refs: .steering/[YYYYMMDD]-[task-name]/"
```

PR を出す場合は `git-workflow` Skill の「PR 作成チェックリスト」を参照。
マージ前に `cargo build` + `cargo clippy` + `npm run build` の全通過を確認する。

---

## 各コマンドによるオーバーライド

このスキルの Step A〜I は共通骨格。`/add-feature`, `/fix-bug`, `/refactor` はそれぞれ追加・上書きする:

| コマンド | 追加・変更する制約 |
|---|---|
| `/add-feature` | Step A〜I をそのまま実行 |
| `/fix-bug` | Step E の **前** に「再現する最小テストを先に書く」を挿入（TDD 順序） |
| `/refactor` | Step B の **前** に「現状の全テストがグリーンであること」を確認。Step E と Step F を交互に繰り返す（小さな単位で実装 → すぐテスト） |

---

## チェックリスト

作業完了前に確認:

- [ ] （設計重タスクなら）Step 0 で Plan Mode の計画承認を得たか
- [ ] Step A で agent-shared.md と requirement.md を読んだか
- [ ] Step B で file-finder + impact-analyzer を並列起動したか
- [ ] Step C でユーザーの設計承認を得たか
- [ ] Step F で cargo test --workspace をパスしたか
- [ ] Step G で code-reviewer + security-checker を並列実行したか
- [ ] Step G で HIGH 指摘に全対応したか
- [ ] `/finish-task` で `/cross-review`（codex 含む）を実行したか（ブロック時のみ縮退・理由明記）
- [ ] Step I でコミットメッセージに `Refs:` を付けたか

---

## 補足資料

- `anti-patterns.md` — 骨格を省略・ショートカットした場合の失敗集

## 関連する他の Skill

- `rust-standards` — Step E で Rust コードを書くとき
- `typescript-standards` — Step E で TypeScript コードを書くとき
- `hook-constraints` — Step E でフックコールバックを触るとき
- `architecture-rules` — Step E でファイル追加・モジュール変更をするとき
- `data-privacy` — Step G の security-checker トリガー判断
- `git-workflow` — Step I のコミット
- `empirical-prompt-tuning` — この Skill 自身の品質評価（最優先評価対象）
