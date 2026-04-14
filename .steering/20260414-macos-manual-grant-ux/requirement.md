# macOS 手動権限付与 UX 改善

## 背景

ad-hoc 署名ではプログラムによる TCC 権限プロンプト (AXIsProcessTrustedWithOptions, CGRequestListenEventAccess) が動作しない。v0.1.17→v0.1.19→v0.1.20 の3回の修正で確認済み。根本解決は Apple Developer Program 署名だが、即時対応として手動付与の UX を改善する。

## ゴール

macOS ユーザーが手動で Accessibility 権限を付与できるよう、Dashboard に具体的な手順とボタンを表示する。

## スコープ

### 含むもの
- Dashboard.tsx の手動付与手順 UI
- open_accessibility_settings Tauri コマンド
- バージョンバンプ 0.1.21

### 含まないもの
- Apple Developer Program 署名 (段階2)
- hook_macos.rs の権限プロンプトロジック変更

## 受け入れ条件

- [ ] 「System Settings を開く」ボタンで Accessibility ペインが開く
- [ ] 手動「+」追加の手順が日本語で表示される
- [ ] cargo check + tsc 通過
