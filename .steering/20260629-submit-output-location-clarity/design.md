# 設計

## アプローチ
`src-tauri/src/bin/submit.rs` の成功時出力 (`Ok(Some(r))` 分岐) のみ変更する。
匿名化/暗号化/出力先決定 (`packaging.rs`) は不変。

1. ヘルパ `reveal_in_file_manager(&Path)` を追加 (best-effort・戻り値なし)。
   - Windows: `explorer /select,<file>` でファイル選択状態で開く。
   - macOS: `open -R <file>` で Finder reveal。
   - Linux: `xdg-open <親フォルダ>`。
   既存パターン (lib.rs 1145-1152) に倣う。
2. 成功メッセージで絶対パスをインデントして目立たせ、OneDrive/iCloud リダイレクト注意書きを追加。
3. 生成後に `reveal_in_file_manager(&r.out_path)` を呼ぶ。

## 変更対象
- `src-tauri/src/bin/submit.rs` のみ。

## テスト戦略
- `cargo build --features package --bin gse-submit` でビルド確認。
- 手動: ダミー session + pubkey で実行し、Finder が .age を選択して開くこと・絶対パス表示を確認。
- 既存ロジック不変のため `cargo test` 回帰は packaging テストで担保。
