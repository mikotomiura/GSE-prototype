# 設計判断記録

## Decision 1: macOS 版リポのクローンを参照しない

**判断**: GSE-prototype-for-mac リポをクローンせず、既存デザイン言語から CSS を設計する。

**Why:** 既存 App.css の `--color-*` 変数・`rgba` 透明度パターン・角丸値が明確で、同じ言語から設計すれば一貫性を保てる。外部 CSS の取り込みはスタイル衝突リスクと不要なマージ作業を生む。

**How to apply:** 新規 CSS クラスは常に既存 App.css のパターンを参照して追加すること。

---

## Decision 2: handleStart エラー時は return で十分

**判断**: エラー通知 UI を新設せず、`catch` 内で `return` するだけにする。

**Why:** エラー時にスタート画面に留まれば、macOS 権限未付与時は `hookActive === false` の permission-banner が説明を担う。エラー専用 UI を追加すると、コードパスが増え整合性の維持が困難になる。

**How to apply:** セッション開始失敗の UX は「スタート画面に戻る + permission-banner で案内」の 2 ステップで完結する設計。

---

## Decision 3: hookActive フォールバックを false（悲観的）にする

**判断**: `get_hook_status` IPC 失敗時は `setHookActive(false)` にする（変更前: `true`）。

**Why:** `true` にすると macOS で権限なし状態が隠蔽され、ユーザーが問題を認識できない。`false` にすれば permission-banner が表示され診断可能になる。Windows では `get_hook_status` がエラーを返すことは通常ないため影響なし。

**How to apply:** IPC の応答欠如は「権限問題の可能性」として扱う。

---

## Decision 4: tauri-plugin-opener の Rust 側は今タスクで削除しない

**判断**: `Cargo.toml` / `lib.rs` の `tauri_plugin_opener` を今タスクのスコープ外とし残置。capabilities/default.json の `opener:default` のみ削除。

**Why:** Rust バックエンドはスコープ外（ユーザー指示）。npm の未使用依存削除は完了しており、capabilities から権限も外れた。Cargo.toml/lib.rs の整理は次の Rust タスクで実施する。

**How to apply:** 次の Rust 側タスクで `Cargo.toml` から `tauri-plugin-opener = "2"` 削除・`lib.rs` の `.plugin(tauri_plugin_opener::init())` 削除を実施すること。

---

## Decision 5: .qr-url の !important は specificity で解決

**判断**: `.qr-url { font-size: 0.8rem !important; ... }` を `.wall-layer .qr-url { font-size: 0.8rem; ... }` に変更。

**Why:** `.wall-layer p` の `font-size: 1.5rem` を上書きするために `!important` が使われていたが、セレクタの specificity を上げることで `!important` 不要になる。`!important` は将来の上書きを困難にするため避けるべき。

**How to apply:** Overlay の `.wall-layer` 内で使うスタイルは `.wall-layer .classname` のようにコンテキスト付きセレクタを使う。
