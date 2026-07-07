# 設計: Phase1 リマインドメール

## 変更対象
- `Form_Phase1/GSE_Phase1_Form_Builder.gs` のみ (追加中心)

## アプローチ
既存の `countByPid_` / `readRoster_` / `f1EmailHtml_` の作法にそのまま乗せる。
単一エントリ `sendReminders()` を 20:00 トリガーで1日1回実行し、
per-person で「日次リマインド / 停滞チェックイン / 送らない」を判定 → 二重メール回避。

## 追加する定数 (config ブロック, line 79 付近)
- `REMINDER_ENABLED` / `REMINDER_AUTO_SEND` (F1 の AUTO_SEND と独立に制御)
- `REMINDER_DAILY_HOUR = 20`
- `REMINDER_STALLED_DAYS = 2`
- `REMINDER_STALLED_THROTTLE_DAYS = 2` (停滞メールの再送間隔)
- `REMINDER_WEBAPP_URL` (Web アプリ公開後に研究者が記入。空なら doGet ボタンをテキスト案内に縮退)
- `REMINDER_DAILY_SUBJECT` / `REMINDER_STALLED_SUBJECT`

## 追加する関数
- `sendReminders()` — 20:00 トリガー本体。ロスター×F4集計×応答ログを突合し送信判定
- `doGet(e)` — `?pid=&action=will_do|rest` を受け「リマインド運用」タブに記録、完了HTML返却
- `buildReminderLogTab_(ss)` — 「リマインド運用」タブ(冪等作成)。列: timestamp / P-ID / 種別 / 日付
- `reminderLogAppend_(ss, pid, kind)` — 追記ヘルパ
- `reminderLogQuery_(ss)` — 当日応答・当日送信・最終停滞送信日を引くヘルパ
- `reminderDailyBody_ / reminderDailyHtml_` — 日次リマインド文面 (ボタン2つ)
- `reminderStalledBody_ / reminderStalledHtml_` — 停滞チェックイン文面 (気遣い)
- `reminderButtonUrl_(pid, action)` — Web アプリ URL 組み立て
- `installReminderTrigger()` / `removeReminderTriggers()` — 時刻トリガー設置/削除
- `readRoster_` に `email`(col3)・`consentDate`(col6) を追加 (additive・既存利用箇所に無害)

## 送信判定ロジック (sendReminders)
```
today = yyyy-MM-dd (script TZ)
f4 = countByPid_("F4")
log = reminderLogQuery_()  // 当日応答/当日送信/最終停滞送信
for each active roster row (excluded を除外, email あり):
  submittedToday = f4[pid].latest === today            -> 送らない
  respondedRestToday = log.rest[pid] === today         -> 日次は送らない
  daysSince = latest ? diffDays(today, latest) : diffDays(today, consentDate or today)
  if daysSince >= STALLED_DAYS:
     if lastStalledSent within THROTTLE_DAYS -> 送らない
     else -> 停滞チェックイン
  else:
     if respondedRestToday -> 送らない
     if dailyAlreadySentToday -> 送らない
     else -> 日次リマインド
  送信したら reminderLogAppend_(kind)  // 冪等記録
```

## テスト戦略 (GAS: cargo test 不可)
- Apps Script では静的検証中心。手動で:
  1. `sendReminders()` を `REMINDER_AUTO_SEND=false` (下書き) で dry-run し、
     Gmail 下書きと「リマインド運用」タブの記録内容を目視確認。
  2. doGet を Web アプリ /dev URL に `?pid=P001&action=rest` で叩き、完了画面と
     タブ記録を確認。
  3. 冪等性: 同じ日に `sendReminders()` を2回叩いても2通目が出ないこと。
- 送信ロジックの純粋部分 (diffDays 等) は小さく切り出しコメントで不変条件を明記。

## セキュリティ / プライバシー
- doGet は未認証公開。pid は擬似匿名(既存短縮URLも pid を URL に載せる方針)。
  action ホワイトリスト + pid 正規表現で不正入力を弾く。実名/メールは URL に載せない。
- ログ出力は maskEmail_ を使う (Apps Script 実行ログはクラウド保存)。

## 運用 (研究者が手動)
1. Web アプリをデプロイ (公開: 全員/匿名, 実行: 自分) → exec URL を `REMINDER_WEBAPP_URL` に記入
2. `installReminderTrigger()` を1回実行して 20:00 日次トリガー設置
3. 初日は `REMINDER_AUTO_SEND=false` で下書き確認してから true に切替推奨
