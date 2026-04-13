# 設計: macOS Input Monitoring 権限問題の改善

## アプローチ

Apple Developer ID なし（ad-hoc 署名）の制約下で、4フェーズの改善を行う。

## Phase 1: CI 署名修正 (ci.yml)

`codesign --force --deep --sign -` → レイヤード署名:
1. 内部バイナリ署名: `codesign --force --sign - --entitlements ... "$APP/Contents/MacOS/gse-next"`
2. 外部バンドル署名: `codesign --force --sign - --entitlements ... "$APP"`
3. CDHash を CI ログに出力

## Phase 2: バックエンド診断強化

### 2a. hook.rs + hook_macos.rs
- `CONSECUTIVE_TAP_FAILURES: AtomicU32` を追加
- 失敗時にインクリメント、成功時にリセット

### 2b. lib.rs 診断拡張
- `consecutive_tap_failures`: タップ連続失敗回数
- `bundle_path`: 実行中の .app パス
- `quarantine_present`: quarantine xattr の有無
- `codesign_valid`: コード署名の有効性

### 2c. lib.rs TCC リセットコマンド
- `reset_input_monitoring`: `tccutil reset ListenEvent` + `CGRequestListenEventAccess()`
- macOS 専用、Windows では no-op

## Phase 3: フロントエンド UX (Dashboard.tsx)

段階的トラブルシューティング:
- 0-30s: 標準メッセージ（System Settings でチェック）
- 30-60s: 「チェック済みなら一度オフ→オンに」（CDHash 対策）
- 60-90s: codesign_valid に応じた条件分岐メッセージ
- 90s+: 「権限をリセット」ボタン + 手動コマンド

## Phase 4: バージョン同期
- Cargo.toml + tauri.conf.json → 0.1.16

## 変更対象ファイル

| ファイル | 変更種別 |
|---|---|
| `.github/workflows/ci.yml` | CI 署名修正 |
| `src-tauri/src/input/hook.rs` | AtomicU32 追加 |
| `src-tauri/src/input/hook_macos.rs` | 失敗カウンタ更新 |
| `src-tauri/src/lib.rs` | 診断拡張 + TCC リセット |
| `src/components/Dashboard.tsx` | UX 改善 |
| `src-tauri/Cargo.toml` | バージョン |
| `src-tauri/tauri.conf.json` | バージョン |
