# 次セッション開始プロンプト (そのまま貼り付け)

> `feedback_handoff_prompt_in_steering` 方針に従い、次タスクの開始プロンプトを CLAUDE.md 制約込みで固定。
> **2026-06-19 のシステム全体トリアージで訂正**: 当初「データ収集 ① 参加者ID」を next としたが、
> 現ブランチ `feature/correction-after-pause-fp-split` が「完成済み・未マージ」で宙ぶらりんと判明。
> 規律上、新トラックを開く前にこのブランチを締めるのが厳密な next。
> cue/ランダムプローブは競合せず (核実装完了 or D-14 で意図的延期)。

---

## 次セッションの一手目: 現ブランチを締める (===A===)、その後 ①(===B===)

===A===

タスク: 現ブランチ `feature/correction-after-pause-fp-split` を finish-task → PR → main マージで締める。

### 状態 (2026-06-19 トリアージ済み)
- `.steering/20260618-correction-after-pause-fp-split/tasklist.md` は 32/32 完了。実装/テスト/レビュー済み。
- 2 コミット先行: `1ce1d6f` (--nudge-diag 診断)、`1970fee` (--corr-floor counterfactual)。**両者 production 不変**
  (`InterventionThresholds` の floor 既定 `None`、veto 発火せず、snapshot byte-equal、新フィールドは `#[serde(skip)]`)。
- 残: finish-task 手続き (tasklist 最終化・PR・マージ) と、作業ツリーの未コミット雑務の整理。

### 手順 (CLAUDE.md 準拠)
1. `git status` / `git diff` で作業ツリーを確認。本ブランチのスコープ外の変更
   (`.codex/budget.json`、今日追加の `docs/*.md` 抽出、`.steering/20260619-*` 設計記録、
   `p000_sweep.json` 等) を**論理単位で分けてコミット**するか restore する。混ぜない。
2. `cargo test --workspace` 緑 / `gse-replay --snapshot` byte-equal / `emit_schema` drift なし を確認。
3. `/finish-task` で steering 最終化 → `/cross-review` (jq 不在なら Claude 単独へ縮退し skip 理由明記)
   → PR 作成 → main マージ。
4. マージ後、下記 go/no-go をユーザーに提示。

### マージ後の意思決定 (ユーザー go/no-go — 実装は別タスク)
- **f4≥2.38 floor を production 既定に採用するか**。試算: FP 22→13, TP 12 維持, HIR 0.647→0.520, burden −26% (Pareto 最適)。
  留保: n=1(P000)・過学習懸念。採用なら `InterventionThresholds::default()` に `correction_f4_floor: Some(2.38)`、
  policy/HMM version bump、golden 再生成、decisions.md に採用理由 → これは新 `/start-task` タスク。

===B=== (===A=== のマージ完了後に着手する新トラック)

タスク: 参加者 ID を設定可能化 (`src-tauri/src/logger.rs` の `P000` ハードコード解消)。
`.steering/20260619-user-validation-data-collection/decisions.md` D1 の前提、punch list ①。

### スコープ (厳密に限定 — これ以外は実装しない)
- `logger.rs` `default_log_path()` (≈L911-926) の `P000` ハードコード解消。
- `GSE_PARTICIPANT_ID` 環境変数から参加者 ID を受け取る (既存 `GSE_DATASET` env+fallback パターンに倣う):
  設定あり → `$GSE_DATASET/raw/$GSE_PARTICIPANT_ID/`、未設定 → 従来どおり `P000` (P000 挙動不変)。
- ID 形式バリデーション (パストラバーサル/パス注入防止)。不正値 (`../`/空/過長/区切り文字) は拒否。
- スコープ外: 採番プール生成・割り当て運用 (研究者オフライン、アプリは受け取るだけ)、
  anonymize.py / package-session / (a)(b)メトリクス / DuckDB / フォーム。すべて別タスク。

### 必須プロトコル (CLAUDE.md 準拠)
1. `/start-task` 起動 → agent-shared.md リンクハブから logger 関連 docs 先読み。
2. Skill 参照: `data-privacy` (logger.rs 対象) / `rust-standards` / `architecture-rules`。
3. 調査を `file-finder` / `impact-analyzer` に委譲 (`GSE_DATASET`・`default_log_path` 参照箇所と影響範囲)。
4. 実装後 `code-reviewer` + `security-checker` を並列起動 (logger.rs 変更は security-checker 必須、焦点=パストラバーサル)。
5. `/cross-review` (jq 不在なら Claude 単独へ縮退し skip 理由明記)。
6. `cargo test --workspace` / `gse-replay --snapshot` byte-equal / `emit_schema` drift なし。
7. 制約: `tracing` のみ (`println!`/`eprintln!` 禁止)、`anyhow::Result`、unsafe 不要、`any` 不使用。
8. `/finish-task`。.steering/ 記録を省略しない。

### 受け入れ条件
- `GSE_PARTICIPANT_ID=P003` で `$GSE_DATASET/raw/P003/`、未設定で `P000` (byte-equal 不変)、不正 ID 拒否、
  cargo test green / snapshot byte-equal / schema drift なし。
