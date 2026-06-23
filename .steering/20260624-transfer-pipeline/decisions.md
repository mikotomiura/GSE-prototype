# 設計判断 (transfer-pipeline)

## D1: 実装形態 = Rust 自己完結 bin (age crate) — ユーザー承認
- D6 当初案 (Python anonymize.py + age CLI) から変更。被験者 (Mac/Win 混在・非技術者) に Python/age
  インストールを要求しない自己完結 exe が圧倒的に堅実。Rust-centric とも整合。

## D2: age は optional dep + feature gate (default ビルドに載せない)
- `age = { optional = true }` + `[features] package` + bin `required-features=["package"]`。
- Tauri アプリ本体 (default-run = gse-next) は age を一切コンパイルしない (RAM/サイズ・既存 profile.dev の
  OOM 対策方針と整合)。`cargo build --features package --bin gse-package` でのみ生成。

## D3: 匿名化は anonymization.md 準拠の純粋関数 (lib 常駐)
- key の vk → KeyCategory (本文再構成不能化)、絶対 epoch (t/ts/session_start/session_end/scheduled_ts/
  analysis_window_*) → session_start 相対。継続時間系 (idle_ms/dwell_ms/latency_ms/...) は触らない。
- 特徴量再計算 (D6 Replay-as-Truth) に必要な backspace/delete の区別は KeyCategory が保持。
- age 非依存なので `cargo test --workspace` で常に検証される。

## D4: replay の category 対応は follow-up (本タスク範囲外)
- 匿名化 NDJSON での特徴量再計算 (D6) には replay が `category` を読む拡張が要るが、データは age 暗号化
  保存され不可逆ではない (解析ツールは後付け可)。本タスクは「匿名化→暗号化→提出」までを閉じる。

## D5: recipient (研究者 age 公開鍵) は運用入力
- `--recipient <age1... | pubkey.txt>` で指定。本実装に鍵は同梱しない (偽鍵を配布しない)。研究者が
  age keypair を生成し公開鍵を被験者配布パッケージに入れる (配布安全=公開鍵のみ)。

## D6: 出力名 = P###_<入力ステム>.age
- 入力 raw (gse_YYYYMMDD_HHMMSS.ndjson) のステムを踏襲しセッション識別を保持 (chrono 依存回避)。
- 暗号塊なので転送経路 (Dropbox File Request) は信用不要 (D6)。
