# GSE (Generative Struggle Engine)

## このファイルについて

このファイルは Codex がセッション開始時に自動で読み込む指示書です。
詳細な情報は `docs/` 配下の各ドキュメントを参照してください。
このファイルの目的は **Codex が探索を始める起点を示すこと** であり、
プロジェクトの全情報を含むことではありません。

## プロジェクト概要

- **名称**: GSE (Generative Struggle Engine)
- **目的**: キーストローク動態から認知状態 (Flow/Incubation/Stuck) を推定し、段階的介入で「生産的苦闘」を守る不便益 HCI フレームワーク
- **主要技術**: Tauri 2.0 + Rust (Backend) + React/TypeScript (Frontend)
- **ターゲット**: Windows 11 + macOS 13+
- **チーム規模**: 小規模 (2-3人)

## 参照すべきドキュメント

作業内容に応じて、必要なドキュメントを Read で読んでください:

| ファイル | いつ読むか |
|---|---|
| `docs/functional-design.md` | 機能の意図・要件・ユースケースを確認したい時 |
| `docs/architecture.md` | アーキテクチャ・スレッドモデル・データフローを確認したい時 |
| `docs/repository-structure.md` | ファイル配置・命名規則・モジュール依存方向を確認したい時 |
| `docs/development-guidelines.md` | コーディング規約・テスト方針・レビュー基準を確認したい時 |
| `docs/glossary.md` | 用語の正確な定義を確認したい時（禁止用語の確認も含む） |

## 技術的制約（厳守）

1. **Windows API**: `windows` crate (v0.58+) のみ。`winapi` は禁止
2. **macOS API**: `core-graphics` + `core-foundation`。低レベル FFI は `#[link]` 宣言
3. **unsafe**: Win32 API / macOS FFI 呼び出しに限定し、ラッパー構造体内に隔離
4. **フックコールバック**: Atomic 操作 + channel send のみ。ブロッキング禁止（Win/mac 共通）
5. **GCD dispatch_sync_f**: メインスレッドからの呼び出し禁止（デッドロック）
6. **TCC 権限**: Input Monitoring → Accessibility のフォールバックチェーンを維持
7. **グローバル TSF フック禁止**: UIPI でブロックされる（Windows のみ）
8. **Rust ログ**: `tracing` のみ。`println!` / `eprintln!` 禁止
9. **エラーハンドリング**: `anyhow::Result` を使用
10. **Tauri 2.0**: capabilities で権限管理。v1 allowlist は使わない

## 作業記録の運用ルール（重要）

**すべての実装作業は `.steering/` 配下に記録を残してください。**

### ディレクトリ命名規則

```
.steering/[YYYYMMDD]-[task-name]/
```

### 各タスクで作成するファイル

| ファイル | 必須/任意 | 内容 |
|---|---|---|
| `requirement.md` | 必須 | 背景、ゴール、受け入れ条件 |
| `design.md` | 必須 | 実装アプローチ、変更対象、テスト戦略 |
| `tasklist.md` | 必須 | チェックボックス形式のタスクリスト |
| `blockers.md` | 任意 | ブロッカーと対処方法 |
| `decisions.md` | 任意 | 重要な設計判断と根拠 |

テンプレートは `.steering/_template/` を参照。

## データ repo (gse-dataset) 連携

セッション NDJSON は本リポジトリに **コミットしない**。共有アーティファクトは `gse-replay --metrics --json` 出力のみで [mikotomiura/gse-dataset](https://github.com/mikotomiura/gse-dataset) (private) の `metrics/P*/<os>/` に置く。NDJSON Schema は `src-tauri/src/schema_dto.rs` から `cargo run --bin emit_schema` で機械生成 (CI が drift 検知)。詳細は `docs/development-guidelines.md §10`。

## コミットメッセージ規約

```
[type]([scope]): [短い説明]
```

- type: feat, fix, refactor, docs, chore, test
- scope: engine, hook, ime, wall, frontend, logger 等

## モデル選択ルール

| タスク種別 | モデル | 理由 |
|---|---|---|
| Plan Mode、設計判断 | Opus | 推論深度が必要 |
| 実装、テスト、リファクタ | Sonnet | バランス最良 |
| リネーム、フォーマット | Haiku | 速度優先 |

## コンテキスト管理ルール

1. **50% ルール**: 使用率 50% 超で次の区切りに `/smart-compact`
2. **タスク切り替え時は `/clear`**: 文脈が変わるなら `/compact` ではなく `/clear`
3. **Plan → Execute の徹底**: 複雑なタスクでは Plan Mode (Opus) → 実装 (Sonnet)

## 禁止事項

- 既存のテストを無断で削除しない
- ドキュメント化されていない設計判断を勝手に変更しない
- `.steering/` への記録を省略しない
- 50% を超えてもセッションを続けない
- 曖昧な指示に対して推測で実装しない（質問する）
- `analysis/` 内で Windows API / macOS フレームワークを直接呼ばない（OS 依存は `input/` に閉じる）

## Hook による自動強制（重要）

Hook は 3 層構造で動作する。全層の出力がユーザーに明示される:

1. **Preflight 層** (`UserPromptSubmit`): 毎ターン `preflight.sh` がタスク状態・git 状態・reimagine 適用状態を表示
2. **Guard 層** (`PreToolUse`): Edit/Write 時に `[guard] PASS` または `BLOCKED` を明示
3. **Report 層** (`PostToolUse` / `Stop`): cargo fmt 適用報告、clippy/tsc チェック結果

Edit/Write が `BLOCKED:` 出力で拒否された場合、メッセージに従って修正してから再試行すること。詳細は `docs/development-guidelines.md` §9 を参照。

## セッション開始時の行動指針

1. **`/start-task`** で作業記録を初期化する
2. **`/implement`** で実装を進める（feat / fix / refactor をモード選択）
3. **必要な docs/ を先に読む** — 闇雲にコードを読まず、まずドキュメントで文脈を把握
4. **Skill 参照**: 該当する Skill があれば `.Codex/skills/` を確認してから着手
5. **サブエージェントを積極的に活用** する（下記参照）

## サブエージェント活用ルール

**並列化できる調査・検証は積極的にサブエージェントへ委譲すること。**

| フェーズ | 使うべきエージェント | タイミング |
|---|---|---|
| 調査 | `file-finder` | 変更対象ファイルの特定 |
| 調査 | `dependency-checker` | 依存関係・影響範囲の把握 |
| 調査 | `impact-analyzer` | 変更の波及先を分析 |
| 実装後 | `code-reviewer` | コード品質・規約違反の検出 |
| 実装後 | `test-analyzer` | テストカバレッジ・不足の指摘 |
| 実装後 | `security-checker` | セキュリティ上の問題検出 |
| 検証 | `test-runner` | テスト実行 |
| 検証 | `build-executor` | ビルド確認 |
| デバッグ | `log-analyzer` | ログ解析 |

- **独立した調査は並列実行**: 例えば `file-finder` と `dependency-checker` は同時に走らせる
- **レビュー系も並列実行**: `code-reviewer` + `security-checker` を同時に走らせる
- 自分で全部やるより、サブエージェントに委譲して結果を統合する方が速く正確

## 利用可能なコマンド一覧

| コマンド | 用途 |
|---|---|
| `/start-task` | 新規タスクの開始（.steering/ 初期化） |
| `/add-feature` | 新機能追加ワークフロー |
| `/fix-bug` | バグ修正ワークフロー（TDD 順序: テスト先行） |
| `/refactor` | リファクタリングワークフロー（振る舞いを変えない・交互実行） |
| `/reimagine` | 破壊と構築（設計深化・確証バイアス排除、実装着手前専用） |
| `/review-changes` | 変更レビュー（動的 git 取得 + エージェント並列） |
| `/finish-task` | タスク完了処理（steering 最終化・テスト・コミット） |
| `/smart-compact` | 50% 超えた時の中間圧縮（設計判断・進捗を保持したまま /compact） |

