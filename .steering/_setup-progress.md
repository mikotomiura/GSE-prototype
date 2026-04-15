# Claude Code 環境構築進捗（再構築）

> このファイルは構築の進捗を記録する。各 setup-* コマンドが完了するたびに更新される。
> セッションを跨いだ継続のための引き継ぎ情報として機能する。

## プロジェクト概要

- **名称**: GSE (Generative Struggle Engine)
- **目的**: キーストローク動態からFlow/Incubation/Stuckの3状態認知推定を行い、段階的介入(Lv1 Nudge → Lv4 The Wall + Physical Anchor)でユーザーの「生産的苦闘」を守る、不便益に基づくHCIフレームワーク
- **技術スタック**: Tauri 2.0 + Rust (Backend: KB Hook, HMM, ONNX Runtime) + React/TypeScript (Frontend) + Python/PyTorch (ML学習) + Flutter (ストレッチゴール: Physical Anchor Outdoor)
- **ターゲット**: Windows 11 (Surface Pro 8 + Type Cover) + macOS (Accessibility/Input Monitoring)
- **チーム規模**: 小規模 (2-3人)
- **重視する品質特性**: 正確性（認知状態推定の精度、誤判定の最小化）
- **初回構築日**: 2026-04-09
- **再構築開始日**: 2026-04-14
- **再構築理由**: 全体的な品質向上（macOS対応反映、実運用知見の織り込み、Hooks強化）

## 構築進捗

- [x] **Phase 0: Bootstrap** (このコマンド)
  - 完了日時: 2026-04-14
  - 備考: 上書きモードで再構築。既存構築物を評価し品質向上ポイントを特定済み
- [x] **Phase 1: /setup-docs** — 永続ドキュメント
  - 完了日時: 2026-04-14
  - 更新ファイル:
    - docs/functional-design.md (200→232行: macOS UC-4追加、Feature 1/2にプラットフォーム振り分け)
    - docs/architecture.md (226→318行: Section 7 プラットフォーム抽象化+TCC権限フロー追加)
    - docs/repository-structure.md (164→176行: input/展開、sensors追加、命名規則拡張)
    - docs/development-guidelines.md (138→178行: macOS開発環境、コーディングガイド、CI/CD目標、テストロードマップ追加)
    - docs/glossary.md (81→94行: macOS技術用語9語、略語3語、禁止用語2語追加)
  - 主要な決定事項:
    - マージ方式で更新（既存構造を維持しつつmacOS対応を追記）
    - CGKeyCode→VKマッピングによるanalysis層のプラットフォーム非依存性を全ドキュメントで統一記載
    - TCC権限フロー（Preflight→Request→Accessibilityフォールバック）をfunctional-design+architectureで整合
- [x] **Phase 2: /setup-claude-md** — CLAUDE.md と .steering
  - 完了日時: 2026-04-14
  - 更新ファイル:
    - CLAUDE.md (137→134行: macOS制約3項目追加、重複セクション削除、GitHubリンク削除、Skill参照追加)
  - 既存維持: .steering/README.md, .steering/_template/ × 5ファイル（品質十分のため変更なし）
  - 品質向上ポイント: マルチプラットフォーム技術的制約、重複削除による軽量化
- [x] **Phase 3: /setup-skills** — Skill 群
  - 完了日時: 2026-04-14
  - 既存 Skill (引き継ぎ): architecture-rules, data-privacy, git-workflow, hmm-analysis,
    intervention-design, ml-workflow, physical-anchor, rust-standards, typescript-standards
  - 更新 Skill:
    - hook-constraints (SKILL.md: Win+macOS 両対応に拡張 / anti-patterns.md: macOS パターン4件追加)
    - project-status (SKILL.md: .steering タスク表示を改善)
  - 動的 Skill 数: 1 (project-status)
  - 全 Skill 数: 11
- [x] **Phase 4: /setup-agents** — サブエージェント群
  - 完了日時: 2026-04-14
  - 作成エージェント:
    - file-finder (sonnet)
    - dependency-checker (sonnet)
    - impact-analyzer (sonnet)
    - code-reviewer (opus)
    - test-analyzer (sonnet)
    - security-checker (opus)
    - test-runner (haiku)
    - build-executor (haiku)
    - log-analyzer (sonnet)
  - 品質向上ポイント: GSE固有Skill参照 (rust-standards, typescript-standards, hook-constraints, data-privacy, hmm-analysis, intervention-design) を各エージェントに反映済み
- [x] **Phase 5: /setup-commands** — ワークフローコマンド群
  - 完了日時: 2026-04-14
  - 作成コマンド:
    - /start-task (Step 3.5 追加: /reimagine 適用判断)
    - /add-feature (新規: 機能追加ワークフロー)
    - /fix-bug (新規: TDD 順序・バグ理解ステップ付き)
    - /refactor (新規: 全グリーン前提・交互実行)
    - /reimagine (新規: 破壊と構築)
    - /review-changes (変更なし)
    - /finish-task (変更なし)
    - /smart-compact (変更なし)
    - /implement → 廃止（/add-feature・/fix-bug・/refactor に分割）
  - 品質向上ポイント: /implement を3分割し各コマンドを単一責任化。/reimagine を追加しデータフロー整合
- [x] **Phase 6: /setup-hooks** — Hook 群
  - 完了日時: 2026-04-14 / 拡張: 2026-04-15
  - 作成 Hook:
    - SessionStart: .claude/hooks/session-start.sh (変更なし・動作確認済み)
    - Stop: .claude/hooks/stop-check.sh (cargo clippy + tsc --noEmit を実行し問題時のみ出力)
    - PostToolUse: cargo fmt --quiet (変更なし)
    - **UserPromptSubmit (2026-04-15 追加)**: リマインダ層 — 毎ターン CLAUDE.md 精読 + /reimagine + /start-task を 2 行で注入
    - **PreToolUse (2026-04-15 追加)**: 強制ブロック層
      - .claude/hooks/pre-edit-steering.sh — src-tauri/src/ または src/ 編集時、直近7日内 .steering/[YYYYMMDD]-*/ に requirement.md/design.md/tasklist.md 全揃いをチェック (欠落でブロック)
      - .claude/hooks/pre-edit-banned.sh — println!/eprintln! (制約8) / winapi crate (制約1) / analysis/ への OS 依存 import (禁止事項) を検出してブロック
  - 動作テスト (2026-04-15): 7/7 ケース合格 (docs通過, steering揃いで通過, 必須欠落でブロック, println!/winapi/analysis 違反を全てブロック, tracing は通過)
  - macOS の /tmp -> /private/tmp symlink 対策で realpath 正規化を追加
- [x] **Phase 7: /verify-setup** — 整合性検証
  - 完了日時: 2026-04-14
  - 検証結果: HEALTHY
  - 修正が必要な項目: 0件 (LOW 1件: 相互参照マップの /implement 表記を /add-feature 等に随時更新)
  - 前回の WARNING 3件: すべて解消確認済み

## 次に実行すべきコマンド

`/verify-setup`

## 各コマンド実行前のチェックリスト

各 setup-* コマンドを実行する前に、以下を必ず確認してください:

1. `/context` で使用率が 30% 以下か
2. 適切なモデルに切り替えてあるか（設計系は Opus、実装系は Sonnet）
3. 前のコマンドが完了し、`/clear` でセッションがリセットされているか
4. このファイル (`.steering/_setup-progress.md`) を Read で読んで進捗を確認したか

## 前回構築からの品質向上ポイント（全Phase共通）

1. **macOS 対応の反映**: Accessibility/Input Monitoring 対応を docs・skills に反映
2. **Commands の明確化**: `/implement` の feat/fix/refactor モード選択フローを改善
3. **Hooks の強化**: cargo clippy、TypeScript lint の自動トリガー追加
4. **Cross-platform 記述**: Windows 限定だった記述をマルチプラットフォーム対応に更新
5. **実運用知見の反映**: 4日間の開発で判明した改善点を各構築物に織り込む

## 前回の検証で報告された問題（Phase 7 で解消確認）

1. code-reviewer.md に intervention-design Skill 参照を追記
2. verify-setup.md の Step 6 を 4 コマンド構成に更新
3. project-status に補足ファイル追加（任意）

## 構築物の相互参照マップ

このセクションは各 setup-* コマンドが完了するたびに更新される。

### Skill リスト (11個)
- architecture-rules
- data-privacy
- git-workflow
- hmm-analysis
- hook-constraints (Win+macOS 両対応)
- intervention-design
- ml-workflow
- physical-anchor
- project-status (動的)
- rust-standards
- typescript-standards

### Skill → Agent 参照
- rust-standards → code-reviewer
- typescript-standards → code-reviewer
- hook-constraints → code-reviewer, test-analyzer, log-analyzer
- architecture-rules → code-reviewer, impact-analyzer, security-checker
- data-privacy → code-reviewer, security-checker
- intervention-design → code-reviewer
- git-workflow → dependency-checker
- hmm-analysis → test-analyzer, log-analyzer

### Agent → Command 参照
- file-finder → /implement (Step 2)
- impact-analyzer → /implement (Step 2)
- log-analyzer → /implement (Step 2, fix 固有)
- code-reviewer → /implement (Step 7), /review-changes, /finish-task
- security-checker → /implement (Step 7, 外部入力時), /review-changes
- test-runner → /implement (Step 5 refactor開始前・交互実行, Step 6), /finish-task
- test-analyzer → /implement (Step 6, 失敗時)

### Command → Command 参照
- /start-task → /implement (完了後に実行)
- /implement → /reimagine (Step 3.5, 条件付き), /finish-task (Step 8)
- /finish-task → /review-changes (Step 3)

### Hook → Command 参照
- SessionStart Hook (.claude/hooks/session-start.sh) → 全コマンドのセッション開始時に動作
- Stop Hook (.claude/hooks/stop-check.sh) → 全コマンドのターン終了時に動作（変更あり時のみ cargo clippy + tsc 実行）
- PostToolUse Hook (cargo fmt) → /add-feature, /fix-bug, /refactor 等の実装系で動作
