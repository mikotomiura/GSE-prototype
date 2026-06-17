# Claude Code 環境構築進捗（v2 フル上書き再構築）

> このファイルは構築の進捗を記録する。各 setup-* コマンドが完了するたびに更新される。
> セッションを跨いだ継続のための引き継ぎ情報として機能する。
> **各 Phase の間で必ず `/clear` を実行すること。**

## プロジェクト概要

- **名称**: GSE (Generative Struggle Engine)
- **目的**: キーストローク動態から Flow/Incubation/Stuck の3状態認知推定を行い、段階的介入 (Lv1 Nudge → Lv4 The Wall + Physical Anchor) でユーザーの「生産的苦闘」を守る、不便益に基づく HCI フレームワーク
- **技術スタック**: Tauri 2.0 + Rust (Backend: KB Hook, HMM, ONNX Runtime) + React/TypeScript (Frontend) + Python/PyTorch (ML学習) + Flutter (ストレッチ: Physical Anchor Outdoor)
- **ターゲット**: Windows 11 (Surface Pro 8 + Type Cover) + macOS 13+ (Accessibility / Input Monitoring)
- **チーム規模**: 小規模 (2-3人)
- **重視する品質特性**: 正確性（認知状態推定の精度、誤判定の最小化）
- **v2 再構築開始日**: 2026-06-16
- **再構築モード**: フル上書き（Phase 0–9 をゼロから再生成）
- **再構築理由**: 新 commands_setup(v2) への移行 — Codex CLI 連携 + anthropics/skills 公式 marketplace + AGENTS.md/agent-shared.md の3ファイル体制を採用

### 採用方針（ユーザー確定 2026-06-16）

- **スコープ**: フル上書き再構築
- **Codex / marketplace 連携**: **採用する**（codex-cli 0.128.0 / gh 2.90.0 導入済み）
  - → Phase 2 (marketplace)、Phase 5 (codex-bridge)、cross-reviewer agent、`/cross-review`、予算/秘匿ガード hook を **すべて構築する**

## 構築進捗

- [x] **Phase 0: Bootstrap** (このコマンド)
  - 完了日時: 2026-06-16
  - 備考: 環境チェック完了（git repo / codex / gh 確認済み）。フル上書きモードで再構築。進捗ファイルを新10Phase体系へリセット。既存 v1 成果物は各 Phase の上書きモードで作り直す。
- [x] **Phase 1: /setup-docs** — 永続ドキュメント (Opus 必須)
  - 完了日時: 2026-06-16
  - 方式: **フル上書きではなく Review & Refresh (マージ)** を採用。成熟プロジェクト (v0.3 較正) のため、5 docs を読み取り専用サブエージェント並列監査 → ドリフトのみパッチ → 横断整合性レビュー。
  - 更新ファイル (新規作成なし、既存をパッチ):
    - docs/repository-structure.md — analysis/ に intervention.rs / intervention_eval.rs / probe_scheduler.rs 追加、存在しない sensors_windows.rs 削除、CLAUDE.md を root へ修正、.agents/ .codex/ scripts/ AGENTS.md .github/ 等を追記
    - docs/glossary.md — hmm_version 0.2.0→0.3.0 修正、UserLabel 定義を 2 経路併存に訂正、v0.3 用語 (ProbeSource/ProbeRef/SkipReason/Track/TaskKind/ExpectedQuadrant)・分析ループ用語 (AnalysisState/TypingPath/TransitionPath/SilencePath/RangeLabel)・Early Unlock を追加
    - docs/functional-design.md — 機能 7 に v0.3 優先順位逆転 (プローブ主・ホットキー補助)・ビネット延期の注記、UC-4 に ad-hoc 再トグル注記
    - docs/architecture.md — §4.7 に v0.3 LogEntry バリアントの emit 状況、§4.8 に self-marker(M)/review-marker(R) ホットキー追加
    - docs/development-guidelines.md — CSP に img-src 'self' data: 反映、capabilities 場所追記、§3 CI/CD を「未構成」→「ci.yml で構成済み (枠超過でローカル代替)」に訂正
  - スコープ外として記録した既知 follow-up (Phase 1 では未対応):
    1. CLAUDE.md 行114 の旧 `/implement` 参照 → Phase 3 で解消済み。start-task.md の参照 → Phase 7 で解消済み。finish-task.md の description 行7 は「/implement の完了後」だが実際の本体は正しいため実害なし（Phase 9 verify で再確認）
    2. テスト fixture `tests/fixtures/minimal.ndjson` の `hmm_version:"0.2.0"` が engine 0.3.0 と不一致 → コード/テスト側の課題 (doc 外)
    3. 「コードが anyhow::Result を使っていない」というレビュー指摘 → CLAUDE.md 制約 #9 と矛盾するため未検証のまま据え置き。要確認
- [x] **Phase 2: /setup-marketplace** — anthropics/skills 公式 plugin の導入
  - 完了日時: 2026-06-16
  - 導入 plugin:
    - claude-api (1 Skill, Apache 2.0)
    - example-skills (12 Skill, Apache 2.0)
    - document-skills: **スキップ** (Proprietary / GSE では PDF/Office 文書生成不要)
  - 個別 Skill コピー: なし (plugin 一括 install)
  - 作成ファイル:
    - docs/external-skills.md
  - ライセンス同意ログ: Apache 2.0 のみ導入 (Proprietary は意図的に除外)
- [x] **Phase 3: /setup-claude-md** — CLAUDE.md / AGENTS.md / docs/agent-shared.md / .steering (Opus)
  - 完了日時: 2026-06-16
  - 方式: 既存 v1 の CLAUDE.md / AGENTS.md (フル内容の重複) を **3 ファイル体制へ再構築**。
    共通事項 (概要 / アーキ / 技術制約 10 項 / 規約 / テスト / git / gse-dataset / CI) を
    新規 docs/agent-shared.md に集約し、CLAUDE.md / AGENTS.md は固有プロトコルのみのポインタ型に。
  - 作成/更新ファイル:
    - CLAUDE.md (114 行 / 上限 150) — Claude 固有: 行動規範 / GSE 固有 Skill 表 / .steering / モデル / context / 禁止 / Hook
    - AGENTS.md (67 行 / 上限 80) — Codex 固有: sandbox / approval / model / 出力形式 / rescue / 禁止事項 (旧 v1 重複版を上書き)
    - docs/agent-shared.md (128 行 / 上限 200) — 新規。両者の共通ハブ + docs/ リンクハブ
  - 同期検証: `grep -c '@docs/agent-shared.md' CLAUDE.md AGENTS.md` → 両方 ≥1 (CLAUDE=4, AGENTS=3)
  - 既知不整合の解消: 廃止 `/implement` 参照を全廃 / AGENTS.md の `.Codex/skills` typo 修正 /
    「50% ルール」を 1M context 前提に再設計 (タスク境界 `/clear` 優先・長期化時のみ `/smart-compact`) /
    Hook が bash 前提 (Windows は git-bash 必須) を agent-shared.md に明記
  - .steering/: 既存 (README + _template/ × 5) を流用。再生成せず。git 追跡済み (gitignore 変更なし)
  - 備考: codex 導入済み (`/c/Users/johnd/.../npm/codex`) のため AGENTS.md は skip せず構築。
    CLAUDE.md / AGENTS.md 中の Codex 連携 Skill (codex-consult/review/rescue) と `.codex/*` は Phase 5 で実体化予定 (現状は前方参照)。
- [x] **Phase 4: /setup-skills** — プロジェクト固有 Skill 群（公式 Skill 重複回避）
  - 完了日時: 2026-06-16
  - 作成 Skill (自前・v1 から継続 + v2 で新規追加):
    - rust-standards (SKILL.md, examples.md) — v1 継続
    - typescript-standards (SKILL.md, patterns.md) — v1 継続
    - git-workflow (SKILL.md, checklist.md) — v1 継続
    - architecture-rules (SKILL.md, decision-tree.md) — v1 継続
    - data-privacy (SKILL.md, anonymization.md) — v1 継続
    - ml-workflow (SKILL.md, migration-guide.md) — v1 継続
    - hmm-analysis (SKILL.md, parameter-reference.md) — v1 継続
    - intervention-design (SKILL.md, state-machine.md) — v1 継続
    - physical-anchor (SKILL.md, flutter-integration.md) — v1 継続
    - hook-constraints (SKILL.md, anti-patterns.md) — v1 継続
    - project-status (SKILL.md, usage-examples.md) — v1 継続・動的 Skill
    - **implementation-workflow** (SKILL.md, anti-patterns.md) — v2 新規・DRY 骨格
    - **empirical-prompt-tuning** (SKILL.md, examples.md) — v2 新規・品質評価手法
  - 動的 Skill 数: 1 (project-status)
  - 公式 Skill 重複回避: docs/external-skills.md 参照済み
    (webapp-testing / mcp-builder / skill-creator / claude-api / web-artifacts-builder はカバー済みのため自前不作成)
  - Phase H 実施:
    - implementation-workflow: Structural-only (Iter 0) 完了。Full tier は Phase 9 /verify-setup で実施予定
      → .steering/deferred-evaluations.md に記録済み
    - empirical-prompt-tuning: Phase H 適用除外（メタ循環）。/reimagine で代替予定
- [x] **Phase 5: /setup-codex-bridge** — Codex CLI 連携基盤
  - 完了日時: 2026-06-16
  - 作成ファイル:
    - .codex/config.toml (model=gpt-5.5, sandbox=read-only, approval=untrusted)
    - .codex/budget.json (200K/day, per_invocation=30K)
    - scripts/secrets-filter.sh (実行権限付与済み, exit-code 2 で fail-closed)
    - scripts/run-codex-review.sh (cross-reviewer 用 wrapper)
    - scripts/run-codex-consult.sh (codex-consult Skill 用 wrapper, --preview 対応)
    - .claude/skills/codex-consult/SKILL.md + examples.md
    - .claude/skills/codex-review/SKILL.md + examples.md
    - .claude/skills/codex-rescue/SKILL.md + decision-tree.md
  - 疎通テスト: PASS (gpt-5.5, exit 0, 応答: 「こんにちは、Codex です。」)
  - 使用モデル: gpt-5.5 (reasoning effort: medium; test は low)
- [x] **Phase 6: /setup-agents** — サブエージェント群（cross-reviewer 追加）
  - 完了日時: 2026-06-16
  - 作成エージェント (9 既存 + 1 新規):
    - file-finder (sonnet) — 既存
    - dependency-checker (sonnet) — 既存
    - impact-analyzer (sonnet) — 既存
    - code-reviewer (opus) — 既存
    - test-analyzer (sonnet) — 既存
    - security-checker (opus) — 既存
    - test-runner (haiku) — 既存
    - build-executor (haiku) — 既存
    - log-analyzer (sonnet) — 既存
    - cross-reviewer (sonnet) — v2 新規（Phase 5 完了により作成）
- [x] **Phase 7: /setup-commands** — ワークフローコマンド群（`/cross-review` 含む）
  - 完了日時: 2026-06-16
  - 作成コマンド (9 個):
    - `/start-task` (v2: `/implement` 参照を削除、/reimagine タイミング修正)
    - `/add-feature` (v2: implementation-workflow Skill への薄いラッパー)
    - `/fix-bug` (v2: implementation-workflow Skill への薄いラッパー + TDD 上書き)
    - `/refactor` (v2: implementation-workflow Skill への薄いラッパー + 交互実行上書き)
    - `/reimagine` (v1 から継続・変更なし)
    - `/review-changes` (v1 から継続・変更なし)
    - `/smart-compact` (v1 から継続・変更なし)
    - `/finish-task` (v1 から継続・schema parity check 含む・変更なし)
    - `/cross-review` (v2 新規: cross-reviewer エージェント + 予算チェック + 機密フィルタ)
- [x] **Phase 8: /setup-hooks** — Hook 群（予算/秘匿ガード含む）
  - 完了日時: 2026-06-16
  - 作成 Hook:
    - SessionStart: .claude/hooks/session-start.sh（動的情報表示）
    - UserPromptSubmit: Preflight 層 / preflight.sh（毎ターン .steering/ 状態・git 状態・reimagine 状態を動的表示、BLOCK せず）
    - PreToolUse (Edit|Write|MultiEdit): Guard 層 / pre-edit-steering.sh + pre-edit-banned.sh（[guard] PASS / [guard] BLOCKED 出力統一）
    - PreToolUse (Bash): Codex 層 / codex-budget-guard.sh + secrets-pre-filter.sh（codex exec 呼び出し前に予算 / 機密検査）
    - PostToolUse (Edit|Write|MultiEdit): Report 層 / post-fmt.sh（cargo fmt、変更時のみ [fmt] applied）
    - Stop: Report 層 / stop-check.sh（clippy / tsc 問題時のみ [stop] WARN、生出力は完全抑制）
    - Stop: Codex 層 / token-report-stop.sh（当日 codex token 使用量を .steering/_token_log.md に記録）
  - v1 → v2 修正:
    - pre-edit-steering.sh: BLOCKED メッセージに [guard] プレフィックス追加（3箇所）
    - pre-edit-banned.sh: BLOCKED メッセージに [guard] プレフィックス追加（3箇所）
    - stop-check.sh: 生 clippy/tsc 出力を >/dev/null 2>&1 で抑制、[stop] WARN 1行のみに変更、exit 0 追加
    - settings.json: MultiEdit PostToolUse 追加（v2 既知不整合 #2 解消）、Codex Bash PreToolUse ブロック追加、token-report-stop Stop hook 追加
  - 出力プレフィックス統一: [preflight] / [guard] / [fmt] / [stop]
  - 全 hook: "type": "command" に統一（"type": "prompt" 混在なし）
- [x] **Phase 9: /verify-setup** — 整合性検証（Codex 疎通 / AGENTS↔CLAUDE 同期 / ライセンス整合 含む）
  - 完了日時: 2026-06-16
  - 検証結果: **✅ HEALTHY** (CRITICAL=0 / HIGH=0 / MEDIUM=1→修正済 / LOW=2)
  - Phase 5 状態: 完了 (Codex 連携あり)
  - Phase 2 状態: 完了 (anthropics/skills 14個導入, document-skills skip)
  - Codex 疎通: ✅ PASS (exit 0、"Hello。こんにちは")
  - AGENTS↔CLAUDE 同期: ✅ (Claude keywords≤1, AGENTS keywords≤2、閾値以内)
  - ライセンス整合: ⚠️ secrets-pre-filter.sh が不要な拡張子フィルタを含む (M-1)
  - 修正が必要な項目: 3件 (CRITICAL=0 / HIGH=0 / MEDIUM=1 / LOW=2)
  - レポート: .steering/_verify-report-20260616.md

## 次に実行すべきコマンド

`/verify-setup`（Phase 9・整合性検証・Codex 疎通含む・**Sonnet で可**）

## 各コマンド実行前のチェックリスト

各 setup-* コマンドを実行する前に、以下を必ず確認してください:

1. `/context` で使用率が 30% 以下か
2. 適切なモデルに切り替えてあるか（設計系は Opus、実装系は Sonnet）
3. 前のコマンドが完了し、`/clear` でセッションがリセットされているか
4. このファイル (`.steering/_setup-progress.md`) を Read で読んで進捗を確認したか

## v2 で新規導入される構築物（v1 から増える差分）

- `docs/agent-shared.md` — Claude / Codex 共通コンテキスト（3ファイル体制の中核）
- `docs/external-skills.md` — 公式 Skill 一覧 + 外部 LLM 送信可否の単一真実源
- 公式 marketplace plugin（Phase 2 で選定）
- `.codex/config.toml` / `.codex/budget.json` — Codex 設定・日次予算
- `codex-consult` / `codex-review` / `codex-rescue` Skill
- `cross-reviewer` agent / `/cross-review` command
- 予算ガード / 秘匿フィルタ hook（`scripts/secrets-filter.sh` 等）

## v1 → v2 で修正すべき既知の不整合（前回レビューで検出）

これらは上書き再構築で各 Phase が自然に解消する想定。Phase 9 verify で再確認する:

1. 廃止コマンド `/implement` への参照残存（旧 CLAUDE.md 行動指針 / start-task.md Step3.5 / finish-task.md）→ Phase 3 / Phase 7 で解消
2. PostToolUse(post-fmt) の matcher が `Edit`/`Write` のみで `MultiEdit` を拾わない → Phase 8 で解消
3. 「50% ルール」が preflight で監視されず、1M context 前提と桁ズレ → Phase 3 / Phase 8 で再設計
4. Hook が全て bash 前提（Windows は git-bash 必須）である旨が未明記 → Phase 3 agent-shared.md / Phase 8 で明記

## 構築物の相互参照マップ

このセクションは各 setup-* コマンドが完了するたびに更新される。

### Skill リスト（自前 13 個）
静的:
- rust-standards, typescript-standards, git-workflow, architecture-rules
- data-privacy, ml-workflow, hmm-analysis, intervention-design
- physical-anchor, hook-constraints, implementation-workflow, empirical-prompt-tuning

動的 (context: fork):
- project-status

公式 (anthropics/skills 由来): docs/external-skills.md を参照

### Skill リスト (Codex 連携)
- codex-consult (read-only、設計相談 / Plan mode 第二意見)
- codex-review (read-only、diff レビュー / cross-reviewer から呼出)
- codex-rescue (workspace-write + worktree 隔離、実装委譲 / 要明示承認)

### Skill → Agent 参照
- rust-standards → code-reviewer
- typescript-standards → code-reviewer
- architecture-rules → impact-analyzer, code-reviewer, security-checker
- git-workflow → dependency-checker
- hook-constraints → code-reviewer (src-tauri/src/input/ レビュー時)
- data-privacy → security-checker
- codex-review → cross-reviewer
- codex-consult → (メインエージェント直呼び / Skill)
- codex-rescue → (メインエージェント直呼び / Skill)

### Agent → Command 参照
- file-finder → implementation-workflow 経由で /add-feature, /fix-bug, /refactor
- impact-analyzer → implementation-workflow 経由で /add-feature, /fix-bug, /refactor
- code-reviewer → implementation-workflow 経由で全実装系 + /review-changes, /finish-task, /cross-review
- security-checker → implementation-workflow 経由で全実装系（外部入力時）+ /review-changes
- test-runner → implementation-workflow 経由で全実装系 + /refactor 交互実行 + /finish-task
- test-analyzer → implementation-workflow 経由で /add-feature, /fix-bug
- log-analyzer → /fix-bug (Step 2 バグ前処理)
- build-executor → (メインエージェント直呼び)
- cross-reviewer → /cross-review (Phase 5 完了により使用可能)

### Skill → Command 参照（/setup-commands 完了）
- implementation-workflow → /add-feature, /fix-bug, /refactor（共通骨格の単一真実源）
- codex-review → /cross-review (cross-reviewer 経由)

### Hook → Command 参照
- SessionStart Hook → 全コマンドのセッション開始時に動作
- UserPromptSubmit Hook (Preflight 層) → 全ターンで動作。編集を伴わないターン（調査・質問・計画）でもプロジェクト状態を可視化
- PreToolUse Hook (Guard 層, Edit|Write|MultiEdit) → /add-feature, /fix-bug, /refactor の実装ステップで動作。パス時は [guard] PASS で可視化
- PostToolUse Hook (Report 層, Edit|Write|MultiEdit) → 実装系コマンドで動作、cargo fmt 変更時のみ [fmt] applied
- Stop Hook (Report 層) → 全コマンドのターン終了時に動作、clippy/tsc 問題時のみ [stop] WARN
- PreToolUse Hook (Codex 層, Bash) → /cross-review および手動 codex exec 呼び出し時に予算 / 秘匿チェック
- Stop Hook (Codex 層) → 全コマンドのターン終了時に当日 codex token 使用量を記録

### 公式 Skill リスト (anthropics/skills 経由)
- claude-api (Apache 2.0, 外部 LLM 送信許可)
- example-skills: algorithmic-art, brand-guidelines, canvas-design, doc-coauthoring, frontend-design, internal-comms, mcp-builder, skill-creator, slack-gif-creator, theme-factory, web-artifacts-builder, webapp-testing (Apache 2.0, 外部 LLM 送信許可)
- document-skills (pdf/docx/xlsx/pptx): **未導入** (Proprietary / GSE では不要)

---

## 付録: 前回構築（v1 / 旧 Phase 0–7 体系）の記録（履歴保存）

> 2026-06-16 の v2 上書き再構築により、以下は履歴として保存。新体系では Phase 番号が再割当て（marketplace=Phase2, codex-bridge=Phase5 が新規挿入）されている点に注意。

- 初回構築: 2026-04-09
- 旧再構築: 2026-04-14〜04-15（macOS 対応反映・Hooks 強化・`/implement` を3分割）
- 旧体系の到達点: 旧 Phase 7 `/verify-setup` まで完了（HEALTHY 判定）
- 旧体系で構築済み: docs 5点 / CLAUDE.md / Skill 11個 / agent 9個 / command 8個 / hook 6個
- アドホックに存在していた Codex 化: `AGENTS.md`（旧スタイル）・`.codex/agents/*.toml`・`.codex/hooks/*.sh`（`.claude` のコピー）。新 Phase 5 で正式版に作り直す。
