# タスクリスト

## 実装
- [x] GCD FFI 宣言 + AxPromptCtx + ax_prompt_main_thread 追加
- [x] ax_prompt_for_trust() を dispatch_sync_f 経由に書き換え
- [x] URL scheme フォールバック復元
- [x] バージョンバンプ 0.1.19 → 0.1.20

## テスト
- [x] cargo check (Windows) — 成功 (エラー0, 警告1=既存)
- [ ] npx tsc --noEmit (Dashboard.tsx 変更なしのため省略可)

## レビュー
- [x] code-reviewer — HIGH 2件 (将来的なデッドロック防御、現時点では安全)
- [x] security-checker — CRITICAL/HIGH なし。spawn() エラーハンドリング対応済み

## 完了処理
- [ ] git commit + push + tag v0.1.20
