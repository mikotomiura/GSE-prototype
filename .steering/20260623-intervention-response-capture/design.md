# 設計 (intervention-response-capture)

## アプローチ (ユーザー承認済みの3決定 — AskUserQuestion 2026-06-23)

1. **イベント表現 = (i) 既存 `InterventionResponse` 拡張**
   - `action="wall"` + `reason ∈ {early_unlock, completed}` + `elapsed_ms: Option<u64>`。
   - Nudge dismiss は `elapsed_ms=None`(JSON から省略)。schema 追加は enum 値 + 任意フィールドのみで最小、
     CD3 (汎用 InterventionResponse) と一貫。
2. **早期/通常(順守) の判定 = (A) Rust サーバ側 elapsed (HTML 不変)**
   - `/shake` 接続時刻を Rust が保持し、`/unlock` で `elapsed_ms = now - shake_at` を算出。
   - JS は `doUnlock()` を timerDone(120s) 後のみ許可、`doEarlyUnlock()` を 120s 前のみ許可するため、
     **server 側 elapsed が押下ボタンを一意に決定**する: `elapsed < 120_000` = early_unlock / `>= 120_000` = completed。
   - HTML/UX/挙動は完全不変。client 送信値を信頼しない (server-authoritative)。
3. **`idle_timeout` enum 値を予約 (未配線)**
   - 自動解除は現状未実装だが intervention-design が Wall 解除条件に「長時間アイドル」を明記。
     捕捉スキーマ凍結思想 (CD7 silent 予約) に沿い enum 値だけ今凍結、配線は将来。

## 現状フロー (code 確認済み)

- Wall 解除の唯一の経路 = スマホ `POST /unlock` (`wall_server.rs` dispatch_request)。
  早期解除ボタン (⏸) も通常解除ボタンも **同一 /unlock** を叩く (区別パラメータなし)。
- フロントは `sensor-accelerometer` イベントのみで `setIsWallActive(false)` (`App.tsx:144`)。
  **PC 側早期解除も idle 自動解除も存在しない**。
- 自動タイマー満了解除は **現状存在しない** (0:00 到達は「Unlock」ボタンを出すだけ)。
  → 実配線は early_unlock / completed の2値。idle_timeout は enum 予約のみ。

## 変更対象

### 修正するファイル
- `src-tauri/src/logger.rs` — `DismissReason` に EarlyUnlock/Completed/IdleTimeout 追加 (as_str/parse)。
  `LogEntry::InterventionResponse` に `elapsed_ms: Option<u64>`。
  `format_intervention_response_line` に elapsed_ms 引数 (Some の時のみ `,"elapsed_ms":N`、None は byte 同一)。
  writer ループ match アームで elapsed_ms 分解。
- `src-tauri/src/schema_dto.rs` — `DismissReasonDto` に EarlyUnlock/Completed/IdleTimeout。
  `LogEntryDto::InterventionResponse` に `elapsed_ms: Option<u64>`。
- `src-tauri/src/lib.rs` — `LogState` と field `tx` を `pub(crate)` に。
  `record_intervention_dismiss` の InterventionResponse 構築に `elapsed_ms: None`。
- `src-tauri/src/wall_server.rs` — `start_wall_server` に `log: State<Arc<Mutex<LogState>>>` 追加、
  tx clone + `shake_at: Arc<AtomicU64>` を server_loop/dispatch_request へ。
  `/shake` で shake_at.store(now_ms())、`/unlock` で elapsed/reason 算出 + try_send。
  `const ZEN_TIMER_MS: u64 = 120_000;` + `now_ms()` ヘルパ。
- `src-tauri/schema/current.json` — `emit_schema` 再生成で更新。

### 新規作成するファイル
- (任意) `src-tauri/tests/fixtures/wall_response.ndjson` — Wall 応答行を含む golden。gse-replay パース確認用。

### 削除するファイル
- なし

## 影響範囲

- `DismissReason` 新値で `as_str`/`parse` match の網羅性が compile 強制 → アーム追加で対応。
- `format_intervention_response_line` / writer アーム / 既存テスト 3件 (intervention_response_line_basic /
  new_enums_roundtrip / writer_loop_emits_new_variants_to_file) のシグネチャ追従。
- `replay.rs::ReplayEvent::InterventionResponse(Value)` は catch-all のため変更不要 (新フィールド/値を無条件受理)。
- `--snapshot` FeatSnapshot は features/engine 不触で byte-equal 不変。`HMM_VERSION` 不変。

## 既存パターンとの整合性

- 固定カテゴリ enum + `as_str`/`parse` 純粋関数 (CD9)、`format_*_line` 純粋関数 (logger 既存流儀)。
- Option フィールドの後方互換 (CD4、SessionMeta の condition/label_pool と同型)。
- try_send 非ブロッキング送信 (record_intervention_dismiss / 1Hz ループと同流儀、hook 制約準拠)。
- wall_server は src-tauri/src/ 直下で logger を使用可 (logger→wall_server の逆依存なし=循環なし)。

## テスト戦略

- 単体: `format_intervention_response_line` の Wall(Some)/Nudge(None)、新 DismissReason の as_str↔parse roundtrip。
  writer ループ E2E に Wall(action=wall, elapsed_ms=Some) 行追加。
- 統合/回帰: `cargo test --workspace` 緑。`--snapshot` byte-equal (features 不触)。
- 後方互換: 旧 NDJSON (elapsed_ms 欠落 / 新 reason 無し) で gse-replay が panic しない。
- schema: `emit_schema` → `current.json` byte-equal + gse-dataset parity (今回 schema 変更で実走必須)。

## ロールバック計画

- 変更は加算的 (新 enum 値 / Option フィールド / 配線追加)。問題時は branch を破棄し main へ戻すだけ。
  schema/current.json も再生成前の状態に戻る。
