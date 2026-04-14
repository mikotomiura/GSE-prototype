# 設計判断

## ad-hoc 署名ではプログラムによる TCC 権限付与は不可能

v0.1.17→v0.1.19→v0.1.20 の3回の修正で確認。URL scheme, AXIsProcessTrustedWithOptions (バックグラウンド), AXIsProcessTrustedWithOptions (メインスレッド GCD) 全て失敗。根本解決は Apple Developer Program 署名。即時対応として手動付与の UX を改善する。

## Tauri 2.0 カスタムコマンドは capabilities 登録不要

code-reviewer が capabilities/default.json への登録を HIGH 指摘したが、Tauri 2.0 ではカスタム `#[tauri::command]` は `core:default` でカバーされる。既存の get_diagnostics, reset_input_monitoring 等が実機動作している事実で確認済み。
