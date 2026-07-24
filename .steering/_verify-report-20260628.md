# Claude Code 環境構築 検証レポート

検証日時: 2026-06-28 03:21
モード: 月次メンテナンス再実行 (前回 2026-06-16 HEALTHY)

## 総合判定

✅ **HEALTHY** (CRITICAL=0 / HIGH=0 / MEDIUM=1 / LOW=2)

構成: Claude + Codex 連携 (Phase 5 完了) / 公式 Skill 14 個 (Phase 2 完了) / 研究トラック (Phase R1) SKIPPED

## 各フェーズの状態

### Phase 1: docs ✅
- 5 ファイル (functional-design / architecture / repository-structure / development-guidelines / glossary) 全存在
- external-skills.md 存在

### Phase 2: Marketplace ✅
- docs/external-skills.md 存在
- 導入: claude-api + example-skills (計 14 Skill, 全 Apache 2.0)
- document-skills (Proprietary): 意図的に未導入 → proprietary 拡張子フィルタ不要
- ライセンス同意ログ: ✅ (_setup-progress.md に記録)

### Phase 3: CLAUDE.md / AGENTS.md / agent-shared.md ✅
- CLAUDE.md: 117 行 (上限 150) ✅
- AGENTS.md: 67 行 (上限 80) ✅
- agent-shared.md: 128 行 (上限 200) ✅
- `@docs/agent-shared.md` 参照: CLAUDE=4 / AGENTS=3 ✅
- `@docs/external-skills.md` 参照 (agent-shared): 1 ✅
- 責務分離 (Step 2.5): Codex keywords in CLAUDE=1 (≤5) / Claude keywords in AGENTS=2 (≤3) ✅
  - 共通キーワード WARN 3 件は全て false positive (CLAUDE.md 行18 のポインタ参照 / AGENTS.md の正当なクロス参照)

### Phase 4: Skills ✅
- 自前 Skill 13 + Codex Skill 3 = 16 (全て name/description/allowed-tools + 補足ファイル完備)
- 動的 Skill: project-status (! shell preprocessing) ✅
- empirical-prompt-tuning 存在 ✅
- deferred-evaluations.md: 未処理項目 0 ✅
- 公式 Skill 重複回避: ✅ (webapp-testing / mcp-builder / skill-creator / claude-api 等は自前不作成)
- **Step 4.5 (procedural-docs-coverage 監査)**: ⚠️ マップ未生成 → 下記 MEDIUM 参照

### Phase 5: Codex Bridge ✅
- .codex/config.toml / budget.json 存在・構造正常 ✅
- scripts/secrets-filter.sh / run-codex-consult.sh / run-codex-review.sh 存在 ✅
- codex-consult / codex-review / codex-rescue Skill 存在 ✅
- 疎通テスト (Step 2.7): ✅ **PASS** (exit 0, 応答「Hello。こんにちは」, gpt-5.5, 17,935 tokens)
  - 注: 出力中の Notion-MCP auth / rollout ERROR 行は codex 応答とは無関係なテレメトリノイズ

### Phase 6: Agents ✅
- 基本 9 エージェント全存在 + cross-reviewer (Phase 5)
- モデル割当: build-executor/test-runner=haiku, code-reviewer/security-checker=opus,
  cross-reviewer/file-finder/dependency-checker/impact-analyzer/test-analyzer/log-analyzer=sonnet ✅

### Phase 7: Commands ✅
- 基本 8 コマンド全存在 + /cross-review (Phase 5)
- implement.md: 廃止 tombstone として正しく残存 (3 分割コマンドへ誘導) ✅

### Phase 8: Hooks ✅
- 5 hook 種別 (SessionStart / UserPromptSubmit / PreToolUse / PostToolUse / Stop) 全登録 ✅
- 全 hook `"type": "command"` 統一 / settings.json JSON 構文正常 ✅
- Codex 層: codex-budget-guard / secrets-pre-filter (早期 exit 実装) / token-report-stop (冪等性キー) 登録済 ✅
- Stop hook に token-report-stop.sh 追加済 ✅
- 全 hook が `bash "..."` 形式で呼ばれる → 実行ビット不要だが下記 LOW 参照

## 相互参照の整合性

- Skill → Agent / Agent → Command / Hook → Command: ✅ (相互参照マップと一致)
- AGENTS↔CLAUDE 同期: ✅ (閾値内)
- ライセンス整合 (external-skills.md ↔ secrets-filter ↔ secrets-pre-filter): ✅
  - document-skills 未導入のため期待拡張子セット = 空。両フィルタの proprietary 拡張子 0 件は正しい
  - **前回 M-1 (secrets-pre-filter.sh の不要拡張子フィルタ) は解消済み** ✅
- Codex 疎通: ✅ PASS

## 修正が必要な項目

### CRITICAL
- なし

### HIGH
- なし

### MEDIUM
- **M-1: procedural-docs-coverage マップ未生成** — Phase 4 (Step 2.5) が生成するはずの
  docs↔skill カバレッジ・マップが `.steering/_setup-progress.md` に存在しない。
  このため Step 4.5 の「手続き的 docs 節 ↔ 発火経路」ドリフト検出監査が設計通り走らない。
  現状 docs/skill は健全だが、将来 development-guidelines.md / repository-structure.md に
  手続き的な節が追加された際に死蔵 (発火経路なし) を自動検出できない。
  → 推奨: 次回 docs 改訂時に `/setup-skills` 相当でマップを生成、または手動で
  `### procedural-docs-coverage` セクションを進捗ファイルに追記。

### LOW
- **L-1: 一部 hook に実行ビット (+x) なし** — session-start / stop-check / codex-budget-guard /
  secrets-pre-filter / token-report-stop の 5 本が `-rw-r--r--`。
  ただし settings.json では全 hook が `bash "<path>"` 形式で起動されるため **機能影響なし**
  (bash がファイルを直接解釈)。気になる場合のみ `chmod +x` で統一。
- **L-2: codex バージョン記録のドリフト** — _setup-progress.md は 0.128.0 と記録、実機は 0.125.0。
  疎通は PASS のため実害なし。記録更新は任意。

## 推奨される次のアクション

1. (任意) M-1: 次回 docs 改訂時に procedural-docs-coverage マップを補完する。
2. (任意) L-1: 気になる場合 `chmod +x .claude/hooks/*.sh` で実行ビットを統一。
3. budget.json は 2026-06-27 分の記録 (31,758 tokens / 1 invocation)。日次予算 200K に対し余裕あり。
4. 月次メンテとして次回も `/verify-setup` を再実行。
