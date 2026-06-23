# 設計 (transfer-pipeline)

## 実装アプローチ
被験者承認のとおり **Rust 自己完結 bin** (`gse-package`)。raw NDJSON → 匿名化 (純粋関数・lib 常駐) →
age 暗号化 (bin 側・feature gate) → `P###_<入力ステム>.age`。Python/age CLI 不要。

- 匿名化は `analysis/anonymize.rs` の純粋関数 (age 非依存・常にテスト)。anonymization.md 準拠:
  key イベントの `vk`(本文再構成可)→ `category`(KeyCategory)、絶対 epoch 時刻 → session_start 相対。
- age は **optional dep + feature "package"**、bin は `required-features=["package"]`。**default の Tauri
  ビルドに age を載せない** (RAM/サイズ抑制・既存 profile 方針と整合)。

## 変更対象
### 新規作成
- `src-tauri/src/analysis/anonymize.rs` — KeyCategory / anonymize_line / find_session_start /
  anonymize_ndjson + 単体テスト (vk→category・時刻相対化・VK 非残留・バッチ)。
- `src-tauri/src/bin/package.rs` — gse-package CLI (引数パース・recipient 解決・age 暗号化・出力)
  + テスト (participant 検証・age 暗号復号ラウンドトリップ・暗号塊に平文非露出)。
### 修正
- `src-tauri/Cargo.toml` — `[[bin]] gse-package` (required-features)・`[features] package`・`age` optional dep。
- `src-tauri/src/analysis/mod.rs` — `pub mod anonymize;`。

## 影響範囲
- logger/replay/engine/features 不変 → `--snapshot` byte-equal・既存テスト緑。HMM/schema 不変。
- default ビルド (Tauri アプリ) は age を含まない (feature gate)。`cargo build --features package --bin
  gse-package` でのみ age をコンパイル。

## 既存パターンとの整合性
- bin は `emit_schema.rs` 流儀で `writeln!(io::stdout/stderr)` (println! 禁止・CLAUDE.md §8)。
- 参加者 ID 検証は lib.rs の is_valid_participant_id と同方針 (パストラバーサル防止)。
- rust-standards: anyhow ではなく軽量 CLI なので `Result<_, String>`、tracing 不使用 (CLI は writeln)。

## テスト戦略
- 単体 (default): anonymize の vk→category・相対化・VK 非残留・バッチ (5 件)。
- feature 付き: participant 検証・age 暗号→復号ラウンドトリップ・暗号塊に "alphabetic" 非露出。
- 回帰: `cargo test --workspace` 緑・`--snapshot` byte-equal。CLI smoke で実 .age 生成 + 平文非露出確認。

## ロールバック計画
- 新規ファイル + optional dep。問題時は branch 破棄。default ビルドは age 非依存なので本体への影響なし。
