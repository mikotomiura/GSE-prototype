# タスクリスト

## 準備
- [x] requirement.md / design.md を読む
- [x] `probe_scheduler.rs` と lib.rs 駆動側を読み、現行パラメータ実値を洗い出す（λ=2/30min・gap_min=8min・cap_count=2・cap_window=30min・away_idle=180s・poll=1Hz・seed=entropy）
- [x] 実機ログの代わりに純ロジック模擬 driver で「初期 2 連→枯渇」を再現（seed10 等）

## (I) スケジューラ是正
- [x] 純ロジックの模擬 driver で「クラスタ→枯渇」を**再現する単体テスト**（`pure_poisson_droughts_but_default_config_does_not`）
- [x] 原因切り分け → **cap dead-zone ＋ 低レート Poisson の裾**が主因（idle→away は無関係）。decisions.md D1
- [x] 是正：**soft max-gap (候補間隔の truncated-exponential 打ち切り 22min) ＋ gap6/cap-window20**。λ 不変・seed 決定性維持。decisions.md D2
- [x] 是正後の**一様性監査**テスト（`fires_spread_across_whole_session_not_just_early` / `default_config_never_empty_over_typical_session` / `soft_max_gap_truncates_candidate_intervals`）

## (II) 非侵襲提示
- [x] 方針確定：**打鍵状態でプローブ時点を条件づけない**（measurement independence＝L0 較正の独立性を優先）。decisions.md D4
- [x] 既存提示（`.probe-card-pop` 0.32s スライドイン・右上非ブロック小ボックス）で非侵襲性は担保済み → frontend 変更不要

## (II') 落合サーベイ（literature-card skill）
- [x] トピック確定（ESM スケジュール / stratified random / interruptibility / 通知受容性）
- [x] WebSearch で実在ソース確認（V18-V23 全 6 件 active・DOI/ISBN 確証・捏造なし）
- [x] 落合カード **5 本** を `docs/literature/20260628-probe-timing-interruptibility.md` に作成
- [x] `docs/literature/_index.md` 追記・出典を `references.md`(V18-V23) に append（citation-ssot・append-only）
- [x] `research-positioning.md` §3/§4 に「やり残し」を還元（層語彙 L0 stratified / L2' opportunity 準拠）

## テスト
- [x] `cargo test --workspace`（24 probe_scheduler + 全体パス）
- [x] `gse-replay --snapshot` 回帰（byte-equal: 15 snapshots match）

## レビュー / 完了
- [ ] code-reviewer + `/cross-review`
- [x] design.md / decisions.md 最終化
- [ ] commit（`fix(probe): スケジュールを分散化` ＋ `docs(research): probe-timing 落合カード追加`）→ `/finish-task`

## 依存・順序メモ
- 落合サーベイは `research-positioning §3/§4` と `references(V)` に追記するため、
  **R1 反映タスク（20260628-r1-positioning-review-reflection）を先に完了**してから走らせると衝突しない。
