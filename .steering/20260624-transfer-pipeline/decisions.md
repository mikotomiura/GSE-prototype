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

## D7: 計画文書を実装 (age) に追従更新 — 2026-06-24, ユーザー承認
- 監査で WBS v2 / codex-review v0.4 が旧記述「ローカル ZIP 暗号化」のままと判明 (実装は D1 で age に変更済)。
  「古い情報で実装した」逆向きの乖離 (実装が先行・文書が未追従) のため、文書を実装に合わせ更新。
- 変更 2 箇所 (python-docx でセル/段落の run 内テキスト置換、書式保持):
  - `GSE_マイルストーン_WBS_半年版_v2.docx` 表 0.15 行: 「ローカル ZIP 暗号化」→「ローカル age(X25519)
    暗号化（gse-package CLI）」。
  - `ユーザー検証_codex-review_v0.4.docx` §6: 「ローカルで ZIP 暗号化し」→「ローカルで age（X25519 公開鍵
    暗号）により暗号化し（gse-package CLI）、研究者だけが秘密鍵を保持することでゼロ知識保管を実現する」。
    ([17] 引用・本文非保存原則は保持)。
- 残務 (本タスク範囲外, WBS 0.15「運用」側): Dropbox File Request 運用手順書・participant_id 再発番ルールは
  未整備。実装完了≠0.15 完了。replay の category 対応も D4 で follow-up 化済。
