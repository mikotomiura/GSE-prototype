# Phase 1 Task 3/3: Dashboard Counter Widget + 実機手動検証

> **用語注記**: 本タスクの「検証」は `docs/development-guidelines.md` §3 の
> **実機手動検証 (manual verification)** に該当する。自動 E2E（Playwright 等）は含まない。
> 回帰保護は Task 2 の `gse-replay --metrics` + ゴールデン byte-equal が担う。

## 背景

Phase 1 Task 1（`phase1-ground-truth`）で UserLabel の記録基盤とグローバルホットキー経路が、Task 2（`phase1-metrics`）で `gse-replay --metrics` の算出基盤がそれぞれ完成した。しかしユーザーがセッション中にラベルを打った結果を**リアルタイムで確認する UI** がまだ存在しない（ラベル後に NDJSON を目視する必要がある）。また Phase 1 全体としての実機手動検証・最終レビューもまだ実施されていない。

Task 3 は Phase 1 クローズのための最終タスクで、Dashboard に読み取り専用の counter widget を追加し、実機でセッション → ラベル → metrics までを通しで検証する。

## ゴール

1. Dashboard に counter widget を追加し、`user_label_recorded` イベントを購読して Flow / Incubation / Stuck 各ラベルの累積数とショートカット hint をリアルタイム表示
2. 実機で以下のフローを手動で通し、すべて正常動作することを確認:
   - セッション開始 → ホットキー (⌘⇧⌥F/I/S) 押下 → counter がインクリメント
   - NDJSON に `{"type":"user_label", ...}` エントリが記録される
   - セッション終了後 `gse-replay --metrics <session.ndjson>` が pretty-print 出力
   - Phase 0 ゴールデン `minimal.json` の byte-equal が維持されている
3. Phase 1 全体スコープで `code-reviewer` + `security-checker` を並列実行し HIGH 指摘ゼロ
4. `.steering/20260415-phase1-ground-truth/requirement.md` の受け入れ条件すべてをクローズ

## スコープ

### 含むもの
- `src/components/Dashboard.tsx` に counter state + `listen("user_label_recorded", ...)` 購読 + 読み取り専用 UI（Flow:N / Inc:N / Stuck:N + ショートカット hint）追加
- 実機手動検証手順書（`verification_log.md`）の作成と実行結果記録
- 実機セッションで meta 行に `"hmm_version":"0.2.0"` が記録されることの目視確認（Phase 0 残条件 5 の消化）
- Phase 1 全体スコープの code-reviewer + security-checker 並列実行
- Task 1/2/3 の変更点を通した最終 `cargo test --workspace` + `cargo build --target aarch64-apple-darwin` (warning 0) + `npx tsc --noEmit`
- `.steering/20260415-phase1-ground-truth/requirement.md` 受け入れ条件のクローズ
- Phase 1 全体の retrospective（`.steering/20260415-phase1-ground-truth/retrospective.md`）

### 含まないもの
- Task 1/2 の実装内容そのものへの大幅変更（致命的バグ修正は除く）
- 多セッション集計・Python ヘルパー
- Phase 2a 以降の作業
- カウンター表示のアニメーションや凝った UI

## 受け入れ条件

- [ ] Dashboard.tsx に counter widget が表示され、ホットキー発火時にリアルタイム更新される
- [ ] ショートカット hint（`⌘⇧⌥ F/I/S` 等）が UI 上で可視
- [ ] `npx tsc --noEmit` エラー 0
- [ ] `cargo test --workspace` 全 PASS
- [ ] `cargo build --target aarch64-apple-darwin` warning 0
- [ ] 実機セッションで 5 件ラベル記録 → NDJSON 目視で `{"type":"user_label", ...}` 確認
- [ ] 実機セッションの meta 行に `"hmm_version":"0.2.0"` が記録されている（Phase 0 条件 5 消化）
- [ ] 同セッションに対して `gse-replay --metrics` 実行 → pretty-print 出力
- [ ] `tests/snapshots/minimal.json` の byte-equal 維持
- [ ] `code-reviewer` + `security-checker` HIGH 指摘ゼロ
- [ ] `phase1-ground-truth/requirement.md` の全受け入れ条件クローズ
- [ ] Phase 1 全体 retrospective が記録されている

## 関連ドキュメント

- `.steering/20260415-phase1-ground-truth/design.md`（Phase 1 v2 設計、counter widget セクション）
- `.steering/20260415-phase1-metrics/design.md`（Task 2 metrics 算出仕様）
- `src/components/Dashboard.tsx`（配置先）
- `docs/functional-design.md`（将来的に GT 仕様セクション追加が必要）
- `CLAUDE.md`（Skill: typescript-standards を参照）

## 運用メモ

- **/reimagine 適用: No**
- **理由**: Phase 1 全体設計で `/reimagine` 済み、Task 3 は Frontend + 検証の実装タスクでアーキテクチャ判断なし。ただし counter widget の配置・スタイリングは既存 Dashboard レイアウトに従う（Skill: typescript-standards 必須参照）。
- **前提**: Task 1 + Task 2 が commit 済み（Task 3 は両者の動作検証を含む）
