# 設計

## 実装アプローチ

`logger.rs` の `default_log_path()` がハードコードしている `P000` を、参加者 ID
解決ヘルパーに置き換える。解決順は **GSE_PARTICIPANT_ID → GSE_PID → "P000"** の 3 段。

- `GSE_PARTICIPANT_ID` = handoff/decisions が指定する logger 用の主変数。
- `GSE_PID` = 既存の sync スクリプト (`sync-session.sh` 他) が `metrics/$PID/` 配置に
  使う変数。logger がこれにフォールバックすることで、研究者が `GSE_PID` を 1 つ設定するだけで
  `raw/`(logger) と `metrics/`(sync) の両方が揃い、**二重管理 footgun を解消**する
  (ユーザー選択: PARTICIPANT_ID→PID→P000、decisions.md D2)。
- いずれも未設定 → 従来どおり `P000` (既定挙動不変)。

ID は path-traversal/injection 防止のため allowlist バリデーション。不正値は拒否して
次候補へフォールバックし、最終的に `P000`。env 値が不正だった場合は `tracing::warn!`。

## 変更対象

### 修正するファイル
- `src-tauri/src/logger.rs`:
  - `default_log_path()` の `.join("P000")` を `resolve_participant_id()` の結果に置換。
  - doc コメントを 3 段解決 + 参加者 ID 可変に更新。
  - 新規ヘルパー (同ファイル内・OS 非依存): `is_valid_participant_id()` /
    `select_participant_id()` (純粋・テスト可能) / `resolve_participant_id()` (env 読取+warn)。
  - `#[cfg(test)]` にバリデーション/選択ロジックの単体テストを追加。

### 新規作成 / 削除するファイル
- なし。

## 影響範囲

- `lib.rs:861` が唯一の呼び出し元。シグネチャ不変のため変更不要。
- **ゴールデンスナップショット非影響**: `default_log_path()` の戻り値 (FS パス) は
  `FeatSnapshot` に含まれない (impact-analyzer 確認済)。`gse-replay --snapshot` byte-equal。
- **schema 非影響**: NDJSON 行フォーマット (`schema_dto.rs`/`emit_schema`) は不変。
- fallback (`~/Documents/GSE-sessions/`) 経路は参加者 ID を含まない既存仕様のまま
  (スコープは `$GSE_DATASET/raw/P000/` の解消に限定)。
- docs/scripts のコメント更新 (`P000 固定` 記述) は **任意の追従**。本タスクの受け入れ条件外
  だが、誤情報を残さないため最小限の追記を検討 (development-guidelines.md / data-privacy SKILL)。

## 既存パターンとの整合性

- `GSE_DATASET` / `USERPROFILE`/`HOME` と同じ `std::env::var(...).ok()` パターン。
- `tracing` のみ (println!/eprintln! 不使用)、`any` 不使用、unsafe 不要。
- 検証ロジックを純粋関数に切り出し、env を汚さずユニットテスト可能にする
  (env 変数はプロセス共有でテスト並列実行と相性が悪いため)。

## テスト戦略

- 単体テスト (logger.rs `#[cfg(test)]`):
  - `is_valid_participant_id`: 正常 (P000/P003/`a-b_C9`)、空、`..`/`../x`/`a/b`/`a\b`/`.`、
    特殊文字 (空白/null/改行/`:`/`~`/`$`)、長さ境界 (64 OK / 65 NG)。
  - `select_participant_id`: 主優先 / 主不正→副 / 全不正→P000 / trim。
- 回帰: `gse-replay --snapshot` byte-equal、`cargo test --workspace`、`emit_schema` drift なし。
- env 依存の `resolve_participant_id` は env 汚染を避け純粋関数経由で間接検証。

## ロールバック計画

単一ファイルの局所変更。問題時は `default_log_path()` を `.join("P000")` に戻すだけ
(ヘルパー削除)。データ破壊リスクなし (書き込み先ディレクトリ選択のみ)。
