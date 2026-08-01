# 実行環境の固定（未実施・実施時に埋める）

> ⚠️ **本実験は設計のみで未実施**。以下は実施時に確定させる項目の一覧である。

| 項目 | 固定方法 | 実施時に記入 |
|---|---|---|
| Rust toolchain | `rust-toolchain.toml` / `cargo --version` | TBD |
| 依存関係 | リポジトリ直下 `Cargo.lock`（実施時の commit hash を記す） | TBD |
| `gse-replay` | 本 repo の commit hash | TBD |
| `HMM_VERSION` | `engine.rs` の定数（結果にも刻む） | TBD |
| 解析（Python を使う場合） | `requirements.txt` を本ディレクトリに置く | TBD |
| OS / 端末 | 被験者端末（Windows 11 / macOS）を記録 | TBD |

⚠️ 実施は **Phase1 完了 ＋ 研究者承認による凍結解除後**。凍結中に `engine.rs` / `schema_dto.rs` を
変更してはならないため、**FS-B（Tier 0/1 特徴量）は凍結解除まで計算できない**。
