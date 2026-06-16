# 次セッション用プロンプト — Task A「probe schema 拡張」

> 用途: 新しいセッションの最初にこのファイルの「プロンプト本文」を貼り付ける。
> 新セッションは CLAUDE.md / MEMORY.md を自動ロードする前提。
> 背景: v0.3 を実装契約として確定(2026-06-16)。実装順は D-14 で A→(B∥C)→D→E。Task A は全ブロッカー。

---

## プロンプト本文(ここから下をコピペ)

```
Task A「probe schema 拡張」を開始する。これは v0.3 較正スモークの全ブロッカー(D-14)。

まず以下を読んで文脈を固めてから着手すること:
- .idea/GSE_事後ラベリングシステム設計書_v0.3.md の §14(データスキーマ)
- .steering/20260612-retro-labeling-and-corner-intervention/decisions.md の D-7(DTOミラー方式)と D-14(最小核スコープ)
- .steering/20260612-retro-labeling-and-corner-intervention/tasklist.md の「Task A」
- docs/development-guidelines.md §10(schema drift / gse-dataset 連携)
- src-tauri/src/logger.rs:99 の enum LogEntry(producer 本体)
- src-tauri/src/schema_dto.rs の enum LogEntryDto(ミラー)と src-tauri/src/bin/emit_schema.rs

手順(CLAUDE.md 厳守):
1. /start-task で 20260616-probe-schema を初期化(requirement/design/tasklist 作成)。
2. /add-feature で実装。
3. 調査は file-finder + dependency-checker を並行起動。実装後は code-reviewer + security-checker を必ず並行起動(logger/schema 変更のため security-checker は必須)。

実装内容(v0.3 §14 の最小核 4 バリアントのみ。beacon/waveform/checkpoint は D-14 で延期につき今回追加しない):
- session_meta { track: "main"|"exploratory", task_kind: "argumentative"|"correspondence"|"creative"|"vibe_coding", monk_mode: bool, intervention_enabled: bool, ts }
- probe_assignment { probe_id, scheduled_ts, session_elapsed_ms }
- realtime_label { probe_id (self_marker時 null), source: "random_probe"|"self_marker", q1_friction (skip時 null), q2_progress (skip時 null), answered: bool, skip_reason: "none"|"dont_remember"|"dismissed", latency_ms, analysis_window_start_ms, analysis_window_end_ms, ts }
- vignette_response { vignette_id, expected_quadrant: "flow"|"stuck"|"incubation"|"idle", q1_friction, q2_progress, ts }

要件:
- logger.rs の LogEntry と schema_dto.rs の LogEntryDto を必ず同期追加(D-7)。付随 enum(Track/TaskKind/ProbeSource/SkipReason/ExpectedQuadrant)も両側に定義。
- producer 側で不変条件を強制: skip(answered=false)⇒ q1/q2=null、source=self_marker ⇒ probe_id=null、answered=true ⇒ q1/q2 が 1..=5。
- プライバシー境界を厳守: 数値・カテゴリのみ。本文・タイトル・選択文字列・Unicode 文字は保存しない。
- emit_schema を再生成(cargo run --bin emit_schema)→ src-tauri/schema/current.json を更新 → drift が出ないことを確認。

スコープ厳守: 上記 4 バリアント以外は追加しない。backend scheduler(Task B)・frontend UI(Task C)・解析(Task D)はこのタスクに含めない。
```
