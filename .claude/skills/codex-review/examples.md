# Codex Review Examples

## 例 1: 機能追加 PR (Rust, 約 150 行 diff)

入力:
- src-tauri/src/analysis/probe_scheduler.rs 追加 (120 行)
- src-tauri/src/analysis/mod.rs 更新 (30 行)

Claude のレビュー: 「1Hz ゲートとの競合なし、エラーハンドリング適切」
Codex のレビュー: 「probe_interval が 0 の時の除算エラーの可能性、scheduler が drop された時の channel 送信エラーが無視されている」

→ 統合判断: 除算エラーは実際には起こらない (u64 で最小 1 が保証されている) が、コメントで不変条件を明記。channel エラーは tracing::warn! で記録するよう修正。

## 例 2: バグ修正 (30 行 diff)

両者一致: 「修正は正しいが、同様の問題が analysis/engine.rs にも存在する可能性」 → engine.rs も確認して修正。

## 例 3: 大規模 refactor (2500 行 diff)

Step 1 で `manual_approval_threshold_lines: 2000` を超過。
`/cross-review` コマンドがユーザーに「2500 行 diff です。Codex に渡しますか?」と確認。
承認後に実行。
