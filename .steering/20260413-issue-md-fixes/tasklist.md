# タスクリスト

## 準備
- [x] 関連する docs を読む (architecture.md, development-guidelines.md)
- [x] 影響範囲を調査 (Explore agents x3)

## 実装 — Phase 1 (v0.1.13, commit a9f62b7)
- [x] Entitlements.plist に allow-jit 追加
- [x] ci.yml: macOS codesign を entitlements 付きに修正
- [x] ci.yml: Windows portable .exe をアーティファクトに追加
- [x] ci.yml: Release ジョブで portable artifact をダウンロード・添付
- [x] Dashboard.tsx: macOS/Windows 診断ガイダンス強化
- [x] lib.rs: get_diagnostics Tauri コマンド追加
- [x] tauri.conf.json: バージョンバンプ 0.1.12 → 0.1.13

## 実装 — Phase 2 (v0.1.14, macOS Input Monitoring 根本修正)
- [x] Cargo.toml: core-graphics 0.23→0.24, core-foundation 0.9→0.10
- [x] Cargo.lock: バージョン競合解消 (core-foundation 2版→1版に統一)
- [x] ci.yml: --options runtime を除去 (ad-hoc 署名との矛盾解消)
- [x] lib.rs: get_diagnostics に macOS CGPreflightListenEventAccess 追加
- [x] tauri.conf.json: バージョンバンプ 0.1.13 → 0.1.14

## テスト
- [x] cargo check が通ることを確認 (Windows)
- [x] npm run build が通ることを確認
- [ ] macOS 実機テスト (v0.1.14 リリース後)

## レビュー
- [x] code-reviewer によるレビュー (Phase 1)
- [x] security-checker によるレビュー (Phase 1)

## 完了処理
- [x] decisions.md の作成
- [ ] git commit + push + tag
