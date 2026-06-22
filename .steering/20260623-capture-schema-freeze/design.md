# 設計 — capture-schema-freeze (WBS M0 捕捉スキーマ凍結)

## 実装アプローチ

`schema_dto.rs`(schema 生成用 DTO)と `logger.rs`(NDJSON 書き出し実体)の**2 箇所平行定義**という
既存ミラー構造に乗り、content-free な捕捉フィールドを 1 回の coordinated schema bump で追加する。
4 つの追加すべてを **後方互換 (`Option` / `#[serde(default)]`)** とし、既存 fixture
(`minimal.ndjson` 等、新フィールド無し)のパース失敗を防ぐ(影響分析 HIGH 指摘)。

FeatSnapshot(features/HMM)には一切触れないため `gse-replay --snapshot` は byte-equal を維持。

## 変更対象

### ① Paste 文字数 (WBS 0.9 capture) — `external_paste_chars`
- `logger.rs` `LogEntry::Paste { timestamp }` → `{ timestamp, external_paste_chars: Option<u64> }`、
  `format` 関数と match arm を更新。
- `schema_dto.rs` `Paste { t }` → `{ t, external_paste_chars: Option<u64> }`。
- `lib.rs` L960 のペースト処理: `is_paste` 検出時に**クリップボードのテキスト長のみ取得 → 文字数を数えて
  即破棄**し、`LogEntry::Paste { external_paste_chars: Some(n) }` を送る。
- `bin/replay.rs` `ReplayEvent::Paste` に `external_paste_chars: Option<u64>` 追加(default で旧 fixture 互換)。
- **⚠ 設計判断 P(privacy・要承認)**: 後述。

### ② 介入応答 / dismiss 理由 (WBS 0.8) — 新 variant `InterventionResponse`
- 現状 `record_intervention_dismiss`(lib.rs L186)は `intervention.record_dismiss` で**メモリ状態
  (cooldown/recent_dismiss)のみ更新**し、**NDJSON には残らない**(確認済)。
- 新 `LogEntryDto::InterventionResponse { action, reason, ts }` を追加。
  - `action`: `InterventionActionDto`(既存 nudge/wall/…)を再利用。
  - `reason`: 新 enum `DismissReasonDto`(4択 + 無言)。
- `logger.rs` に `LogEntry::InterventionResponse` + `format_*` + match arm + `DismissReason` enum
  (`as_str`/`parse`、既存 `SkipReason` 流儀)を追加。
- `lib.rs` `record_intervention_dismiss` を `reason: String` 引数追加に拡張 → state 更新に加えて
  **logger チャンネルへ `InterventionResponse` を送出**。
- フロント `src/components/Overlay.tsx`: Nudge カードに 4択 dismiss UI を追加し
  `invoke("record_intervention_dismiss", { action, reason })`。フェード/無選択時は `silent`。
- `bin/replay.rs`: 新 variant は既存 `_ => {}` で読み飛ばし(panic なし)。fixture に 1 行追加して確認。

### ③ session condition (WBS 0.11) — `SessionMeta.condition`
- 新 enum `ConditionDto`/`Condition` { `blind_calibration`, `a`, `b`, `nudge`, `defer`, `baseline` }。
- `schema_dto.rs` `SessionMeta` に `condition: Option<ConditionDto>` 追加、`logger.rs` 同期、
  `lib.rs` `record_session_meta` に引数追加、`src/App.tsx` invoke に `condition` 追加(既定 `baseline`)。
- `calibration_eval.rs` の `SessionMeta` deserialize は `#[serde(default)]` で無害。

### ④ label_pool (WBS 0.4) — `SessionMeta.label_pool`
- 新 enum `LabelPoolDto`/`LabelPool` { `calibration_blind`, `post_intervention` }。
- **配置判断 L(要承認)**: 後述。推奨 = SessionMeta にセッション単位で付与(condition から導出可能だが
  X1 判定が `calibration_blind` のみを使うため明示タグが安全)。`Option` で後方互換。

### schema 同期(必須手順・全変更共通)
- `cargo run --bin emit_schema > src-tauri/schema/current.json` → diff 確認。
- gse-dataset 側 `schema/current.json` へコピー → `python scripts/check_schema_parity.py
  --dataset C:/gse-dataset` exit 0。

## 既存パターンとの整合性

- enum 2 箇所平行定義: `Track`/`TaskKind`/`SkipReason`/`ProbeSource` と同一流儀
  (DTO=`#[serde(rename_all="snake_case")]`、logger=`as_str`/`parse`)。
- 新フィールドはすべて `Option`(影響分析の後方互換指摘に従う)。
- ペースト検出は既存 `is_paste`(hook_windows/macos)を流用、クリップボード読みは
  **フックコールバック外**(lib.rs main 側)で実施 → hook-constraints(ブロッキング禁止)に抵触しない。

## テスト戦略

- 単体: `DismissReason`/`Condition`/`LabelPool` の `as_str`/`parse` round-trip
  (`new_enums_*` テスト群に追加)。`format_*_line` の新フィールド整形テスト。
- 回帰: `gse-replay --snapshot` byte-equal(FeatSnapshot 不変)。
- パース互換: `paste_event_parses_and_is_skipped_from_replay` が `Option` 化で緑のまま。
  新 variant 行を fixture に足して replay が panic しないこと。
- schema: `emit_schema` 再生成 → `current.json` byte-equal → gse-dataset parity 緑。
- 手動(実機): Nudge dismiss で 4択 → NDJSON に `intervention_response` 行・ペースト時に
  `external_paste_chars` が出る・**中身は一切出ない**。

## 要承認の設計判断(Step C — ユーザー承認待ち)

- **判断 P(privacy)**: `external_paste_chars` を得るには **ペースト時にクリップボードのテキスト長を
  読む**必要がある(GSE は現在クリップボードに一切触れない設計)。提案 = 長さ(整数)のみ取得し
  **中身は即破棄・保存も送信もしない**。これは v0.4 (b) 指標 `manual_contribution_ratio` の分母に必須。
  → GSE のプライバシー姿勢を「クリップボード非接触」から「ペースト時に長さのみ読む」へ変える点の承認。
- **判断 L(label_pool 配置)**: SessionMeta にセッション単位で付与(推奨)。
- **判断 D(dismiss UI 範囲)**: 本タスクは Nudge の 4択 dismiss を実装。Wall の early-unlock/Zen 完了等の
  応答ログは variant を汎用化しておき、配線は別タスク(過剰スコープ回避)。

## 実装中に判明した事実 (最終化)

- **クリップボード読みの実装**: 既存の `windows`/`core-graphics` crate での自前 clipboard 実装は
  unsafe (NSPasteboard/Win32 DataExchange) が増えるため、`arboard`(default-features=false で
  画像デコーダ除外、CD6)を `input/clipboard.rs` に隔離。`get_text()` の長さのみ取得・即破棄。
- **1Hz ループ非ブロッキング化** (CD5): クリップボード open/close が競合で数十 ms ブロックしうるため、
  is_paste 時に `thread::spawn` で読み + Paste 送信を逃がした。`t` は paste 時刻で確定済みで順序不変。
- **`record_intervention_dismiss` は元々 NDJSON 非記録**だった (memory state 更新のみ) ことを確認。
  本タスクで `InterventionResponse` 行の emit を追加し、初めてユーザー応答が NDJSON に残る。
- レビュー結果: code-reviewer / security-checker とも CRITICAL/HIGH なし。security は
  「キーストローク/クリップボード/成果物の中身が NDJSON・metrics・共有物に漏れない」を合格と結論。

## ロールバック計画

- 全変更が新フィールド(Option)/新 variant の**追加のみ**。問題時はブランチ破棄で main に影響なし。
- schema は `current.json` を git revert すれば戻る。features/HMM 不変ゆえ既存データ解釈に影響なし。
