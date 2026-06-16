# タスクリスト — adaptive-baseline (v2)

## 準備 ✅（本セッション完了）
- [x] 関連コード調査（engine.rs / features.rs / loop_step.rs / lib.rs ループ）
- [x] requirement.md / design.md（v2）/ decisions.md / design-comparison.md 記入
- [x] /reimagine 実施（v1→v2 採用）
- [x] Plan 確定パラメータの決定（W=256, W_min=32, GATE=0.40, N=5, friction p60 / F4 p35, κ=2.0）

## 次セッション最初の作業
- [ ] **codex review を実行**（HANDOFF.md 参照。codex レート制限解除後）
- [ ] codex review の指摘を decisions.md / design.md に反映してから実装着手

## 実装（codex review 反映後）
- [ ] `analysis/baseline.rs` 新規: `BetaSet` / `FluentWindow`(リング+パーセンタイル) /
      `ContextBaseline`（push・prior フォールバック・warmup lerp・reset）
- [ ] `engine.rs`: `calculate_latent_axes/update/update_silence` を `beta:&BetaSet` 引数化、
      β 母集団定数を prior として baseline.rs へ移設
- [ ] `engine.rs`: `HMM_VERSION` bump、`UpdateDiagnostics` に β 追加（in-memory）
- [ ] `features.rs`: `phi` を κ 引数化、パーセンタイルヘルパは baseline.rs
- [ ] `loop_step.rs`: state に `ContextBaseline` 保持、context 別 β 注入、
      受理ゲート（p_stuck<GATE ∧ デバウンス N ∧ TypingPath）で流暢サンプル push

## テスト
- [ ] baseline.rs 単体: prior フォールバック / 収束 / 裾破棄 / reset / warmup lerp
- [ ] loop_step 受理ゲート: 高 p_stuck・デバウンス未満・silence/transition で push されない
- [ ] engine 純関数: 同一 (features,β) で決定的、β=prior で旧 golden 一致
- [ ] スナップショット golden 更新（HMM_VERSION 整合）
- [ ] 既存テスト緑

## 検証
- [ ] `gse-replay --metrics --json` で「遅い人/速い人」合成 or 実データの before/after 比較
- [ ] 原点バイアス低減・偽介入/検出漏れ改善を確認

## レビュー
- [ ] code-reviewer + security-checker 並列（実装後）
- [ ] HIGH/MEDIUM 指摘を本タスクで消化（backlog に punt しない）

## ドキュメント
- [ ] docs/glossary.md に baseline/β 適応の用語追加（要否確認）
- [ ] docs 更新（architecture のデータフローに β 注入経路）

## 完了処理
- [ ] design.md 最終化 / decisions.md 更新
- [ ] git commit（feat(engine): adaptive context baseline (β) with contamination-resistant window）
