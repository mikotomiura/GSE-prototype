# タスクリスト

## 準備
- [x] 引き継ぎメモ (`_handoff/next-session-prompt-submission-receipt-and-windows-hook-test.md`) を読む
- [x] ★ 前提を一次資料で確かめる → **引き継ぎメモの「`SubmissionStatus` に `sent` がある」は誤り**
      (`design.md` 冒頭に訂正を記録)

## 実装 (backend)
- [x] `SUBMIT_LAST_SENT_MS` / `SUBMIT_LAST_SENT_COUNT` / `SUBMIT_IN_FLIGHT` を追加
- [x] `record_sent_if_any()` — `sent > 0` のときだけ書く純関数
- [x] `InFlightGuard` — panic でも in-flight を戻す
- [x] `spawn_reconcile` で **スレッドの外**から in-flight を立てる (D-3)
- [x] `SubmissionStatusDto` に `sending` / `last_sent_ms` / `last_sent_count`

## 実装 (frontend)
- [x] `SubmissionStatus` interface を backend と同期
- [x] 送信中カード (新規)
- [x] レシートカード (新規・`awaiting_approval === 0` gate 付き)
- [x] 未送信 0 件の肯定形カード (新規)
- [x] 未送信カードを `!sending` で抑止
- [x] 送信中はポーリングを 1 秒に

## テスト
- [x] `only_a_real_send_writes_the_receipt` (5 段: 根拠無し / 0 件 / 成功 / **空振りで消えない** / 更新)
- [x] `sent_is_read_from_the_real_summary_line` (submit.rs が実際に出す JSON 形)
- [x] `in_flight_returns_to_zero_even_on_panic`
- [x] `cargo test --workspace --features package` → **341 passed / 0 failed** (旧 338 + 3)
- [x] `npx tsc --noEmit` → exit 0
- [x] `cargo clippy --workspace --features package --all-targets` → 新規警告 0 / error 0

## ★ 実マウント検証 (機械検査の外)
- [x] `scripts/tests/submission-receipt-view.html` を作成 (`__TAURI_INTERNALS__` shim)
- [x] 7 状態を **実 CSS・実コンポーネント**で描画 → 表示/非表示が設計表どおり
- [x] ⚠️★ **偽レシートの検査**: `awaiting_after_send` (前回のレシート在り + 確認待ち)
      でレシートが **出ないこと**を実測
- [x] 対照つきの輝度差測定 → 全カードの最小コントラスト比 **8.01**
      (対照 = 既存の未送信カード 10.43 / 確認カード 8.01)
- [x] スクリーンショットで実描画を目視

## レビュー
- [x] 自己レビュー (diff 全読み)
- [ ] ⚠️ `code-reviewer` / `security-checker` / `/cross-review` — **本セッションでは未実施**
      (セッション既定で subagent 起動が禁止されているため。★ 完了報告に明記する)

## ドキュメント
- [x] `design.md` / `decisions.md` を最終化
- [ ] docs/ の更新 — 不要 (画面の追加のみ・schema 不変)

## 完了処理
- [x] git commit
