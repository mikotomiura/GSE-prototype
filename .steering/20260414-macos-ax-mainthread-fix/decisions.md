# 設計判断

## dispatch_sync_f vs dispatch_async_f

**判断**: `dispatch_sync_f` を採用。

**理由**: `ax_prompt_for_trust()` の戻り値 (`bool`) を呼び出し元で即座に使用するため、同期 dispatch が必要。`ime_macos.rs` の TIS クエリと同一パターンで一貫性を保つ。

## pthread_main_np() ガード不採加

**判断**: 現時点では追加しない。

**理由**: `ax_prompt_for_trust()` は `start()` 内の `thread::spawn` クロージャからのみ呼ばれるため、メインスレッドから呼ばれるケースは存在しない。将来的に呼び出し元が増えた場合に検討する。code-reviewer の HIGH 指摘として記録済み。

## URL scheme フォールバック復元

**判断**: ネイティブダイアログ + URL scheme の両方を実行する (ベルト＋サスペンダー)。

**理由**: v0.1.19 でネイティブダイアログのみに切り替えた結果、ダイアログが表示されず権限取得が完全に失敗した。両方実行しても副作用なし。
