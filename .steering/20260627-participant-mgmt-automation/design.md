# 設計

## 実装アプローチ

既存 `GSE_Phase1_Form_Builder.gs` に **GAS 関数を追記**する（新規ファイルは作らない）。
既存の `nextParticipantId_` / 管理シート構造 / `recordFormUrl` をそのまま再利用し、
重複ロジックを避ける。フォーム回答は **Form の destination sheet ではなく
`FormApp.openById(...).getResponses()` で直接取得**する（destination 設定不要・
P-ID 列を直接読める）。そのため `recordFormUrl` を拡張して `id`（form ID）も
Script Properties に保存する。

### Task 1: F1 提出トリガ
- `installF1Trigger()`: 既存の onF1Submit トリガを全削除→`ScriptApp.newTrigger('onF1Submit')
  .forForm(FORM_ID).onFormSubmit().create()`（installable・二重作成防止）。
- `onF1Submit(e)`:
  1. `e.response.getItemResponses()` を **設問タイトルのキーワードで照合**してマップ化
     （title 一致は脆いので「年齢」「IME」「OS」「メールアドレス」「お名前」等の部分一致で頑健化）。
  2. 適格性判定 `isEligibleF1_()`: Q1理解✓ ∧ Q2同意✓ ∧ (Q3=18歳以上 ∨ (18歳未満 ∧ Q4=提出済み))
     ∧ Q6 IME=はい ∧ Q7 OS∈{Windows,macOS} ∧ メール present。不適格は発番せずログのみ。
     ※不適格分岐は contact section 到達前に SUBMIT するためメール/氏名が無い→欠落を許容。
  3. 冪等性: ロスターのメール列(col3)に同一メール（trim/小文字比較）があればスキップ。
  4. `nextParticipantId_(roster)` で発番→ロスターに行追加（P-ID/氏名/メール/OS/同意日/
     condition='baseline'）。
  5. 通知メール: `GmailApp.createDraft(email, subject, body)` で **下書き作成**
     （AUTO_SEND 定数=false。true で MailApp.sendEmail に切替可・既定は下書き）。
     本文は `f1EmailBody_(pid)` テンプレ（P-ID＋次ステップ：アプリ入手・gse-package コマンド例・
     pubkey.txt 入手先・Dropbox File Request URL）。

### Task 2: 管理シート拡充
- `refreshRosterStatus()`: F2/F4/F5 を form ID で開き `getResponses()`、各回答の P-ID 設問値で
  集計。ロスターの該当 P-ID 行に F2事前(○/日付)・F4回答(計)・セッション数(F4のsession_id distinct)
  ・F5事後(○) を書き戻す。手動実行 or 時間トリガ。
- `buildDashboardTab_(ss)`: 「進捗ダッシュボード」タブに 総数/F2完了率/F5完了率/平均セッション数、
  未提出者リスト、MNAR 無回答フラグ（F2提出済かつF4=0、セッション有かつF5未、撤回/除外は除外）。
- データ検証 `applyRosterValidation_(ss)`: condition 列=baseline/intervention、OS 列=Windows/macOS、
  撤回/除外 列=（空）/撤回/除外 のドロップダウン。P-ID 形式 `^P\d{3,}$`・重複は `validateRoster()`
  でログ警告＋条件付き書式で着色。
- 対応表保護: ロスタータブ先頭に「実名↔P-ID 対応表。研究者のみ・共有禁止」注意行を追加。

## 変更対象

### 修正するファイル
- `Form_Phase1/GSE_Phase1_Form_Builder.gs`:
  - `recordFormUrl` に `id` 保存を追加
  - `buildManagementSheet` から `buildDashboardTab_` / `applyRosterValidation_` を呼ぶ
  - `buildRosterTab_` に対応表注意行を追加
  - Task1/Task2 の新規関数群を追記、共通ヘルパ（タイトル照合・ロスター行追加）を追加

### 新規作成するファイル
- なし（全て .gs 内に追記）

## 影響範囲

- 既存の `addParticipant()`（手動採番）は温存（フォールバック）。`onF1Submit` と同じ
  `nextParticipantId_` / ロスター構造を共有するため整合。
- `recordFormUrl` の `id` 追加は後方互換（既存呼び出しの引数不変、保存 JSON にキー追加のみ）。
- フォーム設問タイトルを変更すると照合が壊れる → タイトルは安定前提。部分一致で緩衝。

## 既存パターンとの整合性

- 管理シートのタブ追加は `buildLinksTab_`/`buildRosterTab_`/`buildSubmissionTab_` と同じ
  `insertSheet` + 再実行で入力を壊さないガード方式に揃える。
- ログは既存同様 `Logger.log` に絵文字プレフィックス（✅/❌/ℹ️）。

## テスト戦略

- GAS は手元実行不可のため **`node --check` で構文検証**（GAS グローバルは parse 通過）。
- ロジック検証: 純粋関数（`isEligibleF1_` / `f1EmailBody_` / 集計）を切り出し、Node で
  最小スタブを当てて単体確認（scratchpad、リポには含めない）。
- 実機（トリガ設定・下書き確認・回答取り込み）はユーザーがチェックリストで検証。

## ロールバック計画

- .gs への追記のみ。問題時は branch を破棄 or 該当関数を削除。トリガは
  `installF1Trigger` の削除ロジック相当を手動 or `removeF1Triggers()` で解除。
- 既存フォーム生成 (`buildForm` 等) は不変なので既存運用に影響なし。
