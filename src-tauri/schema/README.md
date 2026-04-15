# NDJSON Schema (auto-generated)

`current.json` は **機械生成物** — 手編集禁止。

## 生成コマンド

```bash
cd src-tauri
cargo run --bin emit_schema > schema/current.json
```

## ソース

`src-tauri/src/schema_dto.rs` の `LogEntryDto` 型から `schemars::schema_for!` で派生。

## なぜ schema/ が `src-tauri/` の下にあるか

Rust 型 (`schema_dto.rs`) が単一の真実 (single source of truth) なので、それに最も近い位置に
生成物を置く。gse-dataset repo 側の `schema/current.json` は本ファイルのコピーで、
`docs/development-guidelines.md §Session データ管理` の同期手順に従って更新する。

## 更新タイミング

- `logger::LogEntry` に新バリアントやフィールドが入ったら、`schema_dto.rs` を同期して
  `cargo run --bin emit_schema > schema/current.json` で再生成
- CI (`.github/workflows/ci.yml` の `check` ジョブ) が `emit_schema` の現在の出力と
  本ファイルを diff して、drift を機械的にブロックする

## 形式

JSON Schema draft-07 (schemars 0.8 のデフォルト)。`oneOf` で 6 バリアント
(`meta` / `session_start` / `key` / `feat` / `ime_state` / `user_label`) を表現。
