# 重要な設計判断

## 判断 1: Entitlements.plist の既存エンタイトルメント維持

- **日時**: 2026-04-13
- **背景**: code-reviewer が `allow-unsigned-executable-memory` と `disable-library-validation` の削除を HIGH で指摘。`allow-jit` のみで十分との提案。
- **選択肢**:
  - A: 3 つとも維持 (現状)
  - B: `allow-jit` のみ残す (reviewer 推奨)
- **決定**: A (3 つとも維持)
- **理由**:
  - macOS 実機で動作確認ができない状態で削除するとアプリが起動しないリスク
  - Tauri 2.0 + ad-hoc 署名環境で `disable-library-validation` が不要かは未検証
  - 次回 macOS 実機テスト時に検証し、不要と確認できれば削除する
- **TODO**: macOS 実機テスト時に entitlement を1つずつ外して動作確認

## 判断 2: wall_server.rs のセキュリティ指摘はスコープ外

- **日時**: 2026-04-13
- **背景**: security-checker が CORS `*` と非暗号的 PRNG を HIGH で指摘
- **決定**: 本タスクのスコープ外。別タスクで対応する
- **理由**: wall_server.rs は今回の変更対象ではなく、修正すると影響範囲が拡大する
