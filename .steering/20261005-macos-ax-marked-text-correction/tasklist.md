# タスクリスト

## 準備
- [x] 引き継ぎ（IME 論文の `next-session-ime-paper-results.md` §2 の 0）と判断 151・153 を読む
- [x] 一次を取り直す（Apple の定数の JSON・C の定数の JSON・WebKit のソース 2 本）
- [x] 消費者を grep で洗う（decisions.md 判断 1）

## 実装
- [x] `docs/agent-shared.md` 制約 7 の末尾
- [x] 調査メモ §3.2・§7.5・§7.6
- [x] `docs/architecture.md` の IME 状態機械の理由
- [x] ~~`src-tauri/src/input/ime_compose.rs` の doc コメント~~ → 戻した（kit の逐語コピー・decisions 判断 4）
- [x] `docs/architecture/workspace-behavior-observation.md` 83 行に注（2 巡目）

## テスト
- [x] `python scripts/check_citations.py` 違反なし
- [x] `ime_compose.rs` が `cf320319` と同じバイト
- [x] grep で旧文が訂正の印つきでだけ残ることを確かめる

## レビュー
- [x] code-reviewer ∥ security-checker
- [x] /cross-review（パス限定・Codex 1 回）
- [x] 指摘への対応（decisions 判断 4）

## 完了処理
- [x] git commit（パス指定）
- [ ] 出荷フロー（git-workflow ルール 6）
