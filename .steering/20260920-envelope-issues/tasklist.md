# タスクリスト

## 準備
- [x] 一次資料の確認（`blockers.md` 起票 2 / 5、`decisions.md` 判断 25 #14、`bin/replay.rs`、
      `issues/*-acceptance.sh`、`docs/glossary.md`）
- [x] §4「先に確かめること」5 項目の裏取り（`build_analysis_db.py` / `emit_schema` /
      `gse-dataset` の CI 不在 / `meta` に `os` が無い / `.gitignore` の名前依存）
- [x] grill（`grilling` skill・Opus・main）で 8 分岐を確定 → `decisions.md`
- [x] `rust-standards` / `architecture-rules` を参照

## 実装
- [x] `Cargo.toml` に `sha2` を追加（★ 既にビルドツリーにあることを確認済み）
- [x] `feat_offline/quality.rs` — `Quality.capabilities` を削除、`quality_column` の引数を
      `capabilities_declared: bool` へ
- [x] `feat_offline/mod.rs` — `QualityInputs.capabilities` → `capabilities_declared`
- [x] `bin/replay.rs` — 封筒の型 4 つ ＋ `collect_meta_session_facts` ＋ `sha256_prefix_of_file`
- [x] `bin/replay.rs` — `--features` 経路を封筒で包む ＋ usage 更新
- [x] `issues/00{1..8}-acceptance.sh` — **8 本すべて** `| jq '.rows'` ＋ コメント
- [x] `issues/007-acceptance.sh` — `capabilities` 関連 AC を封筒側へ
- [x] `scripts/check_no_feature_output.sh`（新規・共有の門）
- [x] `.github/workflows/ci.yml` — 共有の門を載せる
- [x] `.steering/20260920-envelope-issues/envelope-acceptance.sh`（新規）

## テスト
- [x] `cargo test --manifest-path src-tauri/Cargo.toml --workspace` が緑
- [x] `cargo clippy` / `cargo fmt` が緑
- [x] `envelope-acceptance.sh` が緑
- [x] 既存 8 本のうち merge 済み 6 本（001 / 002 / 003 / 005 / 007 / 008）が**実測で緑**
- [x] 004 / 006 が「配列が来ない」では赤にならないことを確認
- [x] 突然変異 M-0〜M-h を `measurements.md` に記録（⚠️ **赤になることを実測する**）

## レビュー
- [x] `code-reviewer` ＋ `security-checker` を並列（opus・範囲/禁止/締切を明記）
- [x] HIGH / MEDIUM 指摘への対応（★ HIGH 1 / MEDIUM 5 / LOW 6 を反映・判断 12〜15）
- [ ] `/cross-review` 2 巡（パス限定・⚠️ 先に secrets-filter が 0 を返すか確認）

## ドキュメント
- [x] `docs/glossary.md` に「封筒」「共有の門」を追加、「特徴行」に封筒の形を追記
- [x] `blockers.md` の起票 2 / 起票 5 を**閉じる**（⚠️ 消さない）

## 完了処理
- [x] `design.md` の最終化
- [x] `decisions.md` に実装中の判断を追記
- [ ] git commit（⚠️ `git add -A` / `git add <dir>` 禁止・明示ステージング）
