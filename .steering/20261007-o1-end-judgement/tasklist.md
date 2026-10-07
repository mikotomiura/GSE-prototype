# タスクリスト
- [x] 基準を研究者が決めた（起算 = 最初に記録した日・暦日 21 日・届いた日数は条件にしない・通知に含める）
- [x] 純関数（`o1LedgerDayKey_` / `o1LedgerKeyToStr_` / `o1LedgerEndJudge_` / `o1LedgerEndShown_` / `o1LedgerEndAlerts_`）
- [x] タブ（`o1LedgerWriteEnd_`）・台帳の処理への組み込み・通知の本文と件名
- [x] テスト §12・変異 14 件・既存の変異の当たる位置の確認
- [ ] リンク集の文言（「判定の機械はまだ無い」）を直す（PR #324 のマージ後に重ねる）
- [ ] 運営ワークフローの docx（版 3）
- [ ] レビュー（code-reviewer ＋ security-checker）。⚠️ Codex は当日の予算超過で不可の可能性（日付が変わったので確かめる）
- [ ] PR・CI・マージ
- [ ] 研究者: 受領台帳の Apps Script に貼り直し → `o1LedgerRun()` を 1 回手で実行
