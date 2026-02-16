cargo testを実行したところ、`windows` クレート (v0.58.0) の仕様変更に起因する37件のコンパイルエラーが発生しました。
以下の指示に従って、コードを `windows` v0.58.0 仕様に適合させてください。

## 1. Cargo.toml の修正
`[dependencies.windows]` の `features` に以下を追加してください。
- `"Win32_UI_Input_KeyboardAndMouse"` (VK_BACK等がここへ移動しました)

## 2. インポートパスの修正
- **`src/input/keyboard.rs`**:
  - `VK_BACK` は `windows::Win32::UI::WindowsAndMessaging` から削除されました。
  - 代わりに `windows::Win32::UI::Input::KeyboardAndMouse::VK_BACK` をインポートしてください。
- **`src/ui/overlay.rs`**:
  - `GetMonitorInfoW`, `MonitorFromPoint`, `MONITOR_DEFAULTTOPRIMARY` は `windows::Win32::Graphics::Gdi` に移動しました。そちらからインポートしてください。
- **`src/main.rs`**:
  - `PostQuitMessageW` は存在しません。`PostQuitMessage` (Wなし) を使用してください。

## 3. 型と戻り値の修正 (v0.58対応)
`windows` v0.58では、多くのAPIが `Result<T>` を返すようになり、ハンドル型 (`HWND`, `HHOOK`) は `isize` ではなく構造体になっています。

### `src/input/keyboard.rs`
- **Hookハンドルの扱い**: `HHOOK` はポインタ型です。`isize` として保持している `HOOK_HANDLE` との変換にはキャストが必要です。
  - `isize` → `HHOOK`: `HHOOK(value as *mut std::ffi::c_void)`
- **`CallNextHookEx`**:
  - 引数の型合わせ: `WPARAM(w_param)`, `LPARAM(l_param)`
  - 戻り値: `LRESULT` 型で返ってきます。`.0` で内部の `isize` を取り出してください。
- **`SetWindowsHookExW`**:
  - 戻り値が `Result<HHOOK>` になりました。`?` または `.unwrap()` で処理してください。
  - 失敗判定は `hook_handle.is_invalid()` ではなく、`Result` の `Err` で判定してください。
- **`UnhookWindowsHookEx`**:
  - 引数を `HHOOK` 型にキャストして渡してください。

### `src/main.rs` & `src/ui/overlay.rs`
- **`CreateWindowExW`**:
  - 戻り値が `Result<HWND>` になりました。`.unwrap()` して `HWND` を取得してください。
- **`GetModuleHandleW`**:
  - 戻り値が `Result<HMODULE>` です。`.unwrap()` してください。
- **`AtomicIsize` との変換**:
  - `HWND` から `isize` への変換: `hwnd.0 as isize`
  - `isize` から `HWND` への変換: `HWND(value as *mut std::ffi::c_void)`
- **`SetLayeredWindowAttributes`**:
  - 戻り値が `windows::core::Result<()>` になりました。`.as_bool()` は削除し、`Err` かどうかで判定してください。

## 4. その他
- `src/input/keyboard.rs` の `last_state != Some(FlowState::Flow)` でエラーが出ています。`mutex_guard` との比較なので、`*last_state` とデリファレンスしてください。

これらの修正を一括で行い、`cargo test --verbose 2>&1 | Tee-Object -FilePath $env:TEMP\cargo_test_output.txt` が通るようにしてください。