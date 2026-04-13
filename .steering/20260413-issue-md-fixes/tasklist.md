# タスクリスト

## 準備
- [x] 関連する docs を読む (architecture.md, development-guidelines.md)
- [x] 影響範囲を調査 (Explore agents x3)

## 実装
- [x] Entitlements.plist に allow-jit 追加
- [x] ci.yml: macOS codesign を entitlements 付きに修正
- [x] ci.yml: Windows portable .exe をアーティファクトに追加
- [x] ci.yml: Release ジョブで portable artifact をダウンロード・添付
- [x] Dashboard.tsx: macOS/Windows 診断ガイダンス強化
- [x] lib.rs: get_diagnostics Tauri コマンド追加
- [x] tauri.conf.json: バージョンバンプ 0.1.12 → 0.1.13

## テスト
- [x] cargo check が通ることを確認
- [x] npm run build が通ることを確認

## レビュー
- [x] code-reviewer によるレビュー
- [x] HIGH 指摘への対応 (Entitlements は decisions.md に判断記録)
- [x] MEDIUM 指摘への対応 (DiagnosticInfo 型、version 追加)
- [x] security-checker によるレビュー
- [x] 既存コードの HIGH 指摘はスコープ外として decisions.md に記録

## 完了処理
- [x] design.md の最終化
- [x] decisions.md の作成
- [ ] git commit
