# Task B — backend プローブ scheduler

## 背景

v0.3 較正スモーク(D-14)の最小核は「計測プラミングを介入 UI より先に作る」方針。
実装順は **A(schema)→ (B∥C)→ D → E**。A は PR #4 で main へ merge 済み(2026-06-16)。
本タスクは A に続く backend タスク **B**。

プローブ生成を **backend が所有**する理由(D-14 技術判断): 主データ(`realtime_label`)の
妥当性は「プローブ時点がモデル出力と無関係な**一様ランダム**であること」に依存する。
これを `probe_assignment`(scheduled_ts / session_elapsed_ms)で**監査証明**するには、
時刻生成を frontend やモデルから切り離し backend に閉じる必要がある(v0.3 §4.1 / §4.3)。

## ゴール

セッション中、v0.3 §4.3 の制約を満たす一様ランダムなプローブ時刻を backend で生成し、
各プローブ確定時に (1) `probe_assignment` を logger へ記録し、(2) `probe_triggered` を
frontend へ emit する。加えて自己マーカー hotkey を 1 つ追加し、押下で self_marker の
`probe_triggered` を emit する。**「いつ・どの窓で聞くか」を確定して frontend に渡すまで**が B の責務。

## スコープ

### 含むもの (Task B のみ)
1. **rolling thinning による一様ランダム時刻生成**(純粋ロジック・`analysis/probe_scheduler.rs`):
   λ≈2回/30分・最小間隔 gap≥8分・cap≤2回/30分・離席(idle≥180s)は適格から除外。
   Poisson 指数間隔サンプリング → gap/cap/away 制約で thinning(棄却)。seed 注入可能。
2. **`probe_assignment` ログ**: 各プローブ確定時に
   `LogEntry::ProbeAssignment { probe_id, scheduled_ts, session_elapsed_ms }` を logger へ送信。
   probe_id は backend 生成の不透明 ID(UUID 等 `[A-Za-z0-9_-]` のみ。Task A 申し送り厳守)。
3. **frontend へ emit**: プローブ発火時に
   `app.emit("probe_triggered", { probe_id, source, analysis_window_start_ms, analysis_window_end_ms })`。
4. **自己マーカー hotkey**(source=self_marker・副データ): 既存 global-shortcut に 1 キー追加
   (Ctrl+Shift+Alt+M、ReviewMarker と同じ debounce)。押下で self_marker の `probe_triggered`
   を emit(probe_id=null・窓は t−35s..t−5s)。

### 含まないもの
- 回答カード UI・ビネットフロー(Task C)。`realtime_label`/`vignette_response`/`session_meta`
  の**ログ生成コマンドは Task C**(B は `probe_triggered` emit まで)。
- 解析窓抽出・C-index・2段ゲート(Task D)。
- `context_beacon`/`waveform_label`/`task_checkpoint`/`intervention_dismiss`(D-14 で延期)。

## 受け入れ条件

- [ ] `analysis/probe_scheduler.rs` が OS API を一切呼ばない純粋モジュール(architecture-rules 準拠)。
- [ ] seeded RNG で gap≥8分 / cap≤2回/30分 / away 除外 を検証する決定論的単体テストが緑。
- [ ] プローブ確定時に `probe_assignment`(scheduled/shown 両追跡可能)が NDJSON へ出る。
- [ ] `probe_triggered` が正しい payload(probe_id, source, window)で emit される。
- [ ] 自己マーカー hotkey 押下で self_marker の `probe_triggered`(probe_id=null, 窓 t−35s..t−5s)が emit。
- [ ] data-privacy 維持: 数値・固定カテゴリ・不透明 ID のみ。本文/タイトル/選択文字列/Unicode 非保存。
- [ ] `cargo test` / `cargo clippy`(新規警告ゼロ)/ `npm run build` 緑。main は常にビルド可能。
- [ ] 既存テストの無断削除なし。

## 関連ドキュメント

- `.idea/GSE_事後ラベリングシステム設計書_v0.3.md` §4(主データ・時間隔離窓)/§4.3(制約)/§14(schema)
- `.steering/20260612-retro-labeling-and-corner-intervention/decisions.md` D-8 / D-14
- `.steering/20260616-probe-schema/decisions.md`(Task A 申し送り: probe_id は backend 生成不透明 ID)
- `docs/architecture.md`(スレッドモデル)
- Skill: architecture-rules / rust-standards / hook-constraints / data-privacy

## 運用メモ
- /reimagine 適用: **Yes**
- 理由: 設計判断が2点(スケジューリング方式 / B↔C イベント契約)あり、複数案ありうる(handoff 推奨)。
