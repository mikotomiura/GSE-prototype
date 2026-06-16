# design.md — Task A「probe schema 拡張」

## 実装アプローチ

既存の DTO ミラー方式(`logger::LogEntry` 本体 ⇄ `schema_dto::LogEntryDto`)へ
忠実に同期追加する。NDJSON 出力は既存同様 `writeln!` ベースの **pure format 関数** +
単体テストで固定する(serde 経由にしない方針は schema_dto.rs 冒頭注記の通り)。

### NDJSON 形状(v0.3 §14)

新 4 バリアントは timestamp フィールドを `ts`(既存の `t` ではなく)で持つ — §14 設計に従う。

```jsonc
{ "type":"session_meta","track":"main","task_kind":"vibe_coding","monk_mode":true,"intervention_enabled":true,"ts":0 }
{ "type":"probe_assignment","probe_id":"...","scheduled_ts":0,"session_elapsed_ms":0 }
{ "type":"realtime_label","probe_id":"...","source":"random_probe","q1_friction":3,"q2_progress":4,"answered":true,"skip_reason":"none","latency_ms":0,"analysis_window_start_ms":0,"analysis_window_end_ms":0,"ts":0 }
{ "type":"vignette_response","vignette_id":"v1","expected_quadrant":"flow","q1_friction":2,"q2_progress":5,"ts":0 }
```

### 付随 enum(両側に定義)

| enum | NDJSON 文字列 |
|---|---|
| `Track` | `main` / `exploratory` |
| `TaskKind` | `argumentative` / `correspondence` / `creative` / `vibe_coding` |
| `ProbeSource` | `random_probe` / `self_marker` |
| `SkipReason` | `none` / `dont_remember` / `dismissed` |
| `ExpectedQuadrant` | `flow` / `stuck` / `incubation` / `idle` |

logger.rs 側は `as_str()` + `parse()`(UserLabelKind と同形)。
schema_dto.rs 側は `#[derive(Serialize, JsonSchema)] #[serde(rename_all="snake_case")]` の
DTO enum(`TrackDto` 等)。

### 不変条件の強制(illegal states unrepresentable + clamp + debug_assert)

producer が誤った組合せを作れないよう、フラットな variant への入口を
**型付きコンストラクタ**に限定する:

- `ProbeRef { RandomProbe{probe_id}, SelfMarker }` で (source, probe_id) を結合
  → source=self_marker ⇒ probe_id=null を型で保証。
- `LogEntry::realtime_label_answered(...)`: q1/q2 を `1..=5` に clamp、answered=true、
  skip_reason=None を設定。
- `LogEntry::realtime_label_skipped(...)`: q1/q2=None、answered=false、skip_reason は
  DontRemember / Dismissed のみ受ける。
- format 関数に `debug_assert!` で不変条件をセーフティネット配置。

### 数値型

- `q1_friction` / `q2_progress`: `Option<u8>`(realtime_label)/ `u8`(vignette_response)。
  1..=5 は producer clamp で担保(schemars の range 制約は既存方針通り付けない)。
- timestamp / *_ms: `u64`。

### プライバシー / セキュリティ

- 保存するのは数値・固定カテゴリ・**生成済み不透明 ID**(probe_id / vignette_id)のみ。
- probe_id / vignette_id は `serde_json::to_string` で **エスケープして** 書き出す
  (JSON injection 防止・defense in depth)。カテゴリ enum は既知安全文字列なので raw。
- 本文・タイトル・選択文字列・Unicode 文字は一切受け取らない(フィールドに存在しない)。

## 変更対象

| ファイル | 変更 |
|---|---|
| `src-tauri/src/logger.rs` | enum 5 個 + `LogEntry` に 4 variant + format 4 関数 + コンストラクタ + writer match arm + tests |
| `src-tauri/src/schema_dto.rs` | `LogEntryDto` に 4 variant + DTO enum 5 個 |
| `src-tauri/schema/current.json` | `emit_schema` 再生成で更新 |

**非対象**: `replay.rs`(Task D)、`lib.rs`(Tauri command = Task B/C の producer 呼出)。
`ReplayEvent` は不変(touch しない)ため replay.rs はコンパイル不変。

## テスト戦略

- 各 format 関数の byte-exact 単体テスト(既存 `*_line` テスト群と同形)。
- enum `as_str`/`parse` round-trip + 未知文字列拒否。
- 不変条件テスト: skipped ⇒ q1/q2=null、answered ⇒ 1..=5(clamp 含む)、
  self_marker ⇒ probe_id=null。
- schema drift: `cargo run --bin emit_schema` 出力が `schema/current.json` と byte-equal。

## リスク

- field 順序: schemars は properties/required をアルファ順に出力するため Rust の
  フィールド宣言順は schema 出力に影響しない。oneOf の variant 順は宣言順 → 末尾追加。
- gse-dataset 側 `schema/current.json` のコピーは別運用(§10.3.1)。本タスクは
  prototype 側ゴールデン更新まで。
