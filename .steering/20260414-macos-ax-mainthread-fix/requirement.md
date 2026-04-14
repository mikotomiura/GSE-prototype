# macOS AXIsProcessTrustedWithOptions メインスレッド修正

## 背景

v0.1.19 で `AXIsProcessTrustedWithOptions` を導入したが、フックスレッド (バックグラウンド) から直接呼び出しており、macOS のネイティブダイアログが表示されなかった。`AXIsProcessTrustedWithOptions` は NSApplication ランループ (メインスレッド) 上でのみダイアログを表示でき、バックグラウンドからは `false` を返すだけで静かに失敗する。

## ゴール

`ax_prompt_for_trust()` を GCD `dispatch_sync_f` でメインスレッドに dispatch し、ネイティブダイアログを確実に表示する。URL scheme フォールバックも復元する。

## スコープ

### 含むもの
- `src-tauri/src/input/hook_macos.rs` の修正
- バージョンバンプ 0.1.19 → 0.1.20

### 含まないもの
- `lib.rs`, `Dashboard.tsx` — v0.1.19 で完了済み

## 受け入れ条件

- [ ] macOS でネイティブ Accessibility ダイアログが表示される
- [ ] ダイアログ抑制時も System Settings が開く (URL scheme)
- [ ] 権限付与後 `hook_active: true` になる
- [ ] Windows `cargo check` が通る

## 関連ドキュメント

- `ime_macos.rs` lines 118-149 — GCD dispatch_sync_f パターン
