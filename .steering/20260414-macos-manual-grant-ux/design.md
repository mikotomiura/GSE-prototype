# 設計

## 実装アプローチ

手動権限付与の具体的手順を Dashboard に表示し、System Settings を開くボタンを提供する。

## 変更対象

### 修正するファイル
- `src/components/Dashboard.tsx` — 手動付与手順 UI + open ボタン
- `src-tauri/src/lib.rs` — `open_accessibility_settings` コマンド追加
- `src-tauri/Cargo.toml` — version 0.1.21
- `src-tauri/tauri.conf.json` — version 0.1.21

## テスト戦略
- cargo check (Windows)
- npx tsc --noEmit
- macOS 実機テスト (GitHub Actions リリース後)
