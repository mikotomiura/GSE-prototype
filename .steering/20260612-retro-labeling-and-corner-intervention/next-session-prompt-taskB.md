# 次セッション用プロンプト — Task B「backend プローブ scheduler」

> 用途: 新しいセッションの最初にこのファイルの「プロンプト本文」を貼り付ける。
> 新セッションは CLAUDE.md / MEMORY.md を自動ロードする前提。
> 背景: Task A(probe schema)は PR #4 で main へ merge 済み(2026-06-16)。
>        実装順は D-14 で A→(B∥C)→D→E。**Task A 完了につき次は B(と C は並行可)**。
>        本セッションは **Task B** を実施する。

---

## プロンプト本文(ここから下をコピペ)

```
Task B「backend プローブ scheduler」を開始する。v0.3 較正スモーク(D-14)の実装順 A→(B∥C)→D→E のうち、
A(schema, PR #4 merge 済み)に続く backend タスク。プローブ生成は backend 所有
(「一様ランダム・モデル非依存」を probe_assignment で監査証明する必要があるため・D-14 技術判断)。

まず以下を読んで文脈を固めてから着手すること:
- .idea/GSE_事後ラベリングシステム設計書_v0.3.md の §14(schema, 既実装の probe_assignment / realtime_label)と
  D-8(時間隔離窓: ランダムプローブ t−31s..t−1s / 自己マーカー t−35s..t−5s, ≤2回/30分・間隔≥8分)
- .steering/20260612-retro-labeling-and-corner-intervention/decisions.md の D-14(最小核・実装順・rolling thinning 技術判断)
- .steering/20260612-retro-labeling-and-corner-intervention/tasklist.md の「Task B」
- .steering/20260616-probe-schema/decisions.md(Task A 申し送り: probe_id は backend 生成の不透明 ID に限定)
- src-tauri/src/logger.rs の LogEntry::ProbeAssignment / RealtimeLabel と realtime_label_* コンストラクタ・ProbeRef(Task A で追加済み)
- docs/architecture.md(スレッドモデル)、Skill: architecture-rules / rust-standards / hook-constraints / data-privacy

手順(CLAUDE.md 厳守):
1. /start-task で 20260617-probe-scheduler を初期化(requirement/design/tasklist 作成)。
2. /reimagine を Step 3 後に実行(下記「設計判断」の 2 点が複数案ありうるため推奨)。
3. /add-feature で実装。
4. 調査は file-finder + dependency-checker を並行起動(rand crate 追加の影響確認)。
   実装後は code-reviewer + security-checker + test-runner を並行起動。

実装スコープ(Task B のみ。C/D は含めない):
- (1) rolling thinning による一様ランダム時刻生成:
    λ≈2回/30分・最小間隔 gap≥8分・cap≤2回/30分・**離席時間(idle≥180s)は適格から除外**。
    Poisson 過程の指数間隔サンプリング → gap/cap/away 制約で thinning(棄却)する純粋ロジック。
- (2) probe_assignment ログ: 各プローブ確定時に LogEntry::ProbeAssignment { probe_id, scheduled_ts, session_elapsed_ms }
    を logger へ送信(probe_id は backend 生成の不透明 ID = UUID 等 [A-Za-z0-9_-] のみ。Task A 申し送り厳守)。
- (3) フロントへ emit: プローブ発火時に app.emit("probe_triggered", json!({ probe_id, source, analysis_window_start_ms, analysis_window_end_ms }))。
    回答カード表示は Task C の責務。B は「いつ・どの窓で聞くか」を確定して渡すところまで。
- (4) 自己マーカー hotkey(source=self_marker・副データ): 既存 global-shortcut ハンドラに 1 キー追加
    (例 Ctrl+Shift+Alt+M、ReviewMarker と同じ debounce パターン)。押下で self_marker の probe_triggered を emit
    (probe_id=null・窓は t−35s..t−5s)。realtime_label のログ自体は Task C の回答コマンドで行う。

要件・制約:
- **アーキテクチャ境界(architecture-rules 必須参照)**: 純粋スケジューリングロジック(指数サンプリング・thinning・
  窓計算)は analysis/ に新モジュール(例 analysis/probe_scheduler.rs)として置き、**OS API を呼ばない**。
  スレッド起動・タイマ・emit・hotkey・idle 取得の OS/Tauri 配線は lib.rs(または input/)側に閉じる。
  mod.rs の pub mod 更新を忘れない。
- **RNG**: src-tauri/Cargo.toml に rand を追加(現状未依存)。dependency-checker で版・影響確認。
  スケジューラは **seed 注入可能**に設計し、決定論的単体テスト(seeded RNG で gap/cap/away 制約を検証)を書く。
- **スレッド**: 既存 1Hz 解析ループ(lib.rs の next_engine_update_ms ゲート)に相乗りするか、IME monitor 風の
  専用ポーリングスレッドを spawn するか design.md で決める。shutdown は既存 channel パターンに合わせる。
- **idle 除外**: 既存 get_keyboard_idle_ms() / input::hook::last_key_ms() と AWAY_IDLE_MS(=180_000ms, intervention.rs)
  を再利用。新規 idle 検出は作らない。
- **session 経過**: session_elapsed_ms = now − session_start。session_start をスレッド間共有する手段が現状ないため
  (logger 内 timestamp のみ)、start_session 時に Arc<AtomicU64> 等で session_start_ms を保持する配線を足す。
- **hook-constraints**: フック/コールバック内はブロッキング禁止(Atomic + channel send のみ)。hotkey ハンドラも軽量に。
- **data-privacy**: 数値・固定カテゴリ・不透明 ID のみ。本文・タイトル・選択文字列・Unicode は一切保存しない。
- **プローブの一様性監査**: scheduled(予定時刻)と shown(実発火)を両方追えるようにログ設計する(D-14)。
- 既存テスト無断削除禁止。cargo test / clippy / npm run build 緑、main は常にビルド可能を維持(git-workflow ルール4)。

設計判断(/reimagine で 2 案比較推奨):
- A. スケジューリング方式: 「指数間隔 Poisson + 制約 thinning」vs「30分窓ごとに一様 2 点を事前抽選し gap で棄却」。
     監査可能性(一様性の証明しやすさ)と実装単純さのトレードオフ。
- B. B↔C のイベント契約: probe_triggered の payload と、回答窓(analysis_window_*)を B/C どちらが確定し
     realtime_label に載せるか。B が窓を確定して emit に含め、C は受け取って realtime_label に転記する案を base にする。

スコープ厳守: 上記 (1)〜(4) 以外は追加しない。
- realtime_label / vignette_response / session_meta の **ログ生成コマンドは Task C**(B は probe_triggered emit まで)。
- 回答カード UI・ビネットフロー(Task C)、解析窓抽出・C-index・2段ゲート(Task D)は含めない。
- context_beacon / waveform_label / task_checkpoint / intervention_dismiss は D-14 で延期につき追加しない。
```
