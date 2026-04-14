# 設計

## 実装アプローチ

`ime_macos.rs` の GCD `dispatch_sync_f` パターンを `hook_macos.rs` に適用。

## 変更対象

### 修正するファイル
- `src-tauri/src/input/hook_macos.rs` — GCD FFI + ax_prompt_for_trust 書き換え + URL fallback 復元
- `src-tauri/Cargo.toml` — version 0.1.20
- `src-tauri/tauri.conf.json` — version 0.1.20

### 新規作成するファイル
- なし

### 削除するファイル
- なし

## 既存パターンとの整合性

| 要素 | ime_macos.rs | hook_macos.rs (今回) |
|------|-------------|---------------------|
| FFI | `#[link(name = "System")]` | 同一 |
| コンテキスト | `TisQueryCtx` | `AxPromptCtx` |
| コールバック | `tis_query_main_thread` | `ax_prompt_main_thread` |

## テスト戦略

- `cargo check` (Windows)
- macOS 実機テスト (GitHub Actions リリース後)
