---
name: rust-standards
description: >
  GSE プロジェクトの Rust コーディング規約。src-tauri/src/ 配下の *.rs ファイルを
  書く・修正する・レビューする際に必須参照。以下の状況で必須参照:
  - unsafe ブロックを書く / 修正するとき
  - Windows API (windows crate) を呼び出すとき
  - エラーハンドリング (anyhow::Result) を追加・変更するとき
  - ログ出力 (tracing) を追加・変更するとき
  - 新しい crate を Cargo.toml に追加するとき
  - hook.rs / ime.rs / features.rs / engine.rs / logger.rs / wall_server.rs を編集するとき
allowed-tools: Read, Grep, Glob, Edit
---

# Rust コーディング規約

## このスキルの目的

GSE の Rust バックエンドに一貫した品質・安全性・保守性を確保する。
特に Windows API の unsafe 呼び出しとフックコールバックの制約を遵守させる。

## 適用範囲

### 適用するもの
- `src-tauri/src/` 配下のすべての `.rs` ファイル
- `Cargo.toml` の依存関係追加・変更

### 適用しないもの
- `src/` (Frontend TypeScript/React)
- `build.rs` (Tauri ビルドスクリプト)

---

## 主要なルール

### ルール 1: Windows API は `windows` crate のみ

`winapi` crate は禁止。`windows` crate v0.58+ のみ使用する。

```rust
// ✅ 良い例
use windows::Win32::UI::Input::KeyboardAndMouse::GetAsyncKeyState;

// ❌ 悪い例
use winapi::um::winuser::GetAsyncKeyState;
```

**Why:** `winapi` crate はメンテナンス停止。用語定義書でも禁止用語として明記。

---

### ルール 2: unsafe ブロックはラッパー構造体内に隔離し、理由をコメントで明記

Win32 API 呼び出しに限定。安全性の根拠を必ずコメントで説明する。

```rust
// ✅ 良い例
/// # Safety
/// `hwnd` は有効なウィンドウハンドルであることを呼び出し元が保証する。
unsafe fn get_window_text(hwnd: HWND) -> String {
    // SAFETY: hwnd は EnumWindows コールバックから受け取った有効な値
    let len = GetWindowTextLengthW(hwnd);
    // ...
}

// ❌ 悪い例
unsafe fn do_stuff() {
    // コメントなし・理由不明の unsafe
    SomeWinApiCall();
}
```

---

### ルール 3: ログは `tracing` のみ。`println!` / `eprintln!` 禁止

```rust
// ✅ 良い例
tracing::info!("session started: session_id={}", id);
tracing::warn!("channel full, dropping event");
tracing::error!("hook registration failed: {:?}", e);

// ❌ 悪い例
println!("session started");
eprintln!("error: {:?}", e);
```

---

### ルール 4: エラーハンドリングは `anyhow::Result`

アプリケーションレベルでは `anyhow::Result<T>` を使用。
ライブラリ的なモジュール（将来の分離を想定する場合）は `thiserror` を検討。

```rust
// ✅ 良い例
use anyhow::{Context, Result};

fn start_hook() -> Result<()> {
    let hook = unsafe { SetWindowsHookExW(...) }
        .context("failed to register keyboard hook")?;
    Ok(())
}

// ❌ 悪い例
fn start_hook() -> std::result::Result<(), Box<dyn std::error::Error>> { ... }
fn start_hook() -> Option<()> { ... }  // エラー情報を失う
```

---

### ルール 5: フックコールバック内は Atomic 操作 + channel send のみ

`hook.rs` のコールバック内でブロッキング操作・Mutex ロック・I/O・メモリアロケーションは禁止。

```rust
// ✅ 良い例（hook コールバック内）
LAST_KEY_MS.store(now_ms, Ordering::Relaxed);
let _ = TX.get().and_then(|tx| tx.try_send(event).ok());

// ❌ 悪い例（hook コールバック内）
let mut guard = ENGINE.lock().unwrap();   // Mutex ロック禁止
std::fs::write("log.txt", data);          // I/O 禁止
tracing::info!("key pressed");            // バッファ操作を伴う場合あり → 禁止
```

---

### ルール 6: 命名規則

| 種類 | 規則 | 例 |
|---|---|---|
| 変数・関数 | snake_case | `last_key_ms`, `start_hook()` |
| 型・構造体・トレイト | PascalCase | `InputEvent`, `FeatureExtractor` |
| 定数・static | SCREAMING_SNAKE_CASE | `LAST_KEY_MS`, `IME_OPEN` |
| ファイル | snake_case.rs | `wall_server.rs`, `features.rs` |

---

### ルール 7: 依存 crate 追加基準

新しい crate を追加する前に確認:
- 既存の依存で代替できないか？
- 最終リリースが 1 年以内か？
- ライセンスは MIT / Apache-2.0 互換か？
- `windows` crate の feature flags は必要最小限か？

---

## チェックリスト

コードレビュー・実装時に確認:

- [ ] `winapi` を使っていないか（`windows` crate v0.58+ のみ）
- [ ] `unsafe` ブロックに安全性コメントがあるか
- [ ] `unsafe` が Win32 API 呼び出し以外で使われていないか
- [ ] `println!` / `eprintln!` を使っていないか（`tracing` を使う）
- [ ] エラーハンドリングが `anyhow::Result` になっているか
- [ ] フックコールバック内でブロッキング処理がないか
- [ ] `cargo fmt` に従っているか
- [ ] `cargo clippy` の警告が解消されているか

---

## 補足資料

- `examples.md` — unsafe 隔離・anyhow エラーチェインの具体例

## 関連する他の Skill

- `hook-constraints` — フックコールバック固有の制約詳細
- `architecture-rules` — モジュール配置・レイヤー依存の規則
