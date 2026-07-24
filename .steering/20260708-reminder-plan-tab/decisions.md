# decisions — 本日のリマインド予定タブ

## D1: 送信判定を純粋関数 reminderClassify_ に一元化
送信(sendReminders)と表示(buildReminderPlanTab_)が別ロジックだと予定一覧と実送信がズレる。
判定を純粋関数へ抽出し単一真実源化。旧インラインとの等価性は property test(20万ケース, send/skip 一致)で担保。

## D2: 専用タブ + installable onOpen トリガー(simple onOpen は不可)
本スクリプトは管理シートの container-bound ではない標準スクリプト。simple onOpen は別スプレッド
シートで発火しないため、buildManagementSheet で `forSpreadsheet(ss).onOpen()` トリガーを冪等設置。
handler名 + getTriggerSourceId で重複ガード、旧シート宛の孤児は掃除。

## D3: P-ID のみ表示(PII 露出面の最小化)
既存ダッシュボード踏襲。実名・メールはロスタータブに閉じる。plan タブ出力は
`[pid, 区分, 詳細, 最終F4, 無音日数]` のみ。

## D4: reminderHhmm_ も Date 型を防御(code-reviewer MEDIUM)
log タブはテキスト書式だが研究者が列書式を変えると Date で返りうる。reminderYmd_ と対称に
[object Date] を先処理し、時刻表示の空欄化を防ぐ。

## ⚠ 研究者向け運用メモ
- コード更新後の**初回 buildManagementSheet 実行時に再認可ダイアログが出る**
  (ScriptApp.newTrigger が script.scripts スコープを要求するため)。承認すればメニューが有効化。
- 以後は管理シート「GSE 運用 > 🔔 本日のリマインド予定を更新」でいつでも最新化可能。
- 「リマインド運用」タブを手動ソートすると本日の送信/応答時刻表示が乱れうる(判定は不変)。
