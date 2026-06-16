# tasklist.md — Task A「probe schema 拡張」

## 実装
- [x] logger.rs: enum `Track` / `TaskKind` / `ProbeSource` / `SkipReason` / `ExpectedQuadrant`(as_str/parse)
- [x] logger.rs: `ProbeRef`(RandomProbe/SelfMarker)で source+probe_id 結合
- [x] logger.rs: `LogEntry` に `SessionMeta` / `ProbeAssignment` / `RealtimeLabel` / `VignetteResponse`
- [x] logger.rs: format 4 関数 + 不変条件コンストラクタ(answered/skipped, clamp 1..=5)
- [x] logger.rs: writer loop に 4 match arm 追加
- [x] schema_dto.rs: `LogEntryDto` に 4 variant + DTO enum 5 個 同期追加

## 不変条件の強制
- [x] skip(answered=false)⇒ q1/q2=null
- [x] answered=true ⇒ q1/q2 = 1..=5(clamp)
- [x] source=self_marker ⇒ probe_id=null(ProbeRef で型保証)
- [x] probe_id / vignette_id を serde_json escape で書き出し
- [x] skip_reason=None 受領時は Dismissed 正規化 + `tracing::warn`(レビュー指摘)

## 検証
- [x] `cargo test --lib`(97 passed) — format byte-exact / enum round-trip / 不変条件 / e2e writer
- [x] `cargo run --bin emit_schema > schema/current.json` 再生成 → drift 緑(byte-equal 確認)
- [x] `cargo clippy` — 変更ファイル新規警告ゼロ(既存 2 件のみ・未変更)
- [x] code-reviewer + security-checker 並行起動 → HIGH/CRITICAL なし
- [x] レビュー指摘の高価値分を本タスクで消化: e2e writer test / as_str リテラル guard test / warn

## スコープ確認(やらない)
- [x] replay.rs / lib.rs は touch しない(Task B/C/D)→ ReplayEvent 不変・replay.rs コンパイル不変
- [x] beacon / waveform / checkpoint / dismiss / ai_reference は追加しない(D-14 延期)
