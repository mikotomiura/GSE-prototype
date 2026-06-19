# 次セッション開始プロンプト — punch list #5: (a)(b) 指標算出

> `feedback_handoff_prompt_in_steering` 方針に従い、CLAUDE.md 制約込みで固定。
> 親設計: `.steering/20260619-user-validation-data-collection/decisions.md` (D7 = (a)(b)(c) 精密定義
> ＋(b) diff量=案A をユーザー承認 2026-06-20)。punch list #5。
> **新規 `/start-task` で着手 (解析・metrics 領域・別 PR)。main から独立ブランチを切る。**

---

## 直前までの状態 (2026-06-20)

- #1 参加者 ID 設定可能化: 完了 (main)。
- #2 ペースト回数記録: **完了**。ブランチ `feature/clipboard-paste-count` (main 基点) commit `25e44a1`。
  NDJSON に `{"type":"paste","t":<ms>}` を 1 ペースト=1 行で記録 (中身は記録しない)。
  - ⚠️ **未 push**・未マージ。実機 (Win/mac) での手動確認と **macOS ビルド確認は未実施**
    (本機 Windows では `hook_macos.rs` が cfg 未コンパイル、CI 不可)。#5 は NDJSON schema に
    対して実装するため capture 検証と並行可能 (schema は test 済みで確定)。
- ⚠️ git 注意: handoff(#2) は「Part 3 (PR #15) main マージ済」とあったが**実際は main は PR #14 止まり**、
  Part 3 (`68b5871`) は `feature/sync-auto-participant-id` 上のみ・未マージ。#5 も **main から**ブランチを切る。

## 解決する問題 (背景)

ユーザー検証 (導入前後比較) のため、提案書定義の (a)(b) を**数値として算出**できるようにする。
現状システムは生データ (paste回数・key打鍵・打鍵タイミング) は持つが、(a)(b) の**指標計算が未実装**。
(c) はアンケート (尺度 [15]) でシステム外、本タスク対象外。

- **(a) AI依存度** = **1 セッションあたりのペースト回数**。導入前後で依存低下を比較。
- **(b) 自力解決率** = **diff量 ÷ 総打鍵数**。自力で試行錯誤して書き進めた割合。
  Mehta et al. (2025) **[11]** の LLM 使用検出 KS メトリクスを「AI コピペか否か」の**客観補助指標**として併用
  (テキスト内容でなく打ち方で AI 支援を検出 → 自力解決の純度証明)。

## スコープ

### 含むもの
- (a) NDJSON の `paste`/`meta`(session境界) 行から **session 単位のペースト回数**を集計。
- (b) **総打鍵数**を NDJSON の `key` 行から算出 (定義は要承認、下記)。
- (b) **diff量** = **案A (成果物由来・content-free)**: コーディング=`git diff --stat` 追加行/文字数、
  文章=完成テキスト文字数/変化量。**保存は数値のみ・中身は保存しない**。NDJSON 外入力として join。
- (b) **Mehta KS 補助指標**を打鍵タイミング (`key` 行の時刻列) から算出 ([11] の手法を確認して特定)。
- 出力: `metrics.json` (agent-shared.md の唯一の共有アーティファクト) に (a)(b) を載せる。

### 含まないもの
- (c) 自己効力感 (アンケート・システム外、D3)。
- #3 anonymize.py / #4 package-session / #6 DuckDB join (ただし本タスクの metrics.json が #6 の入力)。
- features/HMM への (a)(b) 組み込み (本タスクは「指標算出」まで)。
- paste の文字数記録 (案A により不要。中身禁止を維持)。

## 要承認の設計判断 (次セッションで会話で承認を取る)

1. **総打鍵数の定義**: 全 key press / 文字生成キーのみ / press のみ (release 除く) のどれか。
   (b) の分母として何を「打鍵」とみなすか。リピート・修飾キー・backspace の扱いも明確化。
2. **diff量 の供給アーキテクチャ (案A の実装形)**:
   - (i) `gse-replay --metrics` は NDJSON から (a)・総打鍵数・Mehta KS を出し、**diff量 と最終比 (b) は
     別ステップ (解析ハーネス/ラッパー) で成果物から算出して join** する、か
   - (ii) `gse-replay` に diff量 を CLI 引数/サイドカー入力として渡し (b) まで一括算出するか。
   - gse-replay は NDJSON 専用 (成果物を読まない) という現設計との整合を重視。
   - 成果物と session の**紐付け方法** (track 別: vibe-coding=git リポジトリ、文章=テキストファイル) も設計。
3. **Mehta KS 補助指標の具体**: [11] のどの KS 特徴量を使うか。**提案書/技術設計書 PDF の文字化けに注意し
   `docs/` の MD 抽出版で文献 [11] を確認** (`reference_proposal_pdf_md_extracts`: 文献番号は提案書体系で統一)。
4. **出力先**: `--metrics` 拡張 / 新モード (`--ai-metrics` 等) / 別解析スクリプト のどれか。
   既存モードは相互排他フラグ群 (replay.rs)。Replay-as-Truth・schema parity への影響を最小化する形を選ぶ。
5. **/reimagine 適用検討**: (b) の指標設計は複数アプローチがあり最良案が自明でない → プラン段階で
   `/reimagine` を起動し初回案を破棄・再生成して比較することを推奨 (実装着手前)。

## 必須プロトコル (CLAUDE.md 準拠 — この順で)

1. **コマンド選定**: `/start-task` で `.steering/[今日]-ab-metrics-computation/` 作成 → `/add-feature`。
   (上記 5 の判断で /reimagine 適用なら設計承認後に起動)
2. **docs 先読み**: `@docs/agent-shared.md` リンクハブから development-guidelines §3 (Replay-as-Truth)・
   §10 (data repo / metrics.json)・architecture (analysis 層) を先読み。提案書 MD で (a)(b)(c)・文献 [11] 確認。
3. **Skill 参照 (必須)**: `ml-workflow` / `hmm-analysis` (打鍵特徴量・Mehta KS の素性) / `data-privacy`
   (metrics に中身を入れない・diff量は数値のみ) / `rust-standards` / `architecture-rules`
   (analysis 層は OS 非依存、metrics は replay/解析側)。
4. **サブエージェント委譲**: `file-finder`/`impact-analyzer` で `gse-replay --metrics` の現行算出パス
   (`compute_session_metrics` / `collect_user_labels` / `collect_logged_feats` / `SessionMetrics`)・
   `metrics.json` 出力・NDJSON `paste`/`key` 行の読み取り箇所を調査。
5. **実装後 `code-reviewer` + `security-checker` を並列**起動 (焦点 = **diff量・metrics にテキスト内容/
   キーストローク内容が一切混入しないこと**・数値のみであること)。
6. **`/cross-review`**: jq 不在なら Codex 系統 skip → Claude 単独へ縮退し skip 理由を完了報告に明記
   (既知制約: 本機は jq 未導入 = `project_codex_review_needs_jq`)。

## Replay-as-Truth / スキーマ注意

- gse-replay の出力や算出を変えても、**HMM 挙動・`FeatSnapshot` を変えないなら golden は byte-equal のはず**
  (`gse-replay --snapshot` で確認)。(a)(b) は新規集計で feat 経路に触れない設計にする。
- NDJSON schema (`schema_dto.rs`) を**変えないなら** emit_schema / dataset parity は不要。
  metrics.json は schema_dto 管轄外 (別構造) の見込みだが、schema を触る場合は #2 と同じ手順
  (emit_schema 再生成 → `src-tauri/schema/current.json` → gse-dataset コピー → `check_schema_parity.py` 緑)。
- モード系フラグは相互排他 (`--snapshot`/`--metrics`/… )。新モード追加時は排他ルールに従う。

## 検証ゲート

- `cargo test --workspace` 緑 (新規指標の単体テスト含む。合成 fixture で (a)回数・(b)比・KS を検証)。
- `gse-replay --snapshot` byte-equal (feat 経路不変)。
- (a)(b) を含む `metrics.json` が合成 fixture で期待値どおり出る (paste回数・総打鍵数・diff量 join・KS)。
- code-reviewer / security-checker CRITICAL/HIGH なし (特に**中身非混入**)。

## 制約

- `tracing` のみ・`anyhow::Result`・`any` 不使用・`winapi` 禁止。
- `analysis/` は OS 非依存 (OS API 直呼び禁止)。指標算出は replay/解析側に置く。
- **metrics・diff量 にテキスト内容/キーストローク内容を一切入れない** (data-privacy 最優先・数値のみ)。
- 文献引用は**提案書番号で統一** (Mehta=[11], GSE=[15])。PDF 文字化けは `docs/` MD 抽出版で回避。
- `.steering/` 記録を省略しない。`/finish-task` まで完遂。**ブランチは main 基点で別 PR**。

## 受け入れ条件

- (a) session 単位のペースト回数が `metrics.json` に出る (導入前後比較に使える形)。
- (b) `自力解決率 = diff量 ÷ 総打鍵数` が算出される。総打鍵数定義・diff量供給(案A)・Mehta KS 補助が
  設計どおり実装され、会話で承認した形になっている。
- diff量・metrics に中身が一切入らない (security-checker 確認・数値のみ)。
- `cargo test --workspace` green / `gse-replay --snapshot` byte-equal。
- code-reviewer / security-checker CRITICAL/HIGH なし。

---

## 貼り付け用プロンプト (新セッションで /clear 後に投入)

```
.steering/20260619-user-validation-data-collection/handoff-ab-metrics.md に従い、
punch list #5 (ユーザー検証指標 (a) AI依存度 と (b) 自力解決率 の指標算出) を実装してください。

着手前に: /start-task で .steering/[今日]-ab-metrics-computation/ を作成 → /add-feature。
親決定 decisions.md D7 ((a)(b)(c) 精密定義・(b) diff量=案A) と
ml-workflow / hmm-analysis / data-privacy Skill を読む。提案書 MD で (a)(b)(c)・文献[11]を確認。

定義 (提案書真実源):
(a) AI依存度 = 1セッションあたりのペースト回数 (NDJSON の paste 行で集計)、導入前後比較。
(b) 自力解決率 = diff量 ÷ 総打鍵数。diff量は案A=成果物由来 (コーディング=git diff、文章=文字数、
    数値のみ・中身保存禁止)。Mehta et al.(2025)[11] の LLM使用検出 KS メトリクスを AIコピペ判定の
    客観補助指標として併用 (打ち方で検出・内容は見ない)。
(c) は尺度[15]アンケートでシステム外・対象外。

要承認の設計 (会話で承認を取る): ①総打鍵数の定義 ②diff量の供給アーキテクチャ (gse-replay は
NDJSON専用→diff量は別ステップで join するか、サイドカー入力で一括算出するか) と成果物⇔session 紐付け
③Mehta KS の具体メトリクス([11]確認) ④出力先 (--metrics 拡張/新モード/別スクリプト)。
(b)の指標設計は複数案ありうるので、プラン段階で /reimagine を起動して比較することを推奨。

CLAUDE.md 準拠で: /start-task → (/reimagine 検討) → /add-feature → ml-workflow/hmm-analysis/
data-privacy/rust-standards/architecture-rules 参照 → file-finder/impact-analyzer で gse-replay
--metrics 現行算出パスと paste/key 行読み取りを調査 → 実装 → code-reviewer + security-checker 並列
(焦点=metrics/diff量に中身が一切入らない・数値のみ) → /cross-review (jq不在なら Claude単独へ縮退・
skip理由明記) → finish-task。

制約: tracing/anyhow/any禁止/winapi禁止・analysis は OS非依存・metrics と diff量 に
テキスト/キーストローク内容を一切入れない (数値のみ)・文献は提案書番号で統一 (Mehta=[11]/GSE=[15])・
PDF文字化けは docs/ の MD抽出版で回避。Replay-as-Truth: feat経路不変なら --snapshot は byte-equal。
schema(schema_dto)を変える場合のみ emit_schema 再生成→current.json→gse-dataset コピー→parity緑。
ブランチは main 基点で別 PR。

注: #2 ペースト記録は feature/clipboard-paste-count (commit 25e44a1) で実装済みだが未マージ・
未push、実機/macOSビルド検証は未。#5 は NDJSON schema に対して実装するので並行可。
main は PR#14 止まり (Part3 未マージ) なので #5 も main から切る。
```
