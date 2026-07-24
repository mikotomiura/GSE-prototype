# design — 本日のリマインド予定タブ

## アプローチ
`sendReminders` のループ内にあった 1 名分の送信判定を純粋関数 `reminderClassify_` に抽出し、
送信(sendReminders)と表示(buildReminderPlanTab_)の**単一真実源**にする。

### reminderClassify_(p, f4, f2, log, today, tz) → { category, latest, idleDays, ... }
category(10 種):
- send_daily / send_stalled … 今回送る対象(=予定)
- sent_daily / sent_stalled … 本日既に送信済み(停滞は lastStalled===today で判定)
- responded … 本日 doGet 応答済み(抑制)
- throttled_stalled … 停滞スロットル中(直近送信済で連投回避)
- submitted_today … 本日 F4 提出済み(送信不要)
- not_eligible … 未オンボード(NDA未署名/F2未提出 かつ F4無)
- no_email … 送信先メール未登録
- excluded … 撤回/除外(col13)

送信は category ∈ {send_daily, send_stalled} のみ。既存の分岐条件と等価
(eligible ゲート → 本日提出済み除外 → idleDays 算出 → 停滞/日次 → スロットル/応答/送信済み抑制)。

### buildReminderPlanTab_(ss, f4, f2)
- 全再描画(clear + breakApart + CF リセット)。既存 dashSection_/styleTableHeader_ を流用。
- countByPid_("F4"/"F2") は引数優先・無ければ自前取得(buildDashboardTab_ と同パターン)。
- reminderLogQuery_ で判定用マップ、reminderTodayEvents_ で本日の送信/応答時刻(表示用)を取得。
- category → 4 グループにバケット分けし、① 送信予定は無音日数 desc でソート。
- バナー: phase1Status_/REMINDER_ENABLED/REMINDER_AUTO_SEND を反映(送信停止・下書きモード警告)。

### メニュー(installable onOpen)
本スクリプトは管理シートの container-bound ではない(標準スクリプト)ため、simple onOpen は
発火しない。buildManagementSheet で `ScriptApp.newTrigger("onOpenMgmt").forSpreadsheet(ss)` を
冪等設置(handler+sourceId で重複ガード)。onOpenMgmt が「GSE 運用」メニューを生成。

## 変更対象(すべて Form_Phase1/GSE_Phase1_Form_Builder.gs)
- 定数 REMINDER_PLAN_TAB 追加
- sendReminders ループを reminderClassify_ ベースへ置換 + 末尾で buildReminderPlanTab_ 再描画
- 新規: reminderClassify_ / buildReminderPlanTab_ / renderPlanSection_ / reminderPlanDescribe_ /
  reminderTodayEvents_ / reminderHhmm_ / refreshReminderPlan / onOpenMgmt / installMgmtMenuTrigger_
- buildManagementSheet に buildReminderPlanTab_ + installMgmtMenuTrigger_ を追加
- refreshRosterStatus 末尾に buildReminderPlanTab_(ss, f4, f2) を追加

## テスト戦略
GAS のため自動テスト不可。ロジック等価性はコードレビューで担保:
- reminderClassify_ の送信分岐が旧 sendReminders と 1:1 対応することを表で照合。
- 手動: 研究者環境で buildManagementSheet → refreshReminderPlan を実行し 4 グループ表示確認。
