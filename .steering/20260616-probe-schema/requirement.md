# requirement.md — Task A「probe schema 拡張」

## 背景

v0.3 較正スモーク(D-14)の **全ブロッカー**。methodology(v0.3)を初めてコードへ
落とす初回スモークの最小核として、計測プラミングを介入 UI より先に整備する。
Task A はその schema 層 — 後続の Task B(backend scheduler)/ C(frontend collect)/
D(オフライン解析)はすべて本タスクの NDJSON スキーマに依存する。

参照: `.idea/GSE_事後ラベリングシステム設計書_v0.3.md §14`、decisions.md D-7 / D-14、
`next-session-prompt-taskA.md`。

## ゴール

v0.3 §14 の **最小核 4 バリアント** を NDJSON ログに追加する:

- `session_meta` — セッション開始宣言(track / task_kind / monk_mode / intervention_enabled / ts)
- `probe_assignment` — ランダムプローブ割当の監査記録(probe_id / scheduled_ts / session_elapsed_ms)
- `realtime_label` — 主データ(probe_id / source / q1_friction / q2_progress / answered /
  skip_reason / latency_ms / analysis_window_start_ms / analysis_window_end_ms / ts)
- `vignette_response` — 尺度理解テスト(vignette_id / expected_quadrant / q1_friction / q2_progress / ts)

付随 enum も両側に定義: Track / TaskKind / ProbeSource / SkipReason / ExpectedQuadrant。

## 受け入れ条件

1. `logger.rs` の `LogEntry` と `schema_dto.rs` の `LogEntryDto` を **同期追加**(D-7)。
2. producer 側で不変条件を強制:
   - skip(answered=false)⇒ q1_friction / q2_progress = null
   - answered=true ⇒ q1 / q2 が 1..=5
   - source=self_marker ⇒ probe_id = null
3. プライバシー境界厳守: 数値・カテゴリ・**生成済み不透明 ID** のみ。本文・タイトル・
   選択文字列・Unicode 文字は保存しない(data-privacy Skill)。
4. `cargo run --bin emit_schema` 再生成 → `schema/current.json` 更新 → drift 緑。
5. 既存テスト(format_*_line / replay)を壊さない。`cargo test` 緑、clippy 緑。

## スコープ外(やらないこと)

- backend probe scheduler(Task B)— rolling thinning・実際の `probe_assignment` 送信。
- frontend 収集 UI(Task C)— プローブカード・ビネットフロー・`session_meta` 宣言 UI。
- オフライン解析(Task D)— `replay.rs` の `ReplayEvent` への新バリアント consumption。
  ※ 現状 replay は未知 `type` を parse-fail として skip(警告カウントのみ)するため、
    新バリアントを足しても既存 replay はクラッシュしない。Task D で read-skip / 窓抽出を追加する。
- §14 の延期分: `context_beacon` / `waveform_label` / `task_checkpoint` /
  `intervention_dismiss` / `ai_reference`(D-14 で次段送り)。

## 運用メモ
- /reimagine 適用: No
- 理由: schema は v0.3 §14 で実装契約として確定済み。設計の自由度はなく、
  「既存 DTO ミラー方式への忠実な同期追加」という機械的タスク。複数案は生じない。
