# 設計 — Task C frontend 収集

## 実装アプローチ

frontend(React/TS)で 3 つの収集経路を提供し、各回答を **新規 Tauri command** 経由で
既存 logger(`LogState.tx`)へ送る。状態推定ロジックは frontend に置かない(architecture-rules)。
schema は Task A で確定済 → `schema_dto.rs` / `current.json` は touch しない。

### backend(lib.rs commands + logger/probe_scheduler 補助)
- **command 群**(lib.rs, `LogState` を State で受け、parse 失敗は `Result<(), String>` でエラー返却):
  - `record_session_meta(track, task_kind, monk_mode, intervention_enabled)`:
    `Track::parse`/`TaskKind::parse`(不正→Err)→ `LogEntry::SessionMeta` 送信。
  - `record_realtime_answer(probe_id: Option<String>, source, q1, q2, latency_ms, window_start_ms, window_end_ms)`:
    `ProbeSource::parse` → probe_id を `#7` 再検証 → `ProbeRef` 構築 → `realtime_label_answered` 送信。
  - `record_realtime_skip(probe_id, source, skip_reason, latency_ms, window_start_ms, window_end_ms)`:
    同上 + `SkipReason::parse` → `realtime_label_skipped` 送信。
  - `record_vignette_response(vignette_id, expected_quadrant, q1, q2)`:
    `ExpectedQuadrant::parse` + vignette_id 検証 → `LogEntry::vignette_response`(下記 clamp 構築子)送信。
  - 全 command を `tauri::generate_handler![...]` に登録。
- **#7 受領 ID 再検証**(cross-review): `ProbeId::is_valid(&str)`(長さ16 && 全文字が ALPHABET)を
  probe_scheduler に追加(アルファベットの単一情報源化)。command で:
  source=random_probe ⇒ probe_id=Some かつ `is_valid` 必須、source=self_marker ⇒ probe_id=None 必須。
- **VignetteResponse の clamp**(cross-review Codex#1): `LogEntry::vignette_response(ts, vignette_id,
  expected_quadrant, q1, q2)` 構築子を logger に追加し q1/q2 を `1..=5` clamp(schema 不変・producer 強制)。

### frontend(src/)
- 型: `ProbeTriggered { probe_id: string|null, source: "random_probe"|"self_marker",
  analysis_window_start_ms: number, analysis_window_end_ms: number }`(any 禁止)。
- `ProbeCard.tsx`(新): `listen("probe_triggered")` → Q1摩擦/Q2前進 スライダー(1-5)+ skip(理由 2 択)
  + latency 計測(表示〜回答)。回答→`record_realtime_answer` / skip→`record_realtime_skip`。
  **モデル出力(X/Y/p_stuck/状態)を一切表示しない**(原則5)。
- `VignetteTest.tsx`(新): §6.3 の 8 シナリオ(場面文 + expected_quadrant)に Q1/Q2 回答 →
  `record_vignette_response`。場面文は表示のみ・**ログに送らない**(vignette_id + quadrant + q1/q2 のみ)。
  PreReg-1 ゲート(6/8 想定象限)は client-side 推論で**フィードバック表示のみ**(権威採点は Task D)。
- start 画面(App.tsx): task_kind セレクタ + track/monk/intervention を宣言 → `handleStart` で
  `start_session` 後に `record_session_meta`。
- 配置は下記「設計判断 A」に従う。

---

## 設計判断 A(/reimagine 相当)— 回答カードの居場所

| 案 | 長所 | 短所 |
|---|---|---|
| **A1(推奨) Overlay に出す** | 既存 always-on-top 透過ウィンドウ=最上位の割込面。被験者が他アプリで作業中でも見える。card 表示中のみ `setIgnoreCursorEvents(false)` で操作可能。§1.3 中断最小化・原則5(モデル非表示)と整合 | Overlay の責務が Nudge/Wall に加わる(状態が増える) |
| A2 専用 probe ウィンドウ | 責務分離が綺麗 | Windows で `WebviewWindowBuilder::build()` デッドロック注意(既存 setup の制約)・生成コスト |
| A3 main ウィンドウ | 実装単純 | 作業中は GSE main を見ていない→プローブを見逃す。不可 |

**採用: A1**(Overlay にカードを mount し、表示中のみ cursor events を有効化)。

## 設計判断 B(/reimagine 相当)— session_meta 宣言 + ビネット起動導線

| 案 | 内容 |
|---|---|
| **B1(推奨)** | start 画面に task_kind セレクタを置き 開始時に `record_session_meta`。ビネットは start 画面の「尺度理解テスト」エントリから 8 問フロー(再実行可)→ PreReg-1 結果表示。スモークで明示的・シンプル |
| B2 | ビネットを初回起動時のみ強制(永続フラグ)。本番に近いが永続化が必要でスモークには過剰 |

**採用: B1**(start 画面に task_kind 宣言 + 「尺度理解テスト」導線。ゲート結果は表示するが本番ブロックはソフト)。

---

## 変更対象

### 新規作成
- `src/components/ProbeCard.tsx` — probe_triggered listen + 回答カード。
- `src/components/VignetteTest.tsx` — 8 ビネットフロー。
- (任意) `src/probeTypes.ts` — 共有型。

### 修正
- `src-tauri/src/lib.rs` — 4 command 追加 + `generate_handler!` 登録。
- `src-tauri/src/logger.rs` — `LogEntry::vignette_response` clamp 構築子。
- `src-tauri/src/analysis/probe_scheduler.rs` — `ProbeId::is_valid` + テスト。
- `src/App.tsx` — start 画面に task_kind 宣言 + ビネット導線 + handleStart で record_session_meta。
- `src/components/Overlay.tsx` — ProbeCard を mount、card 表示中の cursor events 制御。

### 削除
- なし。

## 影響範囲
- 既存 command/イベントには非干渉(新規追加のみ)。`generate_handler!` への追記のみ。
- schema 不変 → finish-task の parity guard に当たらない。
- Overlay に状態が増える(card 表示フラグ)が Nudge/Wall ロジックには非干渉。

## 既存パターンとの整合性
- IPC: `invoke<T>(...)` / `listen(...)`(App.tsx / Overlay.tsx の既存パターン)。
- command: `lib.rs` の既存 `#[tauri::command]` + `State<Arc<Mutex<LogState>>>` + `guard.tx.try_send`。
- enum parse: logger の `Track/TaskKind/ProbeSource/SkipReason/ExpectedQuadrant::parse`。
- 不変条件: `realtime_label_answered/_skipped` + `ProbeRef`(self_marker⇒probe_id=null を型で保証)。

## テスト戦略
- backend 単体: `ProbeId::is_valid`(有効/長さ違い/不正文字)、`vignette_response` clamp(0→1, 9→5)。
  command の parse 失敗経路は薄いラッパのため、検証ロジック(is_valid/parse)を単体で固める。
- frontend: `npm run build`(tsc 型チェック)で型整合を担保。回答フローは手動スモーク(Task E)。
- 既存テスト不変。`cargo test` / `clippy` 緑。

## ロールバック計画
- 新規 .tsx 2-3 ファイル削除 + lib.rs/logger.rs/probe_scheduler.rs の追加分・App/Overlay の mount を revert。
  既存挙動へ完全復帰(新規追加のみで副作用なし)。
