# タスクリスト

## 準備
- [x] CLAUDE.md / メモリで macOS ビルド手順を確認
- [x] `package.json` / `Cargo.toml` の存在確認

## 実装
- [x] `npm install`
- [x] `npm audit fix`（`--force` は使わない）
- [x] `loop_step.rs:180` に `#[cfg_attr(not(target_os = "windows"), allow(unused_mut))]` を追加

## 試行錯誤の記録
- [x] cfg attr をパターン要素に付与 → 失敗（`expected pattern, found '#'`）
- [x] `cfg_attr(allow)` をパターン要素に付与 → 失敗（同上）
- [x] マッチアーム本体に `cfg_attr(allow)` を付与 → 成功

## テスト
- [x] `cargo build --target aarch64-apple-darwin` (warning 0)
- [x] `npx tsc --noEmit` (パス)
- [x] `npm audit` (0 vulnerabilities)

## レビュー
- [x] code-reviewer + security-checker を並列起動

## ドキュメント
- [x] `setup-log.md` 作成
- [x] `requirement.md` / `design.md` / `tasklist.md` を遡及作成
- [x] `decisions.md` に cfg_attr 配置の判断記録

## 完了処理
- [x] code-reviewer / security-checker レビュー結果を decisions.md に追記
- [ ] git commit（ユーザー承認後）
