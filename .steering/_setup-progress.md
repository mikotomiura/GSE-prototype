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

なし。Loop Engineering 統合 (L0–L7) は 2026-08-01 に全 phase 完了・L7 verify HEALTHY。
日々の運用は `docs/loop-engineering.md` §3 (grill → to-issues → `/clear` → A/B/C 実行 → review → merge) に従う。
月次メンテとして `/verify-loop-setup` を再実行し coverage drift を監視すること。

> L0–L7 は 2026-08-01 完了。詳細は末尾の Loop 統合 phase チェックリストを参照。

> Phase L0 は 2026-08-01 完了（full モード / 実行モード A+B+C / Codex enabled /
> grilling は self-provided へ degrade）。

> 基盤環境 (Phase 0–9) は 2026-06-16 に完了・verify HEALTHY。
> 2026-08-01 に `/bootstrap` を再実行して環境チェックし直し、
> 「基盤は再構築せず Loop 拡張へ進む」をユーザー確定。詳細は末尾の
> 「Loop Engineering 拡張トラック」節を参照。

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

---

## 追補: 2026-08-01 環境ギャップ監査（`/bootstrap` 再実行）

`/bootstrap` を再実行して環境チェックし直した。基盤 Phase 0–9 は 2026-06-16 完了・verify HEALTHY
のため **再構築せず、不足箇所のみ追記モードで補修**することをユーザーが確定。

### 監査で判明した状態（2026-06-16 以降のドリフト）

| 領域 | 2026-06-16 時点 | 2026-08-01 実測 | 判定 |
|---|---|---|---|
| Skill | 自前 13 + Codex 3 | **19** (citation-ssot / literature-card / reproducibility-discipline / empirical-prompt-tuning が後日追加) | 進捗記録・CLAUDE.md 未反映だった |
| Command | 8 + `/cross-review` | 10 (`/implement` 廃止版が残存) | `/literature-review` が**未実装**だった |
| Agent | 10 | 10 | 一致 |
| Hook | 8 | 9 (token-report-stop.sh) | 実体先行 |
| docs | 5 + external-skills | **20** + `adr/` 8 + `architecture/` 3 + `literature/` 8 | リンクハブ未反映だった |
| Research トラック | 進捗記録に **Phase R1 の行が無い** | research-positioning / references / experiment-tracking / literature/_index / experiments/ は**すべて実在** | 後付け構築（Post-Phase1 Epic1・PR #71–73）で成立済み。記録のみ欠落 |

### Phase R1 の遡及記録

- [x] **Phase R1: /setup-research-framing** — 研究トラック土台
  - 状態: enabled（**コマンド経由ではなく Post-Phase1 Epic1 で実質構築**）
  - 完了日時: 2026-07-25 前後（PR #71 / #72 / #73 で main 済み）
  - 実在ファイル: `docs/research-positioning.md` / `docs/references.md`（P 名前空間 28 + V 名前空間）/
    `docs/experiment-tracking.md` / `docs/literature/_index.md` + カード 7 本 / `experiments/`
  - 追加で構築されていたもの: `docs/adr/` (ADR-001〜007) / `docs/architecture/` (v2 再設計)

### 2026-08-01 に実施した補修（サーヴェイ関連＋発見性）

1. **`/literature-review` を新規実装** (`.claude/commands/literature-review.md`)
   — 3 箇所から参照されながら存在しなかった（research-positioning.md §3 / literature/_index.md /
   literature-card SKILL.md）。過去 4 ラウンドの実運用手順（RQ の下位問い分解 → 多角探索 →
   claim 抽出 → **敵対的 3 票検証・対称フィルタ・0-3 否決** → エビデンス温度
   (`確定` / `PLAUSIBLE BUT UNPROVEN` / `判定不能`) → カード → references append-only →
   _index 追記 → positioning 還元）を暗黙知からコマンドへ固定した。
2. **CLAUDE.md** — Skill 表に「研究トラック Skill」節を追加（citation-ssot / literature-card /
   reproducibility-discipline / empirical-prompt-tuning）+ implementation-workflow 行を追加。
   コマンド一覧に `/cross-review` と `/literature-review`、agent 一覧に `cross-reviewer` を追加。
3. **docs/agent-shared.md** — リンクハブに references.md / literature/_index.md /
   experiment-tracking.md / adr/README.md / architecture/gse-v2-overview.md を追加。
4. **dangling 参照の解消** — 「Phase 7 で追加される」表記を実在コマンドの記述へ更新
   (literature-card SKILL.md / literature/_index.md / research-positioning.md)、
   citation-ssot SKILL.md の関連節に `/literature-review` を追加。

5. **`/implement` の削除**（ユーザー確定 2026-08-01）— 2026-04 に 3 分割され廃止済みの
   14 行スタブ。`git rm .claude/commands/implement.md` で削除。併せて `finish-task.md` の
   description 行 7（「/implement の完了後に必ず実行する」＝ Phase 1 で follow-up として
   据え置かれていた最後の残存参照）を `/add-feature, /fix-bug, /refactor` へ修正。
   → **コマンドは 10 本**（実装 9 + 研究 1）、`/implement` 参照はリポジトリ全体でゼロ。

### 未処理（要ユーザー判断）
- `docs/external-skills.md` の plugin 表は 2026-06-16 時点のもの。組み込み系
  (dataviz / artifact-design 等) は未記載だが、送信可否ルール上の影響はない。

<!-- loop:begin -->
## Loop Engineering 統合

- 状態: bootstrapped
- 統合モード: **full**
  - 根拠: `.claude/` 存在 ✓ / `.steering/_setup-progress.md` 存在 ✓ / `docs/agent-shared.md` 存在 ✓
    （3 条件すべて充足。既存の thin-command / verify 慣習に乗せて統合する）
- 開始日: 2026-08-01
- 実行モード (L5 で確定): **A+B+C**（ユーザー確定 2026-08-01・既定どおり全採用）
  - C を入れるため A も必須（C は `loop-issue` / `loop-spawn.sh` に依存）
- CLAUDE.md loop 節: **appended** (2026-08-01 / L1)
  - L0 時点の CLAUDE.md: **あり (128 行)** — 上限 150 に対し**残枠 22 行**。L1 の節 (≤20 行) は
    収まるが余裕がないため、L1 は追記後に行数を再測定すること
  - 追記後の実測: **148 行** (上限 150 以内・残枠 2 行)。以降 CLAUDE.md へ追記する phase は
    **基盤側 (docs/agent-shared.md 等) への退避を先に検討**すること
- Codex ゲート (L6): **enabled**（codex-cli 0.142.5 / 既存 `.codex/config.toml`・`budget.json`・
  `scripts/secrets-filter.sh`・`run-codex-review.sh` を再利用。wrapper を複製しない）
- grilling (L2): **self-provided**（Matt Pocock 外部 skill 未導入。installed_plugins =
  rust-analyzer-lsp / example-skills / claude-api のみ → 自前 grilling / issue-slicing skill に degrade）
- PR 連携: **gh-enabled**（gh 2.90.0）
- 環境前提: claude 2.1.220（`/goal` 必須の 2.1.139 以上 ✓）/ git repo ✓

> L0 時点で Loop 成果物は**皆無**（`docs/loop-engineering.md` / `.claude/commands/loop-issue.md` /
> `loop-status.md` / `.claude/agents/loop-watchdog.md` / `scripts/loop-guard.sh` / `loop-spawn.sh` /
> `loop-run.sh` すべて不在）。L0〜L7 のコマンドファイルは
> `.claude/commands/commands_setup_research_inloop/` に配置済み。

> ⚠ **モードC の 3 条件**（README §2.9）は L5 までに実測すること。GSE は `cargo test --workspace` と
> `gse-replay --snapshot` という機械的 verify を既に持つため成立しやすいが、
> ①events の writer を `loop-run.sh` 一元にする ②AC の検証コマンドが verify に載る
> ③verify がベースラインで緑 ——のどれかが崩れると「客観に見えて無意味な緑/赤」を量産する。

### Loop 統合 phase チェックリスト
- [x] L0 /loop-bootstrap — 環境検出・モード判定（完了: 2026-08-01）
- [x] L1 /setup-loop-docs — docs/loop-engineering.md ＋ steering テンプレ ＋ CLAUDE.md ポインタ節
      (完了: 2026-08-01 / 追加成果物 `.steering/_template/loop-config.README.md` = JSON に書けない
       README §2.3 の ⚠ 集 ＋ GSE 用 verify 置換の申し送り。coverage-map 登録は L7 に defer)
- [x] L2 /setup-loop-grilling — grilling/issue-slicing(Opus) 自前版・start-task grill 化
      (完了: 2026-08-01 / grilling engine 判定 = self-provided。証拠: `.claude/skills/`・
       `~/.claude/skills/` に grilling/to-prd/to-issues 相当の SKILL.md が存在しないことを grep で確認。
       成果物: `.claude/skills/grilling/SKILL.md`・`.claude/skills/issue-slicing/SKILL.md`
       (共に model: Opus をプローズで明記)。`start-task.md` は Step 1「3 問ヒアリング」を
       loop:begin/end マーカで REPLACE (追記のみ・既存 Step 1 本文は保持)。
       issue-slicing は `docs/loop-engineering.md` の 7 基準を逐語埋め込み・自己検査 8 項目・
       Allowed Files 交差表 / DAG 出力義務を保持。docs/external-skills.md への external 登録は
       該当なし (self-provided のため)。)
- [x] L3 /setup-loop-observability — events/board/loop-status (見える化コア)
      (完了: 2026-08-01 / 成果物 `.claude/commands/loop-status.md`。events/board のデータモデルを
       README §2.4/§2.5 準拠の CONTRACT として文書化 (逐語使用・増補なし)。writer 契約
       (append-only・worker が絶対パスで main へ) と single-writer 契約 (`/loop-status` のみが
       board を再描画) を明記。ダミー events (README §2.4 のサンプル 4 行) で smoke test を実施し、
       `.steering/20260801-smoke-observability/` (検証用・確認後 rm -rf 済み) で
       001 ✅ done / 002 🔄 running(test✗1) / 003 ⛔ blocked の board 描画を確認。
       heartbeat の UTC 統一・N分前 算出も動作確認済み。既存ファイルの上書きなし)
- [x] L4 /setup-loop-monitor — loop-watchdog(Haiku) ＋ loop-guard.sh ＋ hook-selfcheck.sh
      (完了: 2026-08-01 / 成果物 `.claude/agents/loop-watchdog.md`(model: haiku・tools 限定・
       parse常時＋recheck/done時のみ独立再実行・報告8行上限・board非書込)、
       `.claude/hooks/loop-guard.sh`(fingerprint連続/attempt/token_ceiling・fail-safe・
       main-root解決+worktreeブランチ束縛・selfcheck: safeマーカ付き)、
       `.claude/hooks/hook-selfcheck.sh`(SessionStart・settings.json 登録済み全 hook を
       静的検査+safe-smokeで毎セッション検証・常に exit 0)。settings.json への登録は
       jq マージで idempotent/reversible (Stop に loop-guard.sh・SessionStart に
       hook-selfcheck.sh を追加、既存 stop-check.sh/token-report-stop.sh/session-start.sh は保持)。
       ⚠ 実装時に判明した既存慣習との差分: 本リポジトリの hook 登録は
       `bash "$(git rev-parse --show-toplevel ...)/.claude/hooks/x.sh"` というラッパー形式のため、
       README 原文の素朴な `grep -oE '[^[:space:]]+\.sh'` 抽出だと `.)/.claude/hooks/x.sh` という
       壊れたパスになり全 hook が missing 扱いになるバグを実装中に検出。
       `sed -E 's#.*(\.claude/hooks/|\.claude/commands/|scripts/)#\1#'` で正規化して修正済み
       (`hook-selfcheck.sh` 内)。実行確認: `bash .claude/hooks/hook-selfcheck.sh` →
       `[hookcheck] OK: 11 hooks healthy`。`loop-guard.sh` は非 loop worktree で
       `[guard] PASS: not a loop worktree` を返すことを確認 (fail-safe)。)
- [x] L5 /setup-loop-executor — [A] loop-issue ＋ loop-spawn.sh / [B] loop-orchestrate ＋ loop-worker / [C] loop-run.sh
      (完了: 2026-08-01 / 実行モード A+B+C 全導入 (2026-08-01 確定どおり)。
       [A] `.claude/commands/loop-issue.md` (薄い executor・full モードで実装骨格は
       `implementation-workflow` skill に委譲・allowed-tools を GSE の cargo/npm スタックに合わせて
       pytest/mypy/ruff から cargo test/clippy/check・npx tsc・npm run に置換)、
       `scripts/loop-spawn.sh` (base 解決・dirty/stale・`--cleanup`・`--no-exec`、chmod +x)、
       worktree ポリシーは `.claude/skills/git-workflow/SKILL.md` に `<!-- loop:begin/end -->` で
       追記 (GIT_WF_OK=true につき SSOT を skill 側に集約、loop-issue/loop-worker/loop-run.sh は参照のみ)。
       [B] `.claude/agents/loop-worker.md` (model: sonnet・subagent 制約明記・要約のみ返却)、
       `.claude/commands/loop-orchestrate.md` (セッション境界ガード・DAG・既定並列 1・review ゲート Opus)。
       [C] `scripts/loop-run.sh` (script が制御・events は exit code・chmod +x)。CLI フラグ/JSON
       スキーマは `claude --version` = 2.1.220 で本コマンド文中の実測値と一致することを確認し
       (`--help` で `--allowedTools`/`--max-budget-usd`/`--model`/`--output-format`/
       `--permission-mode` の 6 択 `acceptEdits/auto/bypassPermissions/manual/dontAsk/plan`/
       `-p`/`-w` の実在を再確認)、`--max-turns` 等 help 非掲載フラグの挙動 (subtype/usage.cache_*)
       は既存の実測記録を再利用 (同一バージョンにつき live `claude -p` 再実験はコスト対効果が
       無いと判断し省略)。fingerprint 抽出は cargo/npx tsc の診断書式 (`error[..]:`/`panicked at`/
       `file:line:col:`) に対応する正規表現へ調整 (spec 既定は pytest/ruff 向けだったため)。
       `.claude/settings.json` に `permissions.deny` を jq で idempotent 追加
       (`git push`/`gh pr merge`/`git reset --hard`/`git rebase`/`sudo`/`rm -rf`/`chmod -R`)。
       いずれも `bash -n` で構文検証済み。Grill Me 完了・アンチパターン一覧との突合せ済み。)
- [x] L6 /setup-loop-codex — タスク境界 Codex ゲート (TASK-PRE / TASK-POST)
      (完了: 2026-08-01 / bridge 検出済み (codex-cli 0.142.5・既存 codex-consult/codex-review skill・
       run-codex-consult.sh/run-codex-review.sh・.codex/budget.json・secrets-filter.sh・/cross-review
       すべて再利用・複製なし) につき skip せず配線。`docs/loop-engineering.md` に
       `<!-- loop:codex:begin/end -->` で altitude 表 (issue ループ内=script/Haiku・
       タスク境界前後=Codex gpt-5.5、~15x コスト根拠) ＋ TASK-PRE (codex-consult・設問 3 種固定・
       保存先 `.steering/[task]/_codex-preplan.md`・助言扱い明記) を追記。
       `.claude/commands/loop-issue.md` に同マーカで TASK-POST (全 issue 緑 + フル CI 後に 1 回・
       既存 `/cross-review` 参照・secrets-filter 経由のフィルタ済み diff のみ・budget.json 尊重・
       `/cross-review` 不在時は codex-review skill 直呼びに degrade) を追記。両ゲートとも
       read-only・issue ループ内には配線せず。Grill Me 実施 (複製なし/read-only/marker 内/
       advisory 明記/bridge 捏造なしを確認)。既存ファイルの上書きなし (追記のみ)。)
- [x] L7 /verify-loop-setup — 整合性検証・coverage-map 登録
  - 完了日時: 2026-08-01 17:29
  - 検証結果: HEALTHY
  - Codex ゲート(L6): enabled · grilling(L2): self-provided
  - coverage-map drift: なし (procedural-docs-coverage: loop-engineering を本検証で新規登録)
  - 修正が必要な項目: 1 件 (CRITICAL 0 / HIGH 0 / MEDIUM 0 / LOW 1)
    LOW: loop-watchdog.md が呼び出し元 (loop-issue/loop-worker) を名指ししていない (discoverability のみ・機能的破綻なし)
  - レポート: `.steering/_verify-loop-report-20260801.md`

### 構築物の相互参照マップ (Loop 層・各 phase が追記)
| 種別 | 名前 | 参照先 |
|---|---|---|
| skill | grilling | `.claude/skills/grilling/SKILL.md` |
| skill | issue-slicing | `.claude/skills/issue-slicing/SKILL.md` |
| command | start-task (grill 化) | `.claude/commands/start-task.md` (loop:begin/end 節) |
| command | /loop-status | `.claude/commands/loop-status.md` → `_loop-board.md` 再描画 |
| contract | `_loop-events.jsonl` | append-only・worker が絶対パスで main へ (README §2.4) |
| contract | `_loop-board.md` | single-writer・`/loop-status` のみ再描画 (README §2.5) |
| 経路 | grill → to-prd → to-issues | `.steering/[task]/issues/00X.md`
  (テンプレ `.steering/_template/loop-issue.md`) + `.steering/[task]/_issue-plan.md` (DAG・交差表) |
| Agent | loop-watchdog   | events(2.4)←parse/recheck ／ 上段: 意味判断(Haiku) |
| Hook  | loop-guard.sh   | _loop-config.json(budget) → settings.json Stop 登録 ／ 下段: fingerprint/attempt/token |
| Hook  | hook-selfcheck.sh | settings.json SessionStart 登録 ／ 毎セッション全 hook を検証 (静的＋safe smoke) |
| command | `.claude/commands/loop-issue.md` | [A][C] docs/loop-engineering.md / _loop-config.json / loop-watchdog / test-runner |
| script  | `scripts/loop-spawn.sh` | [A][C] git worktree ../wt/[repo]-[id]-[short] / --cleanup / --no-exec |
| policy  | Loop worktree policy | `.claude/skills/git-workflow/SKILL.md` (loop:begin/end 節・SSOT) |
| command | `.claude/commands/loop-orchestrate.md` | [B] issues/*.md の DAG / loop-worker / loop-status / code-reviewer |
| agent   | `.claude/agents/loop-worker.md` (sonnet) | [B] docs/loop-engineering.md / test-runner / loop-watchdog / events_path |
| script  | `scripts/loop-run.sh` | [C] _loop-config.json.headless / loop-spawn.sh --no-exec / claude -p /loop-issue / events_path |
| settings | `.claude/settings.json` permissions.deny | [C] git push/reset --hard/rebase・sudo・rm -rf・chmod -R (allowlist の実質境界) |
| Codex ゲート | TASK-PRE (codex-consult) | docs/loop-engineering.md ＜loop:codex＞ → .steering/[task]/_codex-preplan.md |
| Codex ゲート | TASK-POST (/cross-review) | .claude/commands/loop-issue.md ＜loop:codex＞ → 既存 codex-review + code-reviewer |

### procedural-docs-coverage: loop-engineering
(L7 で登録・doc の実見出しと set-difference で drift 監査する。 L1 は defer 済み)

| doc | 節 | 種別 | カバーする発火経路 (skill/agent/command/hook または docs-only) |
|---|---|---|---|
| loop-engineering | 目的 | docs-only | docs-only |
| loop-engineering | 基本単位 | docs-only | docs-only |
| loop-engineering | 原則 | 手続き | loop-issue + loop-worker + loop-watchdog (/goal 客観検証・トランスクリプト自己申告の打消し) |
| loop-engineering | Done Condition (issue 完了の条件・すべて満たす) | 手続き | loop-watchdog (AC↔test 判定) + loop-run.sh (acceptance 段) |
| loop-engineering | Stop Condition (即時停止し人にエスカレートする条件・いずれか) | 手続き | loop-guard.sh (fingerprint/attempt/token) |
| loop-engineering | Budget 方針 | 手続き | loop-guard.sh + _loop-config.json.budget + loop-run.sh (token_ceiling 積算・cache 込み) |
| loop-engineering | Events 語彙 (events.jsonl の event 値・全 10 種) | 手続き | loop-status (契約) + loop-worker/loop-run.sh (writer) |
| loop-engineering | Board 状態機械 | 手続き | loop-status |
| loop-engineering | モデル割当ポリシー | 手続き | .claude/agents/*.md の model: (L7 Step 2c が突き合わせ) |
| loop-engineering | issue-slicing の基準 (7 条件) | 手続き | issue-slicing skill (Opus) |
| loop-engineering | 実行モードとセッション境界 | 手続き | loop-orchestrate (境界ガード) + loop-spawn.sh / loop-run.sh + CLAUDE.md loop 節 |
| loop-engineering | Codex ゲート (任意・タスク境界のみ) | 手続き | TASK-PRE: codex-consult skill → `.steering/[task]/_codex-preplan.md` / TASK-POST: `.claude/commands/loop-issue.md` ＜loop:codex＞ → `/cross-review` |
| loop-engineering | TASK-PRE: issue 独立性の第二意見 (codex-consult, read-only) | 手続き | codex-consult skill (L6 enabled のため実配線・advisory) |
| loop-engineering | 日常運用との対応 (README §3・再掲のみ・新規手順は作らない) | docs-only | docs-only <!-- coverage-ok: README §3 再掲のみ、新規手順を作らない節 --> |
<!-- loop:end -->
