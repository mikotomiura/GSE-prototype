# 要件定義: gse-replay --metrics が label 近接の feat を全取りこぼすバグ調査

## 背景

Windows onboarding (`20260415-windows-onboarding/`) の Stage E で、タイピング混じりの良質セッション `gse_20260415_144120.ndjson` に対し `gse-replay --metrics` を実行したところ、全 6 ラベルが `no FeatSnapshot within ±1000ms` 警告で脱落、confusion matrix 全 0 / per-class support=0 となった。

元 NDJSON を python で解析すると:
- feat イベント 96 件 (ほぼ 1 秒刻み)
- 全 6 ラベルが ±500ms 以内に feat を持つ (12ms / 174ms / 206ms / 234ms / 237ms / -431ms)

にもかかわらず `LABEL_MATCH_WINDOW_MS = 1000` の判定を全件通らない。一方で `detection_lead_ms_median = +26315 ms` は計算されており、feat 列自体は生成され argmax も機能している。

設計上の手がかり: `replay.rs` コメント (`//! 再実行して FeatSnapshot 列を生成する。`) は元 NDJSON の feat を破棄して step() を再実行する旨を明記している。**再生成 feat 列が label 時刻とアライメントしていない**可能性が高い。

## 根本原因の仮説

1. **H1**: step() の feat 発生タイミングが ENGINE_TICK_MS (1s) の固定スケジュールで、ordered events から計算するため、元ランタイムの feat 時刻とずれる
2. **H2**: replay の event ordering で user_label が `timestamp() -> None` で除外されるため、label 時刻を step() 側が知らずに素通りする
3. **H3**: OS 依存の step() 挙動差 (Mac baseline は Stuck support=2 で動作実績あり → Windows 固有の可能性も残る)
4. **H4**: session_start の扱いで feat 開始時刻が原始 NDJSON とずれる

## ゴール

1. 根本原因を再現可能な形で特定
2. 影響範囲を明確化 (Phase 1 全 metrics 計算の信頼性 / per-OS 差)
3. Fix が cheap なら同タスク内で TDD 回帰テスト + 修正を commit。Hard なら別タスクに分離
4. Phase 2a Go/No-Go 判定の可否を結論付け (`baseline_metrics.md` が信頼できるか)

## スコープ

### 含むもの
- `src-tauri/src/bin/replay.rs` の `run_replay()` 読解
- `src-tauri/src/analysis/loop_step.rs` の `step()` 発火条件読解
- `src-tauri/src/analysis/metrics.rs` の `nearest_feat()` / `compute_session_metrics()` 読解
- 実データ (Windows: `gse_20260415_144120.ndjson`、Mac: dataset repo から取得可能な場合) での再現と timestamp 比較
- 回帰テスト追加 (TDD) と修正 (cheap な場合)

### 含まないもの
- BL-1 (セッション NDJSON 保存先) は別タスク
- replay.rs の snapshot 機能の仕様変更
- Phase 2 以降の新機能追加

## 受け入れ条件

- [ ] 再現最小ケース: 単一 label + 周辺 feat の NDJSON で warning が再現する (もしくは再現しないなら Windows 固有要因が特定される)
- [ ] 原因を `decisions.md` の **D1** に記載 (H1-H4 のどれか、または新規)
- [ ] Fix 判断:
  - Option A (cheap): 本タスクで回帰テスト + fix + commit
  - Option B (defer): `.steering/20260416-replay-feat-alignment-fix/` に別タスク起票、本タスクは調査完了扱い
- [ ] Phase 2a Go/No-Go 判定への影響を明記
- [ ] `cargo test` 全 PASS 維持 (本タスク内で修正する場合)

## 関連

- 親タスク: `.steering/20260415-windows-onboarding/blockers.md` BL-2
- Phase 1 retrospective: `.steering/20260415-phase1-ground-truth/retrospective.md` (M1 detection_lead_ms の類似学び)
- 影響先: `.steering/20260415-phase1-ground-truth/baseline_metrics.md` (現 n=2 の信頼性)
