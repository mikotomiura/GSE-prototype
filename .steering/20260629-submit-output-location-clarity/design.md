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

## 追補設計: 参加者ID 対話入力
**問題**: アプリの generate_participant_id() = `P{bits:012x}` (例 P02165e17b7b1) が
そのまま `.age` ファイル名に入り、研究割当の P006 等にならない (Pxxx が「崩れて」見える)。

**方針** (submit.rs のみ。packaging.rs 不変):
- `participant` はファイル名と is_valid_participant_id 検証のみに使われ、暗号化内容には
  不使用 (確認済) なので、ファイル名ラベル用 ID を対話で差し替えても匿名化保証は不変。
- ラベル ID 解決順: `GSE_PARTICIPANT_ID`/`GSE_PID` env (自動化) → 対話入力。
  対話のデフォルトは永続ファイル値。ただし自動生成形式 (P+12桁 hex) はデフォルトに
  採用せず強制入力 (崩れた ID の混入防止)。
- 入力は trim + 大文字化 + is_valid_participant_id 検証、最大3回リトライ。
  EOF/非対話はデフォルトへフォールバック (テスト・headless 互換)。
- セッション探索 (入力 NDJSON の場所) は従来の read_persisted_participant_id のまま
  (default_session_dir は非 dataset 経路で participant 非依存。研究者の GSE_DATASET 経路を壊さない)。
