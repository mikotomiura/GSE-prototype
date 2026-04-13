# 重要な設計判断

## 判断 1: GetMessageW → PeekMessageW ポーリング

- **判断日時**: 2026-04-13
- **背景**: Windows キーボードフック (`WH_KEYBOARD_LL`) のコールバックが呼ばれない問題
- **選択肢**:
  - A: `GetMessageW` ブロッキングループを維持 (Windows 標準パターン)
  - B: `PeekMessageW` + `PM_REMOVE` ポーリングに変更
  - C: `MsgWaitForMultipleObjects` でメッセージ待機
- **採用**: B
- **理由**: スタンドアロン診断テストで `PeekMessageW` パターンが 10/10 イベントを
  正しくキャプチャすることを実証。Tauri のマルチスレッド環境では `GetMessageW` が
  フックメッセージを正しく配信しない可能性がある。
- **トレードオフ**: 1ms のポーリング間隔により微小な CPU 使用量増加 (~0.1%)。
  `GetMessageW` はメッセージがない時に完全にスリープする。
- **影響範囲**: hook_windows.rs のメッセージループのみ
- **見直しタイミング**: CPU 使用量が問題になった場合、`MsgWaitForMultipleObjects` (選択肢 C) を検討

## 判断 2: フック初期化を setup() に移動

- **判断日時**: 2026-04-13
- **背景**: PeekMessageW 変更後もフックが動作しないことから、初期化タイミングを疑った
- **選択肢**:
  - A: `tauri::Builder.run()` の前に初期化 (既存)
  - B: `setup()` クロージャ内で初期化 (Tauri 初期化完了後)
  - C: `setup()` 内で `std::thread::sleep(1s)` の遅延を追加
- **採用**: B
- **理由**: `tauri::Builder.run()` がウィンドウシステム・tokio・WebView2 を初期化する。
  この初期化プロセスがそれ以前にインストールされた低レベルフックを無効化する可能性がある。
  `setup()` は初期化完了後にメインスレッドで実行されるため、安全なタイミング。
- **トレードオフ**: フック開始が Tauri 初期化分（数百ms）遅れるが、ユーザーがボタンを
  押す前に完了するため実用上の影響なし。
- **影響範囲**: lib.rs の初期化フロー、IME ポーリングスレッドも同様に移動
- **見直しタイミング**: Tauri のメジャーバージョンアップ時に setup() の実行タイミングを再確認

## 判断 3: xattr -d → xattr -dr + codesign 再署名

- **判断日時**: 2026-04-13
- **背景**: macOS で `xattr -d` 実行後も Gatekeeper がブロックする問題
- **選択肢**:
  - A: `xattr -d` (非再帰、.app ディレクトリのみ)
  - B: `xattr -cr` (再帰、全属性削除)
  - C: `xattr -dr` + `codesign --force --deep --sign -`
- **採用**: C
- **理由**:
  - A: .app 内部バイナリの quarantine 属性が残り、Gatekeeper がブロック
  - B: コード署名を含む全属性を削除し、Input Monitoring の TCC が壊れる
  - C: quarantine のみ再帰削除 + ローカル ad-hoc 再署名で Gatekeeper パス
- **トレードオフ**: ユーザーに2つのコマンド実行を要求。Apple Developer ID ($99/年) で根本解決可能。
- **影響範囲**: README のインストール手順
- **見直しタイミング**: Apple Developer ID を取得した場合はコマンド不要になる

## 判断 4: HOOK_ACTIVE を全プラットフォーム共通化

- **判断日時**: 2026-04-13
- **背景**: Windows の `get_hook_status` が常に `true` を返し、フック失敗が隠蔽されていた
- **選択肢**:
  - A: macOS のみ HOOK_ACTIVE を使用 (既存)
  - B: 全プラットフォームで HOOK_ACTIVE を使用
- **採用**: B
- **理由**: Windows でもフックの実際の状態を追跡し、失敗時にユーザーに通知すべき。
  macOS と同じ `HOOK_ACTIVE` パターンを使うことでコードの対称性も向上。
- **トレードオフ**: なし
- **影響範囲**: hook.rs, hook_windows.rs, lib.rs, Dashboard.tsx
- **見直しタイミング**: なし（恒久的な改善）
