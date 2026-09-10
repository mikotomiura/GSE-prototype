# タスクリスト

- [x] config 定数ブロックを追加 (line 80 付近)
- [x] readRoster_ に email / consentDate を追加 (consentDate は Date型正規化)
- [x] buildReminderLogTab_ / reminderLogAppend_ (LockService) / reminderLogQuery_
- [x] reminderButtonUrl_ / reminderHtmlPage_
- [x] reminderDailyBody_ / reminderDailyHtml_
- [x] reminderStalledBody_ / reminderStalledHtml_
- [x] sendReminders 本体 (参加フェーズゲート + F2起点の停滞判定)
- [x] doGet
- [x] installReminderTrigger / removeReminderTriggers
- [x] 構文チェック (node --check: SYNTAX OK)
- [x] code-reviewer レビュー → HIGH/MEDIUM 反映、doGet なりすましは受容記録(decisions.md)
- [ ] 【研究者手動】appsscript.json timeZone=Asia/Tokyo 確認
- [ ] 【研究者手動】Web アプリ公開 → exec URL を REMINDER_WEBAPP_URL に記入
- [ ] 【研究者手動】REMINDER_AUTO_SEND=false で sendReminders() dry-run → 下書き確認
- [ ] 【研究者手動】installReminderTrigger() 実行 → AUTO_SEND=true に切替

## 追加要件 (2026-07-08 後半): 管理シート刷新
- [x] 進捗目標定数 (PHASE1_TARGET_SESSIONS_PER_PID=10 / PARTICIPANTS=5) + UIパレット
- [x] buildDashboardTab_ をモダン全面刷新 (到達率/進捗バー/要フォロー自動リストアップ/参加者別進捗)
- [x] progressStatus_ (状態分類: 完了/進行中/停滞/未開始/準備中 + MNARフラグ)
- [x] 運用コントロールタブ (先頭・Phase1ステータス トグル・名前付き範囲 PHASE1_STATUS)
- [x] phase1Status_ 読取 → sendReminders が「終了」で自動停止
- [x] styleRosterModern_ (ロスターのヘッダ帯/バナー/列幅)
- [x] buildManagementSheet に buildControlTab_ / styleRosterModern_ を配線
- [x] refreshRosterStatus → buildDashboardTab_(ss, f4, f2) で集計再利用
- [x] 構文チェック (SYNTAX OK)
- [x] code-reviewer (ダッシュボード/コントロール/再実行耐性) → MEDIUM 3件反映
- [x] /cross-review (Claude+Codex, GAS diff) → 両者一致/Claude/Codex 指摘を反映(decisions D10)
  - [x] doGet を確認ページ方式に(GET プリフェッチ誤記録対策)+ ロスター実在チェック
  - [x] reminderSendingAllowed_ (送信は fail-closed) / phase1Status_ は表示用 fail-open
  - [x] reminderLogAppend_ tryLock+locked / reminderParseYmd_ Date.UTC / dashboard catch にログ
- [x] 構文チェック (SYNTAX OK)
- [ ] コミット
