# decisions.md — Task A「probe schema 拡張」

## TA-1 timestamp は新バリアントで `ts`(既存 `t` ではなく)
- **判断**: 新 4 バリアントの timestamp フィールド名は v0.3 §14 設計どおり `ts` を使う。
- **根拠**: §14 の jsonc 例が `ts` / `scheduled_ts` で統一。既存 `t` に揃えると設計書と乖離し、
  Task D の解析・gse-dataset 側ドキュメントとの突合が崩れる。schema は producer 出力に従う。

## TA-2 不変条件は「型 + コンストラクタ + clamp + debug_assert」の4層
- **判断**: `ProbeRef`(RandomProbe/SelfMarker)で (source, probe_id) を結合し
  `self_marker⇒probe_id=null` を**型**で保証。`realtime_label_answered/_skipped`
  コンストラクタで q1/q2 を 1..=5 clamp・answered/skip_reason を整合。format 関数の
  `debug_assert!` は安全網(release で消えるが、コンストラクタ経由なら不要)。
- **根拠**: schemars の Option は緩く、schema では強制不能(D-7 の既存方針)。producer 側で
  illegal states unrepresentable にするのが最も堅牢(code-reviewer も「秀逸」と評価)。
- **残る穴(許容)**: enum variant フィールドは Rust 仕様で常に pub のため、
  `LogEntry::RealtimeLabel { .. }` 直接構築は同一 crate から可能。doc コメントで
  「コンストラクタ経由を推奨」と明示し、producer(Task B/C)は構築子のみ使う運用で担保。

## TA-3 replay.rs(ReplayEvent)は Task A で触らない
- **判断**: `src-tauri/src/bin/replay.rs` の `enum ReplayEvent`(読み込み専用ミラー)へ
  新バリアントを**追加しない**。Task D(解析)の責務として送る。
- **根拠**: スコープ(D-14)で解析は Task D。現状 replay は未知 `type` を parse-fail として
  skip(`parse_failed_lines` カウント + warn)するため、新バリアントを含む NDJSON でも
  **クラッシュしない**(file-finder 確認)。Task A では ReplayEvent 不変 = replay.rs は
  コンパイル不変。Task D で probe_id 起点の時間隔離窓抽出を実装する際に read-skip /
  consumption variant を追加する。

## TA-4 logger `as_str` ↔ schema snake_case の drift をローカルテストで守る
- **判断**: 付随 enum の `as_str()` 期待値をリテラル固定する
  `new_enum_as_str_matches_schema_snake_case` テストを追加。
- **根拠**: CI の schema drift check は **DTO 側のみ**(emit_schema vs current.json)を
  byte 比較する。logger 側 `as_str` を "vibecoding" 等とタイポしても、NDJSON 実出力が
  schema と食い違うだけで **どのテストも落ちない** 穴(code-reviewer LOW 指摘)。
  両側手書きの整合を保つ砦としてリテラル固定テストを置く。

## 後続タスクへの申し送り(レビュー指摘・本タスク範囲外)
- **Task B/C 配線 PR の必須レビュー観点(security-checker MEDIUM)**:
  `probe_id` / `vignette_id` は **backend 生成の不透明 ID**(UUID 等 `[A-Za-z0-9_-]`)に
  限定する。ユーザー入力・ファイル名・ウィンドウタイトルを ID に混ぜると、escape された
  状態でローカルログに残り data-privacy ルール1違反になりうる。可能なら ID 生成を
  ファクトリ/newtype に閉じ込め、外部由来 String を受け取れなくする。
- **validator 側補検証(code-reviewer LOW)**: realtime_label の不変条件
  (skip⇒null 等)を JSON Logic 等で外部検証するか否かは Task D / 配線時に決める。
