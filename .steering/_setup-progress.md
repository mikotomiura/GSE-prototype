# Claude Code 環境構築進捗

> このファイルは構築の進捗を記録する。各 setup-* コマンドが完了するたびに更新される。
> セッションを跨いだ継続のための引き継ぎ情報として機能する。

## プロジェクト概要

- **名称**: GSE (Generative Struggle Engine)
- **目的**: キーストローク動態からFlow/Incubation/Stuckの3状態認知推定を行い、段階的介入(Lv1 Nudge → Lv4 The Wall + Physical Anchor)でユーザーの「生産的苦闘」を守る、不便益に基づくHCIフレームワーク
- **技術スタック**: Tauri 2.0 + Rust (Backend: KB Hook, HMM, ONNX Runtime) + React/TypeScript (Frontend) + Python/PyTorch (ML学習) + Flutter (ストレッチゴール: Physical Anchor Outdoor)
- **チーム規模**: 小規模 (2-3人)
- **重視する品質特性**: 正確性（認知状態推定の精度、誤判定の最小化）
- **構築開始日**: 2026-04-09
- **備考**: 個人プロジェクトとして継続中。提案書・技術設計書はdocs/内のPDFを参照。

## 構築進捗

- [x] **Phase 0: Bootstrap** (このコマンド)
  - 完了日時: 2026-04-09
  - 備考: 環境チェック完了、ディレクトリ構造作成済み、追記モード
- [x] **Phase 1: /setup-docs** — 永続ドキュメント
  - 完了日時: 2026-04-09
  - 作成ファイル:
    - docs/functional-design.md
    - docs/architecture.md
    - docs/repository-structure.md
    - docs/development-guidelines.md
    - docs/glossary.md
  - 主要な決定事項:
    - セキュリティ方針: リアルタイム運用中はローカル保存のみ、ML学習データ収集はオプトイン+匿名化+セッション終了後バッチ送信
    - アーキテクチャパターン: マルチスレッド・イベント駆動+レイヤードモジュール構成（Clean Architecture は過剰として不採用）
    - テスト方針: analysis/ モジュールの単体テストを優先。input/ は実機手動確認
- [x] **Phase 2: /setup-claude-md** — CLAUDE.md と .steering
  - 完了日時: 2026-04-09
  - 作成ファイル:
    - CLAUDE.md (132 行)
    - .steering/README.md
    - .steering/_template/requirement.md
    - .steering/_template/design.md
    - .steering/_template/tasklist.md
    - .steering/_template/blockers.md
    - .steering/_template/decisions.md
  - .gitignore 更新: なし（Git 追跡する方針）
- [x] **Phase 3: /setup-skills** — Skill 群
  - 完了日時: 2026-04-09
  - 作成 Skill:
    - rust-standards (SKILL.md, examples.md)
    - typescript-standards (SKILL.md, patterns.md)
    - git-workflow (SKILL.md, checklist.md)
    - hook-constraints (SKILL.md, anti-patterns.md)
    - architecture-rules (SKILL.md, decision-tree.md)
    - data-privacy (SKILL.md, anonymization.md)
    - ml-workflow (SKILL.md, migration-guide.md)
    - hmm-analysis (SKILL.md, parameter-reference.md)
    - intervention-design (SKILL.md, state-machine.md)
    - physical-anchor (SKILL.md, flutter-integration.md)
    - project-status (SKILL.md, 動的型)
  - 静的 Skill 数: 10
  - 動的 Skill 数: 1
- [x] **Phase 4: /setup-agents** — サブエージェント群
  - 完了日時: 2026-04-10
  - 作成エージェント:
    - file-finder (sonnet) — ファイル発見・分類
    - dependency-checker (sonnet) — 依存関係・循環参照調査
    - impact-analyzer (sonnet) — 変更影響範囲分析
    - code-reviewer (opus) — コード品質・規約レビュー
    - test-analyzer (sonnet) — テスト失敗原因・カバレッジ分析
    - security-checker (opus) — セキュリティ・プライバシー監査
    - test-runner (haiku) — テスト実行・結果要約
    - build-executor (haiku) — ビルド実行・結果要約
    - log-analyzer (sonnet) — ログ抽出・パターン分析
- [x] **Phase 5: /setup-commands** — ワークフローコマンド群
  - 完了日時: 2026-04-10
  - 設計変更: スキル指示の7コマンドから4コマンドに再設計（重複排除・動的化）
  - 作成コマンド:
    - /start-task (簡素化: 3問ヒアリング)
    - /implement (feat/fix/refactor を統合)
    - /review-changes (動的 git 取得)
    - /finish-task (骨格版)
  - 廃止: /add-feature, /fix-bug, /refactor, /smart-compact
- [x] **Phase 6: /setup-hooks** — Hook 群
  - 完了日時: 2026-04-10
  - 作成 Hook:
    - SessionStart: .claude/hooks/session-start.sh (Branch/Commit/Changed/Tasks)
    - Stop: 自己検証プロンプト (anyhow::Result / スキル名明示)
    - PostToolUse: cargo fmt --quiet (Edit/Write 後、2>/dev/null 抑制済み)
  - settings.json: 新規作成 (.claude/settings.json)
- [x] **Phase 7: /verify-setup** — 整合性検証
  - 完了日時: 2026-04-10
  - 検証結果: WARNINGS
  - 修正が必要な項目: 3 件 (すべて LOW)
    - code-reviewer.md に intervention-design Skill 参照を追記
    - verify-setup.md の Step 6 を 4 コマンド構成に更新
    - project-status に補足ファイル追加 (任意)

## 次に実行すべきコマンド

`/setup-hooks`

## 各コマンド実行前のチェックリスト

各 setup-* コマンドを実行する前に、以下を必ず確認してください:

1. `/context` で使用率が 30% 以下か
2. 適切なモデルに切り替えてあるか（設計系は Opus、実装系は Sonnet）
3. 前のコマンドが完了し、`/clear` でセッションがリセットされているか
4. このファイル (`.steering/_setup-progress.md`) を Read で読んで進捗を確認したか

## 構築物の相互参照マップ

このセクションは各 setup-* コマンドが完了するたびに更新される。

### Skill リスト
- rust-standards — Rust コーディング規約
- typescript-standards — TypeScript/React 規約
- git-workflow — コミット・ブランチ・バージョニング
- hook-constraints — フックコールバック制約
- architecture-rules — レイヤー依存・モジュール配置
- data-privacy — キーストロークデータ・ML収集プライバシー
- ml-workflow — HMM チューニング・ONNX 移行
- hmm-analysis — F1-F6特徴量・潜在軸・観測ビン・EWMA
- intervention-design — Nudge/Wall/ZenTimer/MonkMode
- physical-anchor — Flutter連携・歩数/距離/速度計測
- project-status (動的) — git状態・進捗リアルタイム取得

### Skill → Agent 参照
- rust-standards → code-reviewer
- typescript-standards → code-reviewer
- hook-constraints → code-reviewer, test-analyzer
- architecture-rules → impact-analyzer, code-reviewer, security-checker
- data-privacy → security-checker
- git-workflow → dependency-checker
- hmm-analysis → test-analyzer, log-analyzer
- intervention-design → code-reviewer（wall_server.rs / Overlay.tsx レビュー時）

### Agent → Command 参照
- file-finder, impact-analyzer → /implement (調査フェーズ)
- code-reviewer, security-checker → /implement (レビューフェーズ), /review-changes
- test-runner, build-executor → /implement (検証フェーズ), /finish-task
- test-analyzer → /implement (fix モード), /finish-task
- log-analyzer → /implement (デバッグ用途)

### Hook → Command 参照
- SessionStart Hook → 全コマンドのセッション開始時に動作
- Stop Hook → 全コマンドのターン終了時に動作 (自己検証強制)
- PostToolUse Hook → /implement, /fix-bug 等の実装系コマンドで cargo fmt 自動実行
