# tasklist — 本日のリマインド予定タブ

- [x] 定数 REMINDER_PLAN_TAB 追加
- [x] reminderClassify_ 抽出(単一真実源)
- [x] sendReminders ループを classifier ベースへ等価リファクタ
- [x] 等価性を property test で検証(旧inline vs 新classify、200k ケース一致)
- [x] reminderTodayEvents_ / reminderHhmm_(表示用の本日イベント時刻)
- [x] buildReminderPlanTab_ / renderPlanSection_ / reminderPlanDescribe_
- [x] refreshReminderPlan(手動最新化)
- [x] onOpenMgmt + installMgmtMenuTrigger_(カスタムメニュー)
- [x] buildManagementSheet / refreshRosterStatus / sendReminders への配線
- [x] node --check 構文検証 OK
- [x] code-reviewer で判定等価性レビュー(HIGH 無し。MEDIUM=reminderHhmm_ Date防御 / LOW=孤児トリガー掃除 を反映)
- [ ] 研究者手動: buildManagementSheet → refreshReminderPlan で 4 グループ表示確認(初回は再認可あり)
- [ ] finish-task(steering 最終化) / 必要なら cross-review
