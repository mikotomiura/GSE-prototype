# Decisions — gse-dataset Phase 1 対応

## D1: v2 採用 (schemars 機械生成 + metrics-first sharing)

### 背景
/reimagine で v1 (手書き schema bump + anonymized commit) と v2 (Rust 型から schema 生成 + metrics-first) を比較、v2 を採用。

### 根拠
- Phase 2a/2b/3 で schema 拡張が既定。v1 の手書きバージョニング (`v1.json` → `v2.json` → ...) は運用で破綻する構造的問題
- v2 は CI drift check で schema 不整合を機械的にブロック、Rust 型 (`schema_dto.rs`) を単一の真実とする
- Phase 1 の Go/No-Go 判定に必要なのは metrics.json のみで、anonymized NDJSON のコミットはオーバースペック
- anonymized commit は Phase 2 ML 訓練時に `.gitignore` 1 行で移行可能な不可逆性のない判断

## D2: schema_dto.rs を logger::LogEntry のミラーとして分離

### 背景
`LogEntry` 本体は `writeln!` + 手書き format で NDJSON を吐いている (float 小数桁数固定で gse-replay ゴールデン byte-equal を守るため)。`serde::Serialize` 経由にすると float フォーマットが変わって snapshot 回帰が壊れる。

### 決着
`schema_dto.rs` に `LogEntryDto` を新設し、`schemars::JsonSchema` 派生専用のミラー型として扱う。production path (`logger.rs`) には `Serialize` を追加せず、emit_schema bin のみが DTO を使用。同期漏れは CI drift check (`emit_schema` 出力 vs コミット済み `schema/current.json`) で検知。

## D3: Meta の 2 形状を Option 3 フィールド並列で表現

### 背景
`{"type":"meta","session_start":_,"hmm_version":_}` と `{"type":"meta","session_end":_}` の 2 形状を schemars の tagged enum で別 variant にすると serde tag "meta" の衝突で コンパイル or runtime エラーになる。

### 決着
単一 `Meta { session_start: Option, hmm_version: Option, session_end: Option }` variant で実装。schema 上は排他制約を表現できない loose な状態になるが、producer (`logger.rs`) 側の事実上のルールとして doc コメントに明記。validator 側で厳密チェックしたい場合は外部 JSON Logic で補うか、v3 で `allOf` + `not` を手書き追加する。

## D4: Phase 2a Go/No-Go 閾値を定数化 + n >= 5 ガード

### 背景
code-reviewer HIGH 指摘: `aggregate_metrics.py` で Stuck precision >= 0.6 のマジックナンバー、n=1 でも "GO" が表示されていた (誤った判断を誘発)。

### 決着
`STUCK_GO_THRESHOLD = 0.6` + `MIN_SESSIONS_FOR_GATE = 5` を定数化。n < 5 の場合は `INCONCLUSIVE (n=N < 5 sessions, collect more GT data)` を出力。0.6 の根拠は docstring で `baseline_metrics.md` / roadmap を参照。

## D5: CRLF 問題を .gitattributes で LF 固定

### 背景
code-reviewer MEDIUM: Windows runner の git checkout で `autocrlf = true` の場合 `schema/current.json` が CRLF に変換され、Rust 側 emit_schema (LF 出力) との diff が常時 FAIL。

### 決着
両 repo の `.gitattributes` で `schema/current.json text eol=lf` を強制。`tests/snapshots/*.json` / `tests/fixtures/*.ndjson` / `metrics/**/*.metrics.json` も同様。

## D6: `import_sessions.py --source` の path validation

### 背景
security-checker MEDIUM: `--source /etc` 等の system path を通すと、命名規則に偶然一致したファイルが raw/ に取り込まれる恐れ。

### 決着
`--source` を `resolve()` してから `$HOME` または repo root 配下であることを必須化。system path を指定すると明示的エラーで拒否。将来 `--allow-system-paths` を追加する余地を残す (未実装)。

## D7: anonymize.py は変更なし (既に passthrough で user_label 対応済み)

### 背景
現行実装は `key` バリアントのみ vk→cat 変換、他はそのまま通す設計。

### 決着
`meta` (hmm_version 含む) / `session_start` / `feat` / `ime_state` / `user_label` すべて passthrough で、Phase 1 の新規バリアント `user_label` も自動的に対応済み。コード変更不要。Phase 2 で ML 訓練データ整備時に再検証。

## D8: Phase 1 では anonymized NDJSON をコミットしない

### 背景
requirement.md 受け入れ条件 4 は「anonymized/**/*.ndjson を tracked に」だったが、design v2 で Phase 2 まで先送りと判断。

### 決着
`.gitignore` の `anonymized/**/*.ndjson` を維持。`metrics/**/*.metrics.json` のみが Phase 1 の git-tracked データ。Phase 2 ML 訓練データ準備時に判断し直す (1 行変更で移行可能)。

## レビューで持ち越した LOW

1. `P000` regex の柔軟性 (`^P\d{3,4}$`) — 運用で混乱が出たら修正
2. `validate_schema.py` の Draft fallback WARN — 任意、Phase 2 で整理
3. `schema_dto.rs` の round-trip 単体テスト — Phase 2 で追加候補
4. `schemars = { version = "0.8", default-features = false }` — ビルド時間が気になったら
5. pre-commit フック (raw/ staging 防止) — 必要になったら別タスク
6. `cargo audit` の CI 追加 — 既にスコープ外として別タスク予定
