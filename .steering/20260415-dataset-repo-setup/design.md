# design.md — gse-dataset Phase 1 対応 (v2 — /reimagine 再生成)

> 本 design は requirement.md のみに立脚してゼロから生成。v1 の用語・構造を自動で
> 引き継がない。v1 との比較は `design-comparison.md` を参照。

## 核心的な問い直し

requirement を read した上で、v1 の前提のうち **2 つ** を疑う:

**疑い①: schema を手書き v1 → v2 → v3 と増やしていく前提**
- 根本原因は「Rust 型 (logger::LogEntry) と JSON Schema が別の真実として存在」する二重管理にある
- Phase 2a で `feat` に新フィールドが入る、Phase 2b で `ime_shadow` が入る、Phase 3 で LR スコアが入る。そのたびに v3/v4/v5 と手で追随させるのは破綻する
- **本質的解決**: Rust 型から JSON Schema を自動生成し、gse-dataset 側には **生成物** (`schema/current.json`) のみ置く。gse-prototype の `cargo build` が schema.json の変化を機械的に検知する

**疑い②: anonymized NDJSON をコミットすることが Phase 1 の「共有」である前提**
- 真のニーズは「macOS と Windows のデータを混ぜて Phase 2a の Go/No-Go を判断できる状態」
- それに **必要十分** な情報は `gse-replay --metrics --json` の出力 (SessionMetrics JSON、1 KB/session) であって、40 KB × N の anonymized NDJSON ではない
- anonymized NDJSON の価値が出るのは **Phase 2 の ML training データ準備時**、Phase 1 / 2a の段階ではオーバースペック
- ただし anonymize pipeline 自体は Phase 2 で必ず要るので **スクリプトは用意しておく、コミットは Phase 2 まで先送り**

## 実装アプローチ (v2)

### A. 共有層の最小化 — metrics.json を「共有の主役」にする

```
gse-dataset/metrics/P000/<os>/gse_YYYYMMDD_HHMMSS.metrics.json
```

- 各端末で `cargo run --bin gse-replay -- <raw.ndjson> --metrics --json` の出力を**直接コミット**
- プライバシー: 含まれるのはクラス別 precision / recall / F1、混同行列、中央値のみ。**VK 情報・個別 timestamp を一切含まない**
- サイズ: 1 KB/session、1000 セッション貯めても 1 MB。git 管理に自然
- Phase 2a Go/No-Go 判断 (Stuck precision 平均 ≥ 0.6) はこれだけで算出可能

### B. Schema 生成層 — Rust 型から `schema/current.json` を自動生成

gse-prototype 側の最小変更:

```rust
// src-tauri/Cargo.toml (dev-dependency or bin-only)
[dependencies]
schemars = "0.8"
```

```rust
// src-tauri/src/bin/emit_schema.rs (new ~30 行)
use schemars::schema_for;
fn main() {
    let schema = schema_for!(gse_next_lib::logger::LogEntryDto);
    println!("{}", serde_json::to_string_pretty(&schema).unwrap());
}
```

ただし LogEntry は書き込み専用 enum で Serialize 派生がない。**薄い DTO ミラー型** を作ってそこに `#[derive(Serialize, JsonSchema)]` を付ける (production path に影響しない)。

CI (Actions) への追加:
```yaml
- name: Schema drift check
  run: |
    cargo run --bin emit_schema > /tmp/emitted.json
    diff /tmp/emitted.json ../gse-dataset/schema/current.json
```
→ **schema drift が存在すると CI が落ちる**

### C. Anonymize pipeline は保守のみ、コミットは先送り

- `scripts/anonymize.py`: 現行が `key` 以外 passthrough 実装なので、`user_label` は既に透過。**コード変更不要**
- `.gitignore` の `anonymized/**/*.ndjson` 行は **維持** (requirement 受け入れ条件 4 を意図的に却下)
- 代わりに README に「Phase 2 で ML データ作成時にコミット方針を再判断」と明記

### D. import_sessions.py の OS 別対応

requirement 3 に従う:
- `--os macos|windows` フラグで `raw/P000/<os>/` に配置
- 現行の `raw/P000/` ベタ置きから変更

## 変更対象 (v2)

### gse-dataset 側

| ファイル | 操作 | 内容 |
|---|---|---|
| `schema/current.json` | 新規 (機械生成物) | gse-prototype の emit_schema 実行結果をコミット |
| `schema/v1.json` | 削除 | 廃止 (手書き schema を持たない) |
| `schema/README.md` | 新規 | 「このディレクトリは gse-prototype から機械生成、手編集禁止」 |
| `scripts/validate_schema.py` | 修正 | schema/current.json 参照に変更 |
| `scripts/import_sessions.py` | 修正 | `--os` フラグ |
| `scripts/aggregate_metrics.py` | 新規 | `metrics/**/*.metrics.json` を読み macro F1 / Stuck precision を全体集計 |
| `.gitignore` | 維持 | anonymized/ は ignored のまま (方針変更) |
| `metrics/.gitkeep` | 新規 | ディレクトリ作成 |
| `metrics/P000/macos/*.metrics.json` | 新規 | 初回 2 件の metrics 出力 |
| `README.md` | 全面改訂 | v2 方針反映 |

### gse-prototype 側

| ファイル | 操作 | 内容 |
|---|---|---|
| `src-tauri/Cargo.toml` | 追記 | `schemars = "0.8"` |
| `src-tauri/src/bin/emit_schema.rs` | 新規 ~30 行 | schema 出力バイナリ |
| `src-tauri/src/schema_dto.rs` | 新規 | LogEntry の JsonSchema 派生ミラー DTO |
| `.github/workflows/ci.yml` | 追記 | schema drift 検知ステップ |
| `docs/development-guidelines.md` | §追記 | gse-dataset 連携 + metrics 共有プロトコル |
| `CLAUDE.md` | 1 行 | データ repo ポインタ |

## 既存パターンとの整合性

- **Replay-as-Truth** との共存: gse-replay は変更せず、既存の `--metrics --json` 出力を共有に使う
- **production path 無変更**: schemars は DTO 専用、`logger.rs::LogEntry` 本体には触らない (/reimagine v2 原則維持)
- **CI matrix**: 既に windows/macos で走る既存 check ジョブに schema drift 行を追加
- **gse-prototype 側のタスク粒度**: 「dataset 対応 = gse-prototype の機能追加」として扱い、両 repo の PR を 1 タスクで完結する

## テスト戦略

- **T-V1**: `cargo run --bin emit_schema` が valid JSON を吐く (unit test 不要、CI が diff で検証)
- **T-V2**: 生成された schema/current.json で 2 セッション NDJSON を validate → PASS
- **T-V3**: validate_schema.py が `schema/current.json` をデフォルトで読む
- **T-V4**: `aggregate_metrics.py` が metrics/P000/**/*.metrics.json を読んで全体 macro F1 / Stuck precision を算出 (ユニットテスト不要、実データで動作確認)
- **T-V5**: CI drift check が意図的に schema を書き換えると FAIL する (手動検証)
- **T-V6**: `.gitignore` 挙動 (`git check-ignore` で raw/anonymized が ignored、metrics/schema が tracked)

## ロールバック計画

- gse-prototype: `emit_schema` bin と `schemars` 依存を revert、CI 行削除。機能変化ゼロ
- gse-dataset: `schema/current.json` 削除、`schema/v1.json` 復元。validate_schema.py の schema 参照を revert

## 既知のトレードオフ

- **受け入れ条件 4 (anonymized を tracked にする) を実質却下**: requirement 作成時点で想定していた方針を Phase 2 に先送りする。判断根拠は本 design 冒頭「疑い②」。要承認
- **schemars 追加の build time 増加**: ~数秒。CI には大きな影響なし
- **DTO ミラー型のメンテナンス**: LogEntry に新バリアント追加時に DTO 側も追随が必要。ただし CI drift check で検知できるため漏れない

## Phase 2 へのレール敷き

v2 を採用した場合の Phase 2 移行:
- Phase 2a (Synthetic Friction): `aggregate_metrics.py` で Stuck precision 平均を算出 → Go 判定後に HMM 触る
- Phase 2 (ML training): `.gitignore` の `anonymized/**/*.ndjson` を外す判断をここで行う。`anonymize.py` と pipeline は既に稼働中なのでコマンド 1 発で準備完了
- Phase 2b (IME Shadow): `schema_dto.rs` に `ImeShadow` バリアント追加 → CI drift check で gse-dataset も同期が必要と通知される

## 設計判断の履歴

- 実行回数: 1 回目
- 採用: v2 (再生成案)
- 根拠: Phase 2a/2b/3 で schema 拡張が既定 → 手書き bump 運用は破綻する構造的問題を v2 が機械生成で解決する。Phase 2a の Go/No-Go 判定に必要なのは metrics.json のみであり、anonymized NDJSON の commit は Phase 2 ML 訓練時まで先送りして問題なし (`.gitignore` 1 行で移行可能な不可逆性のない判断)
