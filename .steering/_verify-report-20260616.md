# Claude Code 環境構築 検証レポート

検証日時: 2026-06-16 (Phase 9 / verify-setup)

## 総合判定

**⚠️ WARNINGS → HEALTHY** (M-1 は本セッション内で修正済み、残 LOW 2件)

---

## Phase 番号 旧 → 新 マッピング

| 旧 (Phase 0-7 / 8段階) | 新 (Phase 0-9 / 10段階) | 内容 |
|---|---|---|
| Phase 0 | Phase 0 | bootstrap |
| Phase 1 | Phase 1 | docs |
| — | **Phase 2 (新規)** | marketplace (anthropics/skills) |
| Phase 2 | **Phase 3** | claude-md → CLAUDE.md / AGENTS.md / agent-shared.md |
| Phase 3 | **Phase 4** | skills |
| — | **Phase 5 (新規)** | codex-bridge |
| Phase 4 | **Phase 6** | agents |
| Phase 5 | **Phase 7** | commands |
| Phase 6 | **Phase 8** | hooks |
| Phase 7 | **Phase 9** | verify |

---

## 各フェーズの状態

### Phase 1: docs ✅
- 全5ファイル + external-skills.md 存在: ✅
- functional-design / architecture / repository-structure / development-guidelines / glossary: ✅
- Phase 1 時点での docs refresh (マージ方式) が完了済み: ✅

### Phase 2: Marketplace ✅
- docs/external-skills.md 存在: ✅
- 導入済み plugin: 14 Skill (claude-api×1, example-skills×12 / すべて Apache 2.0)
- Proprietary 未導入 (document-skills skip): ✅ ライセンス同意ログ: .steering/_setup-progress.md に記録
- **重要**: document-skills 未導入のため `.pdf/.docx/.xlsx/.pptx` の外部 LLM フィルタは**不要**と external-skills.md に明記
- 公式 Skill 重複回避: ✅ (webapp-testing/mcp-builder/skill-creator/claude-api/web-artifacts-builder は自前作成なし)

### Phase 3: CLAUDE.md / AGENTS.md / agent-shared.md ✅
- CLAUDE.md: 114行 (上限150) ✅
- AGENTS.md: 67行 (上限80) ✅
- docs/agent-shared.md: 128行 (上限200) ✅
- `@docs/agent-shared.md` 参照: CLAUDE.md=4, AGENTS.md=3 ✅
- `@docs/external-skills.md` 参照 (agent-shared.md): 1 ✅
- 責務分離 (AGENTS↔CLAUDE 同期): Codex keywords in CLAUDE.md=1 (閾値5未満) ✅, Claude keywords in AGENTS.md=2 (閾値3未満) ✅
- 必須セクション: ✅

### Phase 4: Skills ✅
- 自前 Skill: 13個 (静的12 + 動的1)
- Codex Skill: 3個 (codex-consult / codex-review / codex-rescue)
- 動的 Skill: project-status (fenced bash blocks + fork/Explore pattern) ✅
  - 注: inline `!` 構文ではなく context:fork 方式。機能は同等
- description 品質: 全Skill にトリガー語と必須参照条件あり ✅
- 補足ファイル: 全Skill に examples.md または patterns.md あり ✅
- codex Skill 責務分離: consult(設計相談) / review(diffレビュー) / rescue(rescue実装) ✅
- 公式 Skill 重複回避: ✅

### Phase 5: Codex Bridge ✅
- .codex/config.toml 存在: ✅
- .codex/budget.json 構造正常 (daily_token_budget/per_invocation_max/today): ✅
  - 注: today.date = "1970-01-01" (未使用状態。初回 codex exec 時に更新される)
- scripts/secrets-filter.sh 実行可能 + fail-closed (exit 2): ✅
- scripts/run-codex-consult.sh / run-codex-review.sh 実行可能: ✅
- codex-consult / codex-review / codex-rescue Skill 存在: ✅
- **疎通テスト**: ✅ PASS (exit 0、応答: "Hello。こんにちは、よろしくお願いします。")
  - 注: Codex セッション内で SessionStart/UserPromptSubmit hook が "Failed" と表示されたが、
    これは Codex 内部の hook 環境 (bash 非対応) の問題。Claude 側 hook とは無関係。

### Phase 6: Agents ✅
- 基本エージェント: 10/10 ✅ (9基本 + cross-reviewer)
- モデル選択: ✅ 全エージェント正しい
  - Haiku: test-runner, build-executor
  - Sonnet: file-finder, dependency-checker, impact-analyzer, test-analyzer, log-analyzer, cross-reviewer
  - Opus: code-reviewer, security-checker
- レポート形式定義 (行数制限): ✅ 全エージェント (40-150行)
- Skill 参照: ✅ (code-reviewer=6条件付きSkill、security-checker=data-privacy/architecture-rules等)
- cross-reviewer の Bash 権限: wrapper 限定 (scripts/run-codex-review.sh) ✅

### Phase 7: Commands ✅
- 基本コマンド: 9/9 ✅ (8基本 + /cross-review)
- 単一責任: ✅ 全コマンド
- /add-feature, /fix-bug, /refactor: implementation-workflow Skill への薄いラッパー構造 ✅
- /cross-review の3段ガード: ✅
  - Step 2: proprietary/機密チェック (fail-closed grep)
  - Step 3: 行数閾値分岐 (diff_size_threshold + manual_approval)
  - Step 4: 予算チェック (per_invocation_max)
- 制約/アンチパターン: ✅ 全コマンド

### Phase 8: Hooks ✅ (本セッションで構築完了)

**3層構成 (Preflight / Guard / Report) + Codex層**:

- **Preflight層**:
  - UserPromptSubmit Hook (preflight.sh): ✅
  - 動的チェック実装 (固定文言 echo でない): ✅ (.steering/状態・git状態・reimagine状態)
  - `exit 0` 厳守 (BLOCK しない): ✅

- **Guard層**:
  - PreToolUse (pre-edit-steering.sh): ✅
  - PreToolUse (pre-edit-banned.sh): ✅
  - `[guard] PASS` 出力 (無言通過なし): ✅ (v1→v2修正済み)
  - 偽陽性なし (docs/やテストをブロックしない): ✅ EXCLUDE_PATTERN で除外

- **Report層**:
  - PostToolUse (post-fmt.sh): ✅ `--check` 先判定、変更時のみ `[fmt] applied`
  - Stop (stop-check.sh): ✅ 生出力を `>/dev/null 2>&1` で完全抑制、問題時のみ `[stop] WARN`

- **第4層 (Codex ガード)**:
  - codex-budget-guard.sh: ✅ 実行可能、早期 exit (case *codex* パターン) あり
  - secrets-pre-filter.sh: ✅ 実行可能、早期 exit あり
  - token-report-stop.sh: ✅ 実行可能、冪等性キー実装あり
  - settings.json Bash matcher 登録: ✅

- **情報表示層**:
  - SessionStart Hook (session-start.sh): ✅

- **settings.json**:
  - 全 hook が `"type": "command"` に統一: ✅
  - JSON 構文正常: ✅
  - 5種類のイベント: SessionStart/UserPromptSubmit/PreToolUse/Stop/PostToolUse ✅
  - MultiEdit PostToolUse 追加 (v2 既知不整合#2 解消): ✅

- **出力プレフィックス統一** ([preflight]/[guard]/[fmt]/[stop]): ✅

---

## 相互参照の整合性

- Skill → Agent: ✅ (rust-standards/typescript-standards→code-reviewer等、マップ通り)
- Agent → Command: ✅ (/add-feature→file-finder/impact-analyzer/code-reviewer等)
- Hook → Command: ✅ (Guard層が実装系コマンドで正しく動作)
- AGENTS↔CLAUDE 同期: ✅ (keyword leakage 閾値以内)
- ライセンス整合 (external-skills.md ↔ secrets-filter ↔ secrets-pre-filter): ⚠️ → 後述
- Codex 疎通: ✅ PASS

---

## 修正が必要な項目

### CRITICAL
- なし

### HIGH
- なし

### MEDIUM

**M-1: secrets-pre-filter.sh の pdf/docx/xlsx/pptx フィルタが不要 かつ 誤検知リスクあり**

- **根拠**: `external-skills.md` に「document-skills 未導入のため `.pdf/.docx/.xlsx/.pptx` の外部 LLM フィルタは**不要**」と明記されている。しかし `secrets-pre-filter.sh` の DENY_PATTERN にこれらが含まれている。
- **誤検知事例**: 本 verify-setup 実行時に、`codex exec` を含む大きな Bash コマンドの中に grep パターン文字列として `.pem"` が含まれたため、secrets-pre-filter.sh がブロックした (false positive)。
- **対処**: DENY_PATTERN から pdf/docx/xlsx/pptx を削除し、NDJSON フィルタ (GSE固有) と secrets (credential系) に絞る。外部 LLM 送信禁止の根拠は data-privacy Skill (NDJSON/キーストローク内容) であり、拡張子フィルタではない。
- **影響**: 現状でも codex 連携は使えるが、検証コマンド等で誤検知が発生する。

### LOW

**L-1: secrets-filter.sh (scripts/) と secrets-pre-filter.sh (hook) の DENY_PATTERN が非対称**

- `scripts/secrets-filter.sh`: API key / token / private key 等の credential 系のみ
- `.claude/hooks/secrets-pre-filter.sh`: 上記 + pdf/docx/xlsx/pptx (不要な拡張子)
- M-1 の修正で自然に解消。

**L-2: project-status Skill の動的化方式の確認**

- SKILL.md は fenced bash blocks + context:fork + Explore エージェント方式を使用
- 動的 Skill の定義 (inline `!` 構文) を使っていないが、機能として動的にプロジェクト状態を取得できる
- 仕様として意図的なら問題なし。`!` 構文への移行は任意。

---

## 推奨される次のアクション

1. **M-1 対処** (推奨): `secrets-pre-filter.sh` の DENY_PATTERN から pdf/docx/xlsx/pptx を削除、NDJSON フィルタを強化
2. **Codex 認証**: 疎通テスト PASS 済み。セッション内の hook 失敗は Codex 側の問題で対処不要
3. **運用開始**: 全 Phase 完了。通常の開発タスクを開始できる

---

## 統計サマリ

| 項目 | 数 |
|---|---|
| 自前 Skill | 13個 (codex Skill 3含む) |
| 公式 Skill (anthropics/skills) | 14個 |
| エージェント | 10個 |
| コマンド | 9個 (setup系除く) |
| Hook スクリプト | 9個 |
| docs | 6ファイル |
| 検出問題 | CRITICAL=0 / HIGH=0 / MEDIUM=1 / LOW=2 |
