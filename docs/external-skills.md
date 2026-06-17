# 外部 (公式) Skill 一覧

このファイルは anthropics/skills marketplace から導入された公式 Skill のメタデータを記録する。
Phase 3 (`/setup-claude-md`) と Phase 4 (`/setup-skills`)、Phase 5 (`/setup-codex-bridge`)、
Phase 8 (`/setup-hooks`) はこのファイルを動的に読んで、CLAUDE.md / AGENTS.md への反映、
自前 Skill との重複回避、Codex への入力フィルタ、外部 LLM への送信ガードを実施する。

## 導入済み plugin

| plugin | Skill | License | 外部 LLM (Codex 等) への送信 | 主用途 |
|---|---|---|---|---|
| claude-api | claude-api | Apache 2.0 | 許可 | Anthropic SDK / Claude API 実装ガイド |
| example-skills | algorithmic-art | Apache 2.0 | 許可 | アルゴリズムアート生成 |
| example-skills | brand-guidelines | Apache 2.0 | 許可 | ブランドガイドライン適用 |
| example-skills | canvas-design | Apache 2.0 | 許可 | Canvas UI デザイン |
| example-skills | doc-coauthoring | Apache 2.0 | 許可 | 文書共同執筆 |
| example-skills | frontend-design | Apache 2.0 | 許可 | フロントエンドデザイン規約 |
| example-skills | internal-comms | Apache 2.0 | 許可 | 社内コミュニケーション文書 |
| example-skills | mcp-builder | Apache 2.0 | 許可 | MCP server 開発補助 |
| example-skills | skill-creator | Apache 2.0 | 許可 | Skill 自動生成 (Phase 4 で活用) |
| example-skills | slack-gif-creator | Apache 2.0 | 許可 | Slack GIF 生成 |
| example-skills | theme-factory | Apache 2.0 | 許可 | テーマ/スタイル統一 |
| example-skills | web-artifacts-builder | Apache 2.0 | 許可 | React Artifact 生成 |
| example-skills | webapp-testing | Apache 2.0 | 許可 | Playwright E2E テスト |

> **document-skills は未導入**: pdf / docx / xlsx / pptx は Proprietary ライセンスかつ GSE では不要のため導入しない。

## 自前 Skill 作成時のガイドライン (Phase 4 で参照)

Phase 4 で自前 Skill を作るときは、上表が既にカバーする領域を **作らない**:

- Skill 自動生成 → `example-skills:skill-creator` を使う
- E2E テスト (web) → `example-skills:webapp-testing` を使う
- React Artifact 生成 → `example-skills:web-artifacts-builder` を使う
- Claude / Anthropic SDK 実装 → `claude-api:claude-api` を参照する
- MCP server 開発 → `example-skills:mcp-builder` を使う

該当する公式 Skill が無い領域 (Rust/HMM の認知状態推定、キーストローク hook 規約、
介入ロジック設計、GSE 固有の ML ワークフロー等) のみ自前で作る。

## Codex / 外部 LLM 連携時のルール (Phase 5 / 8 で参照)

全ての導入済み Skill は Apache 2.0 ライセンスであり、外部 LLM への送信制限はない。
`document-skills` (Proprietary) を未導入のため、Phase 5 / Phase 8 での
拡張子フィルタ (`.pdf` / `.docx` / `.xlsx` / `.pptx`) は **不要**。

ただし GSE 固有のプライバシー規約として、NDJSON セッションログ・キーストローク内容を
含むファイルは Codex / 外部 LLM に送信しない (data-privacy Skill 参照)。
