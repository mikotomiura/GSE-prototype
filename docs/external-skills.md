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

> ### ⚠️★★★ 2026-09-08 訂正 —— 拡張子フィルタは「不要」ではなく **現に別の物を守っている**
>
> ★ **旧文**: 逐語「`document-skills` (Proprietary) を未導入のため、Phase 5 / Phase 8 での
> 拡張子フィルタ (`.pdf` / `.docx` / `.xlsx` / `.pptx`) は **不要**。」
>
> ⚠️ **これは実装と食い違っていた。**★ `scripts/secrets-filter.sh` は当該フィルタを
> **実装しており**（`PROPRIETARY_EXTS_REGEX`）、⚠️ **守っている対象が旧文の想定と違う** ——
> ★ 実体は **Anthropic の proprietary Skill の出力**ではなく、
> ★★★ **研究者自身の資料**（`docs/mitou_submission/` の未踏提出物 `.pptx` / `.docx`）である。
>
> ★ **2026-09-08 の裁定（研究者判断）**: ⚠️★★★ **`.pptx.md` / `.docx.md`（Markdown 版）も送信禁止に含める。**
> ★ 理由: **拡張子が `.md` なのは `md2pptx.py` の変換の都合にすぎず、中身は資料の本文そのもの**である
> （★ 実測: `.pptx` バイナリを止めても、**Markdown 版から本文 257 行が外へ出ていた**）。
>
> ⚠️ **副作用を承知で入れている**: 未踏提出物に触る diff は **毎回 `rc=2`** になる。
> → ★ そのときは **`--ack-filtered`**（★ 人が `[REDACTED]` の中身を確かめてから通す）で運用する。
> ⚠️★★★ **フィルタを弱めて回避しない**（★ `secrets-filter.sh:64-73` の設計哲学）。
>
> ★ **2026-09-08 追記（案 C）**: ⚠️★★★ **拡張子だけでは足りなかった。**
> ★ `.pptx` を止め `.pptx.md` も止めた後、**`figures/*.svg` が同じ穴のまま**だった
> （★ 中身はデッキ本文そのもの）。→ ★ **図とスライドの置き場をディレクトリで塞ぐ。**
> ⚠️ ただし置き場**全体**ではない —— ★ `README.md` のような普通の文書は**レビュー可能なまま**にする。
> ⚠️ **限界**: ★ 置き場が増えたら `secrets-filter.sh` の `classify()` へ追随が要る。
>
> ★ 記録: `.steering/20260908-secrets-filter-quote-bypass/decisions.md` 判断 2 / 未決 M-1 の裁定。

ただし GSE 固有のプライバシー規約として、NDJSON セッションログ・キーストローク内容を
含むファイルは Codex / 外部 LLM に送信しない (data-privacy Skill 参照)。

### ★★★ 2026-08-16 追加 — 参加者水準の派生統計の扱い (★ 規約の穴を塞ぐ)

⚠️★★★ **これまで条文が存在しなかった。** 2026-08-16 に `docs/literature/_index.md` 全文を
Codex へ送信した際、そこに含まれる **参加者別の回答傾向**
(例:「P012 は 35 件中 34 件『3』」「P010 (n=103) で全特徴量が偶然水準」) が一緒に出た。
★ **既存の規約には違反していない** (禁じていたのは NDJSON 生ログとキーストローク内容のみで、
`scripts/secrets-filter.sh` のパターンも実セッション名は塞ぐが裸の参加者 ID には反応しない)。
⚠️ **しかし人を対象とした研究の個人水準の情報が、可否を規定した条文なしに組織外へ出る経路が
常時開いていた** (security-checker MEDIUM)。

| 種別 | 送信 | 理由 |
|---|---|---|
| NDJSON 生ログ / キーストローク内容 / 実セッション名 `Pnnn_gse_<日付>_<時刻>` | ❌ **禁止** | 既存規約 (data-privacy)。⚠️★★★ **2026-09-13 に射程を明示した** —— ★ **本行が禁ずるのは *GSE 被験者由来* のものである。**⚠️ **第三者の公開研究データ（CC 等）の逐語例は本行の対象外**（★ 実例: **[P360]** ENJA15 の `<Key … IMEtext="…" Type="insert" Value="…" />`。★ CC 公開・**GSE 被験者ではない**ので再識別の増分はゼロ）。→ ★ **それらは下段「設計文書・文献カード・引用 ✅ 可」に載る。**⚠️ **`secrets-filter.sh` は反応しないので、この区別も人が付ける**（★ 下の「運用」と同じ） |
| ★ **未踏提出物などの資料** `.pdf` / `.docx` / `.xlsx` / `.pptx` ＋ ⚠️★★★ **そのMarkdown版**（`.pdf.md` / `.docx.md` / `.xlsx.md` / `.pptx.md`） | ❌ **禁止** | ★ 2026-09-08 追加（研究者判断）。⚠️ `secrets-filter.sh` が hunk ごと除去する（実装は `\.(pdf|docx|xlsx|pptx)(\.md)?` で 4 拡張子とも Markdown 版を含めて塞ぐ） |
| ★★★ **図・スライド・提出文書の置き場**（`docs/mitou_submission/figures/` / `docs/mitou_submission/mitou_pptx/` / `docs/mitou_submission/mitou_docs/` 配下・**拡張子を問わない**） | ❌ **禁止** | ★ 2026-09-08 追加（研究者裁定・案 C）。⚠️★★★ **拡張子の追い掛けっこは終わらない**ため置き場で塞ぐ（★ 実測: `figures/*.svg` の `<text>` にデッキ本文がそのまま入っていた）。⚠️ **`docs/mitou_submission/` を丸ごとにはしない** —— ★ `README.md` はレビュー可能なままにする。★ 2026-09-09 訂正: `mitou_docs/`（提案書/技術設計書/検証レポートの `.docx`/`.docx.md` の置き場）が漏れていた (code-reviewer 指摘・HIGH) |
| **参加者 ID を伴う集計統計** (`P012 の C-index` / 窓数 / CV 等) | ⚠️ **原則回避。必要なら ID を落として送る** | ★ ID→被験者の対応表は研究者が別途管理しており (`development-guidelines.md §10.2`)、**対応表を持つ者にとっては n=5 で再識別可能**。★ 統計的な議論に参加者 ID は通常不要 |
| 参加者 ID を伴わないコホート集計 (中央値・分布・効果量) | ✅ 可 | 個人に紐づかない |
| 設計文書・文献カード・引用 | ✅ 可 | 公開文献の要約 |

★ **運用**: Codex へ送る前に、入力に `P0\d\d` 形式の ID と個人別の値が同居していないか目視する。
⚠️ **`secrets-filter.sh` には PID パターンを足していない** —— 架空名や `_00000000_` 型を
素通りさせる設計思想 (S5C-D8) を壊さないため。★ **人の判断でゲートする。**
